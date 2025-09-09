import pytest
from tools.process_deviation_detector import run

def test_process_deviation_detector():
    input_data = {
        "process_data": [
            {"name": "consent", "steps": ["inform", "sign", "date"]}
        ],
        "standard_processes": {"consent": ["inform", "sign", "date", "copy"]}
    }
    result = run(input_data)
    assert "error" not in result
    assert "deviations" in result
