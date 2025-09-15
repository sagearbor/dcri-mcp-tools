# MCP Implementation Guide

## Overview

This guide documents the complete MCP (Model Context Protocol) implementation for DCRI clinical research tools. The system uses true MCP protocol with JSON-RPC 2.0 over stdio for communication between clients and servers.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│          Schedule Optimizer Backend (FastAPI)       │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │         MCP Integration Module              │   │
│  │  - Connection pooling                       │   │
│  │  - Async execution                          │   │
│  │  - REST fallback support                    │   │
│  └─────────────┬───────────────────────────────┘   │
│                │                                     │
└────────────────┼─────────────────────────────────────┘
                 │ JSON-RPC 2.0 over stdio
    ┌────────────┴────────────┬────────────────┐
    │                         │                │
┌───▼──────────┐  ┌──────────▼──────┐  ┌──────▼──────┐
│ MCP Tools    │  │ Protocol        │  │ Compliance  │
│ Wrapper      │  │ Complexity      │  │ Knowledge   │
│ Server       │  │ Analyzer        │  │ Base        │
│              │  │                 │  │             │
│ - All tools  │  │ - Complexity    │  │ - Compliance│
│   from /tools│  │   analysis      │  │   checking  │
│ - Dynamic    │  │ - Visit burden  │  │ - Regulation│
│   loading    │  │ - Metrics       │  │   info      │
└──────────────┘  └─────────────────┘  └─────────────┘
```

## Quick Start

### 1. Start MCP Servers

```bash
# Start all MCP servers
cd /dcri/sasusers/home/scb2/gitRepos/dcri-mcp-tools
./start_mcp_servers.sh start

# Check server status
./start_mcp_servers.sh status

# View logs
./start_mcp_servers.sh logs
```

### 2. Test MCP Servers

```bash
# Run automated tests
python test_mcp_integration.py

# Interactive testing
python mcp_client.py
> list
> call echo {"message": "Hello MCP"}
> quit
```

### 3. Use from Backend

The backend automatically uses MCP when `USE_MCP=true` (default):

```python
# In backend/main.py
USE_MCP = os.getenv("USE_MCP", "true").lower() == "true"

# MCP integration handles protocol communication
mcp_integration = get_mcp_integration()

# Analyze complexity via MCP
result = await mcp_integration.analyze_complexity(data)

# Check compliance via MCP
result = await mcp_integration.check_compliance(data)
```

## MCP Protocol Details

### Message Format

MCP uses JSON-RPC 2.0 with Content-Length headers:

```
Content-Length: 123\r\n\r\n
{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
```

### Lifecycle

1. **Initialize**: Client sends `initialize` request
2. **Initialized**: Client sends `initialized` notification
3. **Operation**: Client calls tools, reads resources
4. **Shutdown**: Client sends `shutdown` request

### Available Methods

- `initialize` - Initialize connection
- `tools/list` - List available tools
- `tools/call` - Execute a tool
- `resources/list` - List available resources
- `resources/read` - Read a resource
- `ping` - Health check
- `shutdown` - Graceful shutdown

## Server Implementations

### 1. Base MCP Server (`mcp_server.py`)

Core MCP server implementation with:
- JSON-RPC 2.0 message handling
- Tool and resource registration
- Error handling and logging

### 2. Tool Wrapper (`mcp_tool_wrapper.py`)

Automatically wraps existing tools:
- Discovers tools from `/tools` directory
- Parses docstrings for metadata
- Generates JSON schemas
- Handles tool execution

### 3. Protocol Complexity Analyzer

MCP server for complexity analysis:
- **Tools**:
  - `analyze-complexity` - Calculate complexity score
  - `analyze-visit-burden` - Analyze visit burden
  - `get-complexity-metrics` - Get detailed metrics

### 4. Compliance Knowledge Base

MCP server for compliance checking:
- **Tools**:
  - `check-compliance` - Check regulatory compliance
  - `get-regulations` - Get applicable regulations
  - `validate-schedule` - Validate schedule structure

## Configuration

### MCP Configuration (`mcp_config.json`)

```json
{
  "servers": [
    {
      "name": "dcri-mcp-tools",
      "command": ["python", "mcp_tool_wrapper.py"],
      "capabilities": {
        "tools": true,
        "resources": false
      }
    }
  ]
}
```

### Environment Variables

- `USE_MCP` - Enable MCP mode (default: `true`)
- `MCP_SERVER_URL` - REST fallback URL (default: `http://localhost:8210`)

## Testing

### Unit Tests

```bash
# Test MCP protocol implementation
python test_mcp.py
```

### Integration Tests

```bash
# Test all MCP servers
python test_mcp_integration.py
```

### Manual Testing

```bash
# Test specific tool
python mcp_tool_wrapper.py --test echo --test-args '{"message": "test"}'

# List available tools
python mcp_tool_wrapper.py --list
```

## Deployment

### Local Development

1. MCP servers run as separate processes
2. Communication via stdio (stdin/stdout)
3. Logs written to stderr and log files

### Docker Support

```dockerfile
# Example Dockerfile for MCP server
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "mcp_server.py"]
```

### Azure Migration

For Azure deployment:

1. **Container Instances**: Deploy each MCP server as a container
2. **Service Bus**: Alternative to stdio for cloud communication
3. **Key Vault**: Store secrets and configuration
4. **Application Insights**: Monitor MCP server performance

## Troubleshooting

### Server Won't Start

```bash
# Check if port is in use (for REST fallback)
lsof -i :8210

# Check Python path
which python

# Check logs
tail -f logs/mcp-tools-wrapper.log
```

### Communication Errors

```bash
# Test basic connectivity
echo '{"jsonrpc": "2.0", "id": 1, "method": "ping", "params": {}}' | python mcp_server.py

# Check server status
./start_mcp_servers.sh status
```

### Tool Not Found

```bash
# List available tools
python mcp_client.py
> list

# Check tool discovery
python mcp_tool_wrapper.py --list
```

## Development

### Adding New Tools

1. Create tool in `/tools` directory:
```python
def run(input_data: Dict) -> Dict:
    """
    Tool description

    Example:
        Input: Description of input
        Output: Description of output

    Parameters:
        param1 : str
            Description of param1
    """
    return {"result": "success"}
```

2. Restart MCP server:
```bash
./start_mcp_servers.sh restart
```

### Creating New MCP Server

```python
from mcp_server import MCPServer

server = MCPServer(name="my-server", version="1.0.0")

# Register tool
server.register_tool(
    name="my-tool",
    description="My tool description",
    input_schema={"type": "object"},
    handler=my_handler_function
)

# Run server
server.run()
```

## Benefits

1. **Protocol Compliant**: True MCP implementation with JSON-RPC 2.0
2. **Local Testing**: Easy to test and debug locally
3. **Azure Ready**: Can be containerized for cloud deployment
4. **Gradual Migration**: Supports both MCP and REST modes
5. **Tool Reuse**: Existing tools work without modification

## Next Steps

1. **Performance Optimization**: Implement caching and connection pooling
2. **Monitoring**: Add Application Insights integration
3. **Security**: Implement authentication for MCP connections
4. **Scale**: Deploy to Azure Container Instances
5. **Documentation**: Generate OpenAPI specs from MCP tools

## Support

For issues or questions:
- Check logs in `/logs` directory
- Run diagnostic tests: `python test_mcp_integration.py`
- Review this guide and troubleshooting section