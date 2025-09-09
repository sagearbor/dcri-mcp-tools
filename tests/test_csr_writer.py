import pytest
from tools.csr_writer import run


def test_csr_writer_basic():
    """Test basic CSR section generation."""
    input_data = {
        "section_type": "summary",
        "study_data": {
            "study_title": "Phase III Study of Drug X vs Placebo",
            "protocol_number": "DRUG-X-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Indication",
            "study_design": "Randomized, double-blind, placebo-controlled",
            "primary_endpoint": "Overall survival",
            "sample_size": 500,
            "enrollment_period": "24 months"
        },
        "template_requirements": {
            "include_statistical_summary": True,
            "include_safety_overview": True
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["csr_section"]["section_type"] == "summary"
    assert len(result["csr_section"]["content"]) > 0
    assert "Phase III Study" in result["csr_section"]["content"]
    assert result["quality_assessment"]["overall_score"] > 0


def test_csr_writer_methods_section():
    """Test study design section generation."""
    input_data = {
        "section_type": "study_design",
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "design_type": "Multicenter, randomized, double-blind, placebo-controlled trial",
            "randomization": True,
            "blinding": "double-blind",
            "control_type": "placebo-controlled",
            "study_duration": "24 months",
            "number_of_sites": 25,
            "countries": ["US", "Canada", "EU"],
            "sample_size_planned": 500,
            "sample_size_actual": 475,
            "randomization_ratio": "1:1",
            "stratification_factors": ["site", "age_group"],
            "inclusion_criteria": [
                "Age 18-75 years",
                "Confirmed diagnosis of target condition",
                "ECOG performance status 0-1"
            ],
            "exclusion_criteria": [
                "Pregnant or nursing women",
                "Previous treatment with study drug",
                "Significant cardiac disease"
            ],
            "primary_endpoint": "Progression-free survival",
            "secondary_endpoints": ["Overall survival", "Response rate", "Safety"]
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["csr_section"]["section_type"] == "study_design"
    assert "randomized" in result["csr_section"]["content"].lower()
    assert "inclusion and exclusion criteria" in result["csr_section"]["content"].lower()
    assert "study design" in result["csr_section"]["content"].lower()


def test_csr_writer_results_section():
    """Test efficacy results section generation."""
    input_data = {
        "section_type": "efficacy",
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "enrollment": {
                "planned": 500,
                "actual": 478,
                "completion_rate": "89%"
            },
            "demographics": {
                "median_age": 62,
                "gender_distribution": {"male": "55%", "female": "45%"},
                "race_distribution": {"white": "70%", "black": "15%", "other": "15%"}
            },
            "primary_results": {
                "primary_endpoint_met": True,
                "hazard_ratio": 0.72,
                "confidence_interval": "0.58-0.89",
                "p_value": "0.003"
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["csr_section"]["section_type"] == "efficacy"
    assert "enrollment" in result["csr_section"]["content"].lower() or "efficacy" in result["csr_section"]["content"].lower()
    assert result["quality_assessment"]["overall_score"] > 0


def test_csr_writer_safety_section():
    """Test safety section generation."""
    input_data = {
        "section_type": "safety",
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "safety_population": 475,
            "exposure_data": {
                "median_treatment_duration": "12.5 months",
                "total_patient_years": 450
            },
            "adverse_events": {
                "any_ae": {"treatment": "85%", "placebo": "78%"},
                "serious_ae": {"treatment": "25%", "placebo": "30%"},
                "treatment_related_ae": {"treatment": "60%", "placebo": "40%"}
            },
            "common_aes": [
                {"term": "Nausea", "grade": "1-2", "frequency": "35%"},
                {"term": "Fatigue", "grade": "1-2", "frequency": "30%"},
                {"term": "Diarrhea", "grade": "1-3", "frequency": "25%"}
            ]
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["csr_section"]["section_type"] == "safety"
    assert "safety" in result["csr_section"]["content"].lower()
    assert "adverse events" in result["csr_section"]["content"].lower()
    assert result["quality_assessment"]["overall_score"] > 0


def test_csr_writer_discussion_section():
    """Test discussion section generation."""
    input_data = {
        "section_type": "discussion",
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "key_findings": [
                "Significant improvement in primary endpoint",
                "Acceptable safety profile",
                "Benefit observed across subgroups"
            ],
            "clinical_significance": "The observed hazard ratio of 0.72 represents a clinically meaningful benefit",
            "limitations": [
                "Open-label design after progression",
                "Limited long-term follow-up data"
            ],
            "comparison_to_literature": "Results consistent with previous phase II studies"
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["csr_section"]["section_type"] == "discussion"
    assert "discussion" in result["csr_section"]["content"].lower() or "efficacy" in result["csr_section"]["content"].lower()
    assert "clinical" in result["csr_section"]["content"].lower() or "limitations" in result["csr_section"]["content"].lower()


def test_csr_writer_conclusions_section():
    """Test conclusions section generation."""
    input_data = {
        "section_type": "conclusions",
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "primary_conclusion": "Drug X demonstrated superior efficacy compared to placebo",
            "safety_conclusion": "Safety profile was acceptable and manageable",
            "regulatory_implications": "Results support regulatory submission",
            "clinical_impact": "Drug X offers a new treatment option for patients"
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["csr_section"]["section_type"] == "conclusions"
    assert "conclusions" in result["csr_section"]["content"].lower() or "efficacy" in result["csr_section"]["content"].lower()
    assert result["quality_assessment"]["overall_score"] > 0


def test_csr_writer_quality_checks():
    """Test quality check functionality."""
    input_data = {
        "section_type": "efficacy",
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "enrollment": {"planned": 500, "actual": 478},
            "primary_results": {
                "primary_endpoint_met": True,
                "hazard_ratio": 0.72,
                "p_value": "0.003"
            }
        },
        "quality_requirements": {
            "check_statistical_significance": True,
            "check_completeness": True,
            "check_regulatory_compliance": True
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "quality_assessment" in result
    quality = result["quality_assessment"]
    assert "completeness" in quality
    assert "compliance" in quality
    assert quality["overall_score"] > 0


def test_csr_writer_template_adherence():
    """Test template adherence checking."""
    input_data = {
        "section_type": "study_design",
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "study_design": "Randomized controlled trial",
            "primary_endpoint": "Overall survival"
        },
        "template_requirements": {
            "required_subsections": [
                "study_design",
                "study_population", 
                "endpoints",
                "statistical_methods"
            ],
            "word_count_range": {"min": 500, "max": 2000}
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["csr_section"]["word_count"] > 0
    assert result["quality_assessment"]["overall_score"] >= 0


def test_csr_writer_regulatory_compliance():
    """Test regulatory compliance checking."""
    input_data = {
        "section_type": "safety",
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "safety_population": 475,
            "adverse_events": {
                "any_ae": {"treatment": "85%", "placebo": "78%"},
                "serious_ae": {"treatment": "25%", "placebo": "30%"}
            }
        },
        "regulatory_context": ["FDA", "EMA"],
        "compliance_requirements": ["ICH E3", "safety_reporting_standards"]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["quality_assessment"]["compliance"]["score"] >= 0
    compliance = result["compliance_checklist"]
    assert "ich_e3_compliance" in compliance


def test_csr_writer_statistical_integration():
    """Test statistical data integration."""
    input_data = {
        "section_type": "efficacy",
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "statistical_analysis": {
                "analysis_sets": ["ITT", "PP", "Safety"],
                "primary_analysis": "ITT",
                "statistical_methods": "Log-rank test",
                "significance_level": 0.05
            },
            "primary_results": {
                "hazard_ratio": 0.72,
                "confidence_interval": "0.58-0.89",
                "p_value": "0.003"
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    content = result["csr_section"]["content"].lower()
    assert "statistical" in content or "efficacy" in content
    assert result["quality_assessment"]["overall_score"] > 0


def test_csr_writer_empty_study_data():
    """Test handling of empty study data."""
    input_data = {
        "section_type": "results",
        "study_data": {}
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert "No study data provided" in result["error"]


def test_csr_writer_invalid_section_type():
    """Test handling of invalid section type."""
    input_data = {
        "section_type": "invalid_section",
        "study_data": {
            "study_title": "Test Study"
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert "Invalid section type" in result["error"]


def test_csr_writer_appendices_generation():
    """Test supporting materials generation."""
    input_data = {
        "section_type": "summary",  # Use valid section type
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "statistical_output": ["Table 1: Demographics", "Figure 1: Kaplan-Meier"],
            "protocol_deviations": 15,
            "site_information": {
                "total_sites": 25,
                "countries": ["US", "Canada", "EU"]
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["csr_section"]["section_type"] == "summary"
    assert "supporting_materials" in result
    materials = result["supporting_materials"]
    assert "tables" in materials
    assert "figures" in materials


def test_csr_writer_multi_section_generation():
    """Test single section generation (multi-section not supported by API)."""
    input_data = {
        "section_type": "summary",  # Use valid section type
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "study_title": "Comprehensive Phase III Trial",
            "study_design": "Randomized, double-blind",
            "enrollment": {"actual": 500},
            "primary_results": {"primary_endpoint_met": True},
            "adverse_events": {"acceptable_profile": True}
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["csr_section"]["section_type"] == "summary"
    assert len(result["csr_section"]["content"]) > 0
    assert result["quality_assessment"]["overall_score"] > 0


def test_csr_writer_version_control():
    """Test metadata generation (version control info in metadata)."""
    input_data = {
        "section_type": "efficacy",
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "enrollment": {"actual": 500},
            "primary_results": {"primary_endpoint_met": True}
        },
        "version_info": {
            "version": "2.0",
            "previous_version": "1.0",
            "changes": ["Updated efficacy data", "Added subgroup analysis"]
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "metadata" in result
    metadata = result["metadata"]
    assert "generation_timestamp" in metadata
    assert len(result["csr_section"]["content"]) > 0


def test_csr_writer_review_comments_integration():
    """Test revision suggestions (similar to review comments)."""
    input_data = {
        "section_type": "study_design",
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "study_design": "Randomized trial",
            "primary_endpoint": "Overall survival"
        },
        "review_comments": [
            {
                "section": "study_design",
                "comment": "Add more detail on randomization method",
                "status": "open"
            },
            {
                "section": "study_design", 
                "comment": "Clarify inclusion criteria",
                "status": "resolved"
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "revision_suggestions" in result
    suggestions = result["revision_suggestions"]
    assert isinstance(suggestions, list)
    assert result["quality_assessment"]["overall_score"] >= 0


def test_csr_writer_formatting_consistency():
    """Test metadata includes formatting information."""
    input_data = {
        "section_type": "efficacy",
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "enrollment": {"actual": 500},
            "demographics": {"median_age": 65}
        },
        "formatting_requirements": {
            "number_format": "standard",
            "table_style": "professional",
            "figure_numbering": "sequential"
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "metadata" in result
    metadata = result["metadata"]
    assert "template_style" in metadata
    assert result["csr_section"]["template_style"] in ["ich_e3", "company_specific"]


def test_csr_writer_large_study_data():
    """Test with comprehensive study data."""
    # Create comprehensive study data
    large_study_data = {
        "protocol_number": "LARGE-001",
        "sponsor": "Major Pharma",
        "indication": "Advanced Cancer",
        "study_title": "Large Multicenter Phase III Trial",
        "study_design": "Randomized, double-blind, placebo-controlled",
        "enrollment": {
            "planned": 1000,
            "actual": 987,
            "sites": 50,
            "countries": 15
        },
        "demographics": {
            "median_age": 64,
            "age_ranges": {"18-65": "60%", "65+": "40%"},
            "gender": {"male": "55%", "female": "45%"}
        },
        "primary_results": {
            "primary_endpoint": "Overall survival",
            "hazard_ratio": 0.68,
            "confidence_interval": "0.55-0.84",
            "p_value": "<0.001",
            "median_survival": {"treatment": "18.5 months", "control": "12.3 months"}
        },
        "adverse_events": {
            "safety_population": 985,
            "treatment_emergent_aes": "92%",
            "serious_aes": "35%",
            "discontinuations_due_to_aes": "15%"
        }
    }
    
    input_data = {
        "section_type": "summary",  # Use valid section type
        "study_data": large_study_data
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["quality_assessment"]["overall_score"] > 0
    assert len(result["csr_section"]["content"]) > 100
    assert result["csr_section"]["word_count"] > 10


def test_csr_writer_recommendations_generation():
    """Test revision suggestions generation."""
    input_data = {
        "section_type": "efficacy",
        "study_data": {
            "protocol_number": "TEST-001",
            "sponsor": "Test Sponsor",
            "indication": "Test Condition",
            "enrollment": {"completion_rate": "85%"},
            "primary_results": {"primary_endpoint_met": True},
            "adverse_events": {"acceptable_profile": True}
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "revision_suggestions" in result
    suggestions = result["revision_suggestions"]
    assert isinstance(suggestions, list)
    assert result["quality_assessment"]["recommendations"] is not None