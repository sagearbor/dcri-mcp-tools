import pytest
from tools.concomitant_med_coder import run


def test_concomitant_med_coder_basic():
    """Test basic medication coding with known drugs."""
    input_data = {
        "medications": [
            {
                "verbatim_name": "aspirin 81mg",
                "dose": "81",
                "unit": "mg",
                "frequency": "once daily",
                "route": "oral",
                "subject_id": "001"
            },
            {
                "verbatim_name": "metformin",
                "dose": "500",
                "unit": "mg",
                "frequency": "twice daily",
                "subject_id": "002"
            }
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["coded_medications"]) == 2
    
    aspirin = result["coded_medications"][0]
    assert aspirin["drug_name"] == "ASPIRIN"
    assert aspirin["atc_code"] == "B01AC06"
    assert aspirin["therapeutic_class"] == "Antithrombotic agents"
    
    metformin = result["coded_medications"][1]
    assert metformin["drug_name"] == "METFORMIN"
    assert metformin["atc_code"] == "A10BA02"
    assert metformin["therapeutic_class"] == "Drugs used in diabetes"


def test_concomitant_med_coder_brand_names():
    """Test coding of brand name medications."""
    input_data = {
        "medications": [
            {"verbatim_name": "Tylenol", "subject_id": "003"},
            {"verbatim_name": "Lipitor", "subject_id": "004"},
            {"verbatim_name": "Advil", "subject_id": "005"}
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert result["coded_medications"][0]["drug_name"] == "PARACETAMOL"
    assert result["coded_medications"][1]["drug_name"] == "ATORVASTATIN"
    assert result["coded_medications"][2]["drug_name"] == "IBUPROFEN"


def test_concomitant_med_coder_uncoded():
    """Test handling of medications that can't be coded."""
    input_data = {
        "medications": [
            {"verbatim_name": "unknown_drug_xyz", "subject_id": "006"}
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["coded_medications"]) == 1
    assert result["coded_medications"][0]["coding_status"] == "UNCODED"
    assert len(result["uncoded_medications"]) == 1
    assert "unknown_drug_xyz" in result["uncoded_medications"]


def test_concomitant_med_coder_drug_interactions():
    """Test drug interaction checking."""
    input_data = {
        "medications": [
            {"verbatim_name": "warfarin", "subject_id": "007"},
            {"verbatim_name": "aspirin", "subject_id": "007"},
            {"verbatim_name": "metformin", "subject_id": "007"},
            {"verbatim_name": "prednisone", "subject_id": "007"}
        ],
        "include_interactions": True
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["potential_interactions"]) > 0
    
    warfarin_aspirin = False
    metformin_prednisone = False
    
    for interaction in result["potential_interactions"]:
        if interaction["drug1"] == "WARFARIN" and interaction["drug2"] == "ASPIRIN":
            warfarin_aspirin = True
            assert "bleeding" in interaction["interaction_type"].lower()
        if interaction["drug1"] == "METFORMIN" and interaction["drug2"] == "PREDNISONE":
            metformin_prednisone = True
            assert "glucose" in interaction["interaction_type"].lower()
    
    assert warfarin_aspirin
    assert metformin_prednisone


def test_concomitant_med_coder_route_validation():
    """Test route of administration validation."""
    input_data = {
        "medications": [
            {
                "verbatim_name": "insulin",
                "route": "oral",
                "subject_id": "008"
            }
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert len(result["warnings"]) > 0
    assert any("Route" in w for w in result["warnings"])


def test_concomitant_med_coder_summary_statistics():
    """Test summary statistics generation."""
    input_data = {
        "medications": [
            {"verbatim_name": "aspirin"},
            {"verbatim_name": "ibuprofen"},
            {"verbatim_name": "metformin"},
            {"verbatim_name": "lisinopril"},
            {"verbatim_name": "unknown_med"}
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert result["summary"]["total_medications"] == 5
    assert result["summary"]["coded_medications"] == 4
    assert result["summary"]["uncoded_medications"] == 1
    assert result["summary"]["coding_rate"] == 80.0
    assert result["summary"]["unique_drugs"] == 4
    
    assert "Antithrombotic agents" in result["summary"]["therapeutic_class_distribution"]
    assert "Cardiovascular system" in result["summary"]["anatomical_class_distribution"]


def test_concomitant_med_coder_ongoing_medications():
    """Test identification of ongoing medications."""
    input_data = {
        "medications": [
            {
                "verbatim_name": "aspirin",
                "start_date": "2024-01-01",
                "stop_date": "2024-01-31"
            },
            {
                "verbatim_name": "metformin",
                "start_date": "2024-01-01"
            }
        ]
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert result["coded_medications"][0]["ongoing"] is False
    assert result["coded_medications"][1]["ongoing"] is True


def test_concomitant_med_coder_empty_input():
    """Test handling of empty input."""
    result = run({"medications": []})
    
    assert result["error"] == "No medications provided"
    assert result["coded_medications"] == []


def test_concomitant_med_coder_fuzzy_matching():
    """Test fuzzy matching for similar drug names."""
    input_data = {
        "medications": [
            {"verbatim_name": "aspirn"},
            {"verbatim_name": "ibuprofn"}
        ],
        "match_threshold": 0.7
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert result["coded_medications"][0]["drug_name"] == "ASPIRIN"
    assert result["coded_medications"][1]["drug_name"] == "IBUPROFEN"
    assert result["coded_medications"][0]["match_confidence"] < 1.0
    assert result["coded_medications"][1]["match_confidence"] < 1.0