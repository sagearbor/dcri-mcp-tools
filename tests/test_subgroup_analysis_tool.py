"""Tests for subgroup analysis tool Tool"""
import pytest
from tools.subgroup_analysis_tool import run

def test_basic_functionality():
    """Test basic subgroup analysis tool functionality."""
    result = run({
        'data': [1, 2, 3],
        'parameters': {'test': True}
    })
    assert 'analysis_complete' in result or 'error' not in result

def test_with_empty_input():
    """Test subgroup analysis tool with empty input."""
    result = run({})
    assert isinstance(result, dict)

def test_with_parameters():
    """Test subgroup analysis tool with specific parameters."""
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
