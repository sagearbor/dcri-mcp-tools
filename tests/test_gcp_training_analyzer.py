import pytest
from tools.gcp_training_analyzer import run

def test_gcp_training_analyzer():
    """Test GCP training analyzer with various scenarios."""
    # Test with staff having training gaps
    input_data = {
        "staff_data": [
            {
                "name": "Dr. Smith",
                "role": "PI", 
                "training_records": [
                    {"course": "GCP", "completion_date": "2023-01-15"},
                    {"course": "Protocol Training", "completion_date": "2023-02-01"}
                ]
            },
            {
                "name": "Jane Doe",
                "role": "CRC",
                "training_records": [
                    {"course": "GCP", "completion_date": "2022-01-15"}  # This will be expired
                ]
            }
        ]
    }
    result = run(input_data)
    assert "error" not in result
    assert "training_gaps" in result
    assert "compliance_status" in result
    assert "summary" in result
    
    # Should have training gaps
    assert len(result["training_gaps"]) > 0
    
    # Jane Doe should be non-compliant due to expired GCP and missing other training
    assert "Jane Doe" in [gap["name"] for gap in result["training_gaps"]]
    
    # Summary should show compliance rate
    assert "compliance_rate" in result["summary"]
    assert result["summary"]["total_staff"] == 2


def test_gcp_training_analyzer_compliant_staff():
    """Test with fully compliant staff."""
    input_data = {
        "staff_data": [
            {
                "name": "Dr. Current",
                "role": "PI",
                "training_records": [
                    {"course": "GCP", "completion_date": "2024-01-15"},
                    {"course": "Protocol Training", "completion_date": "2024-01-15"},
                    {"course": "Site Training", "completion_date": "2024-01-15"},
                    {"course": "Safety Reporting", "completion_date": "2024-01-15"}
                ]
            }
        ]
    }
    result = run(input_data)
    assert "error" not in result
    assert len(result["training_gaps"]) == 0
    assert result["summary"]["compliance_rate"] == 100.0
    assert any("All staff training is current" in rec for rec in result["recommendations"])


def test_gcp_training_analyzer_no_staff_data():
    """Test error handling when no staff data provided."""
    input_data = {}
    result = run(input_data)
    assert "error" in result
    assert result["error"] == "No staff data provided"
