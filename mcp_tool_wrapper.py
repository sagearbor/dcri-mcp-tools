#!/usr/bin/env python3
"""
MCP Tool Wrapper - Wraps existing tools for MCP protocol
Automatically discovers and loads tools from the tools directory
"""

import os
import sys
import importlib
import inspect
import json
import logging
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """Metadata extracted from tool docstring"""
    name: str
    description: str
    example: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


def parse_tool_docstring(docstring: str) -> ToolMetadata:
    """Parse tool docstring to extract metadata"""
    if not docstring:
        return None

    lines = docstring.strip().split('\n')
    description = lines[0].strip() if lines else ""

    # Parse sections
    example = None
    parameters = {}
    current_section = None
    current_content = []

    for line in lines[1:]:
        line = line.strip()

        if line.startswith("Example:"):
            if current_section == "Parameters":
                # Process parameters before moving to example
                parameters = _parse_parameters(current_content)
            current_section = "Example"
            current_content = []
        elif line.startswith("Parameters:"):
            if current_section == "Example":
                example = '\n'.join(current_content).strip()
            current_section = "Parameters"
            current_content = []
        elif current_section:
            current_content.append(line)

    # Process last section
    if current_section == "Example":
        example = '\n'.join(current_content).strip()
    elif current_section == "Parameters":
        parameters = _parse_parameters(current_content)

    return ToolMetadata(
        name="",  # Will be filled by the wrapper
        description=description,
        example=example,
        parameters=parameters
    )


def _parse_parameters(lines: list) -> Dict[str, Any]:
    """Parse parameter descriptions into a schema"""
    parameters = {}
    current_param = None
    current_desc = []

    for line in lines:
        if line and not line.startswith(' '):
            # New parameter
            if current_param:
                parameters[current_param['name']] = current_param

            parts = line.split(':', 1)
            if len(parts) == 2:
                param_info = parts[0].strip().split()
                param_name = param_info[0] if param_info else ""
                param_type = param_info[1] if len(param_info) > 1 else "string"

                # Handle optional parameters
                is_optional = "optional" in parts[1].lower()

                current_param = {
                    'name': param_name,
                    'type': _map_python_type_to_json(param_type),
                    'description': parts[1].strip(),
                    'required': not is_optional
                }
                current_desc = []
        elif current_param and line.startswith(' '):
            # Continuation of description
            current_param['description'] += ' ' + line.strip()

    # Add last parameter
    if current_param:
        parameters[current_param['name']] = current_param

    return parameters


def _map_python_type_to_json(python_type: str) -> str:
    """Map Python type hints to JSON schema types"""
    type_mapping = {
        'str': 'string',
        'int': 'integer',
        'float': 'number',
        'bool': 'boolean',
        'dict': 'object',
        'list': 'array',
        'Dict': 'object',
        'List': 'array',
        'Any': 'object'
    }
    return type_mapping.get(python_type, 'string')


def create_json_schema_from_metadata(metadata: ToolMetadata) -> Dict[str, Any]:
    """Create JSON schema from tool metadata"""
    schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    if metadata.parameters:
        for param_name, param_info in metadata.parameters.items():
            if isinstance(param_info, dict):
                schema["properties"][param_name] = {
                    "type": param_info.get('type', 'string'),
                    "description": param_info.get('description', '')
                }
                if param_info.get('required', True):
                    schema["required"].append(param_name)

    return schema


class MCPToolWrapper:
    """Wraps existing tools for MCP protocol"""

    def __init__(self, tools_directory: str = "tools"):
        self.tools_directory = tools_directory
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, ToolMetadata] = {}
        self.discover_tools()

    def discover_tools(self):
        """Discover and load tools from the tools directory"""
        if not os.path.exists(self.tools_directory):
            logger.warning(f"Tools directory not found: {self.tools_directory}")
            return

        # Add tools directory to path
        sys.path.insert(0, os.path.abspath(self.tools_directory))

        for filename in os.listdir(self.tools_directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                tool_name = filename[:-3]  # Remove .py extension

                try:
                    # Import the module
                    module = importlib.import_module(tool_name)

                    # Look for 'run' function
                    if hasattr(module, 'run'):
                        run_func = getattr(module, 'run')
                        if callable(run_func):
                            self.tools[tool_name] = run_func

                            # Extract metadata from docstring
                            docstring = inspect.getdoc(run_func)
                            if docstring:
                                metadata = parse_tool_docstring(docstring)
                                if metadata:
                                    metadata.name = tool_name
                                    self.tool_metadata[tool_name] = metadata
                                    logger.info(f"Loaded tool: {tool_name}")
                            else:
                                # Create basic metadata
                                self.tool_metadata[tool_name] = ToolMetadata(
                                    name=tool_name,
                                    description=f"Tool: {tool_name}"
                                )
                                logger.info(f"Loaded tool without metadata: {tool_name}")

                except Exception as e:
                    logger.error(f"Failed to load tool {tool_name}: {e}")

        logger.info(f"Discovered {len(self.tools)} tools")

    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get JSON schema for a tool"""
        if tool_name not in self.tool_metadata:
            # Return a generic schema
            return {
                "type": "object",
                "properties": {},
                "additionalProperties": True
            }

        metadata = self.tool_metadata[tool_name]
        return create_json_schema_from_metadata(metadata)

    def get_tool_description(self, tool_name: str) -> str:
        """Get description for a tool"""
        if tool_name in self.tool_metadata:
            return self.tool_metadata[tool_name].description
        return f"Tool: {tool_name}"

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool with given arguments"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")

        tool_func = self.tools[tool_name]

        try:
            # Execute the tool
            result = tool_func(arguments)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            raise

    def list_tools(self) -> list:
        """List all available tools with their metadata"""
        tools_list = []

        for tool_name in self.tools:
            tool_info = {
                "name": tool_name,
                "description": self.get_tool_description(tool_name),
                "inputSchema": self.get_tool_schema(tool_name)
            }

            # Add example if available
            if tool_name in self.tool_metadata and self.tool_metadata[tool_name].example:
                tool_info["example"] = self.tool_metadata[tool_name].example

            tools_list.append(tool_info)

        return tools_list


def create_mcp_server_with_tools(tools_directory: str = "tools"):
    """Create an MCP server with all discovered tools"""
    from mcp_server import MCPServer

    # Create wrapper and discover tools
    wrapper = MCPToolWrapper(tools_directory)

    # Create MCP server
    server = MCPServer(name="dcri-mcp-tools", version="1.0.0")

    # Register all discovered tools
    for tool_name in wrapper.tools:
        def create_handler(name):
            # Closure to capture tool name
            def handler(args):
                result = wrapper.execute_tool(name, args)
                # Convert result to string if needed
                if isinstance(result, dict) or isinstance(result, list):
                    return json.dumps(result, indent=2)
                return str(result)
            return handler

        server.register_tool(
            name=tool_name,
            description=wrapper.get_tool_description(tool_name),
            input_schema=wrapper.get_tool_schema(tool_name),
            handler=create_handler(tool_name)
        )

    logger.info(f"Created MCP server with {len(wrapper.tools)} tools")
    return server


def main():
    """Main entry point - run MCP server with all tools"""
    import argparse

    parser = argparse.ArgumentParser(description="MCP Tool Wrapper Server")
    parser.add_argument("--tools-dir", default="tools",
                       help="Directory containing tool modules")
    parser.add_argument("--list", action="store_true",
                       help="List available tools and exit")
    parser.add_argument("--test", help="Test a specific tool")
    parser.add_argument("--test-args", help="JSON arguments for testing")

    args = parser.parse_args()

    if args.list:
        # List tools and exit
        wrapper = MCPToolWrapper(args.tools_dir)
        tools = wrapper.list_tools()
        print(f"\nAvailable tools ({len(tools)}):\n")
        for tool in tools:
            print(f"- {tool['name']}: {tool['description']}")
            if 'example' in tool:
                print(f"  Example: {tool['example']}")
        return

    if args.test:
        # Test a specific tool
        wrapper = MCPToolWrapper(args.tools_dir)
        test_args = json.loads(args.test_args) if args.test_args else {}
        result = wrapper.execute_tool(args.test, test_args)
        print(f"Result: {json.dumps(result, indent=2)}")
        return

    # Run MCP server with all tools
    server = create_mcp_server_with_tools(args.tools_dir)
    server.run()


if __name__ == "__main__":
    main()