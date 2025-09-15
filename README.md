# dcri-mcp-tools
A modular tool server for DCRI clinical research with true MCP (Model Context Protocol) support, designed for Azure deployment.

This repository contains both:
1. **MCP Protocol Servers**: True MCP implementation using JSON-RPC 2.0 over stdio for tool communication
2. **REST API Server**: Flask-based REST API for backward compatibility and web access

The system features a dual configuration system for easy local development and secure production deployment using Azure Key Vault.

## Project Structure

```
(dcri-mcp-tools)/
├── auth/                 # Handles Microsoft Graph API authentication.
├── manifests/            # Tool manifests for Copilot Studio integration.
├── sharepoint/           # Client for interacting with SharePoint.
├── tools/                # Individual, self-contained tool modules.
├── tests/                # Unit and integration tests for the application.
├── logs/                 # MCP server logs (created at runtime)
├── pids/                 # MCP server PIDs (created at runtime)
├── mcp_server.py         # Core MCP server implementation (JSON-RPC 2.0)
├── mcp_client.py         # MCP client for testing and integration
├── mcp_tool_wrapper.py   # Automatic tool discovery and wrapping for MCP
├── mcp_config.json       # MCP server configuration
├── start_mcp_servers.sh  # Script to start/stop/manage MCP servers
├── test_mcp.py           # MCP protocol tests
├── test_mcp_integration.py # End-to-end MCP integration tests
├── MCP_IMPLEMENTATION_GUIDE.md # Complete MCP documentation
├── server.py             # Core Flask application (REST API)
├── requirements.txt      # Python dependencies
└── Dockerfile            # Container definition for deployment
```

## Getting Started

Follow these steps to set up and run the project on your local machine.

### 1. Prerequisites

- Python 3.8+
  
- Git
  
- Docker (for containerized deployment)
  

### 2. Clone the Repository

```
git clone [https://github.com/YOUR_ORG/dcri-mcp-tools.git](https://github.com/YOUR_ORG/dcri-mcp-tools.git)
cd dcri-mcp-tools
```

### 3. Run the Setup Script

This script will create the necessary directories and placeholder files.

```
./setup.sh
```

### 4. Set Up Python Environment

Create and activate a virtual environment to manage dependencies.

```
# Create the virtual environment
python -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Or on Windows
# venv\Scripts\activate
```

### 5. Install Dependencies

Install all required Python packages.

```
pip install -r requirements.txt
```

## Configuration

The application uses a dual system for managing configuration and secrets.

### Local Development

For local development, create a `.env` file in the project root by copying the example:

```
cp .env.example .env
```

Now, open the `.env` file and fill in your actual credentials. **This file is listed in `.gitignore` and should never be committed to version control.**

### Production (Azure)

When deployed to Azure, the application detects the `KEY_VAULT_URI` environment variable. If this variable is set in your Azure App Service configuration, the server will ignore any `.env` file and securely fetch all secrets directly from the specified Azure Key Vault.

This requires that your App Service has a Managed Identity with `Get` and `List` secret permissions on the target Key Vault.

## Running the Application

### Running the Server Locally

To run the Flask development server:

```
python server.py
```

The server will start on `http://127.0.0.1:8210`. You can test that it's running by visiting the health check endpoint: `http://127.0.0.1:8210/health`.

### Running MCP Servers

To run the true MCP protocol servers (JSON-RPC 2.0 over stdio):

```bash
# Start all MCP servers
./start_mcp_servers.sh start

# Check server status
./start_mcp_servers.sh status

# View logs
./start_mcp_servers.sh logs

# Stop all servers
./start_mcp_servers.sh stop
```

### Testing MCP Servers

```bash
# Run MCP protocol tests
python test_mcp.py

# Run integration tests
python test_mcp_integration.py

# Interactive MCP client
python mcp_client.py
```

### Running Tests

To run the full test suite using `pytest`:

```
pytest -v
```

## Using the Tools

Each tool is exposed as a POST endpoint. For example, to use the `test_echo` tool created by the setup script:

```
curl -X POST -H "Content-Type: application/json" \
-d '{"text": "hello world"}' \
http://127.0.0.1:8210/run_tool/test_echo
```

**Expected Response:**

```
{
  "output": "hello world"
}
```

### Interactive Demo Pages

Each tool has an interactive demo page accessible at `/demo/<tool_name>`. For example:
- http://127.0.0.1:8210/demo/faq_generator
- http://127.0.0.1:8210/demo/patient_retention_predictor

The demo pages feature:
- Clear tool description
- Collapsible Example section showing input/output
- Collapsible Parameters section with detailed documentation
- Interactive JSON editor with example inputs
- Real-time tool execution and output display

## Developing New Tools

### Tool Documentation Format

All tools must follow this standardized docstring format:

```python
def run(input_data: Dict) -> Dict:
    """
    [One line description of what the tool does]
    
    Example:
        Input: [Natural language description of the input data]
        Output: [Natural language description of what gets returned]
    
    Parameters:
        param_name : type
            Description of parameter
        param_name2 : type, optional
            Description of optional parameter (default: value)
    """
```

This format ensures:
- Consistency across all tools
- Proper display on demo pages with collapsible sections
- Clear documentation for developers and users
- Natural language examples instead of raw JSON

After creating a new tool:
1. Add the tool file to the `tools/` directory
2. Create corresponding tests in `tests/test_<tool_name>.py`
3. Update `checklist.md` with [ExAdded2] marker once documented

## Deployment

This application is designed to be deployed as a Docker container. The `Dockerfile` handles the setup, and the `gunicorn` web server is used for production.

You can build the Docker image locally:

```
docker build -t dcri-mcp-tools .
```

For deployment, push the image to a container registry (like Azure Container Registry) and configure your Azure App Service to use it. Remember to set the environment variables (like `KEY_VAULT_URI`, etc.) in the App Service configuration settings.
