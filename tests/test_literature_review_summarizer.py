import pytest
from tools.literature_review_summarizer import run


def test_literature_review_summarizer_basic():
    """Test basic literature review summarization."""
    input_data = {
        "publications": [
            {
                "title": "Efficacy of Drug X in Cancer Treatment",
                "abstract": "This randomized controlled trial evaluated the efficacy of Drug X versus placebo in 200 cancer patients. Primary endpoint was overall survival.",
                "authors": ["Smith J", "Jones A", "Brown K"],
                "journal": "Journal of Oncology",
                "publication_year": 2023,
                "doi": "10.1000/journal.2023.001"
            },
            {
                "title": "Safety Profile of Drug X: A Meta-Analysis",
                "abstract": "Meta-analysis of 10 studies showed Drug X had acceptable safety profile with manageable adverse events.",
                "authors": ["Wilson R", "Davis M"],
                "journal": "Drug Safety Review",
                "publication_year": 2022,
                "doi": "10.1000/safety.2022.005"
            }
        ],
        "review_focus": "efficacy",
        "summary_type": "narrative"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["literature_review_summary"]["review_metadata"]["total_publications_reviewed"] == 2
    assert result["literature_review_summary"]["review_focus"] == "efficacy"
    assert len(result["key_findings"]) > 0


def test_literature_review_systematic_summary():
    """Test systematic review generation."""
    input_data = {
        "publications": [
            {
                "title": "RCT of Treatment A vs Placebo",
                "abstract": "Randomized trial with 300 patients showing significant improvement in primary endpoint (p<0.05).",
                "publication_year": 2023,
                "journal": "Medical Journal"
            },
            {
                "title": "Safety Study of Treatment A",
                "abstract": "Cohort study of 150 patients evaluating safety profile over 12 months.",
                "publication_year": 2022,
                "journal": "Safety Journal"
            }
        ],
        "summary_type": "systematic",
        "key_questions": [
            "Is Treatment A more effective than placebo?",
            "What is the safety profile of Treatment A?"
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "systematic review" in result["literature_review_summary"]["executive_summary"]
    assert len(result["key_questions"]) == 2


def test_literature_review_meta_analysis():
    """Test meta-analysis summary generation."""
    input_data = {
        "publications": [
            {
                "title": "Meta-analysis of Drug Effectiveness",
                "abstract": "Pooled analysis of 15 RCTs involving 5000 patients showed significant treatment effect.",
                "publication_year": 2023,
                "sample_size": 5000
            }
        ],
        "summary_type": "meta_analysis"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "meta-analysis" in result["literature_review_summary"]["executive_summary"]
    assert result["publication_analysis"]["sample_size_statistics"]["total_participants"] == 5000


def test_literature_review_quality_assessment():
    """Test publication quality assessment."""
    input_data = {
        "publications": [
            {
                "title": "High-Quality RCT Study",
                "abstract": "Double-blind randomized controlled trial with 500 patients.",
                "authors": ["Author A", "Author B"],
                "journal": "Top Medical Journal",
                "publication_year": 2023,
                "sample_size": 500
            },
            {
                "title": "Case Series Report",
                "abstract": "Case series of 10 patients with rare condition.",
                "publication_year": 2022,
                "sample_size": 10
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "quality_assessment" in result
    quality = result["quality_assessment"]
    assert "study_design_quality" in quality
    assert quality["study_design_quality"]["High"] > 0  # RCT should be high quality


def test_literature_review_bias_analysis():
    """Test risk of bias analysis."""
    input_data = {
        "publications": [
            {
                "title": "Randomized Double-Blind Study",
                "abstract": "Well-designed RCT with proper randomization and blinding.",
                "publication_year": 2023
            },
            {
                "title": "Observational Study",
                "abstract": "Retrospective analysis of patient records.",
                "publication_year": 2022
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "bias_analysis" in result
    bias = result["bias_analysis"]
    assert "selection_bias" in bias
    assert "overall_bias_assessment" in bias


def test_literature_review_research_gaps():
    """Test research gap identification."""
    input_data = {
        "publications": [
            {
                "title": "Short-term Study",
                "abstract": "4-week study of treatment effects.",
                "publication_year": 2023,
                "sample_size": 50
            },
            {
                "title": "Small Pilot Study", 
                "abstract": "Pilot study with 25 patients.",
                "publication_year": 2022,
                "sample_size": 25
            }
        ],
        "key_questions": ["What are long-term effects?"]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["literature_review_summary"]["research_gaps_identified"]) > 0
    gaps = result["literature_review_summary"]["research_gaps_identified"]
    assert any(gap["type"] == "sample_size" for gap in gaps)


def test_literature_review_evidence_synthesis():
    """Test evidence synthesis."""
    input_data = {
        "publications": [
            {
                "title": "RCT with Positive Results",
                "abstract": "Significant improvement with p<0.01 in primary endpoint.",
                "publication_year": 2023
            },
            {
                "title": "Large Cohort Study",
                "abstract": "Cohort of 1000 patients followed for 2 years.",
                "publication_year": 2022,
                "sample_size": 1000
            }
        ],
        "review_focus": "efficacy"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "evidence_synthesis" in result["literature_review_summary"]
    synthesis = result["literature_review_summary"]["evidence_synthesis"]
    assert "overall_quality" in synthesis
    assert "grade_assessment" in synthesis


def test_literature_review_inclusion_criteria():
    """Test inclusion criteria application."""
    input_data = {
        "publications": [
            {
                "title": "Recent RCT 2023",
                "abstract": "Randomized controlled trial published in 2023.",
                "publication_year": 2023,
                "sample_size": 200
            },
            {
                "title": "Old Study 2015",
                "abstract": "Study from 2015.",
                "publication_year": 2015,
                "sample_size": 100
            }
        ],
        "inclusion_criteria": [
            "Publication year 2020-2024",
            "Sample size >= 150"
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    # Should include only publications meeting criteria
    assert result["literature_review_summary"]["review_metadata"]["total_publications_reviewed"] == 1


def test_literature_review_empty_publications():
    """Test handling of empty publications list."""
    input_data = {
        "publications": [],
        "review_focus": "safety"
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert "No publications provided" in result["error"]


def test_literature_review_recommendations():
    """Test recommendation generation."""
    input_data = {
        "publications": [
            {
                "title": "High-Quality RCT",
                "abstract": "Well-designed trial with significant results (p<0.001).",
                "publication_year": 2023,
                "sample_size": 500
            }
        ],
        "target_audience": "investigators",
        "review_focus": "efficacy"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "recommendations" in result
    recommendations = result["recommendations"]
    assert "clinical_practice" in recommendations
    assert "research_priorities" in recommendations


def test_literature_review_publication_analysis():
    """Test publication characteristics analysis."""
    input_data = {
        "publications": [
            {
                "title": "Study A",
                "journal": "Journal A",
                "publication_year": 2023,
                "sample_size": 200
            },
            {
                "title": "Study B", 
                "journal": "Journal B",
                "publication_year": 2022,
                "sample_size": 300
            },
            {
                "title": "Study C",
                "journal": "Journal A", 
                "publication_year": 2023,
                "sample_size": 150
            }
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    analysis = result["publication_analysis"]
    assert "temporal_distribution" in analysis
    assert "journal_distribution" in analysis
    assert "sample_size_statistics" in analysis
    assert analysis["temporal_distribution"]["2023"] == 2


def test_literature_review_appendices():
    """Test appendices generation."""
    input_data = {
        "publications": [
            {
                "title": "Clinical Trial Results",
                "authors": ["Smith J", "Jones A"],
                "journal": "Medical Journal", 
                "publication_year": 2023,
                "doi": "10.1000/example.2023"
            }
        ],
        "summary_type": "systematic"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "appendices" in result
    appendices = result["appendices"]
    assert "publication_list" in appendices
    assert "evidence_tables" in appendices
    assert len(appendices["publication_list"]) == 1


def test_literature_review_safety_focus():
    """Test safety-focused review."""
    input_data = {
        "publications": [
            {
                "title": "Safety Analysis of Drug X",
                "abstract": "Comprehensive safety analysis showing mild adverse events in 15% of patients.",
                "publication_year": 2023
            }
        ],
        "review_focus": "safety"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["literature_review_summary"]["review_focus"] == "safety"
    summary = result["literature_review_summary"]["executive_summary"]
    assert "safety" in summary.lower()


def test_literature_review_methodology_focus():
    """Test methodology-focused review.""" 
    input_data = {
        "publications": [
            {
                "title": "Methodological Considerations in Clinical Trials",
                "abstract": "Discussion of randomization methods and blinding techniques in clinical research.",
                "publication_year": 2023
            }
        ],
        "review_focus": "methodology"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["literature_review_summary"]["review_focus"] == "methodology"
    summary = result["literature_review_summary"]["executive_summary"]
    assert "methodology" in summary.lower() or "methods" in summary.lower()


def test_literature_review_large_dataset():
    """Test with larger publication dataset."""
    # Create 20 publications
    publications = []
    for i in range(20):
        publications.append({
            "title": f"Study {i+1}: Clinical Trial Results",
            "abstract": f"Clinical trial {i+1} with {100+i*10} patients showing treatment effects.",
            "publication_year": 2020 + (i % 4),
            "sample_size": 100 + i*10,
            "journal": f"Journal {chr(65 + i%5)}"  # Journal A, B, C, D, E
        })
    
    input_data = {
        "publications": publications,
        "review_focus": "general",
        "summary_type": "systematic"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["literature_review_summary"]["review_metadata"]["total_publications_reviewed"] == 20
    assert len(result["key_findings"]) > 0
    
    # Should have good analysis with larger dataset
    analysis = result["publication_analysis"]
    assert len(analysis["journal_distribution"]) > 1
    assert analysis["sample_size_statistics"]["total_participants"] > 2000