import sys
sys.path.insert(0, '.')
from server_demo import _is_run_call, _extract_dict_from_ast
import ast

code = """
def test_fixed_effect_meta_analysis():
    result = run({
        'studies': [
            {'name': 'Study 1', 'effect_size': 0.8, 'n': 100}
        ],
        'measure': 'OR'
    })
"""

tree = ast.parse(code)
func = tree.body[0]
stmt = func.body[0]  # result = run(...)

print(f'Statement type: {type(stmt).__name__}')
print(f'Is assignment: {isinstance(stmt, ast.Assign)}')
print(f'Value type: {type(stmt.value).__name__}')
print(f'Is call: {isinstance(stmt.value, ast.Call)}')
print(f'Is run call: {_is_run_call(stmt.value)}')

if stmt.value.args:
    arg = stmt.value.args[0]
    print(f'First arg type: {type(arg).__name__}')
    extracted = _extract_dict_from_ast(arg, {})
    print(f'Extracted: {extracted}')
