"""
Tests for Data Dictionary Validator Tool
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.data_dictionary_validator import run


def test_valid_csv_data():
    """Test validation of valid CSV data against schema"""
    csv_data = """subject_id,age,gender,enrollment_date,status
    SUBJ001,45,M,2024-01-15,ACTIVE
    SUBJ002,32,F,2024-01-20,ACTIVE
    SUBJ003,58,M,2024-02-01,SCREENED"""
    
    schema = {
        "fields": {
            "subject_id": {
                "type": "string",
                "pattern": "^SUBJ\\d{3}$"
            },
            "age": {
                "type": "integer",
                "minimum": 18,
                "maximum": 85
            },
            "gender": {
                "type": "string",
                "enum": ["M", "F", "O"]
            },
            "enrollment_date": {
                "type": "date"
            },
            "status": {
                "type": "string",
                "enum": ["SCREENED", "ACTIVE", "COMPLETED", "WITHDRAWN"]
            }
        },
        "required_fields": ["subject_id", "age", "gender"]
    }
    
    result = run({
        "csv_data": csv_data,
        "schema": schema,
        "strict_mode": True
    })
    
    assert result["valid"] == True
    assert len(result["errors"]) == 0
    assert result["statistics"]["total_rows"] == 3
    assert result["statistics"]["valid_rows"] == 3
    assert result["statistics"]["invalid_rows"] == 0


def test_missing_required_fields():
    """Test detection of missing required fields"""
    csv_data = """subject_id,enrollment_date,status
    SUBJ001,2024-01-15,ACTIVE
    SUBJ002,2024-01-20,ACTIVE"""
    
    schema = {
        "fields": {
            "subject_id": {"type": "string"},
            "age": {"type": "integer"},
            "gender": {"type": "string"},
            "enrollment_date": {"type": "date"},
            "status": {"type": "string"}
        },
        "required_fields": ["subject_id", "age", "gender"]
    }
    
    result = run({
        "csv_data": csv_data,
        "schema": schema,
        "strict_mode": True
    })
    
    assert result["valid"] == False
    assert any("Missing required fields" in error for error in result["errors"])
    assert "age" in result["errors"][0]
    assert "gender" in result["errors"][0]


def test_type_validation():
    """Test data type validation"""
    csv_data = """subject_id,age,weight,is_active,visit_date
    SUBJ001,45,75.5,true,2024-01-15
    SUBJ002,invalid_age,80.2,yes,2024-01-20
    SUBJ003,32,not_a_number,invalid,invalid_date"""
    
    schema = {
        "fields": {
            "subject_id": {"type": "string"},
            "age": {"type": "integer"},
            "weight": {"type": "float"},
            "is_active": {"type": "boolean"},
            "visit_date": {"type": "date"}
        },
        "required_fields": []
    }
    
    result = run({
        "csv_data": csv_data,
        "schema": schema,
        "strict_mode": False
    })
    
    assert result["valid"] == False
    assert result["statistics"]["valid_rows"] == 1
    assert result["statistics"]["invalid_rows"] == 2
    assert result["statistics"]["type_mismatches"] > 0


def test_constraint_validation():
    """Test constraint validation (min/max, pattern, enum)"""
    csv_data = """subject_id,age,status,email
    SUBJ001,17,ACTIVE,valid@email.com
    SUBJ002,90,INVALID_STATUS,invalid-email
    SUBJ003,45,COMPLETED,test@example.com"""
    
    schema = {
        "fields": {
            "subject_id": {
                "type": "string",
                "pattern": "^SUBJ\\d{3}$"
            },
            "age": {
                "type": "integer",
                "minimum": 18,
                "maximum": 85
            },
            "status": {
                "type": "string",
                "enum": ["SCREENED", "ACTIVE", "COMPLETED", "WITHDRAWN"]
            },
            "email": {
                "type": "string",
                "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
            }
        },
        "required_fields": ["subject_id"]
    }
    
    result = run({
        "csv_data": csv_data,
        "schema": schema,
        "strict_mode": False
    })
    
    assert result["valid"] == False
    assert result["statistics"]["constraint_violations"] > 0
    errors_str = " ".join(result["errors"])
    assert "less than minimum" in errors_str  # Age 17 < 18
    assert "exceeds maximum" in errors_str  # Age 90 > 85
    assert "not in allowed values" in errors_str  # INVALID_STATUS
    assert "does not match pattern" in errors_str  # invalid-email


def test_empty_csv_data():
    """Test handling of empty CSV data"""
    result = run({
        "csv_data": "",
        "schema": {"fields": {}},
        "strict_mode": True
    })
    
    assert result["valid"] == False
    assert "No CSV data provided" in result["errors"][0]


def test_empty_schema():
    """Test handling of empty schema"""
    csv_data = """col1,col2
    val1,val2"""
    
    result = run({
        "csv_data": csv_data,
        "schema": {},
        "strict_mode": True
    })
    
    assert result["valid"] == False
    assert "No schema provided" in result["errors"][0]


def test_date_format_validation():
    """Test various date format validations"""
    csv_data = """subject_id,visit_date,birth_date,consent_date
    SUBJ001,2024-01-15,1980-05-20,15-Jan-2024
    SUBJ002,01/20/2024,05/25/1975,20-January-2024
    SUBJ003,invalid_date,1990-13-40,2024/02/30"""
    
    schema = {
        "fields": {
            "subject_id": {"type": "string"},
            "visit_date": {"type": "date"},
            "birth_date": {"type": "date"},
            "consent_date": {"type": "date"}
        },
        "required_fields": []
    }
    
    result = run({
        "csv_data": csv_data,
        "schema": schema,
        "strict_mode": False
    })
    
    assert result["statistics"]["valid_rows"] == 2
    assert result["statistics"]["invalid_rows"] == 1
    assert result["statistics"]["type_mismatches"] > 0


def test_field_statistics():
    """Test field statistics generation"""
    csv_data = """subject_id,age,gender,status
    SUBJ001,45,M,ACTIVE
    SUBJ002,32,F,ACTIVE
    SUBJ003,58,M,COMPLETED
    SUBJ004,,F,ACTIVE
    SUBJ005,28,,WITHDRAWN"""
    
    schema = {
        "fields": {
            "subject_id": {"type": "string"},
            "age": {"type": "integer"},
            "gender": {"type": "string"},
            "status": {"type": "string"}
        },
        "required_fields": ["subject_id"]
    }
    
    result = run({
        "csv_data": csv_data,
        "schema": schema,
        "strict_mode": False
    })
    
    assert result["statistics"]["total_rows"] == 5
    assert result["statistics"]["missing_values"] > 0
    
    age_stats = result["statistics"]["field_statistics"]["age"]
    assert age_stats["missing"] == 1
    assert age_stats["valid"] == 4
    
    gender_stats = result["statistics"]["field_statistics"]["gender"]
    assert gender_stats["missing"] == 1
    assert gender_stats["unique_count"] == 2  # M and F


def test_strict_vs_non_strict_mode():
    """Test difference between strict and non-strict validation modes"""
    csv_data = """subject_id,age,extra_field
    SUBJ001,45,extra_value
    SUBJ002,32,another_value"""
    
    schema = {
        "fields": {
            "subject_id": {"type": "string"},
            "age": {"type": "integer"}
        },
        "required_fields": ["subject_id"]
    }
    
    # Strict mode should fail due to extra field
    strict_result = run({
        "csv_data": csv_data,
        "schema": schema,
        "strict_mode": True
    })
    
    assert strict_result["valid"] == False
    assert any("Extra fields" in error for error in strict_result["errors"])
    
    # Non-strict mode should pass with warning
    non_strict_result = run({
        "csv_data": csv_data,
        "schema": schema,
        "strict_mode": False
    })
    
    assert non_strict_result["valid"] == True
    assert any("Extra fields" in warning for warning in non_strict_result["warnings"])


def test_custom_validation_rules():
    """Test custom validation rules"""
    csv_data = """subject_id,enrollment_date,follow_up_date,status
    SUBJ001,2024-01-15,2025-01-15,ACTIVE
    SUBJ002,2024-01-20,2023-01-20,null
    SUBJ003,2024-02-01,2024-03-01,N/A"""
    
    schema = {
        "fields": {
            "subject_id": {"type": "string"},
            "enrollment_date": {
                "type": "date",
                "custom_rules": [{"type": "past_date"}]
            },
            "follow_up_date": {
                "type": "date",
                "custom_rules": [{"type": "future_date"}]
            },
            "status": {
                "type": "string",
                "custom_rules": [{"type": "not_null"}]
            }
        },
        "required_fields": ["subject_id"]
    }
    
    result = run({
        "csv_data": csv_data,
        "schema": schema,
        "strict_mode": False
    })
    
    errors_str = " ".join(result["errors"])
    assert "cannot be null" in errors_str  # Status validation


def test_validation_summary():
    """Test validation summary generation"""
    csv_data = """subject_id,age,gender
    SUBJ001,45,M
    SUBJ002,invalid,F
    SUBJ003,58,INVALID"""
    
    schema = {
        "fields": {
            "subject_id": {"type": "string"},
            "age": {"type": "integer"},
            "gender": {
                "type": "string",
                "enum": ["M", "F"]
            }
        },
        "required_fields": ["subject_id", "age", "gender"]
    }
    
    result = run({
        "csv_data": csv_data,
        "schema": schema,
        "strict_mode": False
    })
    
    summary = result["validation_summary"]
    assert "total_errors" in summary
    assert "total_warnings" in summary
    assert "validation_rate" in summary
    assert summary["total_errors"] > 0
    assert "33.33%" in summary["validation_rate"]  # 1 valid out of 3