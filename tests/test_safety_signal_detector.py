import pytest
from tools.safety_signal_detector import run


def test_safety_signal_detector_basic():
    """Test basic safety signal detection."""
    input_data = {
        "adverse_events": [
            {"event_term": "Headache", "treatment_group": "drug", "subject_id": "001"},
            {"event_term": "Headache", "treatment_group": "drug", "subject_id": "002"},
            {"event_term": "Headache", "treatment_group": "drug", "subject_id": "003"},
            {"event_term": "Headache", "treatment_group": "placebo", "subject_id": "101"},
            {"event_term": "Nausea", "treatment_group": "drug", "subject_id": "004", "serious": True}
        ],
        "total_subjects": {"drug": 50, "placebo": 50}
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["statistics"]) > 0
    assert "signals" in result
    assert "summary" in result


def test_safety_signal_detector_with_threshold():
    """Test signal detection with custom threshold."""
    input_data = {
        "adverse_events": [
            {"event_term": "Rash", "treatment_group": "drug", "subject_id": f"D{i}"}
            for i in range(10)
        ] + [
            {"event_term": "Rash", "treatment_group": "placebo", "subject_id": f"P{i}"}
            for i in range(2)
        ],
        "total_subjects": {"drug": 100, "placebo": 100},
        "signal_threshold": 3.0,
        "min_cases": 5
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["signals"]) > 0
    assert result["signals"][0]["event_term"] == "Rash"


def test_safety_signal_detector_empty_input():
    """Test handling of empty input."""
    result = run({"adverse_events": []})
    assert result["error"] == "Missing adverse events or subject counts"
