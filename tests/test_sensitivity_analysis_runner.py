"""Tests for sensitivity analysis runner Tool"""
import pytest
from tools.sensitivity_analysis_runner import run

def test_basic_functionality():
    """Test basic sensitivity analysis runner functionality."""
    result = run({
        'data': [1, 2, 3],
        'parameters': {'test': True}
    })
    assert 'analysis_complete' in result or 'error' not in result

def test_with_empty_input():
    """Test sensitivity analysis runner with empty input."""
    result = run({})
    assert isinstance(result, dict)

def test_with_parameters():
    """Test sensitivity analysis runner with specific parameters."""
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
