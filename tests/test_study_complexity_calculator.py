"""Tests for Study Complexity Calculator"""
import pytest
from tools.study_complexity_calculator import run

def test_complexity_calculation():
    result = run({
        'phase': '3',
        'randomized': True,
        'blinding': 'double',
        'n_treatment_arms': 3,
        'pediatric': True,
        'n_countries': 5
    })
    assert 'total_score' in result
    assert 'complexity_level' in result
    assert result['total_score'] > 0

def test_complexity_levels():
    low_complexity = run({'phase': '4', 'blinding': 'open'})
    high_complexity = run({
        'phase': 'combined',
        'adaptive_design': True,
        'pediatric': True,
        'first_in_human': True
    })
    assert low_complexity['total_score'] < high_complexity['total_score']
