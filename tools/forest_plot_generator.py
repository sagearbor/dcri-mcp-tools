"""
Forest Plot Generator

Creates forest plots for meta-analysis and subgroup analysis.
"""

from typing import Dict, Any, List
import math


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate forest plot data.
    
    Args:
        input_data: Dictionary containing:
            - studies: list of study data with effect sizes and CIs
            - measure: str ('OR', 'RR', 'HR', 'MD')
            - model: str ('fixed', 'random')
    
    Returns:
        Dictionary with forest plot data and statistics
    """
    
    studies = input_data.get('studies', [])
    measure = input_data.get('measure', 'OR')
    model = input_data.get('model', 'fixed')
    
    if not studies:
        return {'error': 'No studies provided'}
    
    # Calculate individual study statistics
    study_stats = []
    for study in studies:
        stats = _calculate_study_stats(study, measure)
        study_stats.append(stats)
    
    # Perform meta-analysis
    if model == 'fixed':
        pooled = _fixed_effect_meta(study_stats)
    else:
        pooled = _random_effects_meta(study_stats)
    
    # Calculate heterogeneity
    heterogeneity = _calculate_heterogeneity(study_stats, pooled)
    
    # Generate plot data
    plot_data = _generate_plot_data(study_stats, pooled, measure)
    
    return {
        'measure': measure,
        'model': model,
        'n_studies': len(studies),
        'study_results': study_stats,
        'pooled_estimate': pooled,
        'heterogeneity': heterogeneity,
        'plot_data': plot_data,
        'interpretation': _generate_interpretation(pooled, heterogeneity, measure)
    }


def _calculate_study_stats(study: Dict, measure: str) -> Dict:
    """Calculate statistics for individual study."""
    
    if measure in ['OR', 'RR', 'HR']:
        # For ratio measures, work on log scale
        effect = study.get('effect_size', 1.0)
        lower_ci = study.get('lower_ci', effect * 0.8)
        upper_ci = study.get('upper_ci', effect * 1.2)
        
        log_effect = math.log(effect) if effect > 0 else 0
        log_lower = math.log(lower_ci) if lower_ci > 0 else log_effect - 0.5
        log_upper = math.log(upper_ci) if upper_ci > 0 else log_effect + 0.5
        
        # Standard error from CI
        se = (log_upper - log_lower) / (2 * 1.96)
        weight = 1 / (se ** 2) if se > 0 else 1
        
        return {
            'name': study.get('name', 'Unknown'),
            'n': study.get('n', 0),
            'effect': effect,
            'lower_ci': lower_ci,
            'upper_ci': upper_ci,
            'log_effect': log_effect,
            'se': se,
            'weight': weight
        }
    else:
        # Mean difference
        effect = study.get('effect_size', 0)
        se = study.get('se', 1.0)
        weight = 1 / (se ** 2) if se > 0 else 1
        
        return {
            'name': study.get('name', 'Unknown'),
            'n': study.get('n', 0),
            'effect': effect,
            'lower_ci': effect - 1.96 * se,
            'upper_ci': effect + 1.96 * se,
            'se': se,
            'weight': weight
        }


def _fixed_effect_meta(study_stats: List[Dict]) -> Dict:
    """Calculate fixed effect pooled estimate."""
    
    total_weight = sum(s['weight'] for s in study_stats)
    
    if 'log_effect' in study_stats[0]:
        # Ratio measure
        pooled_log = sum(s['log_effect'] * s['weight'] for s in study_stats) / total_weight
        pooled_se = math.sqrt(1 / total_weight)
        
        return {
            'effect': math.exp(pooled_log),
            'lower_ci': math.exp(pooled_log - 1.96 * pooled_se),
            'upper_ci': math.exp(pooled_log + 1.96 * pooled_se),
            'se': pooled_se,
            'p_value': _calculate_p_value(pooled_log / pooled_se)
        }
    else:
        # Mean difference
        pooled_effect = sum(s['effect'] * s['weight'] for s in study_stats) / total_weight
        pooled_se = math.sqrt(1 / total_weight)
        
        return {
            'effect': pooled_effect,
            'lower_ci': pooled_effect - 1.96 * pooled_se,
            'upper_ci': pooled_effect + 1.96 * pooled_se,
            'se': pooled_se,
            'p_value': _calculate_p_value(pooled_effect / pooled_se)
        }


def _random_effects_meta(study_stats: List[Dict]) -> Dict:
    """Calculate random effects pooled estimate."""
    
    # First get fixed effect estimate for heterogeneity calculation
    fixed = _fixed_effect_meta(study_stats)
    
    # Calculate tau-squared (between-study variance)
    Q = sum(s['weight'] * (s.get('log_effect', s['effect']) - 
            math.log(fixed['effect']) if 'log_effect' in s else fixed['effect']) ** 2 
            for s in study_stats)
    
    df = len(study_stats) - 1
    C = sum(s['weight'] for s in study_stats) - \
        sum(s['weight'] ** 2 for s in study_stats) / sum(s['weight'] for s in study_stats)
    
    tau_squared = max(0, (Q - df) / C) if C > 0 else 0
    
    # Adjust weights
    adjusted_weights = [1 / (s['se'] ** 2 + tau_squared) for s in study_stats]
    total_weight = sum(adjusted_weights)
    
    if 'log_effect' in study_stats[0]:
        pooled_log = sum(s['log_effect'] * w for s, w in zip(study_stats, adjusted_weights)) / total_weight
        pooled_se = math.sqrt(1 / total_weight)
        
        return {
            'effect': math.exp(pooled_log),
            'lower_ci': math.exp(pooled_log - 1.96 * pooled_se),
            'upper_ci': math.exp(pooled_log + 1.96 * pooled_se),
            'se': pooled_se,
            'tau_squared': tau_squared,
            'p_value': _calculate_p_value(pooled_log / pooled_se)
        }
    else:
        pooled_effect = sum(s['effect'] * w for s, w in zip(study_stats, adjusted_weights)) / total_weight
        pooled_se = math.sqrt(1 / total_weight)
        
        return {
            'effect': pooled_effect,
            'lower_ci': pooled_effect - 1.96 * pooled_se,
            'upper_ci': pooled_effect + 1.96 * pooled_se,
            'se': pooled_se,
            'tau_squared': tau_squared,
            'p_value': _calculate_p_value(pooled_effect / pooled_se)
        }


def _calculate_heterogeneity(study_stats: List[Dict], pooled: Dict) -> Dict:
    """Calculate heterogeneity statistics."""
    
    # Calculate Q statistic
    if 'log_effect' in study_stats[0]:
        pooled_log = math.log(pooled['effect'])
        Q = sum(s['weight'] * (s['log_effect'] - pooled_log) ** 2 for s in study_stats)
    else:
        Q = sum(s['weight'] * (s['effect'] - pooled['effect']) ** 2 for s in study_stats)
    
    df = len(study_stats) - 1
    
    # Calculate I-squared
    I_squared = max(0, (Q - df) / Q * 100) if Q > 0 else 0
    
    # P-value for heterogeneity
    from scipy import stats
    p_value = 1 - stats.chi2.cdf(Q, df) if df > 0 else 1.0
    
    return {
        'Q': round(Q, 2),
        'df': df,
        'p_value': round(p_value, 4),
        'I_squared': round(I_squared, 1),
        'interpretation': _interpret_heterogeneity(I_squared)
    }


def _calculate_p_value(z_score: float) -> float:
    """Calculate two-tailed p-value from z-score."""
    from scipy import stats
    return 2 * (1 - stats.norm.cdf(abs(z_score)))


def _generate_plot_data(study_stats: List[Dict], pooled: Dict, measure: str) -> Dict:
    """Generate data for forest plot visualization."""
    
    # Determine x-axis range
    all_effects = [s['effect'] for s in study_stats] + [pooled['effect']]
    all_lower = [s['lower_ci'] for s in study_stats] + [pooled['lower_ci']]
    all_upper = [s['upper_ci'] for s in study_stats] + [pooled['upper_ci']]
    
    x_min = min(all_lower)
    x_max = max(all_upper)
    
    # Reference line
    if measure in ['OR', 'RR', 'HR']:
        reference = 1.0  # No effect
    else:
        reference = 0.0  # No difference
    
    return {
        'x_axis': {
            'min': x_min * 0.9 if measure in ['OR', 'RR', 'HR'] else x_min - abs(x_min) * 0.1,
            'max': x_max * 1.1 if measure in ['OR', 'RR', 'HR'] else x_max + abs(x_max) * 0.1,
            'scale': 'log' if measure in ['OR', 'RR', 'HR'] else 'linear',
            'label': _get_measure_label(measure)
        },
        'reference_line': reference,
        'study_points': [
            {
                'y': i,
                'x': s['effect'],
                'ci_lower': s['lower_ci'],
                'ci_upper': s['upper_ci'],
                'weight': s['weight'],
                'label': s['name']
            }
            for i, s in enumerate(study_stats)
        ],
        'pooled_diamond': {
            'y': len(study_stats),
            'x': pooled['effect'],
            'ci_lower': pooled['lower_ci'],
            'ci_upper': pooled['upper_ci'],
            'label': 'Pooled estimate'
        }
    }


def _get_measure_label(measure: str) -> str:
    """Get axis label for measure type."""
    labels = {
        'OR': 'Odds Ratio',
        'RR': 'Risk Ratio',
        'HR': 'Hazard Ratio',
        'MD': 'Mean Difference'
    }
    return labels.get(measure, measure)


def _interpret_heterogeneity(i_squared: float) -> str:
    """Interpret I-squared value."""
    if i_squared < 25:
        return "Low heterogeneity"
    elif i_squared < 50:
        return "Moderate heterogeneity"
    elif i_squared < 75:
        return "Substantial heterogeneity"
    else:
        return "Considerable heterogeneity"


def _generate_interpretation(pooled: Dict, heterogeneity: Dict, measure: str) -> str:
    """Generate interpretation of results."""
    
    effect = pooled['effect']
    p_value = pooled['p_value']
    
    if measure in ['OR', 'RR', 'HR']:
        if p_value < 0.05:
            if effect > 1:
                direction = "increased"
            else:
                direction = "decreased"
            interpretation = f"Pooled {measure} = {effect:.2f}, indicating {direction} risk (p={p_value:.4f})"
        else:
            interpretation = f"Pooled {measure} = {effect:.2f}, not statistically significant (p={p_value:.4f})"
    else:
        if p_value < 0.05:
            direction = "higher" if effect > 0 else "lower"
            interpretation = f"Pooled MD = {effect:.2f}, treatment group {direction} (p={p_value:.4f})"
        else:
            interpretation = f"Pooled MD = {effect:.2f}, no significant difference (p={p_value:.4f})"
    
    interpretation += f". {heterogeneity['interpretation']} (I²={heterogeneity['I_squared']}%)"
    
    return interpretation
