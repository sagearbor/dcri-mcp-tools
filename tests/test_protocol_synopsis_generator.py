"""Tests for Protocol Synopsis Generator"""
import pytest
from tools.protocol_synopsis_generator import run

def test_synopsis_generation():
    result = run({
        'study_title': 'Test Study',
        'protocol_number': 'TEST-001',
        'phase': '2',
        'indication': 'Test Disease',
        'sample_size': 100,
        'primary_objective': 'Test efficacy',
        'primary_endpoint': 'Response rate'
    })
    assert 'synopsis_sections' in result
    assert 'formatted_text' in result
    assert 'structured_data' in result

def test_synopsis_sections():
    result = run({
        'study_title': 'Clinical Trial',
        'treatment_arms': ['Placebo', 'Drug A', 'Drug B']
    })
    sections = result['synopsis_sections']
    assert 'header' in sections
    assert 'objectives' in sections
    assert 'design' in sections
    assert 'endpoints' in sections
