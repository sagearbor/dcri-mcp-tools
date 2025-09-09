import pytest
from tools.cfr_part11_validator import run


def test_cfr_part11_validator_compliant_system():
    """Test validation of a fully compliant 21 CFR Part 11 system."""
    input_data = {
        'electronic_records': [
            {
                'record_id': 'REC001',
                'validation_documented': True,
                'can_generate_copies': True,
                'protected': True
            },
            {
                'record_id': 'REC002',
                'validation_documented': True,
                'can_generate_copies': True,
                'protected': True
            }
        ],
        'signature_system': {
            'contains_signature_information': True,
            'signatures_linked_to_records': True,
            'unique_signatures': True,
            'two_factor_authentication': True
        },
        'user_accounts': [
            {
                'user_id': 'USER001',
                'authorized': True,
                'strong_password': True,
                'password_expiry': True
            },
            {
                'user_id': 'USER002',
                'authorized': True,
                'strong_password': True,
                'password_expiry': True
            }
        ],
        'audit_trail': [
            {
                'entry_id': 'AUDIT001',
                'user_id': 'USER001',
                'action': 'record_created',
                'timestamp': '2024-01-15 10:30:00',
                'record_id': 'REC001',
                'secure': True
            },
            {
                'entry_id': 'AUDIT002',
                'user_id': 'USER002',
                'action': 'record_modified',
                'timestamp': '2024-01-16 14:15:30',
                'record_id': 'REC002',
                'secure': True
            }
        ],
        'validation_documentation': {
            'validation_plan': True,
            'requirements_specification': True,
            'design_specification': True,
            'test_protocols': True,
            'test_results': True,
            'validation_summary': True
        }
    }
    
    result = run(input_data)
    
    assert result['compliance_status'] == 'compliant'
    assert result['compliance_score'] == 100.0
    assert len(result['violations']) == 0
    assert result['summary']['ready_for_inspection'] is True
    assert result['summary']['critical_violations'] == 0


def test_cfr_part11_validator_non_compliant_signatures():
    """Test validation with non-compliant electronic signature system."""
    input_data = {
        'electronic_records': [
            {
                'record_id': 'REC001',
                'validation_documented': True,
                'can_generate_copies': True,
                'protected': True
            }
        ],
        'signature_system': {
            'contains_signature_information': False,  # Non-compliant
            'signatures_linked_to_records': False,   # Non-compliant
            'unique_signatures': True,
            'two_factor_authentication': False       # Non-compliant
        },
        'user_accounts': [
            {
                'user_id': 'USER001',
                'authorized': True,
                'strong_password': True,
                'password_expiry': True
            }
        ],
        'audit_trail': [
            {
                'entry_id': 'AUDIT001',
                'user_id': 'USER001',
                'action': 'record_created',
                'timestamp': '2024-01-15 10:30:00',
                'record_id': 'REC001',
                'secure': True
            }
        ]
    }
    
    result = run(input_data)
    
    assert result['compliance_status'] == 'non_compliant'
    assert result['compliance_score'] < 100.0
    assert len(result['violations']) > 0
    
    # Check for specific signature violations
    violation_sections = [v['section'] for v in result['violations']]
    assert '11.50(a)' in violation_sections
    assert '11.70' in violation_sections
    assert '11.200(a)' in violation_sections


def test_cfr_part11_validator_missing_audit_trail():
    """Test validation with missing audit trail."""
    input_data = {
        'electronic_records': [
            {
                'record_id': 'REC001',
                'validation_documented': True,
                'can_generate_copies': True,
                'protected': True
            }
        ],
        'signature_system': {
            'contains_signature_information': True,
            'signatures_linked_to_records': True,
            'unique_signatures': True,
            'two_factor_authentication': True
        },
        'user_accounts': [
            {
                'user_id': 'USER001',
                'authorized': True,
                'strong_password': True,
                'password_expiry': True
            }
        ],
        'audit_trail': []  # Missing audit trail
    }
    
    result = run(input_data)
    
    assert result['compliance_status'] == 'non_compliant'
    assert len(result['violations']) > 0
    
    # Check for audit trail violation
    audit_violations = [v for v in result['violations'] if '11.10(e)' in v['section']]
    assert len(audit_violations) > 0
    assert audit_violations[0]['severity'] == 'critical'


def test_cfr_part11_validator_partial_compliance():
    """Test validation with partial compliance (warnings but no critical errors)."""
    input_data = {
        'electronic_records': [
            {
                'record_id': 'REC001',
                'validation_documented': True,
                'can_generate_copies': True,
                'protected': True
            },
            {
                'record_id': 'REC002',
                'validation_documented': True,
                'can_generate_copies': True,
                'protected': False  # One record not protected
            }
        ],
        'signature_system': {
            'contains_signature_information': True,
            'signatures_linked_to_records': True,
            'unique_signatures': True,
            'two_factor_authentication': True
        },
        'user_accounts': [
            {
                'user_id': 'USER001',
                'authorized': True,
                'strong_password': True,
                'password_expiry': False  # Password doesn't expire
            }
        ],
        'audit_trail': [
            {
                'entry_id': 'AUDIT001',
                'user_id': 'USER001',
                'action': 'record_created',
                'timestamp': '2024-01-15 10:30:00',
                'record_id': 'REC001',
                'secure': True
            }
        ]
    }
    
    result = run(input_data)
    
    assert result['compliance_status'] == 'partial'
    assert 0 < result['compliance_score'] < 100
    assert len(result['violations']) > 0
    
    # Should have medium severity violations but no critical ones
    critical_violations = [v for v in result['violations'] if v['severity'] == 'critical']
    assert len(critical_violations) == 0


def test_cfr_part11_validator_access_controls():
    """Test validation of access controls specifically."""
    input_data = {
        'electronic_records': [
            {
                'record_id': 'REC001',
                'validation_documented': True,
                'can_generate_copies': True,
                'protected': True
            }
        ],
        'user_accounts': [
            {
                'user_id': 'USER001',
                'authorized': False,  # Unauthorized user
                'strong_password': False,
                'password_expiry': False
            },
            {
                'user_id': 'USER002',
                'authorized': True,
                'strong_password': True,
                'password_expiry': True
            }
        ],
        'check_controls': True
    }
    
    result = run(input_data)
    
    assert result['compliance_status'] == 'non_compliant'
    
    # Check for access control violations
    access_violations = [v for v in result['violations'] if '11.10(d)' in v['section']]
    assert len(access_violations) > 0
    
    password_violations = [v for v in result['violations'] if '11.300' in v['section']]
    assert len(password_violations) > 0


def test_cfr_part11_validator_validation_documentation():
    """Test validation documentation assessment."""
    input_data = {
        'electronic_records': [
            {
                'record_id': 'REC001',
                'validation_documented': True,
                'can_generate_copies': True,
                'protected': True
            }
        ],
        'validation_documentation': {
            'validation_plan': True,
            'requirements_specification': True,
            'design_specification': False,    # Missing
            'test_protocols': False,          # Missing
            'test_results': True,
            'validation_summary': False       # Missing
        }
    }
    
    result = run(input_data)
    
    validation_status = result['validation_status']
    assert validation_status['validation_plan'] is True
    assert validation_status['design_specification'] is False
    assert validation_status['test_protocols'] is False
    
    # Should have validation-related violations
    validation_violations = [v for v in result['violations'] 
                           if 'validation documentation' in v['description'].lower()]
    assert len(validation_violations) > 0


def test_cfr_part11_validator_no_data():
    """Test error handling when no data is provided."""
    input_data = {}
    
    result = run(input_data)
    
    assert 'error' in result
    assert result['compliance_status'] == 'non_compliant'
    assert result['compliance_score'] == 0.0
    assert len(result['validation_errors']) > 0


def test_cfr_part11_validator_invalid_timestamp():
    """Test audit trail with invalid timestamp format."""
    input_data = {
        'electronic_records': [
            {
                'record_id': 'REC001',
                'validation_documented': True,
                'can_generate_copies': True,
                'protected': True
            }
        ],
        'audit_trail': [
            {
                'entry_id': 'AUDIT001',
                'user_id': 'USER001',
                'action': 'record_created',
                'timestamp': 'invalid-timestamp',  # Invalid format
                'record_id': 'REC001',
                'secure': True
            }
        ]
    }
    
    result = run(input_data)
    
    assert result['compliance_status'] == 'non_compliant'
    assert result['audit_findings']['timestamped_entries'] == 0
    
    # Check for audit trail violation
    audit_violations = [v for v in result['violations'] if '11.10(e)' in v['section']]
    assert len(audit_violations) > 0


def test_cfr_part11_validator_recommendations():
    """Test generation of compliance recommendations."""
    input_data = {
        'electronic_records': [
            {
                'record_id': 'REC001',
                'validation_documented': False,  # Missing validation
                'can_generate_copies': False,    # Missing capability
                'protected': True
            }
        ],
        'signature_system': {
            'contains_signature_information': False,
            'signatures_linked_to_records': False,
            'unique_signatures': False,
            'two_factor_authentication': False
        }
    }
    
    result = run(input_data)
    
    assert result['compliance_status'] == 'non_compliant'
    assert len(result['recommendations']) > 0
    
    recommendations_text = ' '.join(result['recommendations'])
    assert 'CRITICAL' in recommendations_text
    assert 'validation' in recommendations_text.lower()
    assert 'remediation' in recommendations_text.lower() or 'comprehensive' in recommendations_text.lower()