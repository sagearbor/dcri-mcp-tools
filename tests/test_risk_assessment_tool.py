"""Tests for Risk Assessment Tool"""
import pytest
from tools.risk_assessment_tool import run

def test_risk_assessment():
    result = run({
        'first_in_human': True,
        'vulnerable_population': True,
        'complex_endpoints': True,
        'inexperienced_sites': True
    })
    assert result['overall_risk_level'] in ['High', 'Medium', 'Low']
    assert 'mitigation_plan' in result
    assert len(result['mitigation_plan']) > 0

def test_risk_categories():
    result = run({
        'invasive_procedures': True,
        'subjective_assessments': True,
        'recruitment_challenges': True,
        'novel_therapy': True
    })
    assert 'risks_by_category' in result
    assert 'safety' in result['risks_by_category']
    assert 'data_integrity' in result['risks_by_category']
