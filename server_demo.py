"""
Demo route handler for interactive tool testing
Dynamically extracts test examples from pytest files
"""

import os
import ast
import json
from flask import render_template_string

def extract_test_examples(tool_name):
    """
    Dynamically extract test input examples from pytest files.
    Looks for dictionaries in run() calls and input variable assignments.
    """
    test_file = f"tests/test_{tool_name}.py"
    examples = {}
    
    if not os.path.exists(test_file):
        return examples
    
    try:
        with open(test_file, 'r') as f:
            content = f.read()
            tree = ast.parse(content)
        
        # Store variable definitions at module level for reference
        module_vars = {}
        
        # First pass: collect module-level variable definitions
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        module_vars[target.id] = node.value
        
        # Walk through test functions and classes
        for node in tree.body:
            # Handle test functions at module level
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_name = node.name.replace('test_', '').replace('_', ' ').title()
                examples.update(_extract_from_function(node, test_name, module_vars))
            
            # Handle test classes
            elif isinstance(node, ast.ClassDef) and 'Test' in node.name:
                for method in node.body:
                    if isinstance(method, ast.FunctionDef) and method.name.startswith('test_'):
                        test_name = method.name.replace('test_', '').replace('_', ' ').title()
                        examples.update(_extract_from_function(method, test_name, module_vars))
                                
    except Exception as e:
        print(f"Error extracting test examples for {tool_name}: {e}")
    
    return examples

def _extract_from_function(func_node, test_name, module_vars):
    """Extract test examples from a function node"""
    examples = {}
    local_vars = dict(module_vars)
    
    for stmt in func_node.body:
        # Track local variable assignments
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    local_vars[target.id] = stmt.value
                    
                    # Check if this is an input_data assignment
                    if 'input' in target.id.lower() and isinstance(stmt.value, ast.Dict):
                        input_dict = _extract_dict_from_ast(stmt.value, local_vars)
                        if input_dict:
                            examples[test_name] = input_dict
        
        # Look for run() calls with inline dictionaries
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            if _is_run_call(stmt.value):
                if stmt.value.args and isinstance(stmt.value.args[0], ast.Dict):
                    input_dict = _extract_dict_from_ast(stmt.value.args[0], local_vars)
                    if input_dict and test_name not in examples:
                        examples[test_name] = input_dict
        
        # Look for result = run({...}) pattern
        elif isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
            if _is_run_call(stmt.value):
                if stmt.value.args and isinstance(stmt.value.args[0], ast.Dict):
                    input_dict = _extract_dict_from_ast(stmt.value.args[0], local_vars)
                    if input_dict and test_name not in examples:
                        examples[test_name] = input_dict
    
    # If we found variables but no direct dict, try to combine them
    if test_name not in examples:
        # Look for patterns like questions = [...] and then input_data using questions
        for var_name, var_value in local_vars.items():
            if 'input' in var_name.lower() and isinstance(var_value, ast.Dict):
                combined_dict = _extract_dict_from_ast(var_value, local_vars)
                if combined_dict:
                    examples[test_name] = combined_dict
                    break
    
    return examples

def _is_run_call(node):
    """Check if a call node is calling 'run' function"""
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == 'run':
            return True
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'run':
            return True
    return False

def _extract_dict_from_ast(dict_node, local_vars=None):
    """Extract a dictionary from an AST Dict node, resolving variable references"""
    if local_vars is None:
        local_vars = {}
    
    result = {}
    
    for k, v in zip(dict_node.keys, dict_node.values):
        # Extract key
        if isinstance(k, ast.Constant):
            key = k.value
        elif isinstance(k, ast.Str):
            key = k.s
        else:
            continue
        
        # Extract value
        value = _extract_value_from_ast(v, local_vars)
        
        if key and value is not None:
            result[key] = value
    
    return result

def _extract_value_from_ast(node, local_vars):
    """Extract a value from an AST node, handling various types"""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.NameConstant):  # True, False, None
        return node.value
    elif isinstance(node, ast.Name):
        # Variable reference - try to resolve it
        if node.id in local_vars:
            return _extract_value_from_ast(local_vars[node.id], local_vars)
        return None
    elif isinstance(node, ast.List):
        result = []
        for item in node.elts:
            val = _extract_value_from_ast(item, local_vars)
            if val is not None:
                result.append(val)
            elif isinstance(item, ast.Dict):
                # Handle list of dicts
                dict_val = _extract_dict_from_ast(item, local_vars)
                if dict_val:
                    result.append(dict_val)
        return result if result else None
    elif isinstance(node, ast.Dict):
        return _extract_dict_from_ast(node, local_vars)
    else:
        return None

def add_demo_route(app):
    """Add the demo route to the Flask app"""
    
    @app.route("/demo/<tool_name>")
    def tool_demo(tool_name):
        """Interactive demo page for a specific tool"""
        
        # Get tool description
        try:
            tool_module = __import__(f"tools.{tool_name}", fromlist=[''])
            description = tool_module.__doc__ or "No description available"
            description = description.strip()
        except:
            description = "Tool documentation not available"
        
        # Extract test examples dynamically
        example_inputs = extract_test_examples(tool_name)
        
        # If no examples found, provide a generic template
        if not example_inputs:
            # Try to extract from the run function signature
            try:
                tool_module = __import__(f"tools.{tool_name}", fromlist=['run'])
                run_func = getattr(tool_module, 'run')
                if run_func.__doc__:
                    # Parse docstring for parameter hints
                    doc_lines = run_func.__doc__.split('\n')
                    for line in doc_lines:
                        if 'dict with' in line.lower() or 'keys:' in line.lower():
                            # Found parameter description
                            example_inputs['Basic Example'] = {
                                "param1": "value1",
                                "param2": 123,
                                "note": "Replace with actual parameters"
                            }
                            break
                    
                if not example_inputs:
                    example_inputs['Empty Template'] = {}
            except:
                example_inputs['Empty Template'] = {}
        
        # Use the first example as default
        default_input = json.dumps(
            list(example_inputs.values())[0] if example_inputs else {},
            indent=2
        )
        
        # Read the template file
        with open('templates/tool_demo.html', 'r') as f:
            template = f.read()
        
        return render_template_string(
            template,
            tool_name=tool_name,
            description=description,
            example_inputs=example_inputs,
            default_input=default_input
        )