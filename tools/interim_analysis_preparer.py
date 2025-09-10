"""
Interim Analysis Preparer

Prepares data for interim analyses with appropriate data cuts and unblinding rules.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare data for interim analyses with appropriate data cuts and unblinding rules.
    
    Example:
        Input: Analysis type, enrollment status, data cutoff date, and unblinding requirements
        Output: Prepared interim analysis plan with stopping boundaries, data subsets, and recommendations
    
    Parameters:
        analysis_type : str
            Type of interim analysis: 'safety', 'efficacy', or 'futility'
        data_cutoff_date : str
            Date for data cutoff in YYYY-MM-DD format
        n_enrolled : int
            Number of subjects currently enrolled
        target_enrollment : int
            Target total enrollment for the study
        unblinding_level : str
            Level of unblinding: 'fully_blinded', 'partially_unblinded', 'unblinded'
        subjects_data : list, optional
            Subject data for analysis preparation
    """
    
    analysis_type = input_data.get('analysis_type', 'safety')
    cutoff_date = input_data.get('data_cutoff_date', datetime.now().strftime('%Y-%m-%d'))
    n_enrolled = input_data.get('n_enrolled', 0)
    target_enrollment = input_data.get('target_enrollment', 100)
    unblinding_level = input_data.get('unblinding_level', 'fully_blinded')
    
    # Calculate information fraction
    information_fraction = n_enrolled / target_enrollment if target_enrollment > 0 else 0
    
    # Determine analysis readiness
    readiness = _assess_readiness(analysis_type, information_fraction, n_enrolled)
    
    # Prepare data subsets
    data_subsets = _prepare_data_subsets(analysis_type, input_data.get('subjects_data', []))
    
    # Generate analysis plan
    analysis_plan = _generate_analysis_plan(analysis_type, information_fraction)
    
    # Calculate stopping boundaries
    stopping_boundaries = _calculate_stopping_boundaries(
        analysis_type, information_fraction, input_data
    )
    
    # Generate recommendations
    recommendations = _generate_recommendations(
        analysis_type, information_fraction, readiness
    )
    
    return {
        'analysis_type': analysis_type,
        'data_cutoff_date': cutoff_date,
        'enrollment_status': {
            'enrolled': n_enrolled,
            'target': target_enrollment,
            'information_fraction': round(information_fraction, 3),
            'percentage_complete': round(information_fraction * 100, 1)
        },
        'readiness': readiness,
        'data_subsets': data_subsets,
        'analysis_plan': analysis_plan,
        'stopping_boundaries': stopping_boundaries,
        'unblinding_level': unblinding_level,
        'recommendations': recommendations
    }


def _assess_readiness(analysis_type: str, info_frac: float, n_enrolled: int) -> Dict:
    """Assess readiness for interim analysis."""
    
    readiness = {
        'is_ready': False,
        'criteria_met': [],
        'criteria_not_met': [],
        'warnings': []
    }
    
    # Check enrollment criteria
    if analysis_type == 'safety':
        min_subjects = 20
        min_info_frac = 0.1
    elif analysis_type == 'efficacy':
        min_subjects = 50
        min_info_frac = 0.5
    else:  # futility
        min_subjects = 30
        min_info_frac = 0.3
    
    if n_enrolled >= min_subjects:
        readiness['criteria_met'].append(f'Minimum subjects enrolled ({n_enrolled} >= {min_subjects})')
    else:
        readiness['criteria_not_met'].append(f'Insufficient subjects ({n_enrolled} < {min_subjects})')
    
    if info_frac >= min_info_frac:
        readiness['criteria_met'].append(f'Information fraction adequate ({info_frac:.1%} >= {min_info_frac:.1%})')
    else:
        readiness['criteria_not_met'].append(f'Information fraction too low ({info_frac:.1%} < {min_info_frac:.1%})')
    
    readiness['is_ready'] = len(readiness['criteria_not_met']) == 0
    
    # Add warnings
    if info_frac > 0.75 and analysis_type == 'futility':
        readiness['warnings'].append('Late futility analysis may have limited value')
    
    return readiness


def _prepare_data_subsets(analysis_type: str, subjects_data: List) -> Dict:
    """Prepare appropriate data subsets for analysis."""
    
    subsets = {
        'safety_population': 'All subjects who received at least one dose',
        'itt_population': 'All randomized subjects',
        'per_protocol_population': 'All subjects without major protocol deviations'
    }
    
    if analysis_type == 'safety':
        subsets['primary_analysis_set'] = 'safety_population'
        subsets['required_data'] = [
            'Demographics',
            'Adverse events',
            'Laboratory results',
            'Vital signs',
            'Concomitant medications'
        ]
    elif analysis_type == 'efficacy':
        subsets['primary_analysis_set'] = 'itt_population'
        subsets['required_data'] = [
            'Primary endpoint data',
            'Secondary endpoints',
            'Protocol deviations',
            'Treatment compliance'
        ]
    else:  # futility
        subsets['primary_analysis_set'] = 'itt_population'
        subsets['required_data'] = [
            'Primary endpoint data',
            'Enrollment trends',
            'Early terminations'
        ]
    
    return subsets


def _generate_analysis_plan(analysis_type: str, info_frac: float) -> Dict:
    """Generate analysis plan based on type and timing."""
    
    plan = {
        'statistical_methods': [],
        'comparisons': [],
        'adjustments': [],
        'output_requirements': []
    }
    
    if analysis_type == 'safety':
        plan['statistical_methods'] = [
            'Descriptive statistics for AEs',
            'Incidence rates by treatment group',
            'Fisher exact test for SAE comparison'
        ]
        plan['comparisons'] = [
            'Treatment vs Control AE rates',
            'Laboratory shift tables',
            'Vital signs change from baseline'
        ]
        plan['output_requirements'] = [
            'Safety summary tables',
            'Listing of SAEs',
            'Laboratory outlier listing'
        ]
        
    elif analysis_type == 'efficacy':
        plan['statistical_methods'] = [
            'Primary endpoint analysis with alpha adjustment',
            'Conditional power calculation',
            'Predictive probability of success'
        ]
        plan['comparisons'] = [
            'Primary endpoint between groups',
            'Key secondary endpoints',
            'Subgroup analyses (if planned)'
        ]
        plan['adjustments'] = [
            f'Alpha spending: O\'Brien-Fleming boundary at {info_frac:.1%}'
        ]
        plan['output_requirements'] = [
            'Efficacy summary tables',
            'Forest plots',
            'Conditional power curves'
        ]
        
    else:  # futility
        plan['statistical_methods'] = [
            'Conditional power calculation',
            'Predictive probability',
            'Trend analysis'
        ]
        plan['comparisons'] = [
            'Observed vs expected effect size',
            'Enrollment rate analysis'
        ]
        plan['output_requirements'] = [
            'Futility assessment report',
            'Probability of success estimates',
            'Enrollment projections'
        ]
    
    return plan


def _calculate_stopping_boundaries(analysis_type: str, info_frac: float, input_data: Dict) -> Dict:
    """Calculate stopping boundaries for interim analysis."""
    
    import math
    
    boundaries = {
        'method': 'O\'Brien-Fleming' if analysis_type == 'efficacy' else 'Pocock',
        'nominal_alpha': 0.025,
        'cumulative_alpha_spent': 0,
        'boundaries': {}
    }
    
    if analysis_type == 'efficacy':
        # O'Brien-Fleming boundaries
        z_final = 1.96  # Two-sided 0.05
        if info_frac > 0:
            z_interim = z_final / math.sqrt(info_frac)
            boundaries['boundaries'] = {
                'efficacy_z_score': round(z_interim, 3),
                'efficacy_p_value': round(0.025 * info_frac, 4),
                'reject_null_if': f'Z > {z_interim:.3f}'
            }
            boundaries['cumulative_alpha_spent'] = round(0.025 * info_frac, 4)
    
    elif analysis_type == 'futility':
        # Futility boundary based on conditional power
        boundaries['boundaries'] = {
            'futility_cp_threshold': 0.20,  # Stop if CP < 20%
            'futility_pp_threshold': 0.10,  # Stop if PP < 10%
            'stop_for_futility_if': 'Conditional power < 20% or Predictive probability < 10%'
        }
    
    else:  # safety
        # Safety stopping guidelines
        boundaries['boundaries'] = {
            'safety_stopping_rules': [
                'Predefined SAE rate threshold exceeded',
                'DSMB recommendation',
                'Regulatory requirement'
            ],
            'review_triggers': [
                'SAE rate difference > 5%',
                'Grade 3+ AE rate > 30%',
                'Treatment-related death'
            ]
        }
    
    return boundaries


def _generate_recommendations(analysis_type: str, info_frac: float, readiness: Dict) -> List[str]:
    """Generate recommendations for interim analysis."""
    
    recommendations = []
    
    if not readiness['is_ready']:
        recommendations.append('Continue enrollment before conducting interim analysis')
        return recommendations
    
    if analysis_type == 'safety':
        recommendations.append('Prepare unblinded safety data for DSMB review')
        recommendations.append('Include all safety data through cutoff date')
        recommendations.append('Ensure medical coding is complete for AEs')
        
    elif analysis_type == 'efficacy':
        recommendations.append('Maintain trial integrity with minimal unblinding')
        recommendations.append('Calculate conditional power for various effect sizes')
        if info_frac < 0.75:
            recommendations.append('Consider sample size re-estimation if allowed')
        
    else:  # futility
        recommendations.append('Assess both statistical and operational futility')
        recommendations.append('Consider enrollment trends and site performance')
        if info_frac > 0.5:
            recommendations.append('Evaluate cost-benefit of continuing vs early termination')
    
    # General recommendations
    recommendations.append('Document all decisions and rationale')
    recommendations.append('Prepare contingency plans for all possible outcomes')
    
    return recommendations
