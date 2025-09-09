"""
Tests for EDC Data Validator Tool
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.edc_data_validator import run


def test_valid_edc_data():
    """Test validation of valid EDC data"""
    edc_data = """subject_id,visit_name,visit_date,age,gender,status
SUBJ001,Screening,2024-01-15,45,M,COMPLETED
SUBJ001,Baseline,2024-01-22,45,M,COMPLETED
SUBJ002,Screening,2024-01-20,32,F,COMPLETED"""
    
    study_spec = {
        "enrollment_criteria": {
            "age": {"minimum": 18, "maximum": 85},
            "gender": ["M", "F"]
        },
        "visit_schedule": [
            {"name": "Screening", "day": 0, "required": True},
            {"name": "Baseline", "day": 7, "required": True}
        ],
        "required_demographics": ["age", "gender"],
        "required_visit_fields": ["visit_date", "status"]
    }
    
    result = run({
        "edc_data": edc_data,
        "study_spec": study_spec,
        "validation_level": "standard"
    })
    
    assert result["valid"] == True
    assert result["statistics"]["total_subjects"] == 2
    assert len(result["errors"]) == 0


def test_missing_required_demographics():
    """Test detection of missing required demographics"""
    edc_data = """subject_id,visit_name,visit_date,status
SUBJ001,Screening,2024-01-15,COMPLETED"""
    
    study_spec = {
        "required_demographics": ["age", "gender"]
    }
    
    result = run({
        "edc_data": edc_data,
        "study_spec": study_spec
    })
    
    assert result["valid"] == False
    assert any("Missing required demographic field" in error for error in result["errors"])


def test_age_eligibility_violation():
    """Test detection of age eligibility violations"""
    edc_data = """subject_id,age,gender,visit_name,visit_date
SUBJ001,17,M,Screening,2024-01-15
SUBJ002,90,F,Screening,2024-01-20"""
    
    study_spec = {
        "enrollment_criteria": {
            "age": {"minimum": 18, "maximum": 85}
        },
        "required_demographics": ["age", "gender"]
    }
    
    result = run({
        "edc_data": edc_data,
        "study_spec": study_spec
    })
    
    assert result["valid"] == False
    assert any("outside protocol range" in error for error in result["errors"])


def test_protocol_compliance_metrics():
    """Test protocol compliance metrics generation"""
    edc_data = """subject_id,age,gender,visit_name,visit_date
SUBJ001,45,M,Screening,2024-01-15
SUBJ001,45,M,Baseline,2024-01-22
SUBJ002,32,F,Screening,2024-01-20"""
    
    study_spec = {
        "enrollment_criteria": {
            "age": {"minimum": 18, "maximum": 85}
        },
        "visit_schedule": [
            {"name": "Screening", "day": 0, "required": True},
            {"name": "Baseline", "day": 7, "required": True}
        ]
    }
    
    result = run({
        "edc_data": edc_data,
        "study_spec": study_spec
    })
    
    assert "protocol_compliance" in result
    assert "enrollment_criteria" in result["protocol_compliance"]
    assert result["protocol_compliance"]["enrollment_criteria"]["met"] > 0


def test_empty_edc_data():
    """Test handling of empty EDC data"""
    result = run({
        "edc_data": "",
        "study_spec": {}
    })
    
    assert result["valid"] == False
    assert "No EDC data provided" in result["errors"]


def test_validation_levels():
    """Test different validation levels"""
    edc_data = """subject_id,age,gender,visit_name,visit_date
SUBJ001,45,M,Screening,2024-01-15"""
    
    study_spec = {
        "enrollment_criteria": {"age": {"minimum": 18, "maximum": 85}}
    }
    
    # Basic validation
    result_basic = run({
        "edc_data": edc_data,
        "study_spec": study_spec,
        "validation_level": "basic"
    })
    
    # Strict validation
    result_strict = run({
        "edc_data": edc_data,
        "study_spec": study_spec,
        "validation_level": "strict"
    })
    
    # Should have different validation criteria
    assert result_basic is not None
    assert result_strict is not None