import pytest
from tools.risk_indicator_monitor import run

def test_risk_indicator_monitor():
    input_data = {
        "kri_data": {"enrollment_rate": 0.5, "query_rate": 15},
        "thresholds": {"enrollment_rate": {"lower": 0.8}, "query_rate": {"upper": 10}}
    }
    result = run(input_data)
    assert "error" not in result
    assert "alerts" in result
