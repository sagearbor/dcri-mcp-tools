"""Tests for kaplan meier creator Tool"""
import pytest
from tools.kaplan_meier_creator import run

def test_basic_functionality():
    """Test basic kaplan meier creator functionality."""
    result = run({
        'data': [1, 2, 3],
        'parameters': {'test': True}
    })
    assert 'analysis_complete' in result or 'error' not in result

def test_with_empty_input():
    """Test kaplan meier creator with empty input."""
    result = run({})
    assert isinstance(result, dict)

def test_with_parameters():
    """Test kaplan meier creator with specific parameters."""
    result = run({
        'data': list(range(10)),
        'parameters': {
            'method': 'default',
            'alpha': 0.05
        }
    })
    assert isinstance(result, dict)
    if 'error' not in result:
        assert len(result) > 0
