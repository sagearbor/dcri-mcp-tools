import pytest
from tools.visit_window_calculator import run

def test_visit_window_calculator_basic():
    """Test basic visit window calculations for DCRI studies."""
    visit_data = """subject_id,enrollment_date,visit_1_date,visit_2_date
DCRI-HEART-001,2024-01-15,2024-02-12,2024-04-15
DCRI-HEART-002,2024-01-20,2024-02-18,2024-04-22"""
    
    protocol_schedule = {
        "visit_1": {"nominal_day": 28, "window_early": -7, "window_late": 7},
        "visit_2": {"nominal_day": 84, "window_early": -14, "window_late": 14}
    }
    
    input_data = {
        "visit_data": visit_data,
        "protocol_schedule": protocol_schedule
    }
    
    result = run(input_data)
    
    assert result["success"] is True
    assert "visit_windows" in result
    assert "DCRI-HEART-001" in result["visit_windows"]
    assert "DCRI-HEART-002" in result["visit_windows"]
    assert result["calculation_summary"]["subjects_calculated"] == 2

def test_visit_window_calculator_compliance():
    """Test visit compliance monitoring."""
    visit_data = """subject_id,enrollment_date,visit_1_date
DCRI-DIABETES-001,2024-01-15,2024-02-12"""
    
    protocol_schedule = {
        "visit_1": {"nominal_day": 28, "window_early": -7, "window_late": 7}
    }
    
    input_data = {
        "visit_data": visit_data,
        "protocol_schedule": protocol_schedule,
        "window_type": "strict"
    }
    
    result = run(input_data)
    
    assert result["success"] is True
    assert "compliance_report" in result
    assert result["compliance_report"]["summary"]["total_subjects"] == 1

def test_visit_window_calculator_multiple_visits():
    """Test with multiple visit types for complex DCRI protocols."""
    visit_data = """subject_id,enrollment_date,screening_date,baseline_date,week_4_date,week_12_date,week_24_date
DCRI-CARDIO-001,2024-01-15,2024-01-10,2024-01-15,2024-02-12,2024-04-15,2024-07-15
DCRI-CARDIO-002,2024-01-20,2024-01-18,2024-01-20,2024-02-18,2024-04-22,2024-07-20"""
    
    protocol_schedule = {
        "baseline_date": {"nominal_day": 0, "window_early": 0, "window_late": 0},
        "week_4_date": {"nominal_day": 28, "window_early": -7, "window_late": 7},
        "week_12_date": {"nominal_day": 84, "window_early": -14, "window_late": 14},
        "week_24_date": {"nominal_day": 168, "window_early": -21, "window_late": 21}
    }
    
    input_data = {
        "visit_data": visit_data,
        "protocol_schedule": protocol_schedule,
        "reference_date_field": "enrollment_date"
    }
    
    result = run(input_data)
    
    assert result["success"] is True
    assert len(result["visit_windows"]) == 2
    assert result["calculation_summary"]["subjects_calculated"] == 2

def test_visit_window_calculator_no_data():
    """Test error handling with no visit data."""
    input_data = {}
    
    result = run(input_data)
    
    assert result["success"] is False
    assert "No visit data provided" in result["errors"]

def test_visit_window_calculator_flexible_windows():
    """Test flexible visit window calculations."""
    visit_data = """subject_id,enrollment_date,visit_date
DCRI-NEURO-001,2024-01-15,2024-02-20"""
    
    protocol_schedule = {
        "visit_date": {"nominal_day": 30, "window_early": -10, "window_late": 10}
    }
    
    input_data = {
        "visit_data": visit_data,
        "protocol_schedule": protocol_schedule,
        "window_type": "flexible"
    }
    
    result = run(input_data)
    
    assert result["success"] is True
    assert result["calculation_summary"]["window_type"] == "flexible"
    assert "statistics" in result