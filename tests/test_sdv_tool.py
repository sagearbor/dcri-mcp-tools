import pytest
from tools.sdv_tool import run

def test_sdv_tool():
    input_data = {
        "sdv_items": [
            {"subject_id": "001", "visit": "V1", "form": "Demographics", "field": "Age", "edc_value": "45", "critical_field": True}
        ],
        "sdv_strategy": "risk-based"
    }
    result = run(input_data)
    assert "error" not in result
    assert "sdv_plan" in result
