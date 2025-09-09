import pytest
from tools.dose_escalation_tool import run


def test_dose_escalation_3plus3():
    """Test traditional 3+3 design."""
    input_data = {
        "cohort_data": {
            "cohort_number": 1,
            "dose_level": 10,
            "subjects_enrolled": 3,
            "subjects_evaluable": 3
        },
        "dlt_events": [],
        "dose_levels": [10, 20, 40, 80],
        "escalation_rules": {"design": "3+3"}
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert result["recommendation"]["decision"] == "ESCALATE"
    assert result["recommendation"]["next_dose"] == 20


def test_dose_escalation_with_dlt():
    """Test dose escalation with DLT."""
    input_data = {
        "cohort_data": {
            "cohort_number": 2,
            "dose_level": 20,
            "subjects_enrolled": 3,
            "subjects_evaluable": 3
        },
        "dlt_events": [
            {
                "subject_id": "001",
                "event_term": "Grade 4 neutropenia",
                "grade": 4,
                "relationship": "Related"
            }
        ],
        "dose_levels": [10, 20, 40, 80],
        "escalation_rules": {"design": "3+3"}
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert result["recommendation"]["decision"] == "EXPAND"
    assert result["dlt_summary"]["dlt_count"] == 1


def test_dose_escalation_empty_input():
    """Test handling of empty input."""
    result = run({})
    assert result["error"] == "No cohort data provided"
