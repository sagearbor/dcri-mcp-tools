#!/usr/bin/env python3
"""
MCP Client for testing MCP servers
Implements JSON-RPC 2.0 client that communicates with MCP servers via stdio
"""

import sys
import json
import subprocess
import threading
import queue
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import uuid
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    command: List[str]
    description: str = ""
    cwd: Optional[str] = None
    env: Optional[Dict[str, str]] = None


class MCPClient:
    """MCP Client that communicates with servers via stdio"""

    def __init__(self, server_config: MCPServerConfig):
        self.config = server_config
        self.process: Optional[subprocess.Popen] = None
        self.response_queue = queue.Queue()
        self.reader_thread: Optional[threading.Thread] = None
        self.writer_lock = threading.Lock()
        self.request_id = 0
        self.pending_requests: Dict[Any, threading.Event] = {}
        self.responses: Dict[Any, Any] = {}
        self.initialized = False

    def start(self) -> bool:
        """Start the MCP server process"""
        try:
            logger.info(f"Starting MCP server: {self.config.name}")
            logger.debug(f"Command: {' '.join(self.config.command)}")

            self.process = subprocess.Popen(
                self.config.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
                cwd=self.config.cwd,
                env=self.config.env
            )

            # Start reader thread
            self.reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self.reader_thread.start()

            # Start stderr reader thread
            stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
            stderr_thread.start()

            # Initialize the connection
            if self._initialize():
                logger.info(f"MCP server {self.config.name} started successfully")
                return True
            else:
                logger.error(f"Failed to initialize MCP server {self.config.name}")
                self.stop()
                return False

        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            return False

    def stop(self):
        """Stop the MCP server process"""
        if self.process:
            try:
                # Send shutdown request
                if self.initialized:
                    self._send_request("shutdown", {})
                    time.sleep(0.5)  # Give server time to shutdown gracefully

                # Terminate process if still running
                if self.process.poll() is None:
                    self.process.terminate()
                    time.sleep(0.5)

                    # Force kill if still running
                    if self.process.poll() is None:
                        self.process.kill()

                logger.info(f"MCP server {self.config.name} stopped")
            except Exception as e:
                logger.error(f"Error stopping MCP server: {e}")

    def _read_stderr(self):
        """Read stderr output from the server"""
        if not self.process or not self.process.stderr:
            return

        try:
            for line in self.process.stderr:
                if line.strip():
                    logger.debug(f"[{self.config.name} stderr] {line.strip()}")
        except Exception as e:
            logger.error(f"Error reading stderr: {e}")

    def _read_output(self):
        """Read stdout output from the server"""
        if not self.process or not self.process.stdout:
            return

        buffer = ""
        while self.process and self.process.poll() is None:
            try:
                # Read character by character to handle both formats
                char = self.process.stdout.read(1)
                if not char:
                    break

                buffer += char

                # Check for Content-Length header
                if buffer.startswith("Content-Length:"):
                    if "\r\n\r\n" in buffer:
                        # Parse headers
                        headers_end = buffer.index("\r\n\r\n")
                        headers = buffer[:headers_end]

                        # Extract content length
                        for line in headers.split("\r\n"):
                            if line.startswith("Content-Length:"):
                                content_length = int(line.split(":")[1].strip())
                                break

                        # Read the content
                        buffer = buffer[headers_end + 4:]  # Skip past headers
                        while len(buffer) < content_length:
                            buffer += self.process.stdout.read(content_length - len(buffer))

                        # Parse JSON message
                        message = json.loads(buffer[:content_length])
                        self._handle_message(message)

                        # Reset buffer for next message
                        buffer = buffer[content_length:] if len(buffer) > content_length else ""

                # Check for direct JSON (newline-delimited)
                elif "\n" in buffer:
                    lines = buffer.split("\n")
                    for line in lines[:-1]:
                        if line.strip():
                            try:
                                message = json.loads(line)
                                self._handle_message(message)
                            except json.JSONDecodeError:
                                pass  # Might be partial message
                    buffer = lines[-1]  # Keep incomplete line

            except Exception as e:
                logger.error(f"Error reading output: {e}")
                buffer = ""

    def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming JSON-RPC message"""
        logger.debug(f"Received message: {message}")

        # Check if it's a response to a request
        if "id" in message and message["id"] in self.pending_requests:
            request_id = message["id"]
            self.responses[request_id] = message
            event = self.pending_requests[request_id]
            event.set()
        else:
            # It's a notification or unsolicited message
            self.response_queue.put(message)

    def _send_message(self, message: Dict[str, Any]):
        """Send a JSON-RPC message to the server"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("Server process not running")

        with self.writer_lock:
            try:
                json_str = json.dumps(message)
                # Send with Content-Length header
                content_length = len(json_str.encode('utf-8'))
                self.process.stdin.write(f"Content-Length: {content_length}\r\n\r\n")
                self.process.stdin.write(json_str)
                self.process.stdin.flush()
                logger.debug(f"Sent message: {message.get('method', 'response')}")
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                raise

    def _send_request(self, method: str, params: Any = None) -> Any:
        """Send a request and wait for response"""
        self.request_id += 1
        request_id = self.request_id

        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method
        }
        if params is not None:
            message["params"] = params

        # Create event for this request
        event = threading.Event()
        self.pending_requests[request_id] = event

        # Send the request
        self._send_message(message)

        # Wait for response (with timeout)
        if event.wait(timeout=10):
            response = self.responses.pop(request_id)
            del self.pending_requests[request_id]

            if "error" in response:
                raise RuntimeError(f"Server error: {response['error']}")

            return response.get("result")
        else:
            del self.pending_requests[request_id]
            raise TimeoutError(f"Timeout waiting for response to {method}")

    def _send_notification(self, method: str, params: Any = None):
        """Send a notification (no response expected)"""
        message = {
            "jsonrpc": "2.0",
            "method": method
        }
        if params is not None:
            message["params"] = params

        self._send_message(message)

    def _initialize(self) -> bool:
        """Initialize the MCP connection"""
        try:
            # Send initialize request
            result = self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp-test-client",
                    "version": "1.0.0"
                }
            })

            logger.info(f"Server info: {result.get('serverInfo', {})}")
            logger.info(f"Server capabilities: {result.get('capabilities', {})}")

            # Send initialized notification
            self._send_notification("initialized", {})

            self.initialized = True
            return True

        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False

    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        result = self._send_request("tools/list", {})
        return result.get("tools", [])

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool"""
        result = self._send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        return result

    def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        result = self._send_request("resources/list", {})
        return result.get("resources", [])

    def read_resource(self, uri: str) -> Any:
        """Read a resource"""
        result = self._send_request("resources/read", {"uri": uri})
        return result

    def ping(self) -> bool:
        """Ping the server"""
        try:
            result = self._send_request("ping", {})
            return result.get("pong", False)
        except:
            return False


def interactive_mode(client: MCPClient):
    """Run interactive mode for testing"""
    print("\nMCP Client Interactive Mode")
    print("Commands: list, call <tool> <args>, resources, read <uri>, ping, quit")
    print("-" * 50)

    while True:
        try:
            command = input("\n> ").strip()
            if not command:
                continue

            parts = command.split(maxsplit=2)
            cmd = parts[0].lower()

            if cmd == "quit" or cmd == "exit":
                break

            elif cmd == "list":
                tools = client.list_tools()
                print(f"\nAvailable tools ({len(tools)}):")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool['description']}")
                    if 'inputSchema' in tool:
                        print(f"    Schema: {json.dumps(tool['inputSchema'], indent=6)}")

            elif cmd == "call":
                if len(parts) < 3:
                    print("Usage: call <tool_name> <json_args>")
                    continue

                tool_name = parts[1]
                try:
                    args = json.loads(parts[2])
                except json.JSONDecodeError:
                    print("Invalid JSON arguments")
                    continue

                result = client.call_tool(tool_name, args)
                print(f"\nResult: {json.dumps(result, indent=2)}")

            elif cmd == "resources":
                resources = client.list_resources()
                print(f"\nAvailable resources ({len(resources)}):")
                for resource in resources:
                    print(f"  - {resource['uri']}: {resource['name']}")

            elif cmd == "read":
                if len(parts) < 2:
                    print("Usage: read <uri>")
                    continue

                uri = parts[1]
                result = client.read_resource(uri)
                print(f"\nResource content: {json.dumps(result, indent=2)}")

            elif cmd == "ping":
                if client.ping():
                    print("Pong! Server is responsive")
                else:
                    print("Server not responding")

            else:
                print(f"Unknown command: {cmd}")

        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MCP Client for testing MCP servers")
    parser.add_argument("command", nargs="?", help="Server command to run")
    parser.add_argument("--args", nargs="*", help="Additional arguments for server")
    parser.add_argument("--test", action="store_true", help="Run automated tests")
    parser.add_argument("--tool", help="Call specific tool with arguments")
    parser.add_argument("--tool-args", help="JSON arguments for tool")

    args = parser.parse_args()

    # Default to test server if no command specified
    if not args.command:
        args.command = "python"
        args.args = ["mcp_server.py"]

    # Build server command
    server_command = [args.command]
    if args.args:
        server_command.extend(args.args)

    # Create server config
    config = MCPServerConfig(
        name="test-server",
        command=server_command,
        description="Test MCP server"
    )

    # Create and start client
    client = MCPClient(config)

    try:
        if not client.start():
            print("Failed to start MCP server")
            return 1

        if args.test:
            # Run automated tests
            print("Running automated tests...")

            # Test ping
            print("Testing ping...")
            assert client.ping(), "Ping failed"
            print("✓ Ping successful")

            # Test tool listing
            print("Testing tool listing...")
            tools = client.list_tools()
            print(f"✓ Found {len(tools)} tools")

            # Test tool execution if echo tool exists
            echo_tools = [t for t in tools if t['name'] == 'echo']
            if echo_tools:
                print("Testing echo tool...")
                result = client.call_tool("echo", {"message": "Hello MCP!"})
                print(f"✓ Echo result: {result}")

            print("\nAll tests passed!")

        elif args.tool:
            # Call specific tool
            tool_args = json.loads(args.tool_args) if args.tool_args else {}
            result = client.call_tool(args.tool, tool_args)
            print(json.dumps(result, indent=2))

        else:
            # Interactive mode
            interactive_mode(client)

    finally:
        client.stop()

    return 0


if __name__ == "__main__":
    sys.exit(main())