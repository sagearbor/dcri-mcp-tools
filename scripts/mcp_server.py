#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Server Implementation
Implements JSON-RPC 2.0 over stdio for tool communication
"""

import sys
import json
import logging
import traceback
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging to stderr (stdout is reserved for JSON-RPC)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class JSONRPCError(Enum):
    """Standard JSON-RPC 2.0 error codes"""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


@dataclass
class MCPTool:
    """Represents an MCP tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable


@dataclass
class MCPResource:
    """Represents an MCP resource definition"""
    uri: str
    name: str
    description: str
    mime_type: str = "text/plain"


class MCPServer:
    """Base MCP Server implementation with JSON-RPC 2.0 over stdio"""

    def __init__(self, name: str = "mcp-server", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.capabilities = {
            "tools": {},
            "resources": {},
            "prompts": {},
            "logging": {}
        }
        self._running = False
        self._initialize_handlers()

    def _initialize_handlers(self):
        """Initialize JSON-RPC method handlers"""
        self.handlers = {
            "initialize": self._handle_initialize,
            "initialized": self._handle_initialized,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "resources/list": self._handle_resources_list,
            "resources/read": self._handle_resources_read,
            "ping": self._handle_ping,
            "shutdown": self._handle_shutdown
        }

    def register_tool(self, name: str, description: str,
                     input_schema: Dict[str, Any], handler: Callable):
        """Register a tool with the MCP server"""
        self.tools[name] = MCPTool(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler
        )
        logger.info(f"Registered tool: {name}")

    def register_resource(self, uri: str, name: str,
                         description: str, mime_type: str = "text/plain"):
        """Register a resource with the MCP server"""
        self.resources[uri] = MCPResource(
            uri=uri,
            name=name,
            description=description,
            mime_type=mime_type
        )
        logger.info(f"Registered resource: {uri}")

    def _read_message(self) -> Optional[Dict[str, Any]]:
        """Read a JSON-RPC message from stdin"""
        try:
            line = sys.stdin.readline()
            if not line:
                return None

            # Handle both single-line and content-length format
            if line.startswith("Content-Length:"):
                # Read headers until empty line
                headers = {}
                while line and line.strip():
                    if ":" in line:
                        key, value = line.split(":", 1)
                        headers[key.strip()] = value.strip()
                    line = sys.stdin.readline()

                # Read content based on Content-Length
                if "Content-Length" in headers:
                    content_length = int(headers["Content-Length"])
                    content = sys.stdin.read(content_length)
                    return json.loads(content)
            else:
                # Direct JSON message
                return json.loads(line)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            self._send_error(None, JSONRPCError.PARSE_ERROR.value, "Parse error")
            return None
        except Exception as e:
            logger.error(f"Error reading message: {e}")
            return None

    def _send_message(self, message: Dict[str, Any]):
        """Send a JSON-RPC message to stdout"""
        try:
            json_str = json.dumps(message)
            # Send with Content-Length header for compatibility
            content_length = len(json_str.encode('utf-8'))
            sys.stdout.write(f"Content-Length: {content_length}\r\n\r\n")
            sys.stdout.write(json_str)
            sys.stdout.flush()
            logger.debug(f"Sent message: {message.get('method', message.get('result', 'response'))}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    def _send_response(self, id: Any, result: Any):
        """Send a successful JSON-RPC response"""
        self._send_message({
            "jsonrpc": "2.0",
            "id": id,
            "result": result
        })

    def _send_error(self, id: Any, code: int, message: str, data: Any = None):
        """Send a JSON-RPC error response"""
        error = {
            "code": code,
            "message": message
        }
        if data is not None:
            error["data"] = data

        self._send_message({
            "jsonrpc": "2.0",
            "id": id,
            "error": error
        })

    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        logger.info(f"Initializing MCP server: {self.name}")

        # Extract client info
        client_info = params.get("clientInfo", {})
        logger.info(f"Client: {client_info.get('name', 'unknown')} "
                   f"v{client_info.get('version', 'unknown')}")

        # Return server capabilities
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": self.capabilities,
            "serverInfo": {
                "name": self.name,
                "version": self.version
            }
        }

    def _handle_initialized(self, params: Dict[str, Any]) -> None:
        """Handle initialized notification"""
        logger.info("MCP server initialized successfully")
        self._running = True

    def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        tools_list = []
        for name, tool in self.tools.items():
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            })

        return {"tools": tools_list}

    def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})

        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")

        tool = self.tools[tool_name]
        logger.info(f"Executing tool: {tool_name}")

        try:
            # Execute the tool handler
            result = tool.handler(tool_args)

            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result) if not isinstance(result, str) else result
                    }
                ],
                "isError": False
            }
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing tool: {str(e)}"
                    }
                ],
                "isError": True
            }

    def _handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request"""
        resources_list = []
        for uri, resource in self.resources.items():
            resources_list.append({
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mime_type
            })

        return {"resources": resources_list}

    def _handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get("uri")

        if uri not in self.resources:
            raise ValueError(f"Resource not found: {uri}")

        # This is a placeholder - actual implementation would read the resource
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": self.resources[uri].mime_type,
                    "text": f"Content of resource: {uri}"
                }
            ]
        }

    def _handle_ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping request"""
        return {"pong": True}

    def _handle_shutdown(self, params: Dict[str, Any]) -> None:
        """Handle shutdown request"""
        logger.info("Shutting down MCP server")
        self._running = False

    def _process_request(self, message: Dict[str, Any]):
        """Process a JSON-RPC request"""
        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")

        logger.debug(f"Processing request: {method}")

        if method not in self.handlers:
            self._send_error(
                msg_id,
                JSONRPCError.METHOD_NOT_FOUND.value,
                f"Method not found: {method}"
            )
            return

        try:
            handler = self.handlers[method]
            result = handler(params)

            # Only send response if this is a request (has id)
            if msg_id is not None and result is not None:
                self._send_response(msg_id, result)

        except Exception as e:
            logger.error(f"Error handling {method}: {e}\n{traceback.format_exc()}")
            if msg_id is not None:
                self._send_error(
                    msg_id,
                    JSONRPCError.INTERNAL_ERROR.value,
                    str(e)
                )

    def run(self):
        """Run the MCP server, listening for JSON-RPC messages on stdin"""
        logger.info(f"Starting MCP server: {self.name} v{self.version}")

        while True:
            try:
                message = self._read_message()
                if message is None:
                    logger.info("No more messages, shutting down")
                    break

                # Validate JSON-RPC message
                if "jsonrpc" not in message or message["jsonrpc"] != "2.0":
                    self._send_error(
                        message.get("id"),
                        JSONRPCError.INVALID_REQUEST.value,
                        "Invalid JSON-RPC version"
                    )
                    continue

                # Process the request
                self._process_request(message)

                # Check if we should shutdown
                if not self._running and message.get("method") == "shutdown":
                    break

            except KeyboardInterrupt:
                logger.info("Received interrupt, shutting down")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}\n{traceback.format_exc()}")

        logger.info("MCP server stopped")


def create_example_server():
    """Create an example MCP server with test tools"""
    server = MCPServer(name="dcri-mcp-tools", version="1.0.0")

    # Register example echo tool
    def echo_handler(args: Dict[str, Any]) -> str:
        return args.get("message", "")

    server.register_tool(
        name="echo",
        description="Echo back the provided message",
        input_schema={
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message to echo"
                }
            },
            "required": ["message"]
        },
        handler=echo_handler
    )

    # Register example calculation tool
    def calculate_handler(args: Dict[str, Any]) -> Dict[str, Any]:
        operation = args.get("operation", "add")
        a = args.get("a", 0)
        b = args.get("b", 0)

        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            result = a / b if b != 0 else "Error: Division by zero"
        else:
            result = "Unknown operation"

        return {"result": result, "operation": operation}

    server.register_tool(
        name="calculate",
        description="Perform basic arithmetic operations",
        input_schema={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The operation to perform"
                },
                "a": {
                    "type": "number",
                    "description": "First operand"
                },
                "b": {
                    "type": "number",
                    "description": "Second operand"
                }
            },
            "required": ["operation", "a", "b"]
        },
        handler=calculate_handler
    )

    return server


if __name__ == "__main__":
    # Create and run the example server
    server = create_example_server()
    server.run()