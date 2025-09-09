"""Tests for Interim Analysis Preparer Tool"""
import pytest
from tools.interim_analysis_preparer import run

def test_safety_analysis():
    """Test safety interim analysis preparation."""
    result = run({
        'analysis_type': 'safety',
        'n_enrolled': 50,
        'target_enrollment': 100,
        'data_cutoff_date': '2024-01-15'
    })
    assert result['analysis_type'] == 'safety'
    assert 'enrollment_status' in result
    assert result['enrollment_status']['information_fraction'] == 0.5

def test_efficacy_analysis():
    """Test efficacy interim analysis."""
    result = run({
        'analysis_type': 'efficacy',
        'n_enrolled': 75,
        'target_enrollment': 100,
        'unblinding_level': 'partially_unblinded'
    })
    assert 'stopping_boundaries' in result
    assert 'analysis_plan' in result

def test_futility_analysis():
    """Test futility analysis preparation."""
    result = run({
        'analysis_type': 'futility',
        'n_enrolled': 40,
        'target_enrollment': 100
    })
    assert 'readiness' in result
    assert 'recommendations' in result
