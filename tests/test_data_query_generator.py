import pytest
from tools.data_query_generator import run


def test_data_query_generator_basic():
    """Test basic query generation functionality."""
    input_data = {
        "data": "subject_id,age,weight\n001,25,70\n002,35,\n003,150,80",
        "query_rules": {
            "categories": {
                "basic_checks": [
                    {
                        "name": "Missing Weight",
                        "type": "missing_required",
                        "fields": ["weight"],
                        "severity": "MAJOR",
                        "message": "Missing required field: {field}"
                    },
                    {
                        "name": "Age Range",
                        "type": "range_check",
                        "field": "age",
                        "min_value": 18,
                        "max_value": 85,
                        "severity": "CRITICAL",
                        "message": "Age {value} is {violation} for field {field}"
                    }
                ]
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["queries"]) == 2
    assert result["statistics"]["total_records_checked"] == 3
    assert result["statistics"]["queries_generated"] == 2
    assert result["statistics"]["critical_queries"] == 1
    assert result["statistics"]["major_queries"] == 1
    
    # Check specific queries
    queries = result["queries"]
    weight_query = next(q for q in queries if q["query_type"] == "missing_required")
    age_query = next(q for q in queries if q["query_type"] == "range_violation")
    
    assert weight_query["subject_id"] == "002"
    assert weight_query["field"] == "weight"
    assert weight_query["severity"] == "MAJOR"
    
    assert age_query["subject_id"] == "003"
    assert age_query["field"] == "age"
    assert age_query["severity"] == "CRITICAL"
    assert age_query["value"] == "150"


def test_data_query_generator_missing_required():
    """Test missing required field detection."""
    input_data = {
        "data": "subject_id,visit,vital_signs\n001,Day1,\n002,Day1,120/80",
        "query_rules": {
            "categories": {
                "required_fields": [
                    {
                        "name": "Missing Vital Signs",
                        "type": "missing_required",
                        "fields": ["vital_signs"],
                        "severity": "MAJOR",
                        "message": "Missing {field} for subject {subject_id}"
                    }
                ]
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["queries"]) == 1
    assert result["queries"][0]["subject_id"] == "001"
    assert result["queries"][0]["field"] == "vital_signs"
    assert "Missing vital_signs for subject 001" in result["queries"][0]["message"]


def test_data_query_generator_range_checks():
    """Test range violation detection."""
    input_data = {
        "data": "subject_id,temperature,heart_rate\n001,98.6,70\n002,105.2,45\n003,96.8,180",
        "query_rules": {
            "categories": {
                "vital_ranges": [
                    {
                        "name": "Temperature Range",
                        "type": "range_check",
                        "field": "temperature",
                        "min_value": 97.0,
                        "max_value": 104.0,
                        "severity": "CRITICAL",
                        "message": "Temperature {value} is {violation}"
                    },
                    {
                        "name": "Heart Rate Range",
                        "type": "range_check",
                        "field": "heart_rate",
                        "min_value": 60,
                        "max_value": 100,
                        "severity": "MAJOR",
                        "message": "Heart rate {value} is {violation}"
                    }
                ]
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["queries"]) == 4
    
    # Check temperature queries (002 high, 003 low)
    temp_queries = [q for q in result["queries"] if q["field"] == "temperature"]
    assert len(temp_queries) == 2
    temp_subjects = [q["subject_id"] for q in temp_queries]
    assert "002" in temp_subjects  # High temperature
    assert "003" in temp_subjects  # Low temperature
    
    # Check heart rate queries
    hr_queries = [q for q in result["queries"] if q["field"] == "heart_rate"]
    assert len(hr_queries) == 2
    hr_subjects = [q["subject_id"] for q in hr_queries]
    assert "002" in hr_subjects  # Low heart rate
    assert "003" in hr_subjects  # High heart rate


def test_data_query_generator_logic_checks():
    """Test logic violation detection."""
    input_data = {
        "data": "subject_id,pregnant,gender\n001,Yes,Female\n002,Yes,Male\n003,No,Female",
        "query_rules": {
            "categories": {
                "logic_checks": [
                    {
                        "name": "Pregnancy Logic",
                        "type": "logic_check",
                        "expression": "{pregnant} == 'Yes' and {gender} == 'Male'",
                        "severity": "CRITICAL",
                        "message": "Male subject marked as pregnant: {subject_id}"
                    }
                ]
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["queries"]) == 1
    assert result["queries"][0]["subject_id"] == "002"
    assert result["queries"][0]["severity"] == "CRITICAL"
    assert "Male subject marked as pregnant" in result["queries"][0]["message"]


def test_data_query_generator_consistency_checks():
    """Test consistency violation detection."""
    input_data = {
        "data": "subject_id,visit,gender\n001,Day1,Male\n001,Day15,Female\n002,Day1,Female\n002,Day15,Female",
        "query_rules": {
            "categories": {
                "consistency_checks": [
                    {
                        "name": "Gender Consistency",
                        "type": "consistency_check",
                        "field": "gender",
                        "consistency_type": "same_value",
                        "severity": "CRITICAL",
                        "message": "Inconsistent {field} values for subject {subject_id}: {violation_msg}"
                    }
                ]
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["queries"]) == 1
    assert result["queries"][0]["subject_id"] == "001"
    assert result["queries"][0]["field"] == "gender"
    assert "Inconsistent gender values" in result["queries"][0]["message"]


def test_data_query_generator_duplicate_checks():
    """Test duplicate record detection."""
    input_data = {
        "data": "subject_id,visit,test_name\n001,Day1,CBC\n002,Day1,CBC\n001,Day1,CBC",
        "query_rules": {
            "categories": {
                "duplicate_checks": [
                    {
                        "name": "Duplicate Tests",
                        "type": "duplicate_check",
                        "key_fields": ["subject_id", "visit", "test_name"],
                        "severity": "MAJOR",
                        "message": "Duplicate record found for {key_fields}: {key_values}"
                    }
                ]
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["queries"]) == 1
    assert result["queries"][0]["subject_id"] == "001"
    assert result["queries"][0]["query_type"] == "duplicate_record"
    assert "duplicate_of_index" in result["queries"][0]


def test_data_query_generator_pattern_checks():
    """Test pattern violation detection."""
    input_data = {
        "data": "subject_id,phone,email\n001,123-456-7890,john@example.com\n002,1234567890,invalid-email\n003,123-45-6789,jane@test.org",
        "query_rules": {
            "categories": {
                "format_checks": [
                    {
                        "name": "Phone Format",
                        "type": "pattern_match",
                        "field": "phone",
                        "pattern": r"^\d{3}-\d{3}-\d{4}$",
                        "pattern_type": "must_match",
                        "severity": "MINOR",
                        "message": "Invalid phone format: {value}"
                    },
                    {
                        "name": "Email Format",
                        "type": "pattern_match",
                        "field": "email",
                        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                        "pattern_type": "must_match",
                        "severity": "MINOR",
                        "message": "Invalid email format: {value}"
                    }
                ]
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["queries"]) == 3
    
    phone_queries = [q for q in result["queries"] if q["field"] == "phone"]
    email_queries = [q for q in result["queries"] if q["field"] == "email"]
    
    assert len(phone_queries) == 2  # 002 and 003 have invalid phone formats
    assert len(email_queries) == 1  # Only 002 has invalid email
    
    # Check one phone query
    phone_query = next(q for q in phone_queries if q["subject_id"] == "002")
    assert phone_query["value"] == "1234567890"
    
    # Check email query
    email_query = email_queries[0]
    assert email_query["subject_id"] == "002"
    assert email_query["value"] == "invalid-email"


def test_data_query_generator_conditional_rules():
    """Test conditional rule application."""
    input_data = {
        "data": "subject_id,study_arm,dose,age\n001,Treatment,100,25\n002,Treatment,,30\n003,Control,50,35",
        "query_rules": {
            "categories": {
                "conditional_checks": [
                    {
                        "name": "Treatment Dose Required",
                        "type": "missing_required",
                        "fields": ["dose"],
                        "conditions": {"study_arm": "Treatment"},
                        "severity": "CRITICAL",
                        "message": "Missing dose for treatment subject {subject_id}"
                    }
                ]
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["queries"]) == 1
    assert result["queries"][0]["subject_id"] == "002"
    assert result["queries"][0]["field"] == "dose"
    assert "treatment subject" in result["queries"][0]["message"].lower()


def test_data_query_generator_date_logic():
    """Test date logic validation."""
    input_data = {
        "data": "subject_id,consent_date,randomization_date,treatment_start\n001,2024-01-01,2024-01-05,2024-01-10\n002,2024-02-01,2024-01-15,2024-02-05",
        "query_rules": {
            "categories": {
                "date_checks": [
                    {
                        "name": "Chronological Order",
                        "type": "date_logic",
                        "date_rule": "chronological_order",
                        "date_fields": ["consent_date", "randomization_date", "treatment_start"],
                        "severity": "CRITICAL",
                        "message": "Date order violation: {field1} ({date1}) should be before {field2} ({date2})"
                    }
                ]
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["queries"]) == 1
    assert result["queries"][0]["subject_id"] == "002"
    assert "Date order violation" in result["queries"][0]["message"]


def test_data_query_generator_empty_data():
    """Test handling of empty data."""
    input_data = {
        "data": "",
        "query_rules": {
            "categories": {
                "basic_checks": [
                    {
                        "name": "Test Rule",
                        "type": "missing_required",
                        "fields": ["test_field"],
                        "severity": "MAJOR",
                        "message": "Test message"
                    }
                ]
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert "No data provided" in result["errors"]


def test_data_query_generator_no_rules():
    """Test handling when no query rules are provided."""
    input_data = {
        "data": "subject_id,test_field\n001,value1",
        "query_rules": {}
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert "No query rules provided" in result["errors"]


def test_data_query_generator_severity_levels():
    """Test custom severity level configuration."""
    input_data = {
        "data": "subject_id,age\n001,150",
        "query_rules": {
            "categories": {
                "age_checks": [
                    {
                        "name": "Age Range",
                        "type": "range_check",
                        "field": "age",
                        "min_value": 18,
                        "max_value": 85,
                        "severity": "URGENT",
                        "message": "Invalid age: {value}"
                    }
                ]
            }
        },
        "severity_levels": {
            "URGENT": {
                "description": "Urgent attention required",
                "priority": 1,
                "response_time_hours": 2,
                "escalation_required": True
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["queries"]) == 1
    assert result["queries"][0]["severity"] == "URGENT"
    assert result["queries"][0]["severity_details"]["response_time_hours"] == 2


def test_data_query_generator_auto_close_rules():
    """Test automatic query closure functionality."""
    input_data = {
        "data": "subject_id,age\n001,150",
        "query_rules": {
            "categories": {
                "age_checks": [
                    {
                        "name": "Age Range",
                        "type": "range_check",
                        "field": "age",
                        "min_value": 18,
                        "max_value": 85,
                        "severity": "INFO",
                        "message": "Invalid age: {value}"
                    }
                ]
            }
        },
        "auto_close_rules": {
            "close_info_queries": {
                "conditions": {
                    "severity_below": ["INFO"]
                },
                "reason": "Auto-closed: INFO level query"
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["statistics"]["auto_closed_queries"] == 1
    assert result["queries"][0]["status"] == "AUTO_CLOSED"
    assert "closure_reason" in result["queries"][0]


def test_data_query_generator_summary_generation():
    """Test query summary generation."""
    input_data = {
        "data": "subject_id,age,weight\n001,25,70\n002,35,\n003,150,80\n004,30,\n005,200,90",
        "query_rules": {
            "categories": {
                "basic_checks": [
                    {
                        "name": "Missing Weight",
                        "type": "missing_required",
                        "fields": ["weight"],
                        "severity": "MAJOR",
                        "message": "Missing weight"
                    },
                    {
                        "name": "Age Range",
                        "type": "range_check",
                        "field": "age",
                        "min_value": 18,
                        "max_value": 85,
                        "severity": "CRITICAL",
                        "message": "Age out of range"
                    }
                ]
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "summary" in result
    
    summary = result["summary"]
    assert "by_severity" in summary
    assert "by_type" in summary
    assert "by_status" in summary
    assert "top_rules" in summary
    assert "recommendation" in summary
    
    assert summary["by_severity"]["CRITICAL"] == 2  # Two age violations
    assert summary["by_severity"]["MAJOR"] == 2  # Two missing weights
    assert summary["affected_subjects"] == 4
    assert "Immediate attention required" in summary["recommendation"]


def test_data_query_generator_large_dataset():
    """Test performance with larger dataset."""
    # Create test data with 100 records
    data_lines = ["subject_id,age,weight"]
    for i in range(100):
        age = 25 + (i % 60)  # Ages from 25 to 84
        weight = 70 + (i % 50)  # Weights from 70 to 119
        # Make every 10th record missing weight to generate queries
        weight_val = weight if i % 10 != 0 else ""
        data_lines.append(f"{i+1:03d},{age},{weight_val}")
    
    input_data = {
        "data": "\n".join(data_lines),
        "query_rules": {
            "categories": {
                "basic_checks": [
                    {
                        "name": "Missing Weight",
                        "type": "missing_required",
                        "fields": ["weight"],
                        "severity": "MAJOR",
                        "message": "Missing weight"
                    }
                ]
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["statistics"]["total_records_checked"] == 100
    assert result["statistics"]["queries_generated"] == 10  # Every 10th record
    assert result["processing_info"]["processing_time_seconds"] < 1.0  # Should be fast