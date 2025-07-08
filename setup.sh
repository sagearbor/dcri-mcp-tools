#!/bin/bash
# This script creates the directory structure for the DCRI MCP Tools project.

echo "Creating project directories..."

# Top-level directories
mkdir -p auth
mkdir -p sharepoint
mkdir -p tools
mkdir -p tests
mkdir -p manifests

# Create __init__.py files to make directories Python packages
echo "Creating __init__.py files..."
touch auth/__init__.py
touch sharepoint/__init__.py
touch tools/__init__.py
touch tests/__init__.py

# Create empty placeholder files to be populated later
echo "Creating placeholder files..."
touch server.py
touch tests/test_server.py
touch auth/graph_auth.py
touch tests/test_auth.py
touch sharepoint/sharepoint_client.py
touch tests/test_sharepoint_client.py

# A simple echo tool for initial testing
echo "Creating a sample echo tool for testing..."
cat <<EOF > tools/test_echo.py
# tools/test_echo.py
"""
A simple tool that echoes back the text it receives.
Used for initial server testing.
"""

def run(input: dict) -> dict:
    """
    Takes a dictionary with a 'text' key and returns it in the output.
    """
    text_input = input.get("text", "No text provided")
    return {"output": text_input}
EOF


echo "Scaffold setup complete."
echo "Next steps:"
echo "1. Create a Python virtual environment: python -m venv venv"
echo "2. Activate it: source venv/bin/activate"
echo "3. Install dependencies: pip install -r requirements.txt"
