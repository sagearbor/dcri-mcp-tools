import pytest
from tools.informed_consent_tracker import run


def test_informed_consent_tracker_all_current():
    """Test tracking when all subjects have current consent versions."""
    input_data = {
        'subjects': [
            {
                'subject_id': 'S001',
                'consent_version': '2.0',
                'consent_date': '2024-01-15',
                'site_id': 'SITE001'
            },
            {
                'subject_id': 'S002',
                'consent_version': '2.0',
                'consent_date': '2024-02-01',
                'site_id': 'SITE001'
            },
            {
                'subject_id': 'S003',
                'consent_version': '2.0',
                'consent_date': '2024-02-15',
                'site_id': 'SITE002'
            }
        ],
        'current_consent_version': '2.0'
    }
    
    result = run(input_data)
    
    assert result['total_subjects'] == 3
    assert result['subjects_current_consent'] == 3
    assert result['subjects_outdated_consent'] == 0
    assert len(result['reconsent_required']) == 0
    assert len(result['consent_violations']) == 0
    assert result['compliance_percentage'] == 100.0
    assert result['summary']['status'] == 'compliant'


def test_informed_consent_tracker_mixed_versions():
    """Test tracking with subjects having different consent versions."""
    input_data = {
        'subjects': [
            {
                'subject_id': 'S001',
                'consent_version': '1.0',
                'consent_date': '2023-12-15',
                'site_id': 'SITE001'
            },
            {
                'subject_id': 'S002',
                'consent_version': '2.0',
                'consent_date': '2024-02-01',
                'site_id': 'SITE001'
            },
            {
                'subject_id': 'S003',
                'consent_version': '1.5',
                'consent_date': '2024-01-10',
                'site_id': 'SITE002'
            }
        ],
        'current_consent_version': '2.0'
    }
    
    result = run(input_data)
    
    assert result['total_subjects'] == 3
    assert result['subjects_current_consent'] == 1
    assert result['subjects_outdated_consent'] == 2
    assert len(result['consent_violations']) == 2
    assert result['compliance_percentage'] == 33.33
    assert result['summary']['status'] == 'violations_found'
    
    # Check version distribution
    expected_distribution = {'1.0': 1, '2.0': 1, '1.5': 1}
    assert result['version_distribution'] == expected_distribution


def test_informed_consent_tracker_with_amendments():
    """Test tracking with protocol amendments requiring reconsent."""
    input_data = {
        'subjects': [
            {
                'subject_id': 'S001',
                'consent_version': '1.0',
                'consent_date': '2023-12-15',
                'site_id': 'SITE001'
            },
            {
                'subject_id': 'S002',
                'consent_version': '1.0',
                'consent_date': '2024-01-10',
                'reconsent_date': '2024-03-01',
                'site_id': 'SITE001'
            }
        ],
        'current_consent_version': '2.0',
        'protocol_amendments': [
            {
                'date': '2024-02-01',
                'consent_version_required': '2.0',
                'requires_reconsent': True
            }
        ]
    }
    
    result = run(input_data)
    
    assert result['total_subjects'] == 2
    assert len(result['reconsent_required']) == 1
    assert result['reconsent_required'][0]['subject_id'] == 'S001'
    assert result['reconsent_required'][0]['required_consent_version'] == '2.0'
    
    # S002 should not require reconsent because they were reconsented after the amendment
    reconsent_subject_ids = [r['subject_id'] for r in result['reconsent_required']]
    assert 'S002' not in reconsent_subject_ids


def test_informed_consent_tracker_missing_data():
    """Test tracking with missing consent information."""
    input_data = {
        'subjects': [
            {
                'subject_id': 'S001',
                'consent_date': '2024-01-15',
                'site_id': 'SITE001'
                # Missing consent_version
            },
            {
                'subject_id': 'S002',
                'consent_version': '2.0',
                'consent_date': '2024-02-01',
                'site_id': 'SITE001'
            }
        ],
        'current_consent_version': '2.0'
    }
    
    result = run(input_data)
    
    assert result['total_subjects'] == 2
    assert result['subjects_current_consent'] == 1
    assert len(result['consent_violations']) >= 1
    
    # Check for missing consent version violation
    missing_version_violations = [
        v for v in result['consent_violations'] 
        if v['violation_type'] == 'missing_consent_version'
    ]
    assert len(missing_version_violations) == 1
    assert missing_version_violations[0]['subject_id'] == 'S001'


def test_informed_consent_tracker_site_filtering():
    """Test tracking with site-specific filtering."""
    input_data = {
        'subjects': [
            {
                'subject_id': 'S001',
                'consent_version': '2.0',
                'consent_date': '2024-01-15',
                'site_id': 'SITE001'
            },
            {
                'subject_id': 'S002',
                'consent_version': '1.0',
                'consent_date': '2024-02-01',
                'site_id': 'SITE002'
            },
            {
                'subject_id': 'S003',
                'consent_version': '2.0',
                'consent_date': '2024-02-15',
                'site_id': 'SITE001'
            }
        ],
        'current_consent_version': '2.0',
        'site_id': 'SITE001'
    }
    
    result = run(input_data)
    
    # Should only process subjects from SITE001
    assert result['total_subjects'] == 2
    assert result['subjects_current_consent'] == 2
    assert result['subjects_outdated_consent'] == 0


def test_informed_consent_tracker_no_data():
    """Test error handling when no subject data is provided."""
    input_data = {
        'current_consent_version': '2.0'
    }
    
    result = run(input_data)
    
    assert 'error' in result
    assert result['total_subjects'] == 0
    assert len(result['recommendations']) > 0


def test_informed_consent_tracker_no_current_version():
    """Test error handling when current consent version is not specified."""
    input_data = {
        'subjects': [
            {
                'subject_id': 'S001',
                'consent_version': '1.0',
                'consent_date': '2024-01-15'
            }
        ]
    }
    
    result = run(input_data)
    
    assert 'error' in result
    assert 'Current consent version not specified' in result['error']
    assert len(result['recommendations']) > 0