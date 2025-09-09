"""Tests for IE Logic Validator"""
import pytest
from tools.ie_logic_validator import run

def test_age_conflict_detection():
    result = run({
        'inclusion_criteria': ['Age 18 to 65 years'],
        'exclusion_criteria': ['Age 60 to 75 years']
    })
    assert len(result['overlaps']) > 0
    # Should be invalid due to overlapping age ranges
    assert result['total_issues'] > 0

def test_condition_conflict():
    result = run({
        'inclusion_criteria': ['Diagnosed with diabetes'],
        'exclusion_criteria': ['History of diabetes']
    })
    assert len(result['conflicts']) > 0

def test_patient_eligibility():
    result = run({
        'inclusion_criteria': ['Age 18 to 65 years'],
        'exclusion_criteria': ['Age over 70'],
        'test_cases': [{'age': 30}, {'age': 68}]
    })
    assert result['test_results'][0]['eligible'] == True
    assert result['test_results'][1]['eligible'] == False
