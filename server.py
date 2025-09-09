import os
import importlib
import logging
import werkzeug.urls
from urllib.parse import quote as _url_quote
import werkzeug
if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "3"
from urllib.parse import urlparse as _url_parse
if not hasattr(werkzeug.urls, "url_parse"):
    werkzeug.urls.url_parse = _url_parse
if not hasattr(werkzeug.urls, "url_quote"):
    werkzeug.urls.url_quote = _url_quote

from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

# --- Configuration Loading ---
# This logic dynamically loads secrets from Azure Key Vault if in production,
# otherwise it falls back to a local .env file for development.

# The KEY_VAULT_URI environment variable is the trigger.
# In Azure App Service, you would set this in the Configuration settings.
key_vault_uri = os.environ.get("KEY_VAULT_URI")

if key_vault_uri:
    # --- PRODUCTION MODE: Load from Azure Key Vault ---
    print("INFO: KEY_VAULT_URI detected. Loading configuration from Azure Key Vault.")
    try:
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential

        # DefaultAzureCredential will automatically use the managed identity of the App Service
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=key_vault_uri, credential=credential)

        # Fetch secrets and set them as environment variables for consistent access
        # The names of the secrets in Key Vault should match the variable names.
        os.environ["CLIENT_SECRET"] = client.get_secret("CLIENT-SECRET").value
        os.environ["TENANT_ID"] = client.get_secret("TENANT-ID").value
        os.environ["CLIENT_ID"] = client.get_secret("CLIENT-ID").value
        os.environ["SHAREPOINT_SITE_ID"] = client.get_secret("SHAREPOINT-SITE-ID").value
        os.environ["DOC_LIBRARY_ID"] = client.get_secret("DOC-LIBRARY-ID").value
        print("INFO: Successfully loaded configuration from Azure Key Vault.")

    except Exception as e:
        print(f"FATAL: Failed to load secrets from Key Vault: {e}")
        # In a real scenario, you might want to exit or have more robust error handling
        exit(1)
else:
    # --- LOCAL DEVELOPMENT MODE: Load from .env file ---
    print("INFO: No KEY_VAULT_URI detected. Loading configuration from local .env file.")
    load_dotenv()
    print("INFO: Configuration loaded from .env file.")


# --- Flask Application Setup ---
app = Flask(__name__)

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@app.route("/", methods=["GET"])
def index():
    """
    Homepage that displays available endpoints and status.
    """
    import glob
    import ast
    
    tools_info = {}
    for tool_file in glob.glob("tools/*.py"):
        tool_name = tool_file.replace("tools/", "").replace(".py", "")
        if tool_name != "__init__":
            # Try to extract docstring from the tool file
            try:
                with open(tool_file, 'r') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    docstring = ast.get_docstring(tree)
                    if docstring:
                        # Clean up the docstring - take first 2-3 lines
                        lines = docstring.strip().split('\n')
                        description = ' '.join(lines[:3]).strip()
                    else:
                        description = "No description available"
            except:
                description = "No description available"
            
            tools_info[tool_name] = description
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DCRI MCP Tools Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            h1 { color: #333; }
            .status { background: #d4edda; color: #155724; padding: 10px; border-radius: 5px; margin: 20px 0; }
            .endpoint { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .method { display: inline-block; padding: 3px 8px; border-radius: 3px; font-weight: bold; margin-right: 10px; }
            .get { background: #28a745; color: white; }
            .post { background: #007bff; color: white; }
            code { background: #f8f9fa; padding: 2px 5px; border-radius: 3px; }
            .tools-count { color: #666; font-size: 14px; margin-top: 10px; }
            .tools-list { 
                background: white; 
                padding: 15px; 
                margin: 20px 0; 
                border-radius: 5px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                word-wrap: break-word;
                line-height: 1.8;
            }
            .tool-item {
                display: inline-block;
                background: #f0f0f0;
                padding: 3px 8px;
                margin: 3px;
                border-radius: 3px;
                font-family: monospace;
                font-size: 13px;
                cursor: pointer;
                position: relative;
                transition: background 0.2s;
            }
            .tool-item:hover {
                background: #007bff;
                color: white;
            }
            .tool-item a {
                color: inherit;
                text-decoration: none;
            }
            .demo-link {
                display: inline-block;
                margin-left: 5px;
                color: #28a745;
                font-weight: bold;
            }
            .tooltip {
                visibility: hidden;
                background-color: #333;
                color: #fff;
                text-align: left;
                border-radius: 5px;
                padding: 10px;
                position: absolute;
                z-index: 1;
                bottom: 125%;
                left: 50%;
                transform: translateX(-50%);
                width: 300px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                line-height: 1.4;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            }
            .tooltip::after {
                content: "";
                position: absolute;
                top: 100%;
                left: 50%;
                margin-left: -5px;
                border-width: 5px;
                border-style: solid;
                border-color: #333 transparent transparent transparent;
            }
            .tool-item:hover .tooltip {
                visibility: visible;
            }
        </style>
    </head>
    <body>
        <h1>🏥 DCRI MCP Tools Server</h1>
        <div class="status">✅ Server is running at http://127.0.0.1:8210</div>
        
        <h2>Available Endpoints:</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/health</code>
            <p>Health check endpoint - returns server status</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/run_tool/&lt;tool_name&gt;</code>
            <p>Execute a clinical research tool</p>
            <p>Body: JSON with tool-specific parameters</p>
        </div>
        
        <h2>Available Tools (""" + str(len(tools_info)) + """ total):</h2>
        <p style="color: #666; font-size: 14px;">Click any tool to try it interactively | Hover for description</p>
        <div class="tools-list">
            """ + "".join([f'<span class="tool-item"><a href="/demo/{tool}">{tool}</a><span class="tooltip">{tools_info[tool]}</span></span>' 
                          for tool in sorted(tools_info.keys())]) + """
        </div>
        
        <h2>Example Usage:</h2>
        <div class="endpoint">
            <pre>curl -X POST http://127.0.0.1:8210/run_tool/test_echo \\
     -H "Content-Type: application/json" \\
     -d '{"text": "Hello DCRI!"}'</pre>
        </div>
    </body>
    </html>
    """
    return html, 200

@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint to confirm the server is running.
    """
    app.logger.info("Health check endpoint was hit.")
    return jsonify({"status": "ok"}), 200


# Import and add demo route
from server_demo import add_demo_route
add_demo_route(app)

@app.route("/run_tool/<tool_name>", methods=["POST"])
def run_tool(tool_name):
    """
    Dynamically loads and runs a tool from the 'tools' directory.
    """
    app.logger.info(f"Received request to run tool: {tool_name}")

    # Validate tool name to prevent directory traversal attacks
    if not tool_name.isalnum() and "_" not in tool_name:
        app.logger.warning(f"Invalid tool name requested: {tool_name}")
        return jsonify({"error": "Invalid tool name"}), 400

    try:
        # Dynamically import the tool module
        tool_module = importlib.import_module(f"tools.{tool_name}")
        app.logger.info(f"Successfully imported module for tool: {tool_name}")
    except ImportError:
        app.logger.error(f"Tool not found: {tool_name}")
        return jsonify({"error": f"Tool '{tool_name}' not found."}), 404

    # Get the input data from the request
    input_data = request.get_json(silent=True)
    if not input_data:
        app.logger.error("Request received with no JSON payload.")
        return jsonify({"error": "Request must contain a JSON payload."}), 400

    try:
        # Call the 'run' function within the tool's module
        result = tool_module.run(input_data)
        app.logger.info(f"Successfully ran tool: {tool_name}")
        return jsonify(result), 200
    except Exception as e:
        app.logger.error(f"An error occurred while running tool '{tool_name}': {e}", exc_info=True)
        # exc_info=True logs the full stack trace
        return jsonify({"error": f"An internal error occurred in tool '{tool_name}'."}), 500


# This block allows you to run the server directly for local testing
if __name__ == "__main__":
    # When running locally, Flask's development server is used.
    # When deployed with Gunicorn, this block is not executed.
    app.run(host="0.0.0.0", port=8210, debug=True)