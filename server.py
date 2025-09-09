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

from flask import Flask, request, jsonify
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


@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint to confirm the server is running.
    """
    app.logger.info("Health check endpoint was hit.")
    return jsonify({"status": "ok"}), 200


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