import pytest
from tools.lab_alert_system import run


def test_lab_alert_system_basic():
    """Test basic lab alert generation."""
    input_data = {
        "lab_results": [
            {
                "subject_id": "001",
                "lab_test": "hemoglobin",
                "value": 7.5,
                "unit": "g/dL",
                "date": "2024-01-15",
                "sex": "male"
            },
            {
                "subject_id": "002",
                "lab_test": "ALT",
                "value": 150,
                "unit": "U/L",
                "date": "2024-01-16"
            }
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["alerts"]) > 0
    assert len(result["graded_results"]) == 2


def test_lab_alert_system_grade_thresholds():
    """Test CTCAE grading."""
    input_data = {
        "lab_results": [
            {
                "subject_id": "003",
                "lab_test": "platelet_count",
                "value": 40,
                "unit": "x10^9/L",
                "date": "2024-02-01"
            }
        ],
        "alert_threshold": 3
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["alerts"]) == 1
    assert result["alerts"][0]["grade"] == 3


def test_lab_alert_system_empty_input():
    """Test handling of empty input."""
    result = run({"lab_results": []})
    assert result["error"] == "No lab results provided"
