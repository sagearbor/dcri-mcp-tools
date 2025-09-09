"""Tests for Forest Plot Generator Tool"""
import pytest
from tools.forest_plot_generator import run

def test_fixed_effect_meta_analysis():
    """Test fixed effect meta-analysis."""
    result = run({
        'studies': [
            {'name': 'Study 1', 'effect_size': 0.8, 'lower_ci': 0.6, 'upper_ci': 1.1, 'n': 100},
            {'name': 'Study 2', 'effect_size': 0.9, 'lower_ci': 0.7, 'upper_ci': 1.2, 'n': 150},
            {'name': 'Study 3', 'effect_size': 0.7, 'lower_ci': 0.5, 'upper_ci': 0.95, 'n': 120}
        ],
        'measure': 'OR',
        'model': 'fixed'
    })
    assert result['model'] == 'fixed'
    assert result['n_studies'] == 3
    assert 'pooled_estimate' in result
    assert 'heterogeneity' in result

def test_random_effects_model():
    """Test random effects model."""
    result = run({
        'studies': [
            {'name': 'Study A', 'effect_size': 1.5, 'lower_ci': 1.2, 'upper_ci': 1.9},
            {'name': 'Study B', 'effect_size': 0.8, 'lower_ci': 0.6, 'upper_ci': 1.0}
        ],
        'measure': 'RR',
        'model': 'random'
    })
    assert result['model'] == 'random'
    assert 'plot_data' in result

def test_empty_studies():
    """Test with no studies."""
    result = run({
        'studies': [],
        'measure': 'OR'
    })
    assert 'error' in result
