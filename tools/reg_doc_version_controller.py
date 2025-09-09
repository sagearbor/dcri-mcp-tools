from typing import Dict, Any, List
from datetime import datetime, timedelta
import re


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Track and control regulatory document versions across clinical trial lifecycle.
    Manages document version control, approval workflows, and distribution tracking.
    
    Args:
        input_data: Dict containing:
            - documents (list): List of regulatory documents to track
            - version_history (list): Historical version information
            - approval_workflow (dict): Document approval process configuration
            - distribution_list (list): Recipients for document distribution
            - check_consistency (bool, optional): Check cross-document consistency
            - regulatory_requirements (dict, optional): Authority-specific requirements
    
    Returns:
        Dict containing:
            - version_control_status (str): 'controlled', 'inconsistent', 'needs_attention'
            - document_inventory (dict): Complete document inventory with versions
            - version_conflicts (list): Version inconsistencies found
            - approval_status (dict): Document approval workflow status
            - distribution_tracking (dict): Document distribution status
            - compliance_check (dict): Regulatory compliance assessment
            - recommendations (list): Version control improvement recommendations
    """
    documents = input_data.get('documents', [])
    version_history = input_data.get('version_history', [])
    approval_workflow = input_data.get('approval_workflow', {})
    distribution_list = input_data.get('distribution_list', [])
    check_consistency = input_data.get('check_consistency', True)
    regulatory_requirements = input_data.get('regulatory_requirements', {})
    
    if not documents:
        return {
            'error': 'No documents provided for version control',
            'version_control_status': 'needs_attention',
            'document_inventory': {},
            'version_conflicts': [],
            'approval_status': {},
            'distribution_tracking': {},
            'compliance_check': {},
            'recommendations': ['Provide document list for version control tracking']
        }
    
    # Initialize tracking variables
    version_conflicts = []
    recommendations = []
    
    # Create document inventory
    document_inventory = _create_document_inventory(documents, version_history)
    
    # Check version conflicts and consistency
    if check_consistency:
        version_conflicts = _check_version_conflicts(documents, document_inventory)
    
    # Assess approval status
    approval_status = _assess_approval_status(documents, approval_workflow)
    
    # Track distribution
    distribution_tracking = _track_document_distribution(documents, distribution_list)
    
    # Check regulatory compliance
    compliance_check = _check_regulatory_compliance(
        documents, regulatory_requirements, version_conflicts
    )
    
    # Determine overall status
    if version_conflicts or approval_status.get('pending_approvals', 0) > 0:
        version_control_status = 'needs_attention'
    elif any(not doc.get('version_controlled', True) for doc in documents):
        version_control_status = 'inconsistent'
    else:
        version_control_status = 'controlled'
    
    # Generate recommendations
    recommendations = _generate_version_control_recommendations(
        version_conflicts, approval_status, distribution_tracking, compliance_check
    )
    
    return {
        'version_control_status': version_control_status,
        'document_inventory': document_inventory,
        'version_conflicts': version_conflicts,
        'approval_status': approval_status,
        'distribution_tracking': distribution_tracking,
        'compliance_check': compliance_check,
        'recommendations': recommendations,
        'summary': {
            'total_documents': len(documents),
            'version_conflicts': len(version_conflicts),
            'pending_approvals': approval_status.get('pending_approvals', 0),
            'outdated_distributions': distribution_tracking.get('outdated_distributions', 0),
            'compliance_issues': len(compliance_check.get('issues', []))
        }
    }


def _create_document_inventory(documents: List[Dict], version_history: List[Dict]) -> Dict:
    """Create comprehensive document inventory with version tracking."""
    
    inventory = {
        'documents_by_type': {},
        'current_versions': {},
        'version_statistics': {
            'total_documents': len(documents),
            'controlled_documents': 0,
            'uncontrolled_documents': 0,
            'latest_version_date': None,
            'oldest_version_date': None
        }
    }
    
    # Process each document
    for doc in documents:
        doc_id = doc.get('document_id', 'Unknown')
        doc_type = doc.get('document_type', 'Unspecified')
        current_version = doc.get('current_version', '1.0')
        
        # Group by document type
        if doc_type not in inventory['documents_by_type']:
            inventory['documents_by_type'][doc_type] = []
        
        # Add to current versions tracking
        inventory['current_versions'][doc_id] = {
            'document_name': doc.get('document_name', 'Unknown'),
            'document_type': doc_type,
            'current_version': current_version,
            'version_date': doc.get('version_date', ''),
            'status': doc.get('status', 'Draft'),
            'author': doc.get('author', ''),
            'approver': doc.get('approver', ''),
            'approval_date': doc.get('approval_date', ''),
            'effective_date': doc.get('effective_date', ''),
            'next_review_date': doc.get('next_review_date', ''),
            'version_controlled': doc.get('version_controlled', True)
        }
        
        inventory['documents_by_type'][doc_type].append(inventory['current_versions'][doc_id])
        
        # Update statistics
        if doc.get('version_controlled', True):
            inventory['version_statistics']['controlled_documents'] += 1
        else:
            inventory['version_statistics']['uncontrolled_documents'] += 1
        
        # Track date ranges
        version_date = doc.get('version_date')
        if version_date:
            try:
                date_obj = datetime.strptime(version_date, '%Y-%m-%d')
                if (not inventory['version_statistics']['latest_version_date'] or 
                    date_obj > inventory['version_statistics']['latest_version_date']):
                    inventory['version_statistics']['latest_version_date'] = date_obj
                
                if (not inventory['version_statistics']['oldest_version_date'] or 
                    date_obj < inventory['version_statistics']['oldest_version_date']):
                    inventory['version_statistics']['oldest_version_date'] = date_obj
            except ValueError:
                pass
    
    # Convert dates back to strings for JSON serialization
    if inventory['version_statistics']['latest_version_date']:
        inventory['version_statistics']['latest_version_date'] = \
            inventory['version_statistics']['latest_version_date'].strftime('%Y-%m-%d')
    
    if inventory['version_statistics']['oldest_version_date']:
        inventory['version_statistics']['oldest_version_date'] = \
            inventory['version_statistics']['oldest_version_date'].strftime('%Y-%m-%d')
    
    return inventory


def _check_version_conflicts(documents: List[Dict], inventory: Dict) -> List[Dict]:
    """Check for version conflicts and inconsistencies."""
    
    conflicts = []
    
    # Check for duplicate document names with different versions
    doc_names = {}
    for doc in documents:
        name = doc.get('document_name', '').lower()
        version = doc.get('current_version', '')
        doc_id = doc.get('document_id', '')
        
        if name in doc_names:
            if doc_names[name]['version'] != version:
                conflicts.append({
                    'conflict_type': 'version_mismatch',
                    'document_name': doc.get('document_name', ''),
                    'description': f'Multiple versions found: {doc_names[name]["version"]} and {version}',
                    'document_ids': [doc_names[name]['id'], doc_id],
                    'severity': 'high'
                })
        else:
            doc_names[name] = {'version': version, 'id': doc_id}
    
    # Check for documents without proper version numbering
    for doc in documents:
        version = doc.get('current_version', '')
        if not _is_valid_version_format(version):
            conflicts.append({
                'conflict_type': 'invalid_version_format',
                'document_name': doc.get('document_name', ''),
                'document_id': doc.get('document_id', ''),
                'description': f'Invalid version format: {version}',
                'severity': 'medium'
            })
    
    # Check for outdated documents (no activity in 6 months)
    cutoff_date = datetime.now() - timedelta(days=180)
    for doc in documents:
        version_date = doc.get('version_date', '')
        if version_date:
            try:
                doc_date = datetime.strptime(version_date, '%Y-%m-%d')
                if doc_date < cutoff_date:
                    conflicts.append({
                        'conflict_type': 'potentially_outdated',
                        'document_name': doc.get('document_name', ''),
                        'document_id': doc.get('document_id', ''),
                        'description': f'Document not updated since {version_date}',
                        'severity': 'low'
                    })
            except ValueError:
                conflicts.append({
                    'conflict_type': 'invalid_date_format',
                    'document_name': doc.get('document_name', ''),
                    'document_id': doc.get('document_id', ''),
                    'description': f'Invalid date format: {version_date}',
                    'severity': 'medium'
                })
    
    # Check for cross-references consistency
    _check_cross_reference_consistency(documents, conflicts)
    
    return conflicts


def _is_valid_version_format(version: str) -> bool:
    """Check if version number follows standard format (e.g., 1.0, 2.1, 1.0.1)."""
    if not version:
        return False
    
    # Accept formats like: 1.0, 2.1, 1.0.1, v1.0, V2.1
    pattern = r'^[vV]?(\d+)\.(\d+)(?:\.(\d+))?$'
    return bool(re.match(pattern, version.strip()))


def _check_cross_reference_consistency(documents: List[Dict], conflicts: List):
    """Check for consistency in cross-referenced document versions."""
    
    # Build reference map
    doc_versions = {doc.get('document_id'): doc.get('current_version') 
                   for doc in documents if doc.get('document_id')}
    
    for doc in documents:
        references = doc.get('references_other_documents', [])
        
        for ref in references:
            ref_doc_id = ref.get('document_id')
            ref_version = ref.get('referenced_version')
            
            if ref_doc_id in doc_versions:
                current_version = doc_versions[ref_doc_id]
                if ref_version and ref_version != current_version:
                    conflicts.append({
                        'conflict_type': 'outdated_reference',
                        'document_name': doc.get('document_name', ''),
                        'document_id': doc.get('document_id', ''),
                        'description': f'References {ref_doc_id} version {ref_version}, but current is {current_version}',
                        'severity': 'medium'
                    })


def _assess_approval_status(documents: List[Dict], approval_workflow: Dict) -> Dict:
    """Assess document approval workflow status."""
    
    status = {
        'total_documents': len(documents),
        'approved_documents': 0,
        'pending_approvals': 0,
        'draft_documents': 0,
        'expired_documents': 0,
        'approval_workflow_enabled': bool(approval_workflow),
        'workflow_compliance': {}
    }
    
    # Analyze document status
    for doc in documents:
        doc_status = doc.get('status', '').lower()
        
        if doc_status in ['approved', 'effective']:
            status['approved_documents'] += 1
        elif doc_status in ['pending_approval', 'under_review']:
            status['pending_approvals'] += 1
        elif doc_status in ['draft', 'in_progress']:
            status['draft_documents'] += 1
        elif doc_status in ['expired', 'superseded']:
            status['expired_documents'] += 1
    
    # Check workflow compliance if workflow is defined
    if approval_workflow:
        required_approvers = approval_workflow.get('required_approvers', [])
        approval_timeframe = approval_workflow.get('approval_timeframe_days', 30)
        
        workflow_compliant = 0
        for doc in documents:
            approver = doc.get('approver', '')
            approval_date = doc.get('approval_date', '')
            
            # Check if approved by authorized approver
            if approver in required_approvers and approval_date:
                workflow_compliant += 1
        
        status['workflow_compliance'] = {
            'compliant_documents': workflow_compliant,
            'compliance_rate': (workflow_compliant / len(documents) * 100) if documents else 0
        }
    
    return status


def _track_document_distribution(documents: List[Dict], distribution_list: List[Dict]) -> Dict:
    """Track document distribution status."""
    
    tracking = {
        'total_recipients': len(distribution_list),
        'documents_distributed': 0,
        'outdated_distributions': 0,
        'pending_distributions': 0,
        'distribution_by_document': {},
        'recipient_status': {}
    }
    
    if not distribution_list:
        return tracking
    
    # Track distribution for each document
    for doc in documents:
        doc_id = doc.get('document_id', '')
        current_version = doc.get('current_version', '')
        
        tracking['distribution_by_document'][doc_id] = {
            'document_name': doc.get('document_name', ''),
            'current_version': current_version,
            'distributed_recipients': 0,
            'outdated_recipients': 0,
            'pending_recipients': 0
        }
        
        # Check each recipient
        for recipient in distribution_list:
            recipient_id = recipient.get('recipient_id', '')
            received_documents = recipient.get('received_documents', {})
            
            if doc_id in received_documents:
                received_version = received_documents[doc_id].get('version', '')
                if received_version == current_version:
                    tracking['distribution_by_document'][doc_id]['distributed_recipients'] += 1
                else:
                    tracking['distribution_by_document'][doc_id]['outdated_recipients'] += 1
                    tracking['outdated_distributions'] += 1
            else:
                tracking['distribution_by_document'][doc_id]['pending_recipients'] += 1
                tracking['pending_distributions'] += 1
    
    # Track recipient status
    for recipient in distribution_list:
        recipient_id = recipient.get('recipient_id', '')
        received_docs = len(recipient.get('received_documents', {}))
        
        tracking['recipient_status'][recipient_id] = {
            'name': recipient.get('name', ''),
            'role': recipient.get('role', ''),
            'documents_received': received_docs,
            'last_update': recipient.get('last_update', '')
        }
    
    return tracking


def _check_regulatory_compliance(documents: List[Dict], regulatory_requirements: Dict, 
                               conflicts: List[Dict]) -> Dict:
    """Check regulatory compliance for document management."""
    
    compliance = {
        'overall_status': 'compliant',
        'issues': [],
        'regulatory_authority': regulatory_requirements.get('authority', 'Not specified'),
        'requirements_checked': []
    }
    
    # Check basic regulatory requirements
    if regulatory_requirements.get('authority') in ['FDA', 'EMA', 'ICH']:
        # Check for required document types
        required_docs = regulatory_requirements.get('required_document_types', [])
        available_types = {doc.get('document_type') for doc in documents}
        
        for req_type in required_docs:
            if req_type not in available_types:
                compliance['issues'].append({
                    'requirement': f'Required document type: {req_type}',
                    'status': 'missing',
                    'severity': 'high'
                })
                compliance['overall_status'] = 'non_compliant'
            else:
                compliance['requirements_checked'].append(f'Document type {req_type} present')
    
    # Check version control requirements
    if regulatory_requirements.get('version_control_required', True):
        uncontrolled_docs = [doc for doc in documents if not doc.get('version_controlled', True)]
        if uncontrolled_docs:
            compliance['issues'].append({
                'requirement': 'Version control for all documents',
                'status': 'non_compliant',
                'severity': 'medium',
                'details': f'{len(uncontrolled_docs)} documents not under version control'
            })
            if compliance['overall_status'] == 'compliant':
                compliance['overall_status'] = 'partial'
    
    # Check approval requirements
    if regulatory_requirements.get('approval_required', True):
        unapproved_docs = [doc for doc in documents 
                          if doc.get('status', '').lower() not in ['approved', 'effective']]
        if unapproved_docs:
            compliance['issues'].append({
                'requirement': 'Document approval',
                'status': 'pending',
                'severity': 'medium',
                'details': f'{len(unapproved_docs)} documents pending approval'
            })
    
    # Factor in version conflicts
    high_severity_conflicts = [c for c in conflicts if c.get('severity') == 'high']
    if high_severity_conflicts:
        compliance['issues'].append({
            'requirement': 'Version consistency',
            'status': 'non_compliant',
            'severity': 'high',
            'details': f'{len(high_severity_conflicts)} high-severity version conflicts'
        })
        compliance['overall_status'] = 'non_compliant'
    
    return compliance


def _generate_version_control_recommendations(version_conflicts: List, approval_status: Dict,
                                            distribution_tracking: Dict, compliance_check: Dict) -> List[str]:
    """Generate recommendations for improving version control."""
    
    recommendations = []
    
    # Version conflict recommendations
    if version_conflicts:
        high_conflicts = [c for c in version_conflicts if c.get('severity') == 'high']
        if high_conflicts:
            recommendations.append(f'Resolve {len(high_conflicts)} high-severity version conflicts immediately')
        
        medium_conflicts = [c for c in version_conflicts if c.get('severity') == 'medium']
        if medium_conflicts:
            recommendations.append(f'Address {len(medium_conflicts)} medium-severity version issues')
    
    # Approval workflow recommendations
    if approval_status.get('pending_approvals', 0) > 0:
        recommendations.append(f'Complete approval process for {approval_status["pending_approvals"]} pending documents')
    
    if approval_status.get('workflow_compliance', {}).get('compliance_rate', 100) < 90:
        recommendations.append('Improve approval workflow compliance - ensure all documents follow required approval process')
    
    # Distribution recommendations
    if distribution_tracking.get('outdated_distributions', 0) > 0:
        recommendations.append(f'Update {distribution_tracking["outdated_distributions"]} outdated document distributions')
    
    if distribution_tracking.get('pending_distributions', 0) > 0:
        recommendations.append(f'Distribute pending documents to {distribution_tracking["pending_distributions"]} recipients')
    
    # Compliance recommendations
    compliance_issues = compliance_check.get('issues', [])
    high_compliance_issues = [i for i in compliance_issues if i.get('severity') == 'high']
    if high_compliance_issues:
        recommendations.append('Address critical regulatory compliance issues in document management')
    
    # General recommendations
    if not version_conflicts and approval_status.get('pending_approvals', 0) == 0:
        recommendations.append('Document version control appears well-managed - maintain current practices')
    
    # Best practice recommendations
    recommendations.append('Implement regular version control audits and cleanup procedures')
    recommendations.append('Consider automated version control and distribution management tools')
    
    return recommendations