#!/bin/bash
# Start the Schedule Converter MCP Server

echo "Starting Schedule Converter MCP Server..."
echo "========================================"
echo ""
echo "This server listens on stdin/stdout for JSON-RPC messages."
echo "It can be called by:"
echo "  1. Claude Desktop (via MCP config)"
echo "  2. Other LLMs via subprocess"
echo "  3. REST API via the Flask server"
echo ""

# Change to the directory containing the server
cd /dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools

# Start the MCP server
python scripts/schedule_converter_mcp.py