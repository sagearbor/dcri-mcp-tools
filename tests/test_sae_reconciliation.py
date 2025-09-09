import pytest
from tools.sae_reconciliation import run


def test_sae_reconciliation_basic_match():
    """Test basic SAE matching between EDC and safety database."""
    input_data = {
        "edc_saes": [
            {
                "subject_id": "001",
                "event_term": "Myocardial infarction",
                "onset_date": "2024-01-15",
                "severity": "Grade 4",
                "outcome": "Recovered",
                "causality": "Possibly related"
            }
        ],
        "safety_db_saes": [
            {
                "subject_id": "001",
                "event_term": "Myocardial infarction",
                "onset_date": "2024-01-15",
                "severity": "Grade 4",
                "outcome": "Recovered",
                "causality": "Possibly related"
            }
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["matched_saes"]) == 1
    assert result["matched_saes"][0]["match_confidence"] > 0.9
    assert result["summary"]["reconciliation_rate"] == 100.0


def test_sae_reconciliation_with_discrepancies():
    """Test SAE reconciliation with field discrepancies."""
    input_data = {
        "edc_saes": [
            {
                "subject_id": "002",
                "event_term": "Pneumonia",
                "onset_date": "2024-02-01",
                "severity": "Grade 3",
                "outcome": "Recovering",
                "causality": "Not related"
            }
        ],
        "safety_db_saes": [
            {
                "subject_id": "002",
                "event_term": "Pneumonia",
                "onset_date": "2024-02-01",
                "severity": "Grade 3",
                "outcome": "Recovered",  # Different outcome
                "causality": "Unlikely related"  # Different causality
            }
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["matched_saes"]) == 1
    assert len(result["discrepancies"]) == 2
    
    outcome_disc = [d for d in result["discrepancies"] if d["discrepancy_type"] == "Outcome"][0]
    assert outcome_disc["severity"] == "critical"
    
    causality_disc = [d for d in result["discrepancies"] if d["discrepancy_type"] == "Causality"][0]
    assert causality_disc["severity"] == "critical"


def test_sae_reconciliation_date_tolerance():
    """Test SAE matching with date tolerance."""
    input_data = {
        "edc_saes": [
            {
                "subject_id": "003",
                "event_term": "Stroke",
                "onset_date": "2024-03-01",
                "severity": "Grade 5"
            }
        ],
        "safety_db_saes": [
            {
                "subject_id": "003",
                "event_term": "Stroke",
                "onset_date": "2024-03-03",  # 2 days difference
                "severity": "Grade 5"
            }
        ],
        "reconciliation_rules": {
            "date_tolerance_days": 3
        }
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["matched_saes"]) == 1
    assert result["matched_saes"][0]["match_confidence"] > 0.7


def test_sae_reconciliation_unmatched():
    """Test identification of unmatched SAEs."""
    input_data = {
        "edc_saes": [
            {
                "subject_id": "004",
                "event_term": "Anaphylaxis",
                "onset_date": "2024-04-01"
            },
            {
                "subject_id": "005",
                "event_term": "Seizure",
                "onset_date": "2024-04-05"
            }
        ],
        "safety_db_saes": [
            {
                "subject_id": "004",
                "event_term": "Anaphylaxis",
                "onset_date": "2024-04-01"
            },
            {
                "subject_id": "006",
                "event_term": "Syncope",
                "onset_date": "2024-04-10"
            }
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["matched_saes"]) == 1
    assert len(result["unmatched_edc"]) == 1
    assert result["unmatched_edc"][0]["subject_id"] == "005"
    assert len(result["unmatched_safety_db"]) == 1
    assert result["unmatched_safety_db"][0]["subject_id"] == "006"


def test_sae_reconciliation_three_sources():
    """Test reconciliation across three data sources."""
    input_data = {
        "edc_saes": [
            {
                "subject_id": "007",
                "event_term": "Hepatitis",
                "onset_date": "2024-05-01",
                "severity": "Grade 3"
            }
        ],
        "safety_db_saes": [
            {
                "subject_id": "007",
                "event_term": "Hepatitis",
                "onset_date": "2024-05-01",
                "severity": "Grade 3"
            }
        ],
        "regulatory_saes": [
            {
                "subject_id": "007",
                "event_term": "Hepatitis",
                "onset_date": "2024-05-02",
                "severity": "Grade 3"
            }
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["matched_saes"]) == 1
    assert "Regulatory" in result["matched_saes"][0]["sources"]
    assert result["summary"]["total_regulatory_saes"] == 1


def test_sae_reconciliation_recommendations():
    """Test generation of reconciliation recommendations."""
    input_data = {
        "edc_saes": [
            {
                "subject_id": "008",
                "event_term": "Renal failure",
                "onset_date": "2024-06-01",
                "outcome": "Fatal",
                "causality": "Related"
            }
        ],
        "safety_db_saes": [
            {
                "subject_id": "008",
                "event_term": "Renal failure",
                "onset_date": "2024-06-01",
                "outcome": "Recovering",  # Critical discrepancy
                "causality": "Not related"  # Critical discrepancy
            },
            {
                "subject_id": "009",
                "event_term": "Cardiac arrest",
                "onset_date": "2024-06-05"
            }
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["recommendations"]) > 0
    
    critical_rec = [r for r in result["recommendations"] if r["priority"] == "CRITICAL"]
    assert len(critical_rec) > 0
    
    high_rec = [r for r in result["recommendations"] if r["priority"] == "HIGH"]
    assert len(high_rec) > 0


def test_sae_reconciliation_empty_input():
    """Test handling of empty input."""
    result = run({"edc_saes": [], "safety_db_saes": []})
    
    assert result["error"] == "No SAE data provided from any source"


def test_sae_reconciliation_fuzzy_term_matching():
    """Test fuzzy matching of event terms."""
    input_data = {
        "edc_saes": [
            {
                "subject_id": "010",
                "event_term": "Myocardial infarction",
                "onset_date": "2024-07-01"
            }
        ],
        "safety_db_saes": [
            {
                "subject_id": "010",
                "event_term": "MI (Myocardial infarction)",
                "onset_date": "2024-07-01"
            }
        ],
        "reconciliation_rules": {
            "term_match_threshold": 0.7
        }
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["matched_saes"]) == 1