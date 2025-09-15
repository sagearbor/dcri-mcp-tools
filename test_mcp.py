#!/usr/bin/env python3
"""
Tests for MCP server and client implementation
"""

import unittest
import json
import threading
import time
import sys
import os
from io import StringIO
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server import MCPServer, MCPTool, JSONRPCError
from mcp_client import MCPClient, MCPServerConfig


class TestMCPServer(unittest.TestCase):
    """Test MCP Server functionality"""

    def setUp(self):
        """Set up test server"""
        self.server = MCPServer(name="test-server", version="1.0.0")

    def test_server_initialization(self):
        """Test server initialization"""
        self.assertEqual(self.server.name, "test-server")
        self.assertEqual(self.server.version, "1.0.0")
        self.assertFalse(self.server._running)

    def test_tool_registration(self):
        """Test tool registration"""
        def test_handler(args):
            return {"result": "success"}

        self.server.register_tool(
            name="test_tool",
            description="A test tool",
            input_schema={"type": "object"},
            handler=test_handler
        )

        self.assertIn("test_tool", self.server.tools)
        tool = self.server.tools["test_tool"]
        self.assertEqual(tool.name, "test_tool")
        self.assertEqual(tool.description, "A test tool")

    def test_handle_initialize(self):
        """Test initialize handler"""
        params = {
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }

        result = self.server._handle_initialize(params)

        self.assertIn("protocolVersion", result)
        self.assertIn("capabilities", result)
        self.assertIn("serverInfo", result)
        self.assertEqual(result["serverInfo"]["name"], "test-server")

    def test_handle_tools_list(self):
        """Test tools/list handler"""
        # Register a test tool
        self.server.register_tool(
            name="test_tool",
            description="Test tool",
            input_schema={"type": "object"},
            handler=lambda x: x
        )

        result = self.server._handle_tools_list({})

        self.assertIn("tools", result)
        self.assertEqual(len(result["tools"]), 1)
        self.assertEqual(result["tools"][0]["name"], "test_tool")

    def test_handle_tools_call(self):
        """Test tools/call handler"""
        # Register a test tool
        def echo_handler(args):
            return args.get("message", "")

        self.server.register_tool(
            name="echo",
            description="Echo tool",
            input_schema={"type": "object"},
            handler=echo_handler
        )

        # Call the tool
        params = {
            "name": "echo",
            "arguments": {"message": "Hello"}
        }

        result = self.server._handle_tools_call(params)

        self.assertIn("content", result)
        self.assertFalse(result["isError"])
        content = result["content"][0]
        self.assertEqual(content["type"], "text")
        self.assertEqual(content["text"], "Hello")

    def test_handle_tools_call_error(self):
        """Test tools/call error handling"""
        # Try to call non-existent tool
        params = {
            "name": "non_existent",
            "arguments": {}
        }

        with self.assertRaises(ValueError):
            self.server._handle_tools_call(params)

    def test_handle_ping(self):
        """Test ping handler"""
        result = self.server._handle_ping({})
        self.assertEqual(result, {"pong": True})

    def test_json_rpc_message_validation(self):
        """Test JSON-RPC message validation"""
        # Mock stdin/stdout for testing
        with patch('sys.stdin', StringIO('{"invalid": "message"}\n')):
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                message = self.server._read_message()

                # Should return the parsed message even if invalid
                self.assertIsNotNone(message)
                self.assertEqual(message.get("invalid"), "message")


class TestMCPClient(unittest.TestCase):
    """Test MCP Client functionality"""

    def setUp(self):
        """Set up test client"""
        self.config = MCPServerConfig(
            name="test-server",
            command=["python", "mcp_server.py"],
            description="Test server"
        )

    def test_client_initialization(self):
        """Test client initialization"""
        client = MCPClient(self.config)
        self.assertEqual(client.config.name, "test-server")
        self.assertIsNone(client.process)
        self.assertFalse(client.initialized)

    def test_message_handling(self):
        """Test message handling"""
        client = MCPClient(self.config)

        # Test response handling
        test_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"test": "data"}
        }

        # Set up pending request
        event = threading.Event()
        client.pending_requests[1] = event

        # Handle the message
        client._handle_message(test_message)

        # Check that response was stored and event was set
        self.assertIn(1, client.responses)
        self.assertEqual(client.responses[1], test_message)
        self.assertTrue(event.is_set())


class TestMCPIntegration(unittest.TestCase):
    """Integration tests for MCP server and client"""

    @classmethod
    def setUpClass(cls):
        """Set up integration test environment"""
        # Create a simple test server file
        cls.test_server_file = "test_mcp_server_temp.py"
        with open(cls.test_server_file, "w") as f:
            f.write("""
import sys
sys.path.insert(0, '.')
from mcp_server import create_example_server

if __name__ == "__main__":
    server = create_example_server()
    server.run()
""")

    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        if os.path.exists(cls.test_server_file):
            os.remove(cls.test_server_file)

    def test_server_client_communication(self):
        """Test actual server-client communication"""
        config = MCPServerConfig(
            name="integration-test",
            command=["python", self.test_server_file],
            description="Integration test server"
        )

        client = MCPClient(config)

        try:
            # Start the server
            self.assertTrue(client.start(), "Failed to start server")

            # Test ping
            self.assertTrue(client.ping(), "Ping failed")

            # Test tool listing
            tools = client.list_tools()
            self.assertIsInstance(tools, list)
            self.assertGreater(len(tools), 0)

            # Find echo tool
            echo_tool = None
            for tool in tools:
                if tool["name"] == "echo":
                    echo_tool = tool
                    break

            self.assertIsNotNone(echo_tool, "Echo tool not found")

            # Test echo tool
            result = client.call_tool("echo", {"message": "Integration test"})
            self.assertIn("content", result)
            content = result["content"][0]
            self.assertEqual(content["text"], "Integration test")

            # Test calculate tool
            result = client.call_tool("calculate", {
                "operation": "add",
                "a": 5,
                "b": 3
            })
            self.assertIn("content", result)
            content = json.loads(result["content"][0]["text"])
            self.assertEqual(content["result"], 8)

        finally:
            client.stop()


class TestMCPProtocol(unittest.TestCase):
    """Test MCP protocol compliance"""

    def test_json_rpc_request_format(self):
        """Test JSON-RPC request format"""
        server = MCPServer()

        # Valid request
        valid_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "ping",
            "params": {}
        }

        # Process should not raise exception
        with patch.object(server, '_send_response') as mock_send:
            server._process_request(valid_request)
            mock_send.assert_called_once()

    def test_json_rpc_error_codes(self):
        """Test JSON-RPC error codes"""
        self.assertEqual(JSONRPCError.PARSE_ERROR.value, -32700)
        self.assertEqual(JSONRPCError.INVALID_REQUEST.value, -32600)
        self.assertEqual(JSONRPCError.METHOD_NOT_FOUND.value, -32601)
        self.assertEqual(JSONRPCError.INVALID_PARAMS.value, -32602)
        self.assertEqual(JSONRPCError.INTERNAL_ERROR.value, -32603)

    def test_content_length_format(self):
        """Test Content-Length header format"""
        server = MCPServer()

        # Mock stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            test_message = {"test": "data"}
            server._send_message(test_message)

            output = mock_stdout.getvalue()
            self.assertIn("Content-Length:", output)
            self.assertIn("\r\n\r\n", output)

            # Extract and verify content
            parts = output.split("\r\n\r\n")
            self.assertEqual(len(parts), 2)

            # Parse content length
            header = parts[0]
            content_length = int(header.split(":")[1].strip())

            # Verify content matches length
            content = parts[1]
            self.assertEqual(len(content.encode('utf-8')), content_length)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    run_tests()