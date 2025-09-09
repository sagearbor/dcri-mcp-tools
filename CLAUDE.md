# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based MCP (Model Context Protocol) tool server for DCRI clinical research that provides REST API endpoints for various clinical research tools. The server uses dynamic module loading to run individual tools and supports both local development and Azure production deployment with Key Vault integration.

## Development Commands

### Setup and Installation
```bash
# Initial project setup (creates directories and test tool)
./setup.sh

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Local development server (runs on http://127.0.0.1:8210)
python server.py

# Production with Gunicorn
gunicorn --bind 0.0.0.0:8210 server:app
```

### Testing
```bash
# Run all tests
pytest -v

# Test specific modules
pytest tests/test_server.py -v
pytest tests/test_auth.py -v
```

### Manual Testing
```bash
# Health check endpoint
curl http://127.0.0.1:8210/health

# Test echo tool example
curl -X POST -H "Content-Type: application/json" \
     -d '{"text": "hello world"}' \
     http://127.0.0.1:8210/run_tool/test_echo
```

## Architecture

### Core Components
- **server.py**: Main Flask application with dynamic tool loading and dual configuration system
- **tools/**: Individual tool modules, each with a `run(input_data)` function
- **auth/**: Microsoft Graph API authentication for SharePoint access
- **sharepoint/**: SharePoint client for document operations
- **tests/**: Unit and integration tests

### Configuration System
The application uses a dual configuration approach:
- **Local development**: Uses `.env` file (copy from `.env.example`)
- **Production (Azure)**: Automatically detects `KEY_VAULT_URI` environment variable and loads secrets from Azure Key Vault using Managed Identity

### Tool Architecture
Each tool is a Python module in the `tools/` directory that exports a `run(input_data: dict) -> dict` function. Tools are loaded dynamically via `/run_tool/<tool_name>` POST endpoints.

### Development Phases
The project follows a phased development approach outlined in `checklist.md`:
1. **Stage 1**: Core server with basic tool (completed)
2. **Stage 2**: Authentication and SharePoint services
3. **Stage 3**: Standalone tools (can be developed in parallel with Stage 2)
4. **Stage 4**: Tools that depend on SharePoint services

## Key Files
- `server.py:73-107`: Dynamic tool loading and execution logic
- `server.py:23-54`: Dual configuration system (local .env vs Azure Key Vault)
- `requirements.txt`: Python dependencies including Flask, Azure libraries, and tool-specific packages
- `Dockerfile`: Container configuration for Azure deployment
- `checklist.md`: Phased development roadmap

## Development Workflow
When completing development tasks, follow the workflow outlined in `AGENTS.md`:
1. Complete the development task
2. Update `checklist.md` by marking completed items with `[x]`
3. Follow the phased development order specified in the checklist

## Azure Deployment
The application is containerized and designed for Azure App Service deployment. Set the `KEY_VAULT_URI` environment variable in Azure App Service configuration to enable automatic secret loading from Key Vault.