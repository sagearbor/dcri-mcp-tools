import pytest
from tools.csr_writer import run


def test_csr_writer_basic():
    """Test basic CSR section generation."""
    input_data = {
        "section_type": "executive_summary",
        "study_data": {
            "study_title": "Phase III Study of Drug X vs Placebo",
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
    assert result["section_type"] == "executive_summary"
    assert len(result["generated_content"]) > 0
    assert "Phase III Study" in result["generated_content"]
    assert result["quality_score"] > 0


def test_csr_writer_methods_section():
    """Test methods section generation."""
    input_data = {
        "section_type": "methods",
        "study_data": {
            "study_design": "Multicenter, randomized, double-blind, placebo-controlled trial",
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
    assert result["section_type"] == "methods"
    assert "randomized" in result["generated_content"].lower()
    assert "inclusion criteria" in result["generated_content"].lower()
    assert "primary endpoint" in result["generated_content"].lower()


def test_csr_writer_results_section():
    """Test results section generation."""
    input_data = {
        "section_type": "results",
        "study_data": {
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
            "efficacy_results": {
                "primary_endpoint_met": True,
                "hazard_ratio": 0.72,
                "confidence_interval": "0.58-0.89",
                "p_value": "0.003"
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["section_type"] == "results"
    assert "enrollment" in result["generated_content"].lower()
    assert "demographics" in result["generated_content"].lower()
    assert "0.72" in result["generated_content"]  # Hazard ratio
    assert result["quality_checks"]["statistical_reporting"]["complete"]


def test_csr_writer_safety_section():
    """Test safety section generation."""
    input_data = {
        "section_type": "safety",
        "study_data": {
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
    assert result["section_type"] == "safety"
    assert "safety population" in result["generated_content"].lower()
    assert "adverse events" in result["generated_content"].lower()
    assert "nausea" in result["generated_content"].lower()
    assert result["quality_checks"]["safety_reporting"]["complete"]


def test_csr_writer_discussion_section():
    """Test discussion section generation."""
    input_data = {
        "section_type": "discussion",
        "study_data": {
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
    assert result["section_type"] == "discussion"
    assert "key findings" in result["generated_content"].lower()
    assert "clinical significance" in result["generated_content"].lower()
    assert "limitations" in result["generated_content"].lower()


def test_csr_writer_conclusions_section():
    """Test conclusions section generation."""
    input_data = {
        "section_type": "conclusions",
        "study_data": {
            "primary_conclusion": "Drug X demonstrated superior efficacy compared to placebo",
            "safety_conclusion": "Safety profile was acceptable and manageable",
            "regulatory_implications": "Results support regulatory submission",
            "clinical_impact": "Drug X offers a new treatment option for patients"
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["section_type"] == "conclusions"
    assert "superior efficacy" in result["generated_content"]
    assert "regulatory submission" in result["generated_content"]
    assert result["quality_checks"]["conclusions_section"]["complete"]


def test_csr_writer_quality_checks():
    """Test quality check functionality."""
    input_data = {
        "section_type": "results",
        "study_data": {
            "enrollment": {"planned": 500, "actual": 478},
            "efficacy_results": {
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
    assert "quality_checks" in result
    quality = result["quality_checks"]
    assert "statistical_reporting" in quality
    assert "regulatory_compliance" in quality
    assert quality["overall_quality_score"] > 0


def test_csr_writer_template_adherence():
    """Test template adherence checking."""
    input_data = {
        "section_type": "methods",
        "study_data": {
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
    assert "template_compliance" in result
    compliance = result["template_compliance"]
    assert "required_sections_present" in compliance
    assert "word_count_appropriate" in compliance


def test_csr_writer_regulatory_compliance():
    """Test regulatory compliance checking."""
    input_data = {
        "section_type": "safety",
        "study_data": {
            "safety_population": 475,
            "adverse_events": {
                "any_ae": {"treatment": "85%", "placebo": "78%"},
                "serious_ae": {"treatment": "25%", "placebo": "30%"}
            }
        },
        "regulatory_context": ["FDA", "EMA"],
        "compliance_requirements": {
            "ich_e3": True,
            "safety_reporting_standards": True
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["quality_checks"]["regulatory_compliance"]["complete"]
    compliance = result["quality_checks"]["regulatory_compliance"]
    assert "ich_e3_compliant" in compliance
    assert "safety_standards_met" in compliance


def test_csr_writer_statistical_integration():
    """Test statistical data integration."""
    input_data = {
        "section_type": "results",
        "study_data": {
            "statistical_analysis": {
                "analysis_sets": ["ITT", "PP", "Safety"],
                "primary_analysis": "ITT",
                "statistical_methods": "Log-rank test",
                "significance_level": 0.05
            },
            "efficacy_results": {
                "hazard_ratio": 0.72,
                "confidence_interval": "0.58-0.89",
                "p_value": "0.003"
            }
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "statistical" in result["generated_content"].lower()
    assert "hazard ratio" in result["generated_content"].lower()
    assert "confidence interval" in result["generated_content"].lower()
    assert result["quality_checks"]["statistical_reporting"]["complete"]


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
    """Test appendices generation."""
    input_data = {
        "section_type": "appendices",
        "study_data": {
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
    assert result["section_type"] == "appendices"
    assert "appendices" in result
    appendices = result["appendices"]
    assert "statistical_outputs" in appendices
    assert "protocol_deviations" in appendices


def test_csr_writer_multi_section_generation():
    """Test multiple section generation."""
    input_data = {
        "section_type": "full_report",
        "study_data": {
            "study_title": "Comprehensive Phase III Trial",
            "study_design": "Randomized, double-blind",
            "enrollment": {"actual": 500},
            "efficacy_results": {"primary_endpoint_met": True},
            "safety_results": {"acceptable_profile": True}
        },
        "sections_to_generate": [
            "executive_summary",
            "methods", 
            "results",
            "conclusions"
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "multi_section_content" in result
    content = result["multi_section_content"]
    assert "executive_summary" in content
    assert "methods" in content
    assert "results" in content
    assert "conclusions" in content


def test_csr_writer_version_control():
    """Test version control functionality."""
    input_data = {
        "section_type": "results",
        "study_data": {
            "enrollment": {"actual": 500},
            "efficacy_results": {"primary_endpoint_met": True}
        },
        "version_info": {
            "version": "2.0",
            "previous_version": "1.0",
            "changes": ["Updated efficacy data", "Added subgroup analysis"]
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "version_control" in result
    version_info = result["version_control"]
    assert version_info["current_version"] == "2.0"
    assert len(version_info["change_summary"]) > 0


def test_csr_writer_review_comments_integration():
    """Test integration of review comments."""
    input_data = {
        "section_type": "methods",
        "study_data": {
            "study_design": "Randomized trial",
            "primary_endpoint": "Overall survival"
        },
        "review_comments": [
            {
                "section": "methods",
                "comment": "Add more detail on randomization method",
                "status": "open"
            },
            {
                "section": "methods", 
                "comment": "Clarify inclusion criteria",
                "status": "resolved"
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "review_integration" in result
    review = result["review_integration"]
    assert "comments_addressed" in review
    assert "pending_comments" in review


def test_csr_writer_formatting_consistency():
    """Test formatting consistency across sections."""
    input_data = {
        "section_type": "results",
        "study_data": {
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
    assert "formatting_metadata" in result
    formatting = result["formatting_metadata"]
    assert "style_applied" in formatting
    assert "consistency_score" in formatting


def test_csr_writer_large_study_data():
    """Test with comprehensive study data."""
    # Create comprehensive study data
    large_study_data = {
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
        "efficacy_results": {
            "primary_endpoint": "Overall survival",
            "hazard_ratio": 0.68,
            "confidence_interval": "0.55-0.84",
            "p_value": "<0.001",
            "median_survival": {"treatment": "18.5 months", "control": "12.3 months"}
        },
        "safety_results": {
            "safety_population": 985,
            "treatment_emergent_aes": "92%",
            "serious_aes": "35%",
            "discontinuations_due_to_aes": "15%"
        }
    }
    
    input_data = {
        "section_type": "full_report",
        "study_data": large_study_data,
        "sections_to_generate": ["executive_summary", "methods", "results", "safety", "discussion", "conclusions"]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["quality_score"] > 80
    assert len(result["generated_content"]) > 1000
    assert result["quality_checks"]["overall_quality_score"] > 75


def test_csr_writer_recommendations_generation():
    """Test recommendations generation."""
    input_data = {
        "section_type": "results",
        "study_data": {
            "enrollment": {"completion_rate": "85%"},
            "efficacy_results": {"primary_endpoint_met": True},
            "safety_results": {"acceptable_profile": True}
        }
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "recommendations" in result
    recommendations = result["recommendations"]
    assert "content_improvements" in recommendations
    assert "quality_enhancements" in recommendations
    assert len(recommendations["content_improvements"]) > 0