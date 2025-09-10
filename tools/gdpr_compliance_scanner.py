from typing import Dict, Any, List
from datetime import datetime, timedelta
import re


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identify GDPR compliance issues in clinical data systems and processes.
    
    Example:
        Input: Data sources, personal data inventory, consent records, and privacy measures for a clinical trial
        Output: GDPR compliance assessment with violations, risk analysis, and remediation recommendations
    
    Parameters:
        data_sources : list
            List of data sources/systems to scan for compliance
        personal_data_inventory : dict
            Inventory of personal data processed in the study
        consent_records : list
            Subject consent and withdrawal records
        data_processing_activities : list
            List of data processing activities and their purposes
        privacy_measures : dict
            Technical and organizational privacy measures implemented
        cross_border_transfers : list
            International data transfers and safeguards
        check_retention : bool, optional
            Whether to check data retention compliance (default: True)
    """
    data_sources = input_data.get('data_sources', [])
    personal_data_inventory = input_data.get('personal_data_inventory', {})
    consent_records = input_data.get('consent_records', [])
    processing_activities = input_data.get('data_processing_activities', [])
    privacy_measures = input_data.get('privacy_measures', {})
    cross_border_transfers = input_data.get('cross_border_transfers', [])
    check_retention = input_data.get('check_retention', True)
    
    if not any([data_sources, personal_data_inventory, consent_records, processing_activities]):
        return {
            'error': 'No data sources or processing information provided',
            'compliance_status': 'needs_review',
            'gdpr_assessment': {},
            'privacy_violations': [],
            'data_subject_rights': {},
            'risk_assessment': {},
            'recommendations': ['Provide data processing information for GDPR assessment'],
            'compliance_score': 0.0
        }
    
    # Initialize compliance tracking
    privacy_violations = []
    recommendations = []
    
    # Assess GDPR principles (Article 5)
    gdpr_assessment = _assess_gdpr_principles(
        personal_data_inventory, processing_activities, privacy_violations
    )
    
    # Check lawful basis for processing (Article 6)
    lawful_basis_compliance = _check_lawful_basis(
        processing_activities, consent_records, privacy_violations
    )
    
    # Assess consent management (Articles 7-8)
    consent_compliance = _assess_consent_management(
        consent_records, privacy_violations
    )
    
    # Check data subject rights (Chapter III)
    data_subject_rights = _assess_data_subject_rights(
        personal_data_inventory, privacy_measures, privacy_violations
    )
    
    # Assess technical and organizational measures (Article 32)
    security_compliance = _assess_security_measures(
        privacy_measures, data_sources, privacy_violations
    )
    
    # Check international transfers (Chapter V)
    transfer_compliance = _assess_international_transfers(
        cross_border_transfers, privacy_violations
    )
    
    # Data retention assessment
    if check_retention:
        retention_compliance = _assess_data_retention(
            personal_data_inventory, processing_activities, privacy_violations
        )
    
    # Risk assessment
    risk_assessment = _conduct_privacy_risk_assessment(
        personal_data_inventory, processing_activities, privacy_violations
    )
    
    # Calculate compliance score
    compliance_areas = [
        gdpr_assessment['overall_compliance'],
        lawful_basis_compliance,
        consent_compliance,
        data_subject_rights['overall_compliance'],
        security_compliance,
        transfer_compliance
    ]
    
    if check_retention:
        compliance_areas.append(retention_compliance)
    
    compliance_score = sum(compliance_areas) / len(compliance_areas) * 100
    
    # Determine overall compliance status
    if compliance_score >= 90:
        compliance_status = 'compliant'
    elif compliance_score >= 70:
        compliance_status = 'needs_review'
    else:
        compliance_status = 'non_compliant'
    
    # Generate recommendations
    recommendations = _generate_gdpr_recommendations(privacy_violations, gdpr_assessment)
    
    return {
        'compliance_status': compliance_status,
        'gdpr_assessment': gdpr_assessment,
        'privacy_violations': privacy_violations,
        'data_subject_rights': data_subject_rights,
        'risk_assessment': risk_assessment,
        'recommendations': recommendations,
        'compliance_score': round(compliance_score, 2),
        'summary': {
            'total_violations': len(privacy_violations),
            'high_risk_violations': len([v for v in privacy_violations if v.get('risk_level') == 'high']),
            'data_subjects_affected': sum(activity.get('data_subjects_count', 0) for activity in processing_activities),
            'requires_dpia': risk_assessment.get('dpia_required', False)
        }
    }


def _assess_gdpr_principles(personal_data_inventory: Dict, processing_activities: List, 
                           violations: List) -> Dict:
    """Assess compliance with GDPR principles (Article 5)."""
    
    principles = {
        'lawfulness_fairness_transparency': {'compliant': False, 'score': 0},
        'purpose_limitation': {'compliant': False, 'score': 0},
        'data_minimisation': {'compliant': False, 'score': 0},
        'accuracy': {'compliant': False, 'score': 0},
        'storage_limitation': {'compliant': False, 'score': 0},
        'integrity_confidentiality': {'compliant': False, 'score': 0},
        'accountability': {'compliant': False, 'score': 0}
    }
    
    # Check lawfulness, fairness and transparency
    lawful_activities = sum(1 for activity in processing_activities 
                           if activity.get('lawful_basis'))
    if lawful_activities == len(processing_activities) and processing_activities:
        principles['lawfulness_fairness_transparency']['compliant'] = True
        principles['lawfulness_fairness_transparency']['score'] = 100
    elif lawful_activities > 0:
        principles['lawfulness_fairness_transparency']['score'] = (lawful_activities / len(processing_activities)) * 100
        violations.append({
            'principle': 'Lawfulness, fairness and transparency',
            'description': f'Not all processing activities have documented lawful basis ({lawful_activities}/{len(processing_activities)})',
            'risk_level': 'high',
            'article': 'Article 5(1)(a)'
        })
    
    # Check purpose limitation
    specific_purposes = sum(1 for activity in processing_activities 
                          if activity.get('purpose') and len(activity['purpose']) > 10)
    if specific_purposes == len(processing_activities) and processing_activities:
        principles['purpose_limitation']['compliant'] = True
        principles['purpose_limitation']['score'] = 100
    else:
        principles['purpose_limitation']['score'] = (specific_purposes / len(processing_activities) * 100) if processing_activities else 0
        violations.append({
            'principle': 'Purpose limitation',
            'description': 'Processing purposes are not sufficiently specific and documented',
            'risk_level': 'medium',
            'article': 'Article 5(1)(b)'
        })
    
    # Check data minimisation
    data_categories = personal_data_inventory.get('data_categories', [])
    if personal_data_inventory.get('minimisation_assessment', False):
        principles['data_minimisation']['compliant'] = True
        principles['data_minimisation']['score'] = 100
    else:
        violations.append({
            'principle': 'Data minimisation',
            'description': 'No evidence of data minimisation assessment',
            'risk_level': 'medium',
            'article': 'Article 5(1)(c)'
        })
    
    # Check accuracy
    if personal_data_inventory.get('accuracy_measures', False):
        principles['accuracy']['compliant'] = True
        principles['accuracy']['score'] = 100
    else:
        violations.append({
            'principle': 'Accuracy',
            'description': 'No measures in place to ensure data accuracy',
            'risk_level': 'medium',
            'article': 'Article 5(1)(d)'
        })
    
    # Check storage limitation
    retention_policies = sum(1 for activity in processing_activities 
                           if activity.get('retention_period'))
    if retention_policies == len(processing_activities) and processing_activities:
        principles['storage_limitation']['compliant'] = True
        principles['storage_limitation']['score'] = 100
    else:
        principles['storage_limitation']['score'] = (retention_policies / len(processing_activities) * 100) if processing_activities else 0
        violations.append({
            'principle': 'Storage limitation',
            'description': 'Retention periods not defined for all processing activities',
            'risk_level': 'medium',
            'article': 'Article 5(1)(e)'
        })
    
    # Calculate overall compliance
    total_score = sum(principle['score'] for principle in principles.values())
    overall_compliance = total_score / (len(principles) * 100)
    
    return {
        'principles': principles,
        'overall_compliance': overall_compliance,
        'compliant_principles': sum(1 for p in principles.values() if p['compliant'])
    }


def _check_lawful_basis(processing_activities: List, consent_records: List, violations: List) -> float:
    """Check lawful basis for processing (Article 6)."""
    
    if not processing_activities:
        return 0.0
    
    valid_lawful_bases = [
        'consent', 'contract', 'legal_obligation', 'vital_interests', 
        'public_task', 'legitimate_interests'
    ]
    
    activities_with_basis = 0
    for activity in processing_activities:
        lawful_basis = activity.get('lawful_basis', '').lower()
        
        if lawful_basis in valid_lawful_bases:
            activities_with_basis += 1
            
            # Special checks for consent
            if lawful_basis == 'consent':
                data_subjects = activity.get('data_subjects', [])
                consented_subjects = [record for record in consent_records 
                                    if record.get('consent_given', False)]
                
                if len(consented_subjects) < len(data_subjects):
                    violations.append({
                        'principle': 'Lawful basis - Consent',
                        'description': f'Not all data subjects have given consent for activity: {activity.get("activity_name", "Unknown")}',
                        'risk_level': 'high',
                        'article': 'Article 6(1)(a)'
                    })
        else:
            violations.append({
                'principle': 'Lawful basis',
                'description': f'Invalid or missing lawful basis for activity: {activity.get("activity_name", "Unknown")}',
                'risk_level': 'high',
                'article': 'Article 6'
            })
    
    return activities_with_basis / len(processing_activities)


def _assess_consent_management(consent_records: List, violations: List) -> float:
    """Assess consent management compliance (Articles 7-8)."""
    
    if not consent_records:
        violations.append({
            'principle': 'Consent management',
            'description': 'No consent records provided for assessment',
            'risk_level': 'high',
            'article': 'Articles 7-8'
        })
        return 0.0
    
    valid_consents = 0
    for consent in consent_records:
        consent_valid = True
        
        # Check if consent is freely given
        if not consent.get('freely_given', False):
            violations.append({
                'principle': 'Consent validity',
                'description': f'Consent not freely given for subject: {consent.get("subject_id", "Unknown")}',
                'risk_level': 'high',
                'article': 'Article 7(4)'
            })
            consent_valid = False
        
        # Check if consent is specific
        if not consent.get('specific_purpose', False):
            violations.append({
                'principle': 'Consent specificity',
                'description': f'Consent not specific for subject: {consent.get("subject_id", "Unknown")}',
                'risk_level': 'medium',
                'article': 'Article 7(2)'
            })
            consent_valid = False
        
        # Check if consent is informed
        if not consent.get('informed', False):
            violations.append({
                'principle': 'Informed consent',
                'description': f'Consent not properly informed for subject: {consent.get("subject_id", "Unknown")}',
                'risk_level': 'medium',
                'article': 'Article 7(1)'
            })
            consent_valid = False
        
        # Check withdrawal mechanism
        if not consent.get('withdrawal_mechanism', False):
            violations.append({
                'principle': 'Consent withdrawal',
                'description': f'No withdrawal mechanism for subject: {consent.get("subject_id", "Unknown")}',
                'risk_level': 'medium',
                'article': 'Article 7(3)'
            })
            consent_valid = False
        
        if consent_valid:
            valid_consents += 1
    
    return valid_consents / len(consent_records)


def _assess_data_subject_rights(personal_data_inventory: Dict, privacy_measures: Dict, 
                               violations: List) -> Dict:
    """Assess data subject rights implementation (Chapter III)."""
    
    rights_compliance = {
        'access_right': {'implemented': False, 'score': 0},  # Article 15
        'rectification_right': {'implemented': False, 'score': 0},  # Article 16
        'erasure_right': {'implemented': False, 'score': 0},  # Article 17
        'restriction_right': {'implemented': False, 'score': 0},  # Article 18
        'portability_right': {'implemented': False, 'score': 0},  # Article 20
        'objection_right': {'implemented': False, 'score': 0}  # Article 21
    }
    
    measures = privacy_measures.get('data_subject_rights', {})
    
    # Check each right
    for right in rights_compliance.keys():
        if measures.get(right, False):
            rights_compliance[right]['implemented'] = True
            rights_compliance[right]['score'] = 100
        else:
            violations.append({
                'principle': f'Data subject {right.replace("_", " ")}',
                'description': f'No mechanism implemented for {right.replace("_", " ")}',
                'risk_level': 'medium',
                'article': f'Chapter III'
            })
    
    # Calculate overall compliance
    implemented_rights = sum(1 for right in rights_compliance.values() if right['implemented'])
    overall_compliance = implemented_rights / len(rights_compliance)
    
    return {
        'rights': rights_compliance,
        'overall_compliance': overall_compliance,
        'implemented_rights': implemented_rights,
        'total_rights': len(rights_compliance)
    }


def _assess_security_measures(privacy_measures: Dict, data_sources: List, violations: List) -> float:
    """Assess technical and organizational measures (Article 32)."""
    
    required_measures = [
        'encryption', 'access_controls', 'backup_recovery', 
        'incident_response', 'staff_training', 'regular_testing'
    ]
    
    implemented_measures = 0
    security_measures = privacy_measures.get('security_measures', {})
    
    for measure in required_measures:
        if security_measures.get(measure, False):
            implemented_measures += 1
        else:
            violations.append({
                'principle': 'Security measures',
                'description': f'Security measure not implemented: {measure.replace("_", " ")}',
                'risk_level': 'high' if measure in ['encryption', 'access_controls'] else 'medium',
                'article': 'Article 32'
            })
    
    # Check data source specific security
    for source in data_sources:
        if not source.get('encrypted', False):
            violations.append({
                'principle': 'Data encryption',
                'description': f'Data source not encrypted: {source.get("name", "Unknown")}',
                'risk_level': 'high',
                'article': 'Article 32(1)(a)'
            })
    
    return implemented_measures / len(required_measures)


def _assess_international_transfers(cross_border_transfers: List, violations: List) -> float:
    """Assess international data transfers (Chapter V)."""
    
    if not cross_border_transfers:
        return 1.0  # No transfers = compliant
    
    compliant_transfers = 0
    for transfer in cross_border_transfers:
        destination = transfer.get('destination_country', '')
        safeguards = transfer.get('safeguards', [])
        
        # Check adequacy decision
        adequate_countries = ['Andorra', 'Argentina', 'Canada', 'Faroe Islands', 'Guernsey', 
                             'Israel', 'Isle of Man', 'Japan', 'Jersey', 'New Zealand', 
                             'South Korea', 'Switzerland', 'United Kingdom', 'Uruguay']
        
        if destination in adequate_countries:
            compliant_transfers += 1
        elif safeguards:
            # Check for appropriate safeguards
            valid_safeguards = ['standard_contractual_clauses', 'binding_corporate_rules', 
                              'certification', 'approved_code_of_conduct']
            if any(safeguard in valid_safeguards for safeguard in safeguards):
                compliant_transfers += 1
            else:
                violations.append({
                    'principle': 'International transfers',
                    'description': f'Invalid safeguards for transfer to {destination}',
                    'risk_level': 'high',
                    'article': 'Chapter V'
                })
        else:
            violations.append({
                'principle': 'International transfers',
                'description': f'No adequacy decision or safeguards for transfer to {destination}',
                'risk_level': 'high',
                'article': 'Article 44'
            })
    
    return compliant_transfers / len(cross_border_transfers)


def _assess_data_retention(personal_data_inventory: Dict, processing_activities: List, 
                          violations: List) -> float:
    """Assess data retention compliance."""
    
    if not processing_activities:
        return 0.0
    
    compliant_activities = 0
    for activity in processing_activities:
        retention_period = activity.get('retention_period')
        
        if retention_period:
            # Check if retention period is justified
            if activity.get('retention_justification'):
                compliant_activities += 1
            else:
                violations.append({
                    'principle': 'Data retention',
                    'description': f'Retention period not justified for activity: {activity.get("activity_name", "Unknown")}',
                    'risk_level': 'medium',
                    'article': 'Article 5(1)(e)'
                })
        else:
            violations.append({
                'principle': 'Data retention',
                'description': f'No retention period defined for activity: {activity.get("activity_name", "Unknown")}',
                'risk_level': 'medium',
                'article': 'Article 5(1)(e)'
            })
    
    return compliant_activities / len(processing_activities)


def _conduct_privacy_risk_assessment(personal_data_inventory: Dict, processing_activities: List, 
                                    violations: List) -> Dict:
    """Conduct privacy impact risk assessment."""
    
    risk_factors = {
        'special_categories': 0,
        'large_scale_processing': 0,
        'vulnerable_subjects': 0,
        'new_technologies': 0,
        'automated_decision_making': 0
    }
    
    # Check for special categories of data
    special_categories = personal_data_inventory.get('special_categories', [])
    if special_categories:
        risk_factors['special_categories'] = len(special_categories)
    
    # Check for large scale processing
    total_subjects = sum(activity.get('data_subjects_count', 0) for activity in processing_activities)
    if total_subjects > 1000:  # Arbitrary threshold for large scale
        risk_factors['large_scale_processing'] = 1
    
    # Check for vulnerable subjects (e.g., children, patients)
    for activity in processing_activities:
        if activity.get('involves_vulnerable_subjects', False):
            risk_factors['vulnerable_subjects'] += 1
    
    # Check for new technologies
    for activity in processing_activities:
        if activity.get('uses_new_technology', False):
            risk_factors['new_technologies'] += 1
    
    # Check for automated decision making
    for activity in processing_activities:
        if activity.get('automated_decision_making', False):
            risk_factors['automated_decision_making'] += 1
    
    # Calculate overall risk level
    total_risk_score = sum(risk_factors.values())
    
    if total_risk_score >= 5:
        risk_level = 'high'
        dpia_required = True
    elif total_risk_score >= 3:
        risk_level = 'medium'
        dpia_required = True
    else:
        risk_level = 'low'
        dpia_required = False
    
    return {
        'risk_factors': risk_factors,
        'total_risk_score': total_risk_score,
        'risk_level': risk_level,
        'dpia_required': dpia_required,
        'high_risk_violations': len([v for v in violations if v.get('risk_level') == 'high'])
    }


def _generate_gdpr_recommendations(violations: List, gdpr_assessment: Dict) -> List[str]:
    """Generate specific GDPR compliance recommendations."""
    
    recommendations = []
    
    # High priority recommendations
    high_risk_violations = [v for v in violations if v.get('risk_level') == 'high']
    if high_risk_violations:
        recommendations.append(f'Address {len(high_risk_violations)} high-risk GDPR violations immediately')
    
    # Principle-specific recommendations
    non_compliant_principles = [name for name, principle in gdpr_assessment.get('principles', {}).items() 
                               if not principle['compliant']]
    
    if 'lawfulness_fairness_transparency' in non_compliant_principles:
        recommendations.append('Document lawful basis for all data processing activities')
    
    if 'purpose_limitation' in non_compliant_principles:
        recommendations.append('Define specific purposes for all data processing activities')
    
    if 'data_minimisation' in non_compliant_principles:
        recommendations.append('Conduct data minimisation assessment for all processing')
    
    if 'storage_limitation' in non_compliant_principles:
        recommendations.append('Implement data retention policies with defined retention periods')
    
    # General recommendations
    if len(violations) > 10:
        recommendations.append('Consider comprehensive GDPR compliance audit and remediation project')
    
    recommendations.append('Implement regular GDPR compliance monitoring and assessment procedures')
    
    if not recommendations:
        recommendations.append('GDPR compliance appears satisfactory - maintain current practices')
    
    return recommendations