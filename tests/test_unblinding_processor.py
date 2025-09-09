import pytest
from tools.unblinding_processor import run


def test_unblinding_processor_emergency():
    """Test emergency unblinding request."""
    input_data = {
        "request_details": {
            "subject_id": "001",
            "site_id": "Site01",
            "requestor": "Dr. Smith",
            "requestor_role": "physician",
            "request_date": "2024-01-15",
            "reason": "Life-threatening allergic reaction",
            "urgency": "emergency"
        },
        "subject_data": {
            "treatment_assignment": "Drug A 100mg",
            "randomization_date": "2024-01-01",
            "current_status": "active"
        }
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert result["authorization"]["approved"] == True
    assert result["unblinding_code"]["treatment_assignment"] == "Drug A 100mg"
    assert len(result["audit_trail"]) > 0


def test_unblinding_processor_routine():
    """Test routine unblinding request."""
    input_data = {
        "request_details": {
            "subject_id": "002",
            "requestor": "Study Coordinator",
            "requestor_role": "coordinator",
            "reason": "Administrative review",
            "urgency": "routine"
        },
        "subject_data": {
            "treatment_assignment": "Placebo"
        }
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert "authorization" in result


def test_unblinding_processor_empty_input():
    """Test handling of empty input."""
    result = run({})
    assert result["error"] == "No request details provided"
