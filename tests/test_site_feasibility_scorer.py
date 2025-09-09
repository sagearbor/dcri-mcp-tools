"""Tests for Site Feasibility Scorer"""
import pytest
from tools.site_feasibility_scorer import run

def test_site_scoring():
    result = run({
        'sites': [
            {
                'site_id': 'S001',
                'name': 'Site A',
                'patient_population': 200,
                'past_enrollment_rate': 5,
                'pi_previous_studies': 10,
                'has_required_equipment': True,
                'adequate_staff': True,
                'gcp_trained': True
            },
            {
                'site_id': 'S002',
                'name': 'Site B',
                'patient_population': 50,
                'past_enrollment_rate': 2,
                'pi_previous_studies': 2
            }
        ]
    })
    assert len(result['ranked_sites']) == 2
    assert result['ranked_sites'][0]['total_score'] > result['ranked_sites'][1]['total_score']

def test_empty_sites():
    result = run({'sites': []})
    assert 'error' in result
