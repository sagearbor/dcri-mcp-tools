import pytest
from tools.adverse_event_coder import run


def test_adverse_event_coder_basic():
    """Test basic AE coding with known terms."""
    input_data = {
        "events": [
            {
                "verbatim_term": "severe headache",
                "severity_description": "severe",
                "subject_id": "001",
                "start_date": "2024-01-15",
                "end_date": "2024-01-17"
            },
            {
                "verbatim_term": "mild nausea",
                "severity_description": "mild",
                "subject_id": "002"
            }
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["coded_events"]) == 2
    
    headache_event = result["coded_events"][0]
    assert headache_event["preferred_term"] == "Headache"
    assert headache_event["system_organ_class"] == "Nervous system disorders"
    assert headache_event["severity_grade"] == 3
    assert headache_event["duration_days"] == 2
    
    nausea_event = result["coded_events"][1]
    assert nausea_event["preferred_term"] == "Nausea"
    assert nausea_event["system_organ_class"] == "Gastrointestinal disorders"
    assert nausea_event["severity_grade"] == 1


def test_adverse_event_coder_uncoded_terms():
    """Test handling of terms that can't be coded."""
    input_data = {
        "events": [
            {
                "verbatim_term": "unknown_syndrome_xyz",
                "subject_id": "003"
            }
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["coded_events"]) == 1
    assert result["coded_events"][0]["coding_status"] == "UNCODED"
    assert len(result["uncoded_terms"]) == 1
    assert "unknown_syndrome_xyz" in result["uncoded_terms"]


def test_adverse_event_coder_fuzzy_matching():
    """Test fuzzy matching for similar terms."""
    input_data = {
        "events": [
            {
                "verbatim_term": "feeling dizzy",
                "subject_id": "004"
            },
            {
                "verbatim_term": "throwing up",
                "subject_id": "005"
            }
        ],
        "match_threshold": 0.6
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["coded_events"]) == 2
    
    assert result["coded_events"][0]["preferred_term"] == "Dizziness"
    assert result["coded_events"][1]["preferred_term"] == "Vomiting"


def test_adverse_event_coder_severity_grading():
    """Test CTCAE severity grading."""
    input_data = {
        "events": [
            {"verbatim_term": "headache", "severity_description": "mild"},
            {"verbatim_term": "headache", "severity_description": "moderate"},
            {"verbatim_term": "headache", "severity_description": "severe"},
            {"verbatim_term": "headache", "severity_description": "life-threatening"},
            {"verbatim_term": "headache", "severity_description": "fatal"}
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert result["coded_events"][0]["severity_grade"] == 1
    assert result["coded_events"][1]["severity_grade"] == 2
    assert result["coded_events"][2]["severity_grade"] == 3
    assert result["coded_events"][3]["severity_grade"] == 4
    assert result["coded_events"][4]["severity_grade"] == 5


def test_adverse_event_coder_summary_statistics():
    """Test summary statistics generation."""
    input_data = {
        "events": [
            {"verbatim_term": "headache", "severity_description": "mild"},
            {"verbatim_term": "nausea", "severity_description": "moderate"},
            {"verbatim_term": "vomiting", "severity_description": "moderate"},
            {"verbatim_term": "fatigue", "severity_description": "mild"},
            {"verbatim_term": "unknown_term", "severity_description": "severe"}
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert result["summary"]["total_events"] == 5
    assert result["summary"]["coded_events"] == 4
    assert result["summary"]["uncoded_events"] == 1
    assert result["summary"]["coding_rate"] == 80.0
    
    assert "Gastrointestinal disorders" in result["summary"]["soc_distribution"]
    assert result["summary"]["soc_distribution"]["Gastrointestinal disorders"] == 2
    
    assert result["summary"]["severity_distribution"]["grade_1"] == 2
    assert result["summary"]["severity_distribution"]["grade_2"] == 2
    assert result["summary"]["severity_distribution"]["grade_3"] == 1


def test_adverse_event_coder_empty_input():
    """Test handling of empty input."""
    result = run({"events": []})
    
    assert result["error"] == "No adverse events provided"
    assert result["coded_events"] == []


def test_adverse_event_coder_missing_verbatim():
    """Test handling of events with missing verbatim terms."""
    input_data = {
        "events": [
            {"subject_id": "001"},
            {"verbatim_term": "", "subject_id": "002"},
            {"verbatim_term": "headache", "subject_id": "003"}
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["coded_events"]) == 1
    assert len(result["warnings"]) > 0