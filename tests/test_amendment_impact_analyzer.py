"""Tests for Amendment Impact Analyzer"""
import pytest
from tools.amendment_impact_analyzer import run

def test_amendment_impact():
    result = run({
        'amendment_type': 'major',
        'changes': [
            'Modified inclusion criteria',
            'Changed primary endpoint',
            'Added safety monitoring'
        ],
        'current_enrollment': 50,
        'total_target': 100,
        'sites_activated': 10
    })
    assert 'overall_impact' in result
    assert 'recommendations' in result
    assert result['requires_fda_submission'] == True

def test_timeline_impact():
    result = run({
        'changes': ['Added new visit procedures'],
        'current_enrollment': 25,
        'sites_activated': 5
    })
    assert 'timeline_impact' in result
    assert result['timeline_impact']['estimated_delay_days'] >= 0
