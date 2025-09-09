import pytest
from tools.gcp_compliance_auditor import run


def test_gcp_compliance_auditor_full_compliance():
    """Test with full GCP compliance."""
    input_data = {
        'audit_areas': ['protocol', 'consent', 'documentation'],
        'site_data': {
            'protocol_version': True,
            'amendments_documented': True,
            'deviations_reported': True,
            'inclusion_exclusion': True,
            'visit_windows': True,
            'consent_current': True,
            'consent_signed': True,
            'consent_dated': True,
            'consent_witnessed': True,
            'consent_copies': True,
            'reconsent_done': True,
            'source_documented': True,
            'alcoa_compliance': True,
            'corrections_proper': True,
            'signatures_current': True,
            'crf_complete': True,
            'queries_resolved': True
        },
        'audit_type': 'full'
    }
    
    result = run(input_data)
    
    assert result['compliance_score'] == 100.0
    assert result['risk_level'] == 'low'
    assert len(result['findings']) == 0
    assert len(result['critical_findings']) == 0


def test_gcp_compliance_auditor_critical_findings():
    """Test detection of critical GCP violations."""
    input_data = {
        'audit_areas': ['consent', 'safety'],
        'site_data': {
            'consent_signed': False,  # Critical
            'consent_dated': False,   # Critical
            'sae_timeline': False,    # Critical
            'susar_reporting': False  # Critical
        }
    }
    
    result = run(input_data)
    
    assert result['risk_level'] == 'critical'
    assert len(result['critical_findings']) > 0
    assert result['compliance_score'] < 70
    assert any('IMMEDIATE ACTION' in r for r in result['recommendations'])


def test_gcp_compliance_auditor_protocol_area():
    """Test protocol compliance audit."""
    input_data = {
        'audit_areas': ['protocol'],
        'site_data': {
            'protocol_version': True,
            'amendments_documented': False,
            'deviations_reported': False,
            'inclusion_exclusion': True,
            'visit_windows': False
        }
    }
    
    result = run(input_data)
    
    assert len(result['findings']) == 3
    assert result['area_scores']['protocol'] < 100
    assert any('protocol' in f['area'] for f in result['findings'])


def test_gcp_compliance_auditor_repeat_findings():
    """Test identification of repeat findings."""
    previous = [
        {'area': 'consent', 'finding': 'Non-compliance: Using current IRB-approved version'},
        {'area': 'documentation', 'finding': 'Non-compliance: ALCOA+ principles followed'}
    ]
    
    input_data = {
        'audit_areas': ['consent', 'documentation'],
        'site_data': {
            'consent_current': False,
            'alcoa_compliance': False
        },
        'findings': previous
    }
    
    result = run(input_data)
    
    assert len(result['repeat_findings']) > 0
    assert result['repeat_findings'][0]['repeat'] is True


def test_gcp_compliance_auditor_risk_levels():
    """Test risk level determination."""
    # High risk (low compliance)
    input_data = {
        'audit_areas': ['protocol'],
        'site_data': {}  # All checks will fail
    }
    
    result = run(input_data)
    assert result['risk_level'] in ['high', 'critical']
    
    # Medium risk
    input_data = {
        'audit_areas': ['documentation'],
        'site_data': {
            'source_documented': True,
            'alcoa_compliance': True,
            'corrections_proper': False,
            'signatures_current': False,
            'crf_complete': True,
            'queries_resolved': True
        }
    }
    
    result = run(input_data)
    assert result['compliance_score'] > 70


def test_gcp_compliance_auditor_drug_accountability():
    """Test drug accountability audit."""
    input_data = {
        'audit_areas': ['drug_accountability'],
        'site_data': {
            'drug_storage': False,  # Critical
            'temp_monitoring': True,
            'accountability_logs': True,
            'expiry_tracking': False,
            'dispensing_records': True
        }
    }
    
    result = run(input_data)
    
    assert any('drug_accountability' in f['area'] for f in result['findings'])
    assert len(result['critical_findings']) > 0  # Drug storage is critical


def test_gcp_compliance_auditor_investigator_area():
    """Test investigator responsibilities audit."""
    input_data = {
        'audit_areas': ['investigator'],
        'site_data': {
            'qualified_staff': True,
            'delegation_log': False,
            'cv_current': False,
            'training_documented': True,
            'oversight_adequate': True
        }
    }
    
    result = run(input_data)
    
    assert 'investigator' in result['area_scores']
    assert len(result['findings']) == 2


def test_gcp_compliance_auditor_recommendations():
    """Test recommendation generation."""
    input_data = {
        'audit_areas': ['consent', 'safety'],
        'site_data': {
            'consent_current': False,
            'ae_reporting': False
        }
    }
    
    result = run(input_data)
    
    assert len(result['recommendations']) > 0
    assert any('consent' in r.lower() for r in result['recommendations'])
    assert any('safety' in r.lower() for r in result['recommendations'])