"""Tests for statistical report generator Tool"""
import pytest
from tools.statistical_report_generator import run

def test_basic_functionality():
    """Test basic statistical report generator functionality."""
    result = run({
        'data': [1, 2, 3],
        'parameters': {'test': True}
    })
    assert 'analysis_complete' in result or 'error' not in result

def test_with_empty_input():
    """Test statistical report generator with empty input."""
    result = run({})
    assert isinstance(result, dict)

def test_with_parameters():
    """Test statistical report generator with specific parameters."""
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
