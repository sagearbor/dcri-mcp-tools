import pytest
from tools.risk_benefit_analyzer import run


def test_risk_benefit_analyzer_favorable():
    """Test favorable risk-benefit profile."""
    input_data = {
        "efficacy_data": {
            "primary_endpoint": {
                "name": "Overall Response Rate",
                "treatment_effect": 25,
                "p_value": 0.001,
                "ci_lower": 15,
                "ci_upper": 35
            },
            "responder_rate": {"treatment": 0.60, "control": 0.35}
        },
        "safety_data": {
            "adverse_events": {"by_frequency": {"nausea": 15, "fatigue": 10}},
            "serious_adverse_events": {"rate": 0.05},
            "discontinuations": {"due_to_ae_rate": 5},
            "deaths": {"rate": 0}
        }
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert result["risk_benefit_ratio"]["weighted_ratio"] > 1
    assert "favorable" in result["risk_benefit_ratio"]["favorability"].lower()


def test_risk_benefit_analyzer_unfavorable():
    """Test unfavorable risk-benefit profile."""
    input_data = {
        "efficacy_data": {
            "primary_endpoint": {
                "name": "Progression-free survival",
                "treatment_effect": 2,
                "p_value": 0.45
            }
        },
        "safety_data": {
            "serious_adverse_events": {"rate": 0.30},
            "discontinuations": {"due_to_ae_rate": 40},
            "deaths": {"rate": 0.05}
        }
    }
    
    result = run(input_data)
    
    assert "error" not in result
    assert result["risk_benefit_ratio"]["weighted_ratio"] < 1


def test_risk_benefit_analyzer_empty_input():
    """Test handling of empty input."""
    result = run({})
    assert result["error"] == "Both efficacy and safety data required"
