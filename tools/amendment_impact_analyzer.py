"""
Protocol Amendment Impact Analyzer

Assesses the impact of protocol amendments on study conduct.
"""

from typing import Dict, Any, List


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes the impact of protocol amendments on study conduct and timeline.
    
    Example:
        Input: Amendment data with type, list of changes, enrollment numbers, and site count
        Output: Impact analysis with severity assessment, timeline delays, and implementation recommendations
    
    Parameters:
        amendment_type : str
            Type of amendment (substantial, minor, administrative)
        changes : list
            List of change descriptions
        current_enrollment : int
            Number of subjects currently enrolled
        total_target : int
            Target enrollment for the study
        sites_activated : int
            Number of sites currently activated
    """
    
    amendment_type = input_data.get('amendment_type', 'minor')
    changes = input_data.get('changes', [])
    current_enrollment = input_data.get('current_enrollment', 0)
    total_target = input_data.get('total_target', 100)
    sites_activated = input_data.get('sites_activated', 1)
    
    # Analyze each change
    change_impacts = []
    for change in changes:
        impact = _assess_change_impact(change, current_enrollment, total_target)
        change_impacts.append(impact)
    
    # Calculate overall impact
    overall_impact = _calculate_overall_impact(change_impacts, amendment_type)
    
    # Generate recommendations
    recommendations = _generate_recommendations(
        overall_impact, current_enrollment, total_target, sites_activated
    )
    
    # Estimate timeline impact
    timeline_impact = _estimate_timeline_impact(overall_impact, sites_activated)
    
    return {
        'change_impacts': change_impacts,
        'overall_impact': overall_impact,
        'recommendations': recommendations,
        'timeline_impact': timeline_impact,
        'requires_irb_approval': overall_impact.get('severity', 'minimal') != 'minimal',
        'requires_fda_submission': overall_impact.get('severity', 'minimal') == 'major',
        'affected_subjects': {
            'enrolled': current_enrollment,
            'percentage': (current_enrollment / total_target * 100) if total_target > 0 else 0
        }
    }


def _assess_change_impact(change: str, current_enrollment: int, total_target: int) -> Dict:
    """Assess impact of individual change."""
    
    change_lower = change.lower()
    
    # Determine category and severity
    if any(term in change_lower for term in ['inclusion', 'exclusion', 'eligibility']):
        category = 'eligibility'
        severity = 'major' if current_enrollment > 0 else 'moderate'
        requires_reconsent = current_enrollment > 0
    elif any(term in change_lower for term in ['safety', 'risk', 'adverse']):
        category = 'safety'
        severity = 'major'
        requires_reconsent = True
    elif any(term in change_lower for term in ['dose', 'dosing', 'administration']):
        category = 'treatment'
        severity = 'major'
        requires_reconsent = True
    elif any(term in change_lower for term in ['visit', 'schedule', 'procedure']):
        category = 'procedures'
        severity = 'moderate'
        requires_reconsent = False
    elif any(term in change_lower for term in ['endpoint', 'primary', 'outcome']):
        category = 'endpoints'
        severity = 'major'
        requires_reconsent = False
    else:
        category = 'administrative'
        severity = 'minimal'
        requires_reconsent = False
    
    return {
        'change_description': change,
        'category': category,
        'severity': severity,
        'requires_reconsent': requires_reconsent,
        'training_required': severity in ['major', 'moderate'],
        'database_changes': category in ['procedures', 'endpoints', 'eligibility'],
        'affects_enrolled': requires_reconsent
    }


def _calculate_overall_impact(change_impacts: List[Dict], amendment_type: str) -> Dict:
    """Calculate overall amendment impact."""
    
    if not change_impacts:
        return {
            'severity': 'minimal',
            'complexity': 'low',
            'risk_level': 'low'
        }
    
    # Get highest severity
    severities = [c['severity'] for c in change_impacts]
    severity_order = {'minimal': 0, 'moderate': 1, 'major': 2}
    max_severity_idx = max(severity_order[s] for s in severities)
    overall_severity = ['minimal', 'moderate', 'major'][max_severity_idx]
    
    # Calculate complexity
    requires_reconsent = any(c['requires_reconsent'] for c in change_impacts)
    requires_training = any(c['training_required'] for c in change_impacts)
    database_changes = any(c['database_changes'] for c in change_impacts)
    
    complexity_score = sum([requires_reconsent, requires_training, database_changes])
    complexity = 'high' if complexity_score >= 2 else 'moderate' if complexity_score >= 1 else 'low'
    
    # Assess risk
    risk_level = 'high' if overall_severity == 'major' else 'moderate' if complexity == 'high' else 'low'
    
    return {
        'severity': overall_severity,
        'complexity': complexity,
        'risk_level': risk_level,
        'requires_reconsent': requires_reconsent,
        'requires_training': requires_training,
        'database_changes': database_changes,
        'total_changes': len(change_impacts)
    }


def _generate_recommendations(overall_impact: Dict, current_enrollment: int, 
                             total_target: int, sites_activated: int) -> List[str]:
    """Generate recommendations based on impact analysis."""
    
    recommendations = []
    
    if overall_impact.get('requires_reconsent', False):
        recommendations.append(
            f"Obtain re-consent from {current_enrollment} enrolled subjects before implementing changes"
        )
    
    if overall_impact.get('requires_training', False):
        recommendations.append(
            f"Conduct training for all {sites_activated} active sites before implementation"
        )
    
    if overall_impact.get('database_changes', False):
        recommendations.append(
            "Update EDC system and test changes before deployment"
        )
    
    if overall_impact.get('severity', 'minimal') == 'major':
        recommendations.append(
            "Submit amendment to FDA and await approval before implementation"
        )
        recommendations.append(
            "Consider impact on statistical power and sample size"
        )
    
    if current_enrollment > total_target * 0.75:
        recommendations.append(
            "Consider delaying implementation until study completion due to high enrollment"
        )
    
    if overall_impact.get('risk_level', 'low') == 'high':
        recommendations.append(
            "Develop detailed implementation plan with risk mitigation strategies"
        )
    
    if not recommendations:
        recommendations.append(
            "Amendment has minimal impact. Proceed with standard implementation process."
        )
    
    return recommendations


def _estimate_timeline_impact(overall_impact: Dict, sites_activated: int) -> Dict:
    """Estimate timeline impact of amendment."""
    
    base_days = 0
    
    # IRB approval time
    if overall_impact.get('severity', 'minimal') != 'minimal':
        base_days += 30  # IRB review
    
    # FDA review time
    if overall_impact.get('severity', 'minimal') == 'major':
        base_days += 60  # FDA review
    
    # Training time
    if overall_impact.get('requires_training', False):
        base_days += max(14, sites_activated * 2)  # Training rollout
    
    # Database changes
    if overall_impact.get('database_changes', False):
        base_days += 21  # EDC updates and testing
    
    # Re-consent process
    if overall_impact.get('requires_reconsent', False):
        base_days += 30  # Re-consent period
    
    return {
        'estimated_delay_days': base_days,
        'estimated_delay_weeks': round(base_days / 7, 1),
        'critical_path_items': [
            item for item, required in [
                ('FDA approval', overall_impact.get('severity', 'minimal') == 'major'),
                ('IRB approval', overall_impact.get('severity', 'minimal') != 'minimal'),
                ('Site training', overall_impact.get('requires_training', False)),
                ('Database updates', overall_impact.get('database_changes', False)),
                ('Re-consent', overall_impact.get('requires_reconsent', False))
            ] if required
        ]
    }
