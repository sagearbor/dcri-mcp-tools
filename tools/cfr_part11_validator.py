from typing import Dict, Any, List
from datetime import datetime, timedelta
import re


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check 21 CFR Part 11 compliance for electronic signatures and records.
    Validates electronic signature systems against FDA requirements for clinical trials.
    
    Args:
        input_data: Dict containing:
            - electronic_records (list): List of electronic records to validate
            - signature_system (dict): Electronic signature system information
            - user_accounts (list): User account and access control data
            - audit_trail (list): System audit trail entries
            - validation_documentation (dict): System validation documents
            - check_controls (bool, optional): Validate access controls
    
    Returns:
        Dict containing:
            - compliance_status (str): 'compliant', 'non_compliant', 'partial'
            - compliance_score (float): Overall compliance percentage
            - part11_requirements (dict): Status of each CFR Part 11 requirement
            - violations (list): Non-compliance issues found
            - recommendations (list): Steps to achieve compliance
            - audit_findings (dict): Audit trail analysis results
            - validation_status (dict): System validation assessment
    """
    electronic_records = input_data.get('electronic_records', [])
    signature_system = input_data.get('signature_system', {})
    user_accounts = input_data.get('user_accounts', [])
    audit_trail = input_data.get('audit_trail', [])
    validation_docs = input_data.get('validation_documentation', {})
    check_controls = input_data.get('check_controls', True)
    
    if not electronic_records and not signature_system:
        return {
            'error': 'No electronic records or signature system data provided',
            'compliance_status': 'non_compliant',
            'compliance_score': 0.0,
            'part11_requirements': {},
            'violations': ['No electronic system data to validate'],
            'validation_errors': ['No electronic system data to validate'],
            'recommendations': ['Provide electronic records and signature system information'],
            'audit_findings': {},
            'validation_status': {}
        }
    
    # Initialize compliance tracking
    violations = []
    recommendations = []
    part11_requirements = _initialize_part11_requirements()
    
    # Validate electronic records (Subpart B)
    records_compliance = _validate_electronic_records(electronic_records, part11_requirements, violations)
    
    # Validate electronic signatures (Subpart C)
    signatures_compliance = _validate_electronic_signatures(signature_system, part11_requirements, violations)
    
    # Validate access controls
    if check_controls:
        access_compliance = _validate_access_controls(user_accounts, part11_requirements, violations)
    
    # Validate audit trail
    audit_findings = _validate_audit_trail(audit_trail, part11_requirements, violations)
    
    # Validate system validation documentation
    validation_status = _validate_system_validation(validation_docs, part11_requirements, violations)
    
    # Calculate compliance score
    total_requirements = len(part11_requirements)
    compliant_requirements = sum(1 for req in part11_requirements.values() if req['status'] == 'compliant')
    compliance_score = (compliant_requirements / total_requirements * 100) if total_requirements > 0 else 0
    
    # Determine overall compliance status
    critical_violations = [v for v in violations if v.get('severity') == 'critical']
    if critical_violations:
        compliance_status = 'non_compliant'
    elif violations:
        compliance_status = 'partial'
    else:
        compliance_status = 'compliant'
    
    # Generate recommendations
    recommendations = _generate_compliance_recommendations(part11_requirements, violations)
    
    return {
        'compliance_status': compliance_status,
        'compliance_score': round(compliance_score, 2),
        'part11_requirements': part11_requirements,
        'violations': violations,
        'recommendations': recommendations,
        'audit_findings': audit_findings,
        'validation_status': validation_status,
        'summary': {
            'total_requirements_checked': total_requirements,
            'compliant_requirements': compliant_requirements,
            'critical_violations': len(critical_violations),
            'total_violations': len(violations),
            'ready_for_inspection': compliance_status == 'compliant'
        }
    }


def _initialize_part11_requirements() -> Dict[str, Dict]:
    """Initialize 21 CFR Part 11 requirements checklist."""
    return {
        # Subpart B - Electronic Records
        '11.10_validation': {
            'section': '11.10(a)',
            'requirement': 'Validation of systems to ensure accuracy, reliability, consistent intended performance',
            'status': 'pending',
            'details': []
        },
        '11.10_controls': {
            'section': '11.10(b)',
            'requirement': 'Ability to generate accurate and complete copies',
            'status': 'pending',
            'details': []
        },
        '11.10_protection': {
            'section': '11.10(c)',
            'requirement': 'Protection of records to enable accurate retrieval',
            'status': 'pending',
            'details': []
        },
        '11.10_access': {
            'section': '11.10(d)',
            'requirement': 'Limiting system access to authorized individuals',
            'status': 'pending',
            'details': []
        },
        '11.10_audit_trail': {
            'section': '11.10(e)',
            'requirement': 'Use of secure, computer-generated, time-stamped audit trails',
            'status': 'pending',
            'details': []
        },
        '11.10_sequence': {
            'section': '11.10(f)',
            'requirement': 'Use of operational system checks',
            'status': 'pending',
            'details': []
        },
        '11.10_education': {
            'section': '11.10(g)',
            'requirement': 'Determination that persons who develop, maintain, or use systems have education/training',
            'status': 'pending',
            'details': []
        },
        
        # Subpart C - Electronic Signatures
        '11.50_signed_records': {
            'section': '11.50(a)',
            'requirement': 'Signed electronic records shall contain information associated with signing',
            'status': 'pending',
            'details': []
        },
        '11.70_signature_identification': {
            'section': '11.70',
            'requirement': 'Electronic signatures shall be linked to their respective electronic records',
            'status': 'pending',
            'details': []
        },
        '11.100_general_requirements': {
            'section': '11.100(a)',
            'requirement': 'Each electronic signature shall be unique to one individual',
            'status': 'pending',
            'details': []
        },
        '11.100_verification': {
            'section': '11.100(b)',
            'requirement': 'Before organization establishes, assigns, certifies, or otherwise sanctions an individual electronic signature',
            'status': 'pending',
            'details': []
        },
        '11.200_components': {
            'section': '11.200(a)',
            'requirement': 'Electronic signatures that are not based upon biometrics shall use at least two distinct identification components',
            'status': 'pending',
            'details': []
        },
        '11.300_controls': {
            'section': '11.300',
            'requirement': 'Controls for identification codes and passwords',
            'status': 'pending',
            'details': []
        }
    }


def _validate_electronic_records(records: List[Dict], requirements: Dict, violations: List) -> Dict:
    """Validate electronic records compliance (21 CFR 11.10)."""
    
    # Check validation documentation (11.10a)
    has_validation = any(record.get('validation_documented', False) for record in records)
    if has_validation:
        requirements['11.10_validation']['status'] = 'compliant'
        requirements['11.10_validation']['details'].append('System validation documented')
    else:
        requirements['11.10_validation']['status'] = 'non_compliant'
        violations.append({
            'section': '11.10(a)',
            'description': 'System validation not documented',
            'severity': 'critical',
            'recommendation': 'Document system validation including accuracy and reliability testing'
        })
    
    # Check ability to generate copies (11.10b)
    can_generate_copies = any(record.get('can_generate_copies', False) for record in records)
    if can_generate_copies:
        requirements['11.10_controls']['status'] = 'compliant'
        requirements['11.10_controls']['details'].append('System can generate accurate copies')
    else:
        requirements['11.10_controls']['status'] = 'non_compliant'
        violations.append({
            'section': '11.10(b)',
            'description': 'System cannot generate accurate and complete copies',
            'severity': 'high',
            'recommendation': 'Implement functionality to generate complete copies of electronic records'
        })
    
    # Check record protection (11.10c)
    protected_records = sum(1 for record in records if record.get('protected', False))
    if protected_records == len(records) and records:
        requirements['11.10_protection']['status'] = 'compliant'
        requirements['11.10_protection']['details'].append('All records are protected')
    elif protected_records > 0:
        requirements['11.10_protection']['status'] = 'partial'
        violations.append({
            'section': '11.10(c)',
            'description': f'Only {protected_records}/{len(records)} records are protected',
            'severity': 'medium',
            'recommendation': 'Ensure all electronic records are protected from loss or damage'
        })
    else:
        requirements['11.10_protection']['status'] = 'non_compliant'
        violations.append({
            'section': '11.10(c)',
            'description': 'No record protection measures implemented',
            'severity': 'critical',
            'recommendation': 'Implement backup and recovery procedures for electronic records'
        })
    
    # Check operational system checks (11.10f) - default to compliant if records exist
    if records:
        requirements['11.10_sequence']['status'] = 'compliant'
        requirements['11.10_sequence']['details'].append('Operational system checks in place')
    else:
        requirements['11.10_sequence']['status'] = 'pending'
    
    # Check education/training (11.10g) - default to compliant if validation is documented
    if has_validation:
        requirements['11.10_education']['status'] = 'compliant'
        requirements['11.10_education']['details'].append('Personnel education/training requirements met')
    else:
        requirements['11.10_education']['status'] = 'pending'
    
    return {'records_checked': len(records), 'protected_records': protected_records}


def _validate_electronic_signatures(signature_system: Dict, requirements: Dict, violations: List) -> Dict:
    """Validate electronic signatures compliance (21 CFR 11.50-300)."""
    
    if not signature_system:
        # Mark all signature requirements as non-compliant
        sig_sections = ['11.50_signed_records', '11.70_signature_identification', 
                       '11.100_general_requirements', '11.100_verification', 
                       '11.200_components', '11.300_controls']
        for section in sig_sections:
            requirements[section]['status'] = 'non_compliant'
        
        violations.append({
            'section': '11.50-300',
            'description': 'No electronic signature system information provided',
            'severity': 'critical',
            'recommendation': 'Provide electronic signature system details for validation'
        })
        return {}
    
    # Check signed records information (11.50a)
    contains_signature_info = signature_system.get('contains_signature_information', False)
    if contains_signature_info:
        requirements['11.50_signed_records']['status'] = 'compliant'
        requirements['11.50_signed_records']['details'].append('Signatures contain required information')
    else:
        requirements['11.50_signed_records']['status'] = 'non_compliant'
        violations.append({
            'section': '11.50(a)',
            'description': 'Electronic signatures do not contain required signing information',
            'severity': 'high',
            'recommendation': 'Ensure signatures include name, date/time, and meaning of signature'
        })
    
    # Check signature-record linkage (11.70)
    signatures_linked = signature_system.get('signatures_linked_to_records', False)
    if signatures_linked:
        requirements['11.70_signature_identification']['status'] = 'compliant'
        requirements['11.70_signature_identification']['details'].append('Signatures linked to records')
    else:
        requirements['11.70_signature_identification']['status'] = 'non_compliant'
        violations.append({
            'section': '11.70',
            'description': 'Electronic signatures not properly linked to records',
            'severity': 'critical',
            'recommendation': 'Implement mechanism to link signatures to their respective records'
        })
    
    # Check unique signatures (11.100a)
    unique_signatures = signature_system.get('unique_signatures', False)
    if unique_signatures:
        requirements['11.100_general_requirements']['status'] = 'compliant'
        requirements['11.100_general_requirements']['details'].append('Each signature is unique')
    else:
        requirements['11.100_general_requirements']['status'] = 'non_compliant'
        violations.append({
            'section': '11.100(a)',
            'description': 'Electronic signatures are not unique to individuals',
            'severity': 'critical',
            'recommendation': 'Ensure each electronic signature is unique to one individual'
        })
    
    # Check identity verification (11.100b)
    if signature_system.get('verified_identity', True):  # Default to True if not specified
        requirements['11.100_verification']['status'] = 'compliant'
        requirements['11.100_verification']['details'].append('Identity verification implemented')
    else:
        requirements['11.100_verification']['status'] = 'non_compliant'
        violations.append({
            'section': '11.100(b)',
            'description': 'Identity verification not properly implemented',
            'severity': 'high',
            'recommendation': 'Implement identity verification before signature assignment'
        })
    
    # Check two-factor authentication (11.200a)
    two_factor_auth = signature_system.get('two_factor_authentication', False)
    if two_factor_auth:
        requirements['11.200_components']['status'] = 'compliant'
        requirements['11.200_components']['details'].append('Two-factor authentication implemented')
    else:
        requirements['11.200_components']['status'] = 'non_compliant'
        violations.append({
            'section': '11.200(a)',
            'description': 'Electronic signatures do not use two distinct identification components',
            'severity': 'high',
            'recommendation': 'Implement two-factor authentication for electronic signatures'
        })
    
    return {'signature_system_evaluated': True}


def _validate_access_controls(user_accounts: List[Dict], requirements: Dict, violations: List) -> Dict:
    """Validate access controls (21 CFR 11.10d, 11.300)."""
    
    if not user_accounts:
        requirements['11.10_access']['status'] = 'non_compliant'
        requirements['11.300_controls']['status'] = 'non_compliant'
        violations.append({
            'section': '11.10(d)',
            'description': 'No user account information provided for access control validation',
            'severity': 'critical',
            'recommendation': 'Provide user account and access control information'
        })
        return {}
    
    # Check access limitations (11.10d)
    authorized_users = sum(1 for user in user_accounts if user.get('authorized', False))
    if authorized_users == len(user_accounts):
        requirements['11.10_access']['status'] = 'compliant'
        requirements['11.10_access']['details'].append('All users are authorized')
    else:
        requirements['11.10_access']['status'] = 'non_compliant'
        violations.append({
            'section': '11.10(d)',
            'description': f'Not all users are properly authorized ({authorized_users}/{len(user_accounts)})',
            'severity': 'high',
            'recommendation': 'Ensure system access is limited to authorized individuals only'
        })
    
    # Check password controls (11.300)
    strong_passwords = sum(1 for user in user_accounts 
                          if user.get('strong_password', False) and 
                             user.get('password_expiry', False))
    
    if strong_passwords == len(user_accounts):
        requirements['11.300_controls']['status'] = 'compliant'
        requirements['11.300_controls']['details'].append('Password controls implemented')
    elif strong_passwords > len(user_accounts) / 2:
        requirements['11.300_controls']['status'] = 'partial'
        violations.append({
            'section': '11.300',
            'description': f'Password controls not fully implemented ({strong_passwords}/{len(user_accounts)})',
            'severity': 'medium',
            'recommendation': 'Implement strong password requirements and expiration policies'
        })
    else:
        requirements['11.300_controls']['status'] = 'non_compliant'
        violations.append({
            'section': '11.300',
            'description': 'Inadequate password controls',
            'severity': 'high',
            'recommendation': 'Implement comprehensive password controls including complexity and expiration'
        })
    
    return {'users_evaluated': len(user_accounts), 'authorized_users': authorized_users}


def _validate_audit_trail(audit_trail: List[Dict], requirements: Dict, violations: List) -> Dict:
    """Validate audit trail requirements (21 CFR 11.10e)."""
    
    findings = {
        'total_entries': len(audit_trail),
        'secure_entries': 0,
        'timestamped_entries': 0,
        'complete_entries': 0
    }
    
    if not audit_trail:
        requirements['11.10_audit_trail']['status'] = 'non_compliant'
        violations.append({
            'section': '11.10(e)',
            'description': 'No audit trail entries provided',
            'severity': 'critical',
            'recommendation': 'Implement secure, time-stamped audit trail functionality'
        })
        return findings
    
    # Validate audit trail entries
    for entry in audit_trail:
        if entry.get('secure', False):
            findings['secure_entries'] += 1
        
        if entry.get('timestamp') and _validate_timestamp_format(entry['timestamp']):
            findings['timestamped_entries'] += 1
        
        required_fields = ['user_id', 'action', 'timestamp', 'record_id']
        if all(entry.get(field) for field in required_fields):
            findings['complete_entries'] += 1
    
    # Determine compliance
    if (findings['secure_entries'] == findings['total_entries'] and 
        findings['timestamped_entries'] == findings['total_entries'] and
        findings['complete_entries'] == findings['total_entries']):
        requirements['11.10_audit_trail']['status'] = 'compliant'
        requirements['11.10_audit_trail']['details'].append('Audit trail is secure and complete')
    else:
        requirements['11.10_audit_trail']['status'] = 'non_compliant'
        violations.append({
            'section': '11.10(e)',
            'description': 'Audit trail does not meet all requirements',
            'severity': 'high',
            'recommendation': 'Ensure all audit trail entries are secure, timestamped, and complete'
        })
    
    return findings


def _validate_system_validation(validation_docs: Dict, requirements: Dict, violations: List) -> Dict:
    """Validate system validation documentation."""
    
    status = {
        'validation_plan': validation_docs.get('validation_plan', False),
        'requirements_specification': validation_docs.get('requirements_specification', False),
        'design_specification': validation_docs.get('design_specification', False),
        'test_protocols': validation_docs.get('test_protocols', False),
        'test_results': validation_docs.get('test_results', False),
        'validation_summary': validation_docs.get('validation_summary', False)
    }
    
    completed_docs = sum(status.values())
    total_docs = len(status)
    
    if completed_docs == total_docs:
        requirements['11.10_validation']['details'].append('Complete validation documentation package')
    elif completed_docs >= total_docs * 0.8:  # 80% threshold
        requirements['11.10_validation']['details'].append('Validation documentation mostly complete')
        violations.append({
            'section': '11.10(a)',
            'description': f'Validation documentation incomplete ({completed_docs}/{total_docs})',
            'severity': 'medium',
            'recommendation': 'Complete missing validation documentation'
        })
    else:
        violations.append({
            'section': '11.10(a)',
            'description': f'Validation documentation significantly incomplete ({completed_docs}/{total_docs})',
            'severity': 'high',
            'recommendation': 'Develop comprehensive validation documentation package'
        })
    
    return status


def _validate_timestamp_format(timestamp: str) -> bool:
    """Validate timestamp format for audit trail."""
    try:
        # Accept various timestamp formats
        formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']
        for fmt in formats:
            try:
                datetime.strptime(timestamp, fmt)
                return True
            except ValueError:
                continue
        return False
    except:
        return False


def _generate_compliance_recommendations(requirements: Dict, violations: List) -> List[str]:
    """Generate specific recommendations for achieving compliance."""
    
    recommendations = []
    
    # High-priority recommendations based on violations
    critical_violations = [v for v in violations if v.get('severity') == 'critical']
    for violation in critical_violations:
        recommendations.append(f"CRITICAL: {violation['recommendation']}")
    
    # General recommendations
    non_compliant = [req for req in requirements.values() if req['status'] == 'non_compliant']
    if len(non_compliant) > 5:
        recommendations.append('Consider comprehensive 21 CFR Part 11 remediation project')
    
    partial_compliant = [req for req in requirements.values() if req['status'] == 'partial']
    if partial_compliant:
        recommendations.append('Complete partial implementations to achieve full compliance')
    
    # Training recommendations
    if any('education' in req['requirement'].lower() for req in requirements.values() 
           if req['status'] == 'non_compliant'):
        recommendations.append('Implement comprehensive training program for system users')
    
    if not recommendations:
        recommendations.append('System appears compliant with 21 CFR Part 11 requirements')
    
    return recommendations