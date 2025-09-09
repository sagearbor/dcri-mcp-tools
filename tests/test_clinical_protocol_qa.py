import pytest
from tools.clinical_protocol_qa import run


def test_clinical_protocol_qa_basic():
    """Test basic protocol Q&A with simple question."""
    input_data = {
        "question": "What is the primary endpoint?",
        "protocol_sections": {
            "Objectives": "The primary endpoint is overall survival measured from randomization to death from any cause.",
            "Study Design": "This is a randomized controlled trial comparing treatment A versus placebo.",
            "Statistical Analysis": "Primary analysis will use log-rank test for survival comparison."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "answer" in result
    assert "confidence_score" in result
    assert result["confidence_score"] > 0.7
    assert "primary endpoint" in result["answer"].lower()
    assert result["question_classification"] == "definition"


def test_clinical_protocol_qa_definition_question():
    """Test definition-type questions."""
    input_data = {
        "question": "What is overall survival?",
        "protocol_sections": {
            "Definitions": "Overall survival is defined as the time from randomization to death from any cause.",
            "Endpoints": "Primary endpoint: Overall survival (OS). Secondary endpoints include progression-free survival."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["question_classification"] == "definition"
    assert "overall survival" in result["answer"].lower()
    assert "randomization to death" in result["answer"].lower()


def test_clinical_protocol_qa_quantitative_question():
    """Test quantitative questions."""
    input_data = {
        "question": "How many patients will be enrolled?",
        "protocol_sections": {
            "Study Design": "This study will enroll 500 patients across 25 sites over 18 months.",
            "Sample Size": "Sample size calculation: 500 patients needed for 80% power to detect hazard ratio of 0.75.",
            "Statistics": "Primary analysis population: 500 randomized patients."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["question_classification"] == "quantitative"
    assert "500" in result["answer"]


def test_clinical_protocol_qa_temporal_question():
    """Test timing/schedule questions."""
    input_data = {
        "question": "When are the follow-up visits scheduled?",
        "protocol_sections": {
            "Schedule": "Follow-up visits at weeks 2, 4, 8, 12, then every 12 weeks until progression.",
            "Procedures": "Safety assessments at each visit. Imaging every 8 weeks.",
            "Timeline": "Study duration estimated at 36 months including follow-up."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["question_classification"] == "temporal"
    assert any(word in result["answer"].lower() for word in ["week", "visit", "schedule"])


def test_clinical_protocol_qa_safety_question():
    """Test safety-related questions."""
    input_data = {
        "question": "What are the safety monitoring requirements?",
        "protocol_sections": {
            "Safety": "Safety monitoring includes weekly lab tests for first month, then monthly. DSMB reviews every 6 months.",
            "Adverse Events": "All AEs recorded and graded using CTCAE v5.0. SAEs reported within 24 hours.",
            "Stopping Rules": "Study may be stopped for unacceptable toxicity or futility."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["question_classification"] == "safety"
    assert any(word in result["answer"].lower() for word in ["safety", "monitoring", "adverse"])


def test_clinical_protocol_qa_no_relevant_sections():
    """Test when no relevant sections are found."""
    input_data = {
        "question": "What is the biomarker analysis plan?",
        "protocol_sections": {
            "Demographics": "Age 18-75 years, both genders eligible.",
            "Inclusion": "Confirmed diagnosis, adequate organ function.",
            "Exclusion": "Pregnancy, prior therapy within 4 weeks."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "couldn't find relevant information" in result["answer"]
    assert result["confidence_score"] == 0.0
    assert len(result["suggested_sections"]) > 0


def test_clinical_protocol_qa_empty_question():
    """Test handling of empty question."""
    input_data = {
        "question": "",
        "protocol_sections": {
            "Objectives": "Primary endpoint is overall survival.",
            "Design": "Randomized controlled trial."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert "No question provided" in result["error"]


def test_clinical_protocol_qa_empty_protocol():
    """Test handling of empty protocol sections."""
    input_data = {
        "question": "What is the primary endpoint?",
        "protocol_sections": {}
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert "No protocol sections provided" in result["error"]


def test_clinical_protocol_qa_follow_up_questions():
    """Test generation of follow-up questions."""
    input_data = {
        "question": "What is the dosing schedule?",
        "protocol_sections": {
            "Treatment": "Study drug administered orally once daily at 100mg for 28-day cycles.",
            "Modifications": "Dose reductions allowed for toxicity: 75mg, then 50mg."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "follow_up_questions" in result
    assert len(result["follow_up_questions"]) > 0
    assert isinstance(result["follow_up_questions"], list)


def test_clinical_protocol_qa_context_analysis():
    """Test context analysis functionality."""
    input_data = {
        "question": "What are the inclusion criteria for elderly patients?",
        "context": "We are reviewing eligibility criteria for a geriatric oncology protocol.",
        "protocol_sections": {
            "Inclusion": "Age ≥65 years, ECOG PS 0-2, life expectancy >3 months.",
            "Exclusion": "Significant cardiac disease, dementia, prior cancer within 5 years."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "context_analysis" in result
    assert result["context_analysis"] is not None


def test_clinical_protocol_qa_metadata():
    """Test metadata generation."""
    input_data = {
        "question": "What is the statistical analysis plan?",
        "protocol_sections": {
            "Statistics": "Primary analysis uses intent-to-treat population with log-rank test."
        },
        "complexity_level": "advanced"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "answer_metadata" in result
    assert "generated_at" in result["answer_metadata"]
    assert "sections_searched" in result["answer_metadata"]
    assert result["complexity_level"] == "advanced"


def test_clinical_protocol_qa_multiple_sections():
    """Test with multiple relevant sections."""
    input_data = {
        "question": "What are the efficacy endpoints?",
        "protocol_sections": {
            "Primary Objectives": "Assess overall survival in treatment vs control.",
            "Secondary Objectives": "Evaluate progression-free survival, response rate, and quality of life.",
            "Exploratory": "Correlative studies on biomarkers and pharmacokinetics.",
            "Statistical Plan": "Primary endpoint powered for hazard ratio of 0.75."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["source_sections"]) > 1
    assert "overall survival" in result["answer"].lower()
    assert any("secondary" in section.lower() for section in result["source_sections"])


def test_clinical_protocol_qa_long_protocol():
    """Test with very long protocol sections."""
    long_section = "This is a very long protocol section. " * 100
    
    input_data = {
        "question": "What is mentioned about the protocol?",
        "protocol_sections": {
            "Long Section": long_section
        },
        "context_window": 500
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "answer" in result
    assert len(result["answer"]) > 0


def test_clinical_protocol_qa_keyword_extraction():
    """Test keyword extraction functionality."""
    input_data = {
        "question": "What are the adverse event reporting requirements for serious events?",
        "protocol_sections": {
            "Safety": "Serious adverse events must be reported to sponsor within 24 hours of awareness.",
            "Reporting": "All SAEs require detailed narrative and follow-up until resolution."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "serious" in result["answer"].lower() or "sae" in result["answer"].lower()
    assert "24 hours" in result["answer"] or "reporting" in result["answer"].lower()


def test_clinical_protocol_qa_eligibility_question():
    """Test eligibility-related questions."""
    input_data = {
        "question": "Who is eligible for this study?",
        "protocol_sections": {
            "Inclusion Criteria": "Adult patients ≥18 years with confirmed diagnosis and adequate performance status.",
            "Exclusion Criteria": "Pregnancy, significant comorbidities, prior experimental therapy within 4 weeks.",
            "Subject Selection": "Patients screened for eligibility before randomization."
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["question_classification"] == "eligibility"
    assert any(word in result["answer"].lower() for word in ["eligible", "inclusion", "criteria"])