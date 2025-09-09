"""
Study Complexity Calculator

Calculates ICH E6(R2) study complexity score.
"""

from typing import Dict, Any


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate study complexity score.
    
    Args:
        input_data: Dictionary with study characteristics
    
    Returns:
        Dictionary with complexity scores
    """
    
    # Calculate component scores
    design_score = _calculate_design_complexity(input_data)
    population_score = _calculate_population_complexity(input_data)
    intervention_score = _calculate_intervention_complexity(input_data)
    operational_score = _calculate_operational_complexity(input_data)
    
    # Calculate total score
    total_score = (design_score + population_score + 
                  intervention_score + operational_score) / 4
    
    # Determine complexity level
    if total_score >= 75:
        level = 'Very High'
    elif total_score >= 60:
        level = 'High'
    elif total_score >= 40:
        level = 'Moderate'
    else:
        level = 'Low'
    
    return {
        'total_score': round(total_score, 1),
        'complexity_level': level,
        'component_scores': {
            'design': design_score,
            'population': population_score,
            'intervention': intervention_score,
            'operational': operational_score
        },
        'recommendations': _generate_recommendations(total_score, level)
    }


def _calculate_design_complexity(data: Dict) -> float:
    """Calculate design complexity score."""
    score = 0
    
    # Study phase
    phase = data.get('phase', '2')
    phase_scores = {'1': 30, '2': 40, '3': 60, '4': 20, 'combined': 80}
    score += phase_scores.get(phase, 40)
    
    # Randomization
    if data.get('randomized', True):
        score += 10
    if data.get('adaptive_design', False):
        score += 20
    
    # Blinding
    blinding = data.get('blinding', 'open')
    blinding_scores = {'open': 0, 'single': 10, 'double': 20}
    score += blinding_scores.get(blinding, 0)
    
    # Multiple arms
    n_arms = data.get('n_treatment_arms', 2)
    if n_arms > 2:
        score += min(20, (n_arms - 2) * 5)
    
    return min(100, score)


def _calculate_population_complexity(data: Dict) -> float:
    """Calculate population complexity score."""
    score = 0
    
    # Vulnerable population
    if data.get('pediatric', False):
        score += 30
    if data.get('elderly', False):
        score += 20
    if data.get('pregnant_women', False):
        score += 40
    
    # Rare disease
    if data.get('rare_disease', False):
        score += 25
    
    # Comorbidities
    if data.get('multiple_comorbidities', False):
        score += 15
    
    # Geographic spread
    n_countries = data.get('n_countries', 1)
    if n_countries > 1:
        score += min(30, n_countries * 5)
    
    return min(100, score)


def _calculate_intervention_complexity(data: Dict) -> float:
    """Calculate intervention complexity score."""
    score = 0
    
    # Route of administration
    route = data.get('route_of_administration', 'oral')
    route_scores = {'oral': 10, 'injection': 30, 'infusion': 50, 'surgery': 80}
    score += route_scores.get(route, 20)
    
    # Combination therapy
    if data.get('combination_therapy', False):
        score += 20
    
    # Dose escalation
    if data.get('dose_escalation', False):
        score += 25
    
    # Special handling
    if data.get('cold_chain_required', False):
        score += 15
    if data.get('controlled_substance', False):
        score += 20
    
    return min(100, score)


def _calculate_operational_complexity(data: Dict) -> float:
    """Calculate operational complexity score."""
    score = 0
    
    # Number of visits
    n_visits = data.get('n_visits', 5)
    score += min(30, n_visits * 2)
    
    # Special assessments
    if data.get('imaging_required', False):
        score += 15
    if data.get('central_lab', False):
        score += 10
    if data.get('biomarkers', False):
        score += 20
    if data.get('pharmacokinetics', False):
        score += 25
    
    # Data collection
    if data.get('epro', False):
        score += 10
    if data.get('wearables', False):
        score += 15
    
    return min(100, score)


def _generate_recommendations(score: float, level: str) -> list:
    """Generate recommendations based on complexity."""
    recommendations = []
    
    if level in ['Very High', 'High']:
        recommendations.append('Consider simplified protocol design where possible')
        recommendations.append('Implement robust risk-based quality management')
        recommendations.append('Ensure adequate site training and support')
        recommendations.append('Consider centralized monitoring approach')
    
    if score > 60:
        recommendations.append('Develop comprehensive training materials')
        recommendations.append('Plan for increased monitoring frequency')
    
    return recommendations
