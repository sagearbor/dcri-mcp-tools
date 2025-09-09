import pytest
from tools.patient_narrative_generator import run


def test_patient_narrative_generator_basic():
    """Test basic narrative generation."""
    input_data = {
        "patient_data": {
            "subject_id": "001",
            "age": 45,
            "sex": "female",
            "medical_history": ["Hypertension", "Diabetes"],
            "enrollment_date": "2024-01-15",
            "treatment_group": "Drug A 100mg",
            "completion_status": "completed"
        },
        "adverse_events": [
            {
                "event_term": "Headache",
                "onset_date": "2024-02-01",
                "severity": "Mild",
                "outcome": "Resolved"
            }
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["narrative"]) > 0
    assert "001" in result["narrative"]
    assert result["word_count"] > 0


def test_patient_narrative_generator_sae():
    """Test SAE narrative generation."""
    input_data = {
        "patient_data": {
            "subject_id": "002",
            "age": 65,
            "sex": "male",
            "treatment_group": "Drug B",
            "completion_status": "discontinued"
        },
        "adverse_events": [
            {
                "event_term": "Myocardial infarction",
                "onset_date": "2024-03-01",
                "severity": "Grade 4",
                "serious": True,
                "outcome": "Recovering",
                "causality": "Possibly related"
            }
        ],
        "narrative_type": "sae"
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert "SERIOUS ADVERSE EVENT" in result["narrative"]
    assert "Myocardial infarction" in result["narrative"]


def test_patient_narrative_generator_empty_input():
    """Test handling of empty input."""
    result = run({})
    assert result["error"] == "No patient data provided"
