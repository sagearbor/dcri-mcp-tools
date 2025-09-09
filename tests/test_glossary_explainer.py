import pytest
from tools.glossary_explainer import run


def test_glossary_explainer_basic():
    """Test basic term explanation with exact match."""
    input_data = {
        "term": "adverse event",
        "glossary_data": {
            "adverse event": "An untoward medical occurrence in a patient or clinical investigation subject administered a pharmaceutical product."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["term"] == "adverse event"
    assert result["match_type"] == "exact"
    assert result["confidence_score"] > 0.9
    assert "untoward medical occurrence" in result["explanation"]


def test_glossary_explainer_fuzzy_match():
    """Test fuzzy matching for similar terms."""
    input_data = {
        "term": "AE",
        "glossary_data": {
            "adverse event": "An untoward medical occurrence in a patient or clinical investigation subject.",
            "serious adverse event": "An adverse event that is life-threatening or requires hospitalization."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["match_type"] in ["fuzzy", "exact"]
    assert result["confidence_score"] > 0.6


def test_glossary_explainer_no_match():
    """Test handling when no match is found."""
    input_data = {
        "term": "unknown_medical_term",
        "glossary_data": {
            "adverse event": "An untoward medical occurrence.",
            "serious adverse event": "A life-threatening adverse event."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["match_type"] == "none"
    assert result["confidence_score"] == 0.0
    assert "don't have a specific definition" in result["explanation"]
    assert "suggested_terms" in result


def test_glossary_explainer_with_context():
    """Test explanation enhancement with context."""
    input_data = {
        "term": "SAE",
        "context": "The patient experienced a serious adverse event requiring immediate hospitalization.",
        "glossary_data": {
            "serious adverse event": "An adverse event that results in death, is life-threatening, requires hospitalization, or results in significant disability.",
            "sae": "Serious Adverse Event"
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "context_analysis" in result
    assert result["context_analysis"] is not None
    assert "safety" in result["explanation"].lower() or "hospitalization" in result["explanation"].lower()


def test_glossary_explainer_complexity_levels():
    """Test different complexity levels."""
    term_data = {
        "term": "pharmacokinetics",
        "glossary_data": {
            "pharmacokinetics": "The study of how the body processes a drug, including absorption, distribution, metabolism, and excretion (ADME)."
        }
    }
    
    # Test basic level
    basic_result = run({**term_data, "complexity_level": "basic"})
    assert basic_result["success"] == True
    assert basic_result["complexity_level"] == "basic"
    
    # Test advanced level
    advanced_result = run({**term_data, "complexity_level": "advanced"})
    assert advanced_result["success"] == True
    assert advanced_result["complexity_level"] == "advanced"
    
    # Advanced should have more detailed explanation
    assert len(advanced_result["explanation"]) >= len(basic_result["explanation"])


def test_glossary_explainer_related_terms():
    """Test related terms functionality."""
    input_data = {
        "term": "adverse event",
        "glossary_data": {
            "adverse event": "An untoward medical occurrence in a patient.",
            "serious adverse event": "An adverse event that is life-threatening.",
            "expected adverse event": "An adverse event that is documented in the investigator brochure.",
            "unexpected adverse event": "An adverse event not listed in the investigator brochure.",
            "drug reaction": "An adverse response to a drug."
        },
        "include_related": True
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "related_terms" in result
    assert len(result["related_terms"]) > 0
    assert any("serious adverse event" in term["term"] for term in result["related_terms"])


def test_glossary_explainer_empty_term():
    """Test handling of empty term."""
    input_data = {
        "term": "",
        "glossary_data": {
            "adverse event": "An untoward medical occurrence."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert "No term provided" in result["error"]


def test_glossary_explainer_empty_glossary():
    """Test handling of empty glossary."""
    input_data = {
        "term": "adverse event",
        "glossary_data": {}
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["match_type"] == "generated"
    assert "clinical trial term" in result["explanation"]


def test_glossary_explainer_usage_examples():
    """Test usage examples generation."""
    input_data = {
        "term": "informed consent",
        "context": "The patient signed the informed consent form before participating in the study.",
        "glossary_data": {
            "informed consent": "A process by which a subject voluntarily confirms their willingness to participate in a particular trial."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "usage_examples" in result
    assert len(result["usage_examples"]) > 0
    assert any("icf" in example.lower() or "consent" in example.lower() for example in result["usage_examples"])


def test_glossary_explainer_medical_abbreviations():
    """Test medical abbreviation explanations."""
    input_data = {
        "term": "GCP",
        "glossary_data": {
            "good clinical practice": "An international quality standard for clinical trials that ensures the rights, safety and well-being of trial subjects are protected.",
            "gcp": "Good Clinical Practice"
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["match_type"] in ["exact", "fuzzy"]
    assert "good clinical practice" in result["explanation"].lower()


def test_glossary_explainer_term_categorization():
    """Test term categorization functionality."""
    input_data = {
        "term": "serious adverse event",
        "glossary_data": {
            "serious adverse event": "An adverse event that results in death, is life-threatening, requires hospitalization, or results in significant disability."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "explanation_metadata" in result
    assert "term_category" in result["explanation_metadata"]
    assert result["explanation_metadata"]["term_category"] == "safety"


def test_glossary_explainer_regulatory_relevance():
    """Test regulatory relevance assessment."""
    high_relevance_terms = [
        ("SAE", {"sae": "Serious Adverse Event"}),
        ("GCP", {"gcp": "Good Clinical Practice"}),
        ("ICF", {"icf": "Informed Consent Form"})
    ]
    
    for term, glossary in high_relevance_terms:
        input_data = {
            "term": term,
            "glossary_data": glossary
        }
        
        result = run(input_data)
        
        assert result["success"] == True
        assert "explanation_metadata" in result
        assert "regulatory_relevance" in result["explanation_metadata"]
        assert result["explanation_metadata"]["regulatory_relevance"] in ["high", "medium", "low"]


def test_glossary_explainer_additional_resources():
    """Test additional resources provision."""
    input_data = {
        "term": "protocol deviation",
        "glossary_data": {
            "protocol deviation": "Any departure from the approved protocol."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "additional_resources" in result
    assert len(result["additional_resources"]) > 0
    assert any("ICH Guidelines" in resource["type"] for resource in result["additional_resources"])


def test_glossary_explainer_pattern_based_explanation():
    """Test pattern-based explanation generation."""
    # Test with terms not in glossary but matching patterns
    pattern_terms = [
        "appendectomy",  # -ectomy pattern
        "arthritis",     # -itis pattern
        "fibrosis"       # -osis pattern
    ]
    
    for term in pattern_terms:
        input_data = {
            "term": term,
            "glossary_data": {}  # Empty glossary to trigger pattern-based explanation
        }
        
        result = run(input_data)
        
        assert result["success"] == True
        assert result["match_type"] == "generated"
        assert "medical term" in result["explanation"]


def test_glossary_explainer_normalization():
    """Test term normalization functionality."""
    input_data = {
        "term": "  ADVERSE  EVENT  ",  # Extra spaces and different case
        "glossary_data": {
            "adverse event": "An untoward medical occurrence."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["match_type"] == "exact"
    assert result["term"] == "  ADVERSE  EVENT  "  # Original preserved
    assert "untoward medical occurrence" in result["explanation"]


def test_glossary_explainer_suggested_terms():
    """Test suggested terms when no match found."""
    input_data = {
        "term": "drug reaction",
        "glossary_data": {
            "adverse drug reaction": "A response to a drug that is noxious and unintended.",
            "drug interaction": "A situation in which a substance affects the activity of a drug.",
            "unexpected reaction": "A reaction not listed in the investigator brochure."
        }
    }
    
    result = run(input_data)
    
    # Should find some match due to similarity
    assert result["success"] == True
    if result["match_type"] == "none":
        assert "suggested_terms" in result
        assert len(result["suggested_terms"]) > 0


def test_glossary_explainer_large_glossary():
    """Test performance with large glossary."""
    # Create a larger glossary
    large_glossary = {}
    for i in range(100):
        large_glossary[f"term_{i}"] = f"Definition for term {i} in clinical trials."
    
    large_glossary["target_term"] = "This is the term we're looking for."
    
    input_data = {
        "term": "target_term",
        "glossary_data": large_glossary
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["match_type"] == "exact"
    assert "term we're looking for" in result["explanation"]
    assert result["explanation_metadata"]["glossary_entries_searched"] == 101