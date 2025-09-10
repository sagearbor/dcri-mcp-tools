from typing import Dict, Any, List
from datetime import datetime, timedelta


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audit clinical trial processes against ICH-GCP requirements and identify compliance gaps.
    
    Example:
        Input: Site data with audit areas like protocol compliance, consent management, and documentation practices
        Output: Compliance assessment with scores, findings, recommendations, and risk level classification
    
    Parameters:
        audit_areas : list
            Areas to audit (e.g., 'protocol', 'consent', 'documentation')
        site_data : dict
            Site-specific information and compliance indicators
        findings : list, optional
            Previous audit findings to track repeat violations
        audit_type : str
            Type of audit: 'full', 'focused', or 'for_cause'
    """
    audit_areas = input_data.get('audit_areas', ['protocol', 'consent', 'documentation'])
    site_data = input_data.get('site_data', {})
    previous_findings = input_data.get('findings', [])
    audit_type = input_data.get('audit_type', 'full')
    
    findings = []
    critical_findings = []
    scores = {}
    
    # Audit each area
    for area in audit_areas:
        area_findings, area_score = _audit_area(area, site_data)
        findings.extend(area_findings)
        scores[area] = area_score
        
        # Identify critical findings
        critical = [f for f in area_findings if f.get('severity') == 'critical']
        critical_findings.extend(critical)
    
    # Calculate overall compliance score
    compliance_score = sum(scores.values()) / len(scores) if scores else 0
    
    # Determine risk level
    risk_level = _determine_risk_level(compliance_score, critical_findings)
    
    # Generate recommendations
    recommendations = _generate_recommendations(findings, critical_findings, risk_level)
    
    # Track repeat findings
    repeat_findings = _identify_repeat_findings(findings, previous_findings)
    
    return {
        'audit_type': audit_type,
        'compliance_score': round(compliance_score, 1),
        'findings': findings,
        'critical_findings': critical_findings,
        'repeat_findings': repeat_findings,
        'recommendations': recommendations,
        'risk_level': risk_level,
        'area_scores': scores,
        'summary': {
            'total_findings': len(findings),
            'critical_count': len(critical_findings),
            'repeat_count': len(repeat_findings),
            'areas_audited': len(audit_areas)
        }
    }


def _audit_area(area: str, site_data: Dict) -> tuple:
    """Audit a specific GCP area."""
    findings = []
    score = 100.0
    
    if area == 'protocol':
        # Check protocol compliance
        checks = [
            ('protocol_version', 'Current protocol version on file'),
            ('amendments_documented', 'All amendments properly documented'),
            ('deviations_reported', 'Protocol deviations reported within 24h'),
            ('inclusion_exclusion', 'I/E criteria consistently applied'),
            ('visit_windows', 'Visit windows adhered to')
        ]
        
        for check_id, description in checks:
            if not site_data.get(check_id, False):
                findings.append({
                    'area': 'protocol',
                    'finding': f"Non-compliance: {description}",
                    'severity': 'major' if 'deviations' in check_id else 'minor',
                    'gcp_reference': 'ICH-GCP 4.5'
                })
                score -= 10
                
    elif area == 'consent':
        # Check informed consent compliance
        checks = [
            ('consent_current', 'Using current IRB-approved version'),
            ('consent_signed', 'All subjects have signed consent'),
            ('consent_dated', 'Consent dated before procedures'),
            ('consent_witnessed', 'Witness signatures where required'),
            ('consent_copies', 'Copies provided to subjects'),
            ('reconsent_done', 'Re-consent for protocol amendments')
        ]
        
        for check_id, description in checks:
            if not site_data.get(check_id, False):
                severity = 'critical' if check_id in ['consent_signed', 'consent_dated'] else 'major'
                findings.append({
                    'area': 'consent',
                    'finding': f"Non-compliance: {description}",
                    'severity': severity,
                    'gcp_reference': 'ICH-GCP 4.8'
                })
                score -= 15 if severity == 'critical' else 10
                
    elif area == 'documentation':
        # Check documentation practices
        checks = [
            ('source_documented', 'Source documents complete'),
            ('alcoa_compliance', 'ALCOA+ principles followed'),
            ('corrections_proper', 'Corrections single line-through'),
            ('signatures_current', 'Signature logs up to date'),
            ('crf_complete', 'CRFs completed timely'),
            ('queries_resolved', 'Data queries resolved promptly')
        ]
        
        for check_id, description in checks:
            if not site_data.get(check_id, False):
                findings.append({
                    'area': 'documentation',
                    'finding': f"Non-compliance: {description}",
                    'severity': 'major' if 'alcoa' in check_id else 'minor',
                    'gcp_reference': 'ICH-GCP 4.9'
                })
                score -= 8
                
    elif area == 'investigator':
        # Check investigator responsibilities
        checks = [
            ('qualified_staff', 'Staff qualified and trained'),
            ('delegation_log', 'Delegation log current'),
            ('cv_current', 'CVs and licenses current'),
            ('training_documented', 'GCP training documented'),
            ('oversight_adequate', 'PI oversight demonstrated')
        ]
        
        for check_id, description in checks:
            if not site_data.get(check_id, False):
                findings.append({
                    'area': 'investigator',
                    'finding': f"Non-compliance: {description}",
                    'severity': 'major',
                    'gcp_reference': 'ICH-GCP 4.1-4.2'
                })
                score -= 10
                
    elif area == 'drug_accountability':
        # Check drug accountability
        checks = [
            ('drug_storage', 'Proper storage conditions'),
            ('temp_monitoring', 'Temperature logs maintained'),
            ('accountability_logs', 'Drug accountability accurate'),
            ('expiry_tracking', 'Expiry dates monitored'),
            ('dispensing_records', 'Dispensing properly documented')
        ]
        
        for check_id, description in checks:
            if not site_data.get(check_id, False):
                severity = 'critical' if check_id == 'drug_storage' else 'major'
                findings.append({
                    'area': 'drug_accountability',
                    'finding': f"Non-compliance: {description}",
                    'severity': severity,
                    'gcp_reference': 'ICH-GCP 4.6'
                })
                score -= 12
                
    elif area == 'safety':
        # Check safety reporting
        checks = [
            ('ae_reporting', 'AEs reported per protocol'),
            ('sae_timeline', 'SAEs reported within 24h'),
            ('susar_reporting', 'SUSARs reported to authorities'),
            ('safety_database', 'Safety database current')
        ]
        
        for check_id, description in checks:
            if not site_data.get(check_id, False):
                severity = 'critical' if 'sae' in check_id or 'susar' in check_id else 'major'
                findings.append({
                    'area': 'safety',
                    'finding': f"Non-compliance: {description}",
                    'severity': severity,
                    'gcp_reference': 'ICH-GCP 4.11'
                })
                score -= 15 if severity == 'critical' else 10
    
    return findings, max(0, score)


def _determine_risk_level(compliance_score: float, critical_findings: List) -> str:
    """Determine overall risk level based on findings."""
    if critical_findings:
        return 'critical'
    elif compliance_score < 70:
        return 'high'
    elif compliance_score < 85:
        return 'medium'
    else:
        return 'low'


def _generate_recommendations(findings: List, critical_findings: List, 
                             risk_level: str) -> List[str]:
    """Generate corrective action recommendations."""
    recommendations = []
    
    if critical_findings:
        recommendations.append("IMMEDIATE ACTION REQUIRED for critical findings")
        recommendations.append("Suspend enrollment until critical issues resolved")
        recommendations.append("Notify sponsor and IRB within 24 hours")
    
    # Group findings by area
    areas_affected = set(f['area'] for f in findings)
    
    for area in areas_affected:
        area_findings = [f for f in findings if f['area'] == area]
        if area == 'consent':
            recommendations.append("Retrain staff on consent procedures")
            recommendations.append("Implement consent checklist")
        elif area == 'protocol':
            recommendations.append("Review protocol with all staff")
            recommendations.append("Implement deviation prevention plan")
        elif area == 'documentation':
            recommendations.append("Provide ALCOA+ training")
            recommendations.append("Implement documentation QC process")
        elif area == 'safety':
            recommendations.append("Review safety reporting timelines")
            recommendations.append("Implement safety event tracking log")
    
    if risk_level in ['high', 'critical']:
        recommendations.append("Schedule follow-up audit within 30 days")
        recommendations.append("Develop comprehensive CAPA plan")
    
    return recommendations


def _identify_repeat_findings(current_findings: List, previous_findings: List) -> List:
    """Identify findings that are repeats from previous audits."""
    repeat_findings = []
    
    for current in current_findings:
        for previous in previous_findings:
            if (current.get('area') == previous.get('area') and 
                current.get('finding') == previous.get('finding')):
                repeat_findings.append({
                    **current,
                    'repeat': True,
                    'escalated_severity': True
                })
    
    return repeat_findings