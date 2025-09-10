from typing import Dict, Any, List
from datetime import datetime


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify and categorize protocol deviations by severity and regulatory impact.
    
    Example:
        Input: Protocol deviation description with date, subject, and safety impact information
        Output: Deviation classification with severity, category, reportability, and corrective actions
    
    Parameters:
        deviation_text : str
            Detailed description of the protocol deviation
        deviation_date : str
            Date when the deviation occurred
        subject_id : str, optional
            Subject identifier associated with the deviation
        visit_info : dict, optional
            Visit-related information and context
        safety_impact : bool, optional
            Whether the deviation had potential safety implications
    """
    deviation_text = input_data.get('deviation_text', '').lower()
    deviation_date = input_data.get('deviation_date', '')
    subject_id = input_data.get('subject_id', '')
    visit_info = input_data.get('visit_info', {})
    safety_impact = input_data.get('safety_impact', False)
    
    # Classify deviation
    classification = _classify_severity(deviation_text, safety_impact)
    category = _categorize_deviation(deviation_text)
    reportable = _determine_reportability(classification, category)
    
    # Assess impact
    impact = _assess_impact(classification, category, safety_impact)
    
    # Generate corrective actions
    corrective_actions = _generate_corrective_actions(classification, category)
    
    # Determine if systematic issue
    systematic = _check_systematic_issue(deviation_text)
    
    return {
        'classification': classification,
        'category': category,
        'reportable': reportable,
        'corrective_actions': corrective_actions,
        'impact_assessment': impact,
        'systematic_issue': systematic,
        'subject_id': subject_id,
        'deviation_date': deviation_date,
        'documentation_requirements': _get_documentation_requirements(classification),
        'notification_required': _get_notification_requirements(classification, reportable)
    }


def _classify_severity(text: str, safety_impact: bool) -> str:
    """Classify deviation severity."""
    critical_keywords = [
        'safety', 'sae', 'death', 'life-threatening', 'hospitalization',
        'unblinding', 'randomization error', 'wrong drug', 'overdose',
        'eligibility violation', 'no consent', 'ethics violation'
    ]
    
    major_keywords = [
        'missed visit', 'out of window', 'incorrect dose', 'missing data',
        'protocol violation', 'prohibited medication', 'assessment not done',
        'procedure omitted', 'wrong sequence'
    ]
    
    if safety_impact or any(keyword in text for keyword in critical_keywords):
        return 'critical'
    elif any(keyword in text for keyword in major_keywords):
        return 'major'
    else:
        return 'minor'


def _categorize_deviation(text: str) -> str:
    """Categorize type of deviation."""
    categories = {
        'enrollment': ['eligibility', 'inclusion', 'exclusion', 'enrollment', 'screening'],
        'consent': ['consent', 'icf', 'informed consent', 'assent'],
        'randomization': ['randomization', 'randomized', 'allocation', 'treatment assignment'],
        'dosing': ['dose', 'dosing', 'medication', 'drug', 'administration'],
        'visit_schedule': ['visit', 'window', 'schedule', 'appointment', 'missed'],
        'procedure': ['procedure', 'assessment', 'test', 'examination', 'sample'],
        'safety': ['ae', 'adverse', 'sae', 'safety', 'concomitant'],
        'data': ['data', 'crf', 'source', 'documentation', 'record'],
        'other': []
    }
    
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category
    
    return 'other'


def _determine_reportability(classification: str, category: str) -> bool:
    """Determine if deviation requires regulatory reporting."""
    if classification == 'critical':
        return True
    if classification == 'major' and category in ['enrollment', 'consent', 'randomization', 'safety']:
        return True
    return False


def _assess_impact(classification: str, category: str, safety_impact: bool) -> Dict:
    """Assess impact of deviation on trial."""
    impact = {
        'data_integrity': 'high' if classification in ['critical', 'major'] else 'low',
        'subject_safety': 'high' if safety_impact else 'low',
        'statistical_analysis': 'high' if category in ['enrollment', 'randomization'] else 'medium',
        'regulatory_compliance': 'high' if classification == 'critical' else 'medium',
        'overall_risk': classification
    }
    
    return impact


def _generate_corrective_actions(classification: str, category: str) -> List[str]:
    """Generate corrective action recommendations."""
    actions = []
    
    # Universal actions
    actions.append("Document deviation in subject file")
    actions.append("Complete deviation report form")
    
    # Classification-specific actions
    if classification == 'critical':
        actions.append("Notify sponsor within 24 hours")
        actions.append("Notify IRB/IEC if required")
        actions.append("Implement immediate corrective measures")
        actions.append("Consider subject discontinuation if safety impacted")
    elif classification == 'major':
        actions.append("Review with study team")
        actions.append("Implement preventive measures")
        actions.append("Monitor for recurrence")
    
    # Category-specific actions
    if category == 'consent':
        actions.append("Re-consent subject if possible")
        actions.append("Review consent process with staff")
    elif category == 'dosing':
        actions.append("Verify correct dosing going forward")
        actions.append("Review dosing calculations")
    elif category == 'visit_schedule':
        actions.append("Reschedule missed assessments if within acceptable window")
        actions.append("Document impact on endpoint assessment")
    
    return actions


def _check_systematic_issue(text: str) -> bool:
    """Check if deviation indicates systematic issue."""
    systematic_keywords = [
        'multiple', 'repeated', 'consistent', 'pattern', 'systematic',
        'widespread', 'all subjects', 'all sites', 'recurring'
    ]
    
    return any(keyword in text for keyword in systematic_keywords)


def _get_documentation_requirements(classification: str) -> List[str]:
    """Get documentation requirements based on classification."""
    requirements = ['Deviation log entry', 'Source documentation']
    
    if classification in ['critical', 'major']:
        requirements.extend([
            'Deviation report form',
            'Root cause analysis',
            'CAPA documentation'
        ])
    
    if classification == 'critical':
        requirements.extend([
            'Sponsor notification',
            'IRB/IEC notification (if applicable)',
            'Regulatory notification (if applicable)'
        ])
    
    return requirements


def _get_notification_requirements(classification: str, reportable: bool) -> Dict:
    """Get notification requirements."""
    notifications = {
        'sponsor': classification in ['critical', 'major'],
        'irb_iec': classification == 'critical' or reportable,
        'regulatory': reportable,
        'dsmb': classification == 'critical',
        'timeline': '24 hours' if classification == 'critical' else '7 days'
    }
    
    return notifications
