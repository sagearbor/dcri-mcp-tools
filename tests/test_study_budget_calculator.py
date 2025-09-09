"""Tests for Study Budget Calculator"""
import pytest
from tools.study_budget_calculator import run

def test_basic_budget_calculation():
    result = run({
        'n_subjects': 100,
        'n_sites': 10,
        'study_duration_months': 24,
        'visits_per_subject': 8
    })
    assert 'total_budget' in result
    assert result['total_budget'] > 0
    assert 'cost_per_subject' in result

def test_budget_categories():
    result = run({
        'n_subjects': 50,
        'n_sites': 5
    })
    assert 'subject_costs' in result
    assert 'site_costs' in result
    assert 'staff_costs' in result
    assert 'operational_costs' in result

def test_monthly_burn_rate():
    result = run({
        'n_subjects': 100,
        'study_duration_months': 12
    })
    assert result['monthly_burn_rate'] > 0
    assert result['monthly_burn_rate'] == result['total_budget'] / 12
