"""
Sample Size Calculator Tool for Clinical Trials

Calculates sample sizes for various clinical trial designs including:
- Two-sample comparisons (continuous, binary)
- Non-inferiority trials
- Superiority trials
- Crossover designs
"""

import math
from scipy import stats
from typing import Dict, Any, Optional


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate sample size for clinical trials with various designs and endpoint types.
    
    Example:
        Input: Study design parameters with effect size, power, and allocation ratio
        Output: Calculated sample size with power analysis and design recommendations
    
    Parameters:
        design_type : str
            Study design: 'superiority', 'non_inferiority', 'equivalence'
        outcome_type : str
            Primary endpoint type: 'continuous', 'binary', 'time_to_event'
        alpha : float, optional
            Type I error rate (default: 0.05)
        power : float, optional
            Statistical power (default: 0.8)
        effect_size : float
            Expected clinically meaningful effect size
        allocation_ratio : float, optional
            Ratio of treatment to control group (default: 1.0)
        dropout_rate : float, optional
            Expected dropout rate (default: 0.1)
            - mean_difference: float (Expected mean difference)
            - std_dev: float (Standard deviation)
            
            For binary outcomes:
            - control_rate: float (Event rate in control group)
            - treatment_rate: float (Event rate in treatment group)
            
            For non-inferiority:
            - margin: float (Non-inferiority margin)
    
    Returns:
        Dictionary containing:
            - sample_size_per_arm: int
            - total_sample_size: int
            - adjusted_for_dropout: int
            - calculation_details: dict
            - recommendations: list
    """
    
    design_type = input_data.get('design_type', 'superiority')
    outcome_type = input_data.get('outcome_type', 'continuous')
    alpha = input_data.get('alpha', 0.05)
    power = input_data.get('power', 0.8)
    allocation_ratio = input_data.get('allocation_ratio', 1)
    dropout_rate = input_data.get('dropout_rate', 0.1)
    
    try:
        if outcome_type == 'continuous':
            sample_size = _calculate_continuous_sample_size(
                input_data, design_type, alpha, power, allocation_ratio
            )
        elif outcome_type == 'binary':
            sample_size = _calculate_binary_sample_size(
                input_data, design_type, alpha, power, allocation_ratio
            )
        elif outcome_type == 'time_to_event':
            sample_size = _calculate_survival_sample_size(
                input_data, design_type, alpha, power, allocation_ratio
            )
        else:
            return {
                'error': f'Unsupported outcome type: {outcome_type}',
                'supported_types': ['continuous', 'binary', 'time_to_event']
            }
        
        # Adjust for dropout
        adjusted_size = math.ceil(sample_size / (1 - dropout_rate))
        
        # Calculate per-arm sizes
        n_control = math.ceil(adjusted_size / (1 + allocation_ratio))
        n_treatment = math.ceil(n_control * allocation_ratio)
        total_size = n_control + n_treatment
        
        # Generate recommendations
        recommendations = _generate_recommendations(
            design_type, outcome_type, total_size, dropout_rate, power
        )
        
        return {
            'sample_size_per_arm': {
                'control': n_control,
                'treatment': n_treatment
            },
            'total_sample_size': total_size,
            'unadjusted_size': math.ceil(sample_size),
            'adjusted_for_dropout': total_size,
            'calculation_details': {
                'design_type': design_type,
                'outcome_type': outcome_type,
                'alpha': alpha,
                'power': power,
                'allocation_ratio': allocation_ratio,
                'dropout_rate': dropout_rate
            },
            'recommendations': recommendations
        }
        
    except Exception as e:
        return {
            'error': f'Sample size calculation failed: {str(e)}',
            'input_data': input_data
        }


def _calculate_continuous_sample_size(
    input_data: Dict[str, Any],
    design_type: str,
    alpha: float,
    power: float,
    allocation_ratio: float
) -> float:
    """Calculate sample size for continuous outcomes."""
    
    mean_diff = input_data.get('mean_difference')
    std_dev = input_data.get('std_dev')
    
    if mean_diff is None or std_dev is None:
        raise ValueError('mean_difference and std_dev required for continuous outcomes')
    
    # Standardized effect size
    effect_size = abs(mean_diff) / std_dev
    
    # Critical values
    z_alpha = stats.norm.ppf(1 - alpha/2) if design_type == 'superiority' else stats.norm.ppf(1 - alpha)
    z_beta = stats.norm.ppf(power)
    
    # Sample size formula for two-sample t-test
    n = ((z_alpha + z_beta) ** 2) * (1 + 1/allocation_ratio) / (effect_size ** 2)
    
    if design_type == 'non_inferiority':
        margin = input_data.get('margin', 0)
        adjusted_effect = (mean_diff - margin) / std_dev
        n = ((z_alpha + z_beta) ** 2) * (1 + 1/allocation_ratio) / (adjusted_effect ** 2)
    
    return n * 2  # Total for both arms


def _calculate_binary_sample_size(
    input_data: Dict[str, Any],
    design_type: str,
    alpha: float,
    power: float,
    allocation_ratio: float
) -> float:
    """Calculate sample size for binary outcomes."""
    
    p1 = input_data.get('control_rate')
    p2 = input_data.get('treatment_rate')
    
    if p1 is None or p2 is None:
        raise ValueError('control_rate and treatment_rate required for binary outcomes')
    
    # Average proportion
    p_avg = (p1 + allocation_ratio * p2) / (1 + allocation_ratio)
    
    # Critical values
    z_alpha = stats.norm.ppf(1 - alpha/2) if design_type == 'superiority' else stats.norm.ppf(1 - alpha)
    z_beta = stats.norm.ppf(power)
    
    # Sample size formula for two proportions
    numerator = (z_alpha * math.sqrt(p_avg * (1 - p_avg) * (1 + 1/allocation_ratio)) +
                 z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2) / allocation_ratio)) ** 2
    denominator = (p1 - p2) ** 2
    
    n_control = numerator / denominator
    n_total = n_control * (1 + allocation_ratio)
    
    if design_type == 'non_inferiority':
        margin = input_data.get('margin', 0)
        adjusted_diff = p1 - p2 - margin
        denominator = adjusted_diff ** 2
        n_control = numerator / denominator
        n_total = n_control * (1 + allocation_ratio)
    
    return n_total


def _calculate_survival_sample_size(
    input_data: Dict[str, Any],
    design_type: str,
    alpha: float,
    power: float,
    allocation_ratio: float
) -> float:
    """Calculate sample size for time-to-event outcomes."""
    
    hazard_ratio = input_data.get('hazard_ratio', 1.5)
    median_survival_control = input_data.get('median_survival_control', 12)
    accrual_time = input_data.get('accrual_time', 24)
    follow_up_time = input_data.get('follow_up_time', 12)
    
    # Calculate event probability
    lambda_control = math.log(2) / median_survival_control
    
    # Schoenfeld formula for survival analysis
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)
    
    log_hr = math.log(hazard_ratio)
    
    # Number of events required
    d = ((z_alpha + z_beta) ** 2) / (log_hr ** 2)
    
    # Probability of event during study
    prob_event = 1 - math.exp(-lambda_control * (accrual_time / 2 + follow_up_time))
    
    # Total sample size
    n_total = d / prob_event
    
    return n_total


def _generate_recommendations(
    design_type: str,
    outcome_type: str,
    total_size: int,
    dropout_rate: float,
    power: float
) -> list:
    """Generate recommendations based on calculated sample size."""
    
    recommendations = []
    
    # Sample size recommendations
    if total_size > 1000:
        recommendations.append(
            "Large sample size required. Consider feasibility and recruitment strategies."
        )
    elif total_size > 500:
        recommendations.append(
            "Moderate sample size. Multi-site recruitment may be beneficial."
        )
    
    # Dropout rate recommendations
    if dropout_rate > 0.2:
        recommendations.append(
            f"High dropout rate ({dropout_rate*100:.0f}%). Consider retention strategies."
        )
    
    # Power recommendations
    if power < 0.8:
        recommendations.append(
            f"Statistical power ({power*100:.0f}%) is below standard 80%. Consider increasing."
        )
    elif power > 0.9:
        recommendations.append(
            f"High statistical power ({power*100:.0f}%) may indicate over-powered study."
        )
    
    # Design-specific recommendations
    if design_type == 'non_inferiority':
        recommendations.append(
            "Non-inferiority design: Ensure margin is clinically justified."
        )
    
    # Outcome-specific recommendations
    if outcome_type == 'time_to_event':
        recommendations.append(
            "Survival analysis: Consider competing risks and censoring patterns."
        )
    elif outcome_type == 'binary' and total_size < 100:
        recommendations.append(
            "Small sample for binary outcome. Consider exact tests."
        )
    
    # Interim analysis recommendation
    if total_size > 200:
        recommendations.append(
            "Consider interim analysis for futility or efficacy."
        )
    
    return recommendations if recommendations else [
        "Sample size calculation complete. Review assumptions before finalizing."
    ]