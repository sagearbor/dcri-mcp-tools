import pytest
from tools.query_response_analyzer import run

def test_query_response_analyzer():
    input_data = {
        "queries": [
            {"query_id": "Q001", "site_id": "S01", "severity": "high", "issued_date": "2024-01-01", "status": "open"}
        ]
    }
    result = run(input_data)
    assert "error" not in result
    assert "summary" in result
