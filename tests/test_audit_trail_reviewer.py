import pytest
from tools.audit_trail_reviewer import run

def test_audit_trail_reviewer():
    input_data = {
        "audit_entries": [
            {"timestamp": "2024-01-01T10:00:00", "user": "user1", "action": "update", "entity": "CRF"},
            {"timestamp": "2024-01-01T23:00:00", "user": "user2", "action": "delete", "entity": "Query"}
        ]
    }
    result = run(input_data)
    assert "error" not in result
    assert "summary" in result
