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
