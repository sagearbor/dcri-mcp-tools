"""
Tests for Missing Data Reporter Tool
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.missing_data_reporter import run


def test_basic_missing_data_analysis():
    """Test basic missing data analysis"""
    data = """subject_id,age,gender,visit_date,weight
SUBJ001,45,M,2024-01-15,75.5
SUBJ002,,F,2024-01-20,80.2
SUBJ003,58,,2024-02-01,
SUBJ004,32,M,,68.5"""
    
    result = run({
        "data": data,
        "required_fields": ["subject_id", "age", "gender"],
        "analysis_level": "detailed"
    })
    
    assert result["success"] == True
    assert result["statistics"]["overall_completeness_rate"] < 100
    assert result["statistics"]["total_missing_cells"] > 0


def test_field_level_analysis():
    """Test field-level missing data analysis"""
    data = """subject_id,age,gender,status
SUBJ001,45,M,ACTIVE
SUBJ002,,F,ACTIVE
SUBJ003,58,,COMPLETED
SUBJ004,32,M,"""
    
    result = run({
        "data": data,
        "required_fields": ["subject_id", "age", "gender"],
        "analysis_level": "detailed"
    })
    
    field_analysis = result["missing_data_report"]["field_analysis"]["field_details"]
    
    # Age should have 1 missing value
    assert field_analysis["age"]["missing_count"] == 1
    assert field_analysis["age"]["completeness_rate"] == 75.0
    
    # Gender should have 1 missing value
    assert field_analysis["gender"]["missing_count"] == 1
    
    # Status should have 1 missing value
    assert field_analysis["status"]["missing_count"] == 1


def test_subject_level_analysis():
    """Test subject-level missing data analysis"""
    data = """subject_id,age,gender,visit_date
SUBJ001,45,M,2024-01-15
SUBJ002,,F,2024-01-20
SUBJ003,58,,"""
    
    result = run({
        "data": data,
        "required_fields": ["age", "gender"],
        "analysis_level": "detailed"
    })
    
    subject_analysis = result["missing_data_report"]["subject_analysis"]["subject_details"]
    
    # SUBJ001 should have no missing required fields
    assert subject_analysis["SUBJ001"]["required_missing"] == 0
    assert subject_analysis["SUBJ001"]["completeness_rate"] == 100.0
    
    # SUBJ002 should have 1 missing required field
    assert subject_analysis["SUBJ002"]["required_missing"] == 1
    
    # SUBJ003 should have 1 missing required field (gender is missing, age is not)
    assert subject_analysis["SUBJ003"]["required_missing"] == 1


def test_missing_patterns_analysis():
    """Test missing data patterns analysis"""
    data = """subject_id,field1,field2,field3
SUBJ001,val1,,val3
SUBJ002,val1,,val3
SUBJ003,,,val3
SUBJ004,val1,val2,val3"""
    
    result = run({
        "data": data,
        "analysis_level": "detailed"
    })
    
    patterns = result["missing_data_report"]["pattern_analysis"]["common_patterns"]
    
    # Should detect the pattern of field2 being consistently missing
    assert len(patterns) > 0


def test_data_quality_scoring():
    """Test data quality score calculation"""
    # High quality data
    good_data = """subject_id,age,gender,status
SUBJ001,45,M,ACTIVE
SUBJ002,32,F,ACTIVE
SUBJ003,58,M,COMPLETED"""
    
    result_good = run({
        "data": good_data,
        "required_fields": ["subject_id", "age", "gender"],
        "analysis_level": "detailed"
    })
    
    # Poor quality data
    poor_data = """subject_id,age,gender,status
SUBJ001,,M,
SUBJ002,32,,
SUBJ003,,,"""
    
    result_poor = run({
        "data": poor_data,
        "required_fields": ["subject_id", "age", "gender"],
        "analysis_level": "detailed"
    })
    
    assert result_good["statistics"]["data_quality_score"] > result_poor["statistics"]["data_quality_score"]


def test_recommendations_generation():
    """Test recommendations generation"""
    data = """subject_id,age,gender,required_field
SUBJ001,,M,
SUBJ002,32,,
SUBJ003,,,"""
    
    result = run({
        "data": data,
        "required_fields": ["age", "gender", "required_field"],
        "analysis_level": "detailed"
    })
    
    recommendations = result["recommendations"]
    
    # Should have recommendations for required field issues
    assert len(recommendations) > 0
    assert any("required" in rec["issue"].lower() for rec in recommendations)


def test_empty_data():
    """Test handling of empty data"""
    result = run({
        "data": "",
        "required_fields": ["age", "gender"],
        "analysis_level": "detailed"
    })
    
    assert result["success"] == False
    assert "No data provided" in result["errors"]


def test_comprehensive_analysis():
    """Test comprehensive analysis level"""
    data = """subject_id,age,gender,field1,field2
SUBJ001,45,M,val1,val2
SUBJ002,,F,,val2
SUBJ003,58,,val1,
SUBJ004,32,M,,"""
    
    result = run({
        "data": data,
        "required_fields": ["age", "gender"],
        "analysis_level": "comprehensive"
    })
    
    assert result["success"] == True
    assert "correlation_analysis" in result["missing_data_report"]
    # Should have additional advanced analysis
    assert len(result["missing_data_report"]) >= 6