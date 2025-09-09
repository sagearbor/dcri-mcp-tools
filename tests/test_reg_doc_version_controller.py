import pytest
from tools.reg_doc_version_controller import run


def test_reg_doc_version_controller_well_controlled():
    """Test version control for a well-managed document system."""
    input_data = {
        'documents': [
            {
                'document_id': 'DOC001',
                'document_name': 'Protocol Version 2.0',
                'document_type': 'Protocol',
                'current_version': '2.0',
                'version_date': '2025-07-15',
                'status': 'Approved',
                'author': 'Dr. Smith',
                'approver': 'Dr. Johnson',
                'approval_date': '2025-07-20',
                'effective_date': '2025-08-01',
                'next_review_date': '2026-07-15',
                'version_controlled': True
            },
            {
                'document_id': 'DOC002',
                'document_name': 'Informed Consent Form',
                'document_type': 'Consent Form',
                'current_version': '1.5',
                'version_date': '2025-08-01',
                'status': 'Approved',
                'author': 'Clinical Team',
                'approver': 'Dr. Johnson',
                'approval_date': '2025-08-05',
                'effective_date': '2025-08-10',
                'version_controlled': True
            }
        ],
        'approval_workflow': {
            'required_approvers': ['Dr. Johnson', 'Dr. Wilson'],
            'approval_timeframe_days': 30
        },
        'distribution_list': [
            {
                'recipient_id': 'SITE001',
                'name': 'Site 001',
                'role': 'Investigator Site',
                'received_documents': {
                    'DOC001': {'version': '2.0', 'date_received': '2025-08-01'},
                    'DOC002': {'version': '1.5', 'date_received': '2025-08-10'}
                },
                'last_update': '2025-08-10'
            }
        ],
        'regulatory_requirements': {
            'authority': 'FDA',
            'version_control_required': True,
            'approval_required': True,
            'required_document_types': ['Protocol', 'Consent Form']
        }
    }
    
    result = run(input_data)
    
    assert result['version_control_status'] == 'controlled'
    assert len(result['version_conflicts']) == 0
    assert result['approval_status']['approved_documents'] == 2
    assert result['approval_status']['pending_approvals'] == 0
    assert result['distribution_tracking']['outdated_distributions'] == 0
    assert result['compliance_check']['overall_status'] == 'compliant'
    assert result['summary']['version_conflicts'] == 0


def test_reg_doc_version_controller_version_conflicts():
    """Test detection of version conflicts and inconsistencies."""
    input_data = {
        'documents': [
            {
                'document_id': 'DOC001',
                'document_name': 'Protocol Version 2.0',
                'document_type': 'Protocol',
                'current_version': '2.0',
                'version_date': '2024-01-15',
                'status': 'Approved'
            },
            {
                'document_id': 'DOC002',
                'document_name': 'Protocol Version 2.0',  # Same name, different version
                'document_type': 'Protocol',
                'current_version': '1.5',  # Version mismatch
                'version_date': '2024-01-10',
                'status': 'Draft'
            },
            {
                'document_id': 'DOC003',
                'document_name': 'Old Document',
                'document_type': 'Manual',
                'current_version': 'invalid-version',  # Invalid format
                'version_date': '2023-06-01',  # Very old
                'status': 'Approved'
            }
        ],
        'check_consistency': True
    }
    
    result = run(input_data)
    
    assert result['version_control_status'] == 'needs_attention'
    assert len(result['version_conflicts']) > 0
    
    # Check for specific conflict types
    conflict_types = [c['conflict_type'] for c in result['version_conflicts']]
    assert 'version_mismatch' in conflict_types
    assert 'invalid_version_format' in conflict_types
    assert 'potentially_outdated' in conflict_types
    
    # Check for high severity conflicts
    high_severity_conflicts = [c for c in result['version_conflicts'] if c['severity'] == 'high']
    assert len(high_severity_conflicts) > 0


def test_reg_doc_version_controller_approval_workflow():
    """Test approval workflow tracking and compliance."""
    input_data = {
        'documents': [
            {
                'document_id': 'DOC001',
                'document_name': 'Approved Protocol',
                'current_version': '1.0',
                'status': 'Approved',
                'approver': 'Dr. Authorized',
                'approval_date': '2024-01-15'
            },
            {
                'document_id': 'DOC002',
                'document_name': 'Pending Protocol',
                'current_version': '1.0',
                'status': 'Pending_Approval',
                'approver': '',
                'approval_date': ''
            },
            {
                'document_id': 'DOC003',
                'document_name': 'Draft Document',
                'current_version': '0.5',
                'status': 'Draft'
            },
            {
                'document_id': 'DOC004',
                'document_name': 'Unauthorized Approval',
                'current_version': '1.0',
                'status': 'Approved',
                'approver': 'Unauthorized Person',  # Not in approved list
                'approval_date': '2024-01-20'
            }
        ],
        'approval_workflow': {
            'required_approvers': ['Dr. Authorized', 'Dr. Johnson'],
            'approval_timeframe_days': 30
        }
    }
    
    result = run(input_data)
    
    approval_status = result['approval_status']
    assert approval_status['approved_documents'] == 2  # DOC001 and DOC004 (even if unauthorized)
    assert approval_status['pending_approvals'] == 1   # DOC002
    assert approval_status['draft_documents'] == 1     # DOC003
    
    # Check workflow compliance
    workflow_compliance = approval_status['workflow_compliance']
    assert workflow_compliance['compliant_documents'] == 1  # Only DOC001
    assert workflow_compliance['compliance_rate'] < 100


def test_reg_doc_version_controller_distribution_tracking():
    """Test document distribution tracking."""
    input_data = {
        'documents': [
            {
                'document_id': 'DOC001',
                'document_name': 'Current Protocol',
                'current_version': '2.0',
                'status': 'Approved'
            },
            {
                'document_id': 'DOC002',
                'document_name': 'Updated Manual',
                'current_version': '1.5',
                'status': 'Approved'
            }
        ],
        'distribution_list': [
            {
                'recipient_id': 'SITE001',
                'name': 'Site 001',
                'role': 'Investigator Site',
                'received_documents': {
                    'DOC001': {'version': '1.0', 'date_received': '2024-01-01'},  # Outdated
                    'DOC002': {'version': '1.5', 'date_received': '2024-02-01'}   # Current
                },
                'last_update': '2024-02-01'
            },
            {
                'recipient_id': 'SITE002',
                'name': 'Site 002',
                'role': 'Investigator Site',
                'received_documents': {
                    'DOC001': {'version': '2.0', 'date_received': '2024-02-15'}  # Current
                    # DOC002 missing - pending distribution
                },
                'last_update': '2024-02-15'
            }
        ]
    }
    
    result = run(input_data)
    
    distribution_tracking = result['distribution_tracking']
    assert distribution_tracking['total_recipients'] == 2
    assert distribution_tracking['outdated_distributions'] == 1  # SITE001 has old DOC001
    assert distribution_tracking['pending_distributions'] == 1   # SITE002 missing DOC002
    
    # Check document-specific distribution
    doc001_dist = distribution_tracking['distribution_by_document']['DOC001']
    assert doc001_dist['distributed_recipients'] == 1  # SITE002
    assert doc001_dist['outdated_recipients'] == 1     # SITE001
    
    doc002_dist = distribution_tracking['distribution_by_document']['DOC002']
    assert doc002_dist['distributed_recipients'] == 1  # SITE001
    assert doc002_dist['pending_recipients'] == 1      # SITE002


def test_reg_doc_version_controller_regulatory_compliance():
    """Test regulatory compliance assessment."""
    input_data = {
        'documents': [
            {
                'document_id': 'DOC001',
                'document_name': 'Protocol',
                'document_type': 'Protocol',
                'current_version': '1.0',
                'status': 'Approved',
                'version_controlled': True
            },
            {
                'document_id': 'DOC002',
                'document_name': 'Manual',
                'document_type': 'Manual',
                'current_version': '1.0',
                'status': 'Draft',  # Not approved
                'version_controlled': False  # Not version controlled
            }
        ],
        'regulatory_requirements': {
            'authority': 'FDA',
            'version_control_required': True,
            'approval_required': True,
            'required_document_types': ['Protocol', 'Consent Form']  # Consent Form missing
        }
    }
    
    result = run(input_data)
    
    compliance_check = result['compliance_check']
    assert compliance_check['overall_status'] == 'non_compliant'
    assert len(compliance_check['issues']) > 0
    
    # Check for specific compliance issues
    issue_requirements = [issue['requirement'] for issue in compliance_check['issues']]
    assert any('Consent Form' in req for req in issue_requirements)  # Missing required doc type
    assert any('version control' in req.lower() for req in issue_requirements)  # Version control issue


def test_reg_doc_version_controller_cross_references():
    """Test cross-reference consistency checking."""
    input_data = {
        'documents': [
            {
                'document_id': 'DOC001',
                'document_name': 'Main Protocol',
                'current_version': '2.0',
                'status': 'Approved',
                'references_other_documents': [
                    {
                        'document_id': 'DOC002',
                        'referenced_version': '1.0'  # Outdated reference
                    }
                ]
            },
            {
                'document_id': 'DOC002',
                'document_name': 'Supporting Document',
                'current_version': '1.5',  # Current version is 1.5, not 1.0
                'status': 'Approved'
            }
        ],
        'check_consistency': True
    }
    
    result = run(input_data)
    
    # Should detect outdated reference
    reference_conflicts = [c for c in result['version_conflicts'] 
                          if c['conflict_type'] == 'outdated_reference']
    assert len(reference_conflicts) > 0
    assert 'DOC002 version 1.0' in reference_conflicts[0]['description']
    assert 'current is 1.5' in reference_conflicts[0]['description']


def test_reg_doc_version_controller_no_documents():
    """Test error handling when no documents are provided."""
    input_data = {}
    
    result = run(input_data)
    
    assert 'error' in result
    assert result['version_control_status'] == 'needs_attention'
    assert len(result['recommendations']) > 0
    assert 'Provide document list' in result['recommendations'][0]


def test_reg_doc_version_controller_recommendations():
    """Test generation of version control recommendations."""
    input_data = {
        'documents': [
            {
                'document_id': 'DOC001',
                'document_name': 'Conflicted Document',
                'current_version': 'invalid',  # Invalid version
                'status': 'Draft',  # Not approved
                'version_controlled': False  # Not controlled
            }
        ],
        'approval_workflow': {
            'required_approvers': ['Dr. Johnson']
        },
        'distribution_list': [
            {
                'recipient_id': 'SITE001',
                'received_documents': {}  # No documents received
            }
        ]
    }
    
    result = run(input_data)
    
    assert result['version_control_status'] == 'needs_attention'
    assert len(result['recommendations']) > 0
    
    recommendations_text = ' '.join(result['recommendations'])
    assert 'version' in recommendations_text.lower()
    assert 'approval' in recommendations_text.lower()


def test_reg_doc_version_controller_document_inventory():
    """Test document inventory creation and statistics."""
    input_data = {
        'documents': [
            {
                'document_id': 'DOC001',
                'document_name': 'Protocol A',
                'document_type': 'Protocol',
                'current_version': '1.0',
                'version_date': '2024-01-01',
                'status': 'Approved',
                'version_controlled': True
            },
            {
                'document_id': 'DOC002',
                'document_name': 'Manual B',
                'document_type': 'Manual',
                'current_version': '2.0',
                'version_date': '2024-02-01',
                'status': 'Draft',
                'version_controlled': False
            },
            {
                'document_id': 'DOC003',
                'document_name': 'Protocol C',
                'document_type': 'Protocol',
                'current_version': '1.5',
                'version_date': '2024-01-15',
                'status': 'Approved',
                'version_controlled': True
            }
        ]
    }
    
    result = run(input_data)
    
    inventory = result['document_inventory']
    
    # Check document grouping by type
    assert 'Protocol' in inventory['documents_by_type']
    assert 'Manual' in inventory['documents_by_type']
    assert len(inventory['documents_by_type']['Protocol']) == 2
    assert len(inventory['documents_by_type']['Manual']) == 1
    
    # Check version statistics
    stats = inventory['version_statistics']
    assert stats['total_documents'] == 3
    assert stats['controlled_documents'] == 2
    assert stats['uncontrolled_documents'] == 1
    assert stats['latest_version_date'] == '2024-02-01'
    assert stats['oldest_version_date'] == '2024-01-01'
    
    # Check current versions tracking
    assert 'DOC001' in inventory['current_versions']
    assert inventory['current_versions']['DOC001']['current_version'] == '1.0'
    assert inventory['current_versions']['DOC001']['document_type'] == 'Protocol'