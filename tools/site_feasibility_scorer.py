"""
Site Feasibility Scorer

Scores potential clinical trial sites based on various criteria.
"""

from typing import Dict, Any, List


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score sites based on feasibility criteria.
    
    Args:
        input_data: Dictionary containing:
            - sites: list of site dictionaries with attributes
            - criteria_weights: dict of weight for each criterion
    
    Returns:
        Dictionary with scored and ranked sites
    """
    
    sites = input_data.get('sites', [])
    weights = input_data.get('criteria_weights', _get_default_weights())
    
    if not sites:
        return {'error': 'No sites provided for scoring'}
    
    scored_sites = []
    for site in sites:
        score_details = _calculate_site_score(site, weights)
        scored_sites.append({
            'site_id': site.get('site_id', 'Unknown'),
            'site_name': site.get('name', 'Unknown'),
            'total_score': score_details['total'],
            'score_breakdown': score_details['breakdown'],
            'recommendation': _get_recommendation(score_details['total']),
            'site_data': site
        })
    
    # Sort by score
    scored_sites.sort(key=lambda x: x['total_score'], reverse=True)
    
    return {
        'ranked_sites': scored_sites,
        'top_sites': scored_sites[:5] if len(scored_sites) >= 5 else scored_sites,
        'criteria_used': weights,
        'summary': {
            'total_sites_evaluated': len(sites),
            'recommended_sites': len([s for s in scored_sites if s['total_score'] >= 70]),
            'average_score': sum(s['total_score'] for s in scored_sites) / len(scored_sites)
        }
    }


def _get_default_weights() -> Dict:
    """Get default criteria weights."""
    return {
        'patient_population': 0.25,
        'enrollment_history': 0.20,
        'investigator_experience': 0.15,
        'facility_capabilities': 0.15,
        'regulatory_compliance': 0.10,
        'geographic_location': 0.10,
        'competing_studies': 0.05
    }


def _calculate_site_score(site: Dict, weights: Dict) -> Dict:
    """Calculate score for a single site."""
    scores = {}
    
    # Patient population score (0-100)
    patient_pop = site.get('patient_population', 0)
    scores['patient_population'] = min(100, patient_pop / 10) if patient_pop else 0
    
    # Enrollment history score
    past_enrollment = site.get('past_enrollment_rate', 0)
    scores['enrollment_history'] = min(100, past_enrollment * 10) if past_enrollment else 50
    
    # Investigator experience
    pi_studies = site.get('pi_previous_studies', 0)
    scores['investigator_experience'] = min(100, pi_studies * 5) if pi_studies else 0
    
    # Facility capabilities
    has_equipment = site.get('has_required_equipment', False)
    has_staff = site.get('adequate_staff', False)
    scores['facility_capabilities'] = 50 * has_equipment + 50 * has_staff
    
    # Regulatory compliance
    gcp_trained = site.get('gcp_trained', False)
    no_violations = site.get('no_recent_violations', True)
    scores['regulatory_compliance'] = 50 * gcp_trained + 50 * no_violations
    
    # Geographic location
    urban = site.get('urban_location', False)
    accessible = site.get('accessible', True)
    scores['geographic_location'] = 50 * urban + 50 * accessible
    
    # Competing studies
    competing = site.get('competing_studies', 0)
    scores['competing_studies'] = max(0, 100 - competing * 20)
    
    # Calculate weighted total
    total = sum(scores.get(criterion, 0) * weight 
               for criterion, weight in weights.items())
    
    return {
        'total': round(total, 1),
        'breakdown': scores
    }


def _get_recommendation(score: float) -> str:
    """Get recommendation based on score."""
    if score >= 80:
        return 'Highly Recommended'
    elif score >= 70:
        return 'Recommended'
    elif score >= 60:
        return 'Acceptable'
    elif score >= 50:
        return 'Marginal'
    else:
        return 'Not Recommended'
