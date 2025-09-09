"""
Screen Failure Analyzer Tool
Analyze screening failure patterns in clinical trials
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import statistics

def run(input_data: Dict) -> Dict:
    """
    Analyze screening failure patterns and identify improvement opportunities
    
    Args:
        input_data: Dictionary containing:
            - screening_data: List of screening records with outcomes
            - inclusion_criteria: Study inclusion criteria definitions
            - exclusion_criteria: Study exclusion criteria definitions
            - sites: Site information for analysis
            - analysis_period: Time period for analysis
    
    Returns:
        Dictionary with screening failure analysis and recommendations
    """
    try:
        screening_data = input_data.get('screening_data', [])
        inclusion_criteria = input_data.get('inclusion_criteria', [])
        exclusion_criteria = input_data.get('exclusion_criteria', [])
        sites = input_data.get('sites', [])
        analysis_period = input_data.get('analysis_period', 90)  # Default 90 days
        
        if not screening_data:
            return {
                'success': False,
                'error': 'No screening data provided'
            }
        
        current_date = datetime.now()
        period_start = current_date - timedelta(days=analysis_period)
        
        # Create site lookup
        site_lookup = {site.get('site_id'): site for site in sites}
        
        # Filter screening data by analysis period
        relevant_screenings = []
        for screening in screening_data:
            screen_date_str = screening.get('screening_date')
            if screen_date_str:
                try:
                    screen_date = datetime.fromisoformat(screen_date_str)
                    if screen_date >= period_start:
                        relevant_screenings.append(screening)
                except ValueError:
                    continue
        
        if not relevant_screenings:
            return {
                'success': False,
                'error': 'No screening data found for the specified analysis period'
            }
        
        # Initialize analysis results
        overall_stats = {
            'total_screened': len(relevant_screenings),
            'enrolled': 0,
            'screen_failures': 0,
            'screen_failure_rate': 0,
            'analysis_period_days': analysis_period
        }
        
        # Analyze failure reasons
        failure_reasons = {}
        site_performance = {}
        temporal_analysis = {}
        demographic_analysis = {
            'age_groups': {},
            'gender': {},
            'race_ethnicity': {}
        }
        
        # Process each screening record
        for screening in relevant_screenings:
            site_id = screening.get('site_id')
            outcome = screening.get('outcome', 'unknown')
            failure_reason = screening.get('failure_reason')
            screen_date = datetime.fromisoformat(screening.get('screening_date'))
            
            # Demographics
            age = screening.get('age')
            gender = screening.get('gender')
            race = screening.get('race')
            ethnicity = screening.get('ethnicity')
            
            # Site analysis
            if site_id not in site_performance:
                site_info = site_lookup.get(site_id, {})
                site_performance[site_id] = {
                    'site_name': site_info.get('site_name', f'Site {site_id}'),
                    'total_screened': 0,
                    'enrolled': 0,
                    'failed': 0,
                    'failure_reasons': {},
                    'screen_failure_rate': 0
                }
            
            site_performance[site_id]['total_screened'] += 1
            
            # Temporal analysis (by month)
            month_key = screen_date.strftime('%Y-%m')
            if month_key not in temporal_analysis:
                temporal_analysis[month_key] = {
                    'total_screened': 0,
                    'enrolled': 0,
                    'failed': 0,
                    'failure_rate': 0
                }
            temporal_analysis[month_key]['total_screened'] += 1
            
            if outcome == 'enrolled':
                overall_stats['enrolled'] += 1
                site_performance[site_id]['enrolled'] += 1
                temporal_analysis[month_key]['enrolled'] += 1
            elif outcome == 'failed':
                overall_stats['screen_failures'] += 1
                site_performance[site_id]['failed'] += 1
                temporal_analysis[month_key]['failed'] += 1
                
                # Analyze failure reasons
                if failure_reason:
                    # Parse multiple failure reasons if comma-separated
                    reasons = [r.strip() for r in failure_reason.split(',')]
                    for reason in reasons:
                        if reason not in failure_reasons:
                            failure_reasons[reason] = {
                                'count': 0,
                                'percentage': 0,
                                'sites_affected': set(),
                                'criteria_type': self._categorize_failure_reason(reason, inclusion_criteria, exclusion_criteria)
                            }
                        failure_reasons[reason]['count'] += 1
                        failure_reasons[reason]['sites_affected'].add(site_id)
                        
                        # Site-specific failure tracking
                        if reason not in site_performance[site_id]['failure_reasons']:
                            site_performance[site_id]['failure_reasons'][reason] = 0
                        site_performance[site_id]['failure_reasons'][reason] += 1
                
                # Demographic analysis for failures
                if age:
                    age_group = self._get_age_group(age)
                    if age_group not in demographic_analysis['age_groups']:
                        demographic_analysis['age_groups'][age_group] = {'screened': 0, 'failed': 0}
                    demographic_analysis['age_groups'][age_group]['screened'] += 1
                    demographic_analysis['age_groups'][age_group]['failed'] += 1
                
                if gender:
                    if gender not in demographic_analysis['gender']:
                        demographic_analysis['gender'][gender] = {'screened': 0, 'failed': 0}
                    demographic_analysis['gender'][gender]['screened'] += 1
                    demographic_analysis['gender'][gender]['failed'] += 1
            
            # Track demographics for all screenings
            if age:
                age_group = self._get_age_group(age)
                if age_group not in demographic_analysis['age_groups']:
                    demographic_analysis['age_groups'][age_group] = {'screened': 0, 'failed': 0}
                demographic_analysis['age_groups'][age_group]['screened'] += 1
            
            if gender:
                if gender not in demographic_analysis['gender']:
                    demographic_analysis['gender'][gender] = {'screened': 0, 'failed': 0}
                demographic_analysis['gender'][gender]['screened'] += 1
        
        # Calculate rates and percentages
        if overall_stats['total_screened'] > 0:
            overall_stats['screen_failure_rate'] = round(
                (overall_stats['screen_failures'] / overall_stats['total_screened']) * 100, 1
            )
        
        # Calculate failure reason percentages
        for reason_data in failure_reasons.values():
            reason_data['percentage'] = round(
                (reason_data['count'] / max(overall_stats['screen_failures'], 1)) * 100, 1
            )
            reason_data['sites_affected'] = len(reason_data['sites_affected'])
        
        # Calculate site failure rates
        for site_data in site_performance.values():
            if site_data['total_screened'] > 0:
                site_data['screen_failure_rate'] = round(
                    (site_data['failed'] / site_data['total_screened']) * 100, 1
                )
        
        # Calculate temporal failure rates
        for month_data in temporal_analysis.values():
            if month_data['total_screened'] > 0:
                month_data['failure_rate'] = round(
                    (month_data['failed'] / month_data['total_screened']) * 100, 1
                )
        
        # Calculate demographic failure rates
        for demo_category in demographic_analysis.values():
            for demo_data in demo_category.values():
                if demo_data['screened'] > 0:
                    demo_data['failure_rate'] = round(
                        (demo_data['failed'] / demo_data['screened']) * 100, 1
                    )
        
        # Identify patterns and insights
        insights = []
        
        # Top failure reasons
        sorted_failures = sorted(
            failure_reasons.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        if sorted_failures:
            top_failure = sorted_failures[0]
            insights.append({
                'type': 'Top Failure Reason',
                'finding': f"'{top_failure[0]}' accounts for {top_failure[1]['percentage']}% of screen failures",
                'impact': f"Affects {top_failure[1]['sites_affected']} sites",
                'recommendation': self._get_failure_reason_recommendation(top_failure[0], top_failure[1])
            })
        
        # Site performance variation
        site_rates = [site['screen_failure_rate'] for site in site_performance.values()]
        if len(site_rates) > 1:
            rate_variance = statistics.variance(site_rates)
            if rate_variance > 100:  # High variance threshold
                min_rate = min(site_rates)
                max_rate = max(site_rates)
                insights.append({
                    'type': 'Site Performance Variation',
                    'finding': f"Screen failure rates vary significantly across sites ({min_rate}% to {max_rate}%)",
                    'impact': 'Inconsistent screening practices',
                    'recommendation': 'Standardize screening procedures and provide additional training'
                })
        
        # Temporal trends
        if len(temporal_analysis) >= 2:
            months = sorted(temporal_analysis.keys())
            recent_rates = [temporal_analysis[month]['failure_rate'] for month in months[-3:]]
            early_rates = [temporal_analysis[month]['failure_rate'] for month in months[:3]]
            
            if recent_rates and early_rates:
                recent_avg = statistics.mean(recent_rates)
                early_avg = statistics.mean(early_rates)
                
                if recent_avg > early_avg * 1.2:
                    insights.append({
                        'type': 'Increasing Failure Rate',
                        'finding': f"Screen failure rate increased from {early_avg:.1f}% to {recent_avg:.1f}%",
                        'impact': 'Declining screening efficiency',
                        'recommendation': 'Review recent protocol changes and site training needs'
                    })
                elif recent_avg < early_avg * 0.8:
                    insights.append({
                        'type': 'Improving Performance',
                        'finding': f"Screen failure rate decreased from {early_avg:.1f}% to {recent_avg:.1f}%",
                        'impact': 'Improved screening efficiency',
                        'recommendation': 'Document successful practices for replication'
                    })
        
        # Generate recommendations
        recommendations = []
        
        if overall_stats['screen_failure_rate'] > 50:
            recommendations.append("High screen failure rate - review inclusion/exclusion criteria feasibility")
        
        # Criteria-specific recommendations
        inclusion_failures = sum(
            data['count'] for data in failure_reasons.values()
            if data['criteria_type'] == 'inclusion'
        )
        exclusion_failures = sum(
            data['count'] for data in failure_reasons.values()
            if data['criteria_type'] == 'exclusion'
        )
        
        if inclusion_failures > exclusion_failures * 2:
            recommendations.append("High inclusion criteria failures - consider protocol amendments")
        
        # Site-specific recommendations
        high_failure_sites = [
            site_id for site_id, data in site_performance.items()
            if data['screen_failure_rate'] > overall_stats['screen_failure_rate'] * 1.3
        ]
        
        if high_failure_sites:
            recommendations.append(f"Sites {', '.join(high_failure_sites[:3])} have high failure rates - targeted training needed")
        
        return {
            'success': True,
            'analysis_data': {
                'generated_at': current_date.isoformat(),
                'analysis_period': {
                    'start_date': period_start.isoformat(),
                    'end_date': current_date.isoformat(),
                    'days': analysis_period
                },
                'overall_statistics': overall_stats,
                'failure_reasons': dict(sorted(failure_reasons.items(), key=lambda x: x[1]['count'], reverse=True)),
                'site_performance': site_performance,
                'temporal_analysis': dict(sorted(temporal_analysis.items())),
                'demographic_analysis': demographic_analysis,
                'insights': insights,
                'recommendations': recommendations
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error analyzing screen failures: {str(e)}'
        }

def _categorize_failure_reason(reason: str, inclusion_criteria: List, exclusion_criteria: List) -> str:
    """Categorize failure reason as inclusion, exclusion, or other"""
    reason_lower = reason.lower()
    
    # Check against inclusion criteria
    for criterion in inclusion_criteria:
        if criterion.get('keyword', '').lower() in reason_lower:
            return 'inclusion'
    
    # Check against exclusion criteria
    for criterion in exclusion_criteria:
        if criterion.get('keyword', '').lower() in reason_lower:
            return 'exclusion'
    
    # Common categorizations
    if any(word in reason_lower for word in ['age', 'too young', 'too old']):
        return 'inclusion'
    elif any(word in reason_lower for word in ['medication', 'drug', 'treatment']):
        return 'exclusion'
    elif any(word in reason_lower for word in ['condition', 'disease', 'diagnosis']):
        return 'exclusion'
    else:
        return 'other'

def _get_age_group(age: int) -> str:
    """Categorize age into groups"""
    if age < 18:
        return 'Under 18'
    elif age < 30:
        return '18-29'
    elif age < 45:
        return '30-44'
    elif age < 65:
        return '45-64'
    else:
        return '65+'

def _get_failure_reason_recommendation(reason: str, reason_data: Dict) -> str:
    """Generate specific recommendation based on failure reason"""
    if reason_data['percentage'] > 30:
        return f"Major contributor - review protocol feasibility for '{reason}'"
    elif reason_data['sites_affected'] > 3:
        return f"Multi-site issue - standardize assessment procedures for '{reason}'"
    else:
        return f"Monitor '{reason}' for trend development"