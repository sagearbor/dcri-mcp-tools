import pytest
from tools.audit_finding_tracker import run

def test_audit_finding_tracker():
    input_data = {
        "findings": [
            {"finding_id": "F001", "capa": {"due_date": "2024-12-31", "status": "pending"}}
        ]
    }
    result = run(input_data)
    assert "error" not in result
    assert "total_findings" in result
