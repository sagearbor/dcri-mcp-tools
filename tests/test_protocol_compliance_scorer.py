import pytest
from tools.protocol_compliance_scorer import run

def test_protocol_compliance_scorer():
    input_data = {
        "compliance_data": [
            {"subject_id": "001", "site_id": "S01", "visit_data": {"total_visits": 5, "completed_visits": 4}}
        ]
    }
    result = run(input_data)
    assert "error" not in result
    assert "overall_score" in result
