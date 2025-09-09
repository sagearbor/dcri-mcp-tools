# dcri-mcp-tools
A modular tool server for DCRI clinical research, designed for Azure deployment and integration using MCP.

This repository contains the backend server that hosts a suite of tools accessible via a REST API. It's built with Flask and designed to be deployed as a containerized application on Azure. It features a dual configuration system for easy local development and secure production deployment using Azure Key Vault.

## Project Structure

```
(dcri-mcp-tools)/
├── auth/                 # Handles Microsoft Graph API authentication.
├── manifests/            # Tool manifests for Copilot Studio integration.
├── sharepoint/           # Client for interacting with SharePoint.
├── tools/                # Individual, self-contained tool modules.
├── tests/                # Unit and integration tests for the application.
├── .env.example          # Template for environment variables.
├── .gitignore            # Specifies files for Git to ignore.
├── CHECKLIST.md          # Phased development checklist.
├── Dockerfile            # Container definition for deployment.
├── requirements.txt      # Python dependencies.
└── server.py             # Core Flask application and endpoint routing.
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

## Deployment

This application is designed to be deployed as a Docker container. The `Dockerfile` handles the setup, and the `gunicorn` web server is used for production.

You can build the Docker image locally:

```
docker build -t dcri-mcp-tools .
```

For deployment, push the image to a container registry (like Azure Container Registry) and configure your Azure App Service to use it. Remember to set the environment variables (like `KEY_VAULT_URI`, etc.) in the App Service configuration settings.
