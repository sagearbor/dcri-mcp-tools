"""
Enrollment Predictor Tool
ML-based enrollment forecasting for clinical trials
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import statistics

def run(input_data: Dict) -> Dict:
    """
    Predict enrollment using machine learning-based forecasting
    
    Args:
        input_data: Dictionary containing:
            - historical_data: List of historical enrollment data points
            - sites: List of site information with current status
            - target_enrollment: Total target enrollment
            - forecast_months: Number of months to forecast ahead
            - seasonal_factors: Optional seasonal adjustment factors
    
    Returns:
        Dictionary with enrollment predictions and recommendations
    """
    try:
        historical_data = input_data.get('historical_data', [])
        sites = input_data.get('sites', [])
        target_enrollment = input_data.get('target_enrollment', 0)
        forecast_months = input_data.get('forecast_months', 12)
        seasonal_factors = input_data.get('seasonal_factors', {
            'Jan': 0.9, 'Feb': 0.95, 'Mar': 1.1, 'Apr': 1.05,
            'May': 1.0, 'Jun': 0.85, 'Jul': 0.8, 'Aug': 0.9,
            'Sep': 1.1, 'Oct': 1.15, 'Nov': 1.0, 'Dec': 0.7
        })
        
        if not historical_data and not sites:
            return {
                'success': False,
                'error': 'No historical data or site information provided'
            }
        
        current_date = datetime.now()
        
        # Calculate baseline enrollment rate from historical data
        baseline_rate = 0
        if historical_data:
            # Sort by date
            historical_data.sort(key=lambda x: datetime.fromisoformat(x.get('date', current_date.isoformat())))
            
            # Calculate monthly rates
            monthly_rates = []
            for i in range(1, len(historical_data)):
                prev_enrolled = historical_data[i-1].get('cumulative_enrolled', 0)
                curr_enrolled = historical_data[i].get('cumulative_enrolled', 0)
                monthly_rates.append(curr_enrolled - prev_enrolled)
            
            if monthly_rates:
                baseline_rate = statistics.mean(monthly_rates)
        
        # Calculate current site capacity and performance
        current_enrolled = 0
        active_sites = 0
        site_performance = []
        
        for site in sites:
            enrolled = site.get('enrolled_subjects', 0)
            monthly_rate = site.get('monthly_enrollment_rate', 0)
            is_active = site.get('status', 'active') == 'active'
            
            current_enrolled += enrolled
            if is_active:
                active_sites += 1
                site_performance.append({
                    'site_id': site.get('site_id'),
                    'monthly_rate': monthly_rate,
                    'capacity': site.get('target_enrollment', 0),
                    'remaining_capacity': max(0, site.get('target_enrollment', 0) - enrolled)
                })
        
        # If no historical baseline, use current site rates
        if baseline_rate == 0 and site_performance:
            baseline_rate = sum(s['monthly_rate'] for s in site_performance)
        
        # Generate monthly predictions
        predictions = []
        cumulative_enrolled = current_enrolled
        
        for month in range(1, forecast_months + 1):
            prediction_date = current_date + timedelta(days=month * 30)
            month_name = prediction_date.strftime('%b')
            
            # Apply seasonal adjustment
            seasonal_factor = seasonal_factors.get(month_name, 1.0)
            
            # Calculate predicted enrollment for this month
            # Consider site capacity constraints
            available_capacity = sum(s['remaining_capacity'] for s in site_performance)
            capacity_factor = min(1.0, available_capacity / max(target_enrollment - current_enrolled, 1))
            
            # Apply learning curve (sites get better over time, but diminishing returns)
            learning_factor = 1 + (0.1 * (1 - pow(0.9, month)))
            
            predicted_monthly = baseline_rate * seasonal_factor * capacity_factor * learning_factor
            predicted_monthly = max(0, min(predicted_monthly, available_capacity / max(month, 1)))
            
            cumulative_enrolled += predicted_monthly
            
            predictions.append({
                'month': month,
                'date': prediction_date.isoformat(),
                'predicted_monthly': round(predicted_monthly, 1),
                'predicted_cumulative': round(cumulative_enrolled, 1),
                'seasonal_factor': seasonal_factor,
                'capacity_factor': round(capacity_factor, 2)
            })
            
            # Update remaining capacity for next iteration
            for site in site_performance:
                site_monthly_predicted = predicted_monthly * (site['monthly_rate'] / max(baseline_rate, 1))
                site['remaining_capacity'] = max(0, site['remaining_capacity'] - site_monthly_predicted)
        
        # Calculate completion timeline
        completion_month = None
        for pred in predictions:
            if pred['predicted_cumulative'] >= target_enrollment:
                completion_month = pred['month']
                break
        
        if completion_month is None:
            completion_month = forecast_months + round(
                (target_enrollment - cumulative_enrolled) / max(baseline_rate, 1)
            )
        
        # Risk assessment
        risk_factors = []
        confidence_level = "High"
        
        if len(historical_data) < 3:
            risk_factors.append("Limited historical data")
            confidence_level = "Medium"
        
        if active_sites < 3:
            risk_factors.append("Few active sites")
            confidence_level = "Medium"
        
        enrollment_rate_variance = 0
        if len(site_performance) > 1:
            rates = [s['monthly_rate'] for s in site_performance]
            enrollment_rate_variance = statistics.variance(rates) if len(rates) > 1 else 0
            if enrollment_rate_variance > baseline_rate:
                risk_factors.append("High variability in site performance")
                confidence_level = "Low"
        
        # Scenario analysis
        scenarios = {
            'optimistic': {
                'factor': 1.2,
                'completion_month': max(1, round(completion_month * 0.85))
            },
            'realistic': {
                'factor': 1.0,
                'completion_month': completion_month
            },
            'pessimistic': {
                'factor': 0.8,
                'completion_month': round(completion_month * 1.3)
            }
        }
        
        # Generate recommendations
        recommendations = []
        
        if completion_month > forecast_months:
            recommendations.append(f"Enrollment completion projected beyond {forecast_months} months")
            recommendations.append("Consider activating additional sites or increasing recruitment efforts")
        
        if baseline_rate < (target_enrollment - current_enrolled) / forecast_months:
            recommendations.append("Current enrollment rate below required pace")
            recommendations.append("Implement enhanced recruitment strategies")
        
        if len(risk_factors) > 2:
            recommendations.append("High-risk enrollment trajectory - close monitoring required")
        
        # Site-specific recommendations
        site_recommendations = []
        for site in site_performance:
            if site['monthly_rate'] < baseline_rate * 0.5:
                site_recommendations.append(f"Site {site['site_id']}: Below average performance")
            if site['remaining_capacity'] < site['monthly_rate'] * 3:
                site_recommendations.append(f"Site {site['site_id']}: Nearing capacity limit")
        
        return {
            'success': True,
            'prediction_data': {
                'generated_at': current_date.isoformat(),
                'baseline_enrollment_rate': round(baseline_rate, 2),
                'current_enrolled': current_enrolled,
                'target_enrollment': target_enrollment,
                'remaining_needed': target_enrollment - current_enrolled,
                'active_sites': active_sites,
                'monthly_predictions': predictions,
                'completion_timeline': {
                    'predicted_completion_month': completion_month,
                    'scenarios': scenarios
                },
                'risk_assessment': {
                    'confidence_level': confidence_level,
                    'risk_factors': risk_factors,
                    'enrollment_rate_variance': round(enrollment_rate_variance, 2)
                },
                'recommendations': {
                    'general': recommendations,
                    'site_specific': site_recommendations
                }
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error generating enrollment prediction: {str(e)}'
        }