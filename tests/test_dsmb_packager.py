import pytest
from tools.dsmb_packager import run


def test_dsmb_packager_basic():
    """Test basic DSMB package preparation."""
    input_data = {
        "meeting_details": {
            "meeting_date": "2024-03-15",
            "meeting_type": "scheduled",
            "review_period": "2024-01-01 to 2024-02-28"
        },
        "enrollment_data": {
            "total_enrolled": 150,
            "target_enrollment": 200,
            "currently_active": 140
        },
        "safety_data": {
            "adverse_events": {"by_severity": {"mild": 50, "moderate": 20, "severe": 5}},
            "serious_adverse_events": [{"event_term": "Pneumonia", "outcome": "Recovered"}],
            "deaths": []
        }
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["package_contents"]) > 0
    assert "executive_summary" in result
    assert result["executive_summary"]["enrollment_progress"]["percent_complete"] == 75.0


def test_dsmb_packager_with_safety_issues():
    """Test DSMB package with safety concerns."""
    input_data = {
        "meeting_details": {
            "meeting_date": "2024-04-01",
            "meeting_type": "ad-hoc"
        },
        "enrollment_data": {"total_enrolled": 100, "target_enrollment": 200},
        "safety_data": {
            "adverse_events": {},
            "serious_adverse_events": [{"event_term": "MI"} for _ in range(10)],
            "deaths": [{"subject_id": "001", "cause": "Cardiac arrest"}]
        }
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["open_issues"]) > 0
    assert len(result["recommendations"]) > 0


def test_dsmb_packager_empty_input():
    """Test handling of empty input."""
    result = run({})
    assert result["error"] == "No meeting details provided"
