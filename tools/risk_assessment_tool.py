"""
Risk Assessment Tool for RBQM

Risk-Based Quality Management categorization tool.
"""

from typing import Dict, Any, List


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform risk assessment for RBQM.
    
    Args:
        input_data: Dictionary with risk factors
    
    Returns:
        Dictionary with risk assessment results
    """
    
    # Assess different risk categories
    safety_risks = _assess_safety_risks(input_data)
    data_risks = _assess_data_risks(input_data)
    operational_risks = _assess_operational_risks(input_data)
    regulatory_risks = _assess_regulatory_risks(input_data)
    
    # Calculate overall risk score
    all_risks = safety_risks + data_risks + operational_risks + regulatory_risks
    
    # Categorize risks
    high_risks = [r for r in all_risks if r['severity'] == 'high']
    medium_risks = [r for r in all_risks if r['severity'] == 'medium']
    low_risks = [r for r in all_risks if r['severity'] == 'low']
    
    # Generate mitigation strategies
    mitigation_plan = _generate_mitigation_plan(high_risks + medium_risks)
    
    # Calculate overall risk level
    if len(high_risks) > 2 or (len(high_risks) > 0 and len(medium_risks) > 3):
        overall_level = 'High'
    elif len(high_risks) > 0 or len(medium_risks) > 2:
        overall_level = 'Medium'
    else:
        overall_level = 'Low'
    
    return {
        'overall_risk_level': overall_level,
        'risk_summary': {
            'high': len(high_risks),
            'medium': len(medium_risks),
            'low': len(low_risks),
            'total': len(all_risks)
        },
        'risks_by_category': {
            'safety': safety_risks,
            'data_integrity': data_risks,
            'operational': operational_risks,
            'regulatory': regulatory_risks
        },
        'high_priority_risks': high_risks,
        'mitigation_plan': mitigation_plan,
        'monitoring_recommendations': _generate_monitoring_recommendations(all_risks)
    }


def _assess_safety_risks(data: Dict) -> List[Dict]:
    """Assess safety-related risks."""
    risks = []
    
    # Check for high-risk intervention
    if data.get('first_in_human', False):
        risks.append({
            'risk': 'First-in-human study',
            'category': 'safety',
            'severity': 'high',
            'impact': 'critical',
            'likelihood': 'possible'
        })
    
    if data.get('vulnerable_population', False):
        risks.append({
            'risk': 'Vulnerable population',
            'category': 'safety',
            'severity': 'high',
            'impact': 'major',
            'likelihood': 'likely'
        })
    
    if data.get('invasive_procedures', False):
        risks.append({
            'risk': 'Invasive procedures',
            'category': 'safety',
            'severity': 'medium',
            'impact': 'moderate',
            'likelihood': 'possible'
        })
    
    return risks


def _assess_data_risks(data: Dict) -> List[Dict]:
    """Assess data integrity risks."""
    risks = []
    
    if data.get('complex_endpoints', False):
        risks.append({
            'risk': 'Complex endpoint assessment',
            'category': 'data_integrity',
            'severity': 'medium',
            'impact': 'major',
            'likelihood': 'likely'
        })
    
    if data.get('subjective_assessments', False):
        risks.append({
            'risk': 'Subjective outcome measures',
            'category': 'data_integrity',
            'severity': 'medium',
            'impact': 'moderate',
            'likelihood': 'likely'
        })
    
    if data.get('multiple_data_sources', False):
        risks.append({
            'risk': 'Multiple data source integration',
            'category': 'data_integrity',
            'severity': 'low',
            'impact': 'minor',
            'likelihood': 'possible'
        })
    
    return risks


def _assess_operational_risks(data: Dict) -> List[Dict]:
    """Assess operational risks."""
    risks = []
    
    if data.get('inexperienced_sites', False):
        risks.append({
            'risk': 'Sites with limited experience',
            'category': 'operational',
            'severity': 'medium',
            'impact': 'moderate',
            'likelihood': 'likely'
        })
    
    if data.get('recruitment_challenges', False):
        risks.append({
            'risk': 'Difficult recruitment',
            'category': 'operational',
            'severity': 'medium',
            'impact': 'major',
            'likelihood': 'very_likely'
        })
    
    if data.get('supply_chain_complexity', False):
        risks.append({
            'risk': 'Complex supply chain',
            'category': 'operational',
            'severity': 'low',
            'impact': 'moderate',
            'likelihood': 'possible'
        })
    
    return risks


def _assess_regulatory_risks(data: Dict) -> List[Dict]:
    """Assess regulatory compliance risks."""
    risks = []
    
    if data.get('multiple_regulatory_bodies', False):
        risks.append({
            'risk': 'Multiple regulatory jurisdictions',
            'category': 'regulatory',
            'severity': 'medium',
            'impact': 'major',
            'likelihood': 'possible'
        })
    
    if data.get('novel_therapy', False):
        risks.append({
            'risk': 'Novel therapy regulatory pathway',
            'category': 'regulatory',
            'severity': 'high',
            'impact': 'critical',
            'likelihood': 'possible'
        })
    
    return risks


def _generate_mitigation_plan(risks: List[Dict]) -> List[Dict]:
    """Generate mitigation strategies for identified risks."""
    mitigation_strategies = []
    
    for risk in risks:
        strategy = {
            'risk': risk['risk'],
            'mitigation_actions': [],
            'monitoring_approach': '',
            'responsible_party': ''
        }
        
        # Determine mitigation based on risk type
        if risk['category'] == 'safety':
            strategy['mitigation_actions'] = [
                'Implement enhanced safety monitoring',
                'Increase frequency of safety reviews',
                'Establish clear stopping rules'
            ]
            strategy['monitoring_approach'] = 'Real-time safety data review'
            strategy['responsible_party'] = 'Medical Monitor'
            
        elif risk['category'] == 'data_integrity':
            strategy['mitigation_actions'] = [
                'Implement source data verification',
                'Provide additional training',
                'Increase monitoring frequency'
            ]
            strategy['monitoring_approach'] = 'Centralized statistical monitoring'
            strategy['responsible_party'] = 'Data Management Team'
            
        elif risk['category'] == 'operational':
            strategy['mitigation_actions'] = [
                'Provide intensive site support',
                'Implement recruitment support strategies',
                'Develop contingency plans'
            ]
            strategy['monitoring_approach'] = 'Weekly metrics review'
            strategy['responsible_party'] = 'Clinical Operations'
            
        elif risk['category'] == 'regulatory':
            strategy['mitigation_actions'] = [
                'Early regulatory consultation',
                'Develop comprehensive regulatory strategy',
                'Ensure proper documentation'
            ]
            strategy['monitoring_approach'] = 'Regulatory milestone tracking'
            strategy['responsible_party'] = 'Regulatory Affairs'
        
        mitigation_strategies.append(strategy)
    
    return mitigation_strategies


def _generate_monitoring_recommendations(risks: List[Dict]) -> List[str]:
    """Generate monitoring recommendations based on risks."""
    recommendations = []
    
    # Count risks by severity
    high_count = len([r for r in risks if r['severity'] == 'high'])
    medium_count = len([r for r in risks if r['severity'] == 'medium'])
    
    if high_count > 0:
        recommendations.append('Implement enhanced monitoring for high-risk areas')
        recommendations.append('Establish risk review committee with weekly meetings')
    
    if medium_count > 2:
        recommendations.append('Use centralized monitoring for efficiency')
        recommendations.append('Develop key risk indicators (KRIs) dashboard')
    
    # Category-specific recommendations
    categories = set(r['category'] for r in risks)
    
    if 'safety' in categories:
        recommendations.append('Implement real-time safety data monitoring')
    
    if 'data_integrity' in categories:
        recommendations.append('Perform regular data quality checks')
    
    if 'operational' in categories:
        recommendations.append('Track site performance metrics closely')
    
    return recommendations
