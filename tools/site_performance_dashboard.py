"""
Site Performance Dashboard Tool
Track enrollment, quality metrics across sites for clinical trials
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import statistics

def run(input_data: Dict) -> Dict:
    """
    Track enrollment and quality metrics across clinical trial sites
    
    Args:
        input_data: Dictionary containing:
            - sites: List of site data with enrollment and metrics
            - time_period: Optional time period filter (days)
            - metrics_threshold: Quality thresholds for alerts
    
    Returns:
        Dictionary with site performance dashboard data
    """
    try:
        sites = input_data.get('sites', [])
        time_period = input_data.get('time_period', 30)  # Default 30 days
        thresholds = input_data.get('metrics_threshold', {
            'enrollment_rate': 5,  # subjects per month
            'protocol_deviation_rate': 0.1,  # 10%
            'query_rate': 0.2,  # 20%
            'dropout_rate': 0.15  # 15%
        })
        
        if not sites:
            return {
                'success': False,
                'error': 'No site data provided'
            }
        
        # Calculate performance metrics for each site
        site_metrics = []
        overall_stats = {
            'total_enrollment': 0,
            'total_target': 0,
            'sites_count': len(sites),
            'high_performers': 0,
            'underperformers': 0
        }
        
        enrollment_rates = []
        deviation_rates = []
        
        for site in sites:
            site_id = site.get('site_id', 'Unknown')
            
            # Enrollment metrics
            enrolled = site.get('enrolled_subjects', 0)
            target = site.get('target_enrollment', 0)
            enrollment_rate = site.get('monthly_enrollment_rate', 0)
            
            # Quality metrics
            protocol_deviations = site.get('protocol_deviations', 0)
            total_visits = site.get('total_visits', 1)
            queries = site.get('data_queries', 0)
            dropouts = site.get('dropouts', 0)
            
            # Calculate rates
            deviation_rate = protocol_deviations / max(total_visits, 1)
            query_rate = queries / max(enrolled, 1)
            dropout_rate = dropouts / max(enrolled, 1)
            enrollment_progress = (enrolled / max(target, 1)) * 100
            
            # Performance assessment
            performance_score = 0
            alerts = []
            
            if enrollment_rate >= thresholds['enrollment_rate']:
                performance_score += 25
            else:
                alerts.append(f"Low enrollment rate: {enrollment_rate:.1f}/month")
                
            if deviation_rate <= thresholds['protocol_deviation_rate']:
                performance_score += 25
            else:
                alerts.append(f"High deviation rate: {deviation_rate:.1%}")
                
            if query_rate <= thresholds['query_rate']:
                performance_score += 25
            else:
                alerts.append(f"High query rate: {query_rate:.1%}")
                
            if dropout_rate <= thresholds['dropout_rate']:
                performance_score += 25
            else:
                alerts.append(f"High dropout rate: {dropout_rate:.1%}")
            
            # Categorize performance
            if performance_score >= 75:
                performance_category = "High Performer"
                overall_stats['high_performers'] += 1
            elif performance_score >= 50:
                performance_category = "Average"
            else:
                performance_category = "Underperformer"
                overall_stats['underperformers'] += 1
            
            site_metric = {
                'site_id': site_id,
                'site_name': site.get('site_name', f'Site {site_id}'),
                'enrollment': {
                    'enrolled': enrolled,
                    'target': target,
                    'progress_percent': round(enrollment_progress, 1),
                    'monthly_rate': enrollment_rate
                },
                'quality_metrics': {
                    'protocol_deviation_rate': round(deviation_rate, 3),
                    'query_rate': round(query_rate, 3),
                    'dropout_rate': round(dropout_rate, 3)
                },
                'performance_score': performance_score,
                'performance_category': performance_category,
                'alerts': alerts,
                'last_updated': site.get('last_updated', datetime.now().isoformat())
            }
            
            site_metrics.append(site_metric)
            
            # Update overall stats
            overall_stats['total_enrollment'] += enrolled
            overall_stats['total_target'] += target
            enrollment_rates.append(enrollment_rate)
            deviation_rates.append(deviation_rate)
        
        # Calculate overall statistics
        if enrollment_rates:
            overall_stats['avg_enrollment_rate'] = round(statistics.mean(enrollment_rates), 2)
            overall_stats['median_enrollment_rate'] = round(statistics.median(enrollment_rates), 2)
        
        if deviation_rates:
            overall_stats['avg_deviation_rate'] = round(statistics.mean(deviation_rates), 3)
        
        overall_stats['overall_progress'] = round(
            (overall_stats['total_enrollment'] / max(overall_stats['total_target'], 1)) * 100, 1
        )
        
        # Generate recommendations
        recommendations = []
        
        if overall_stats['underperformers'] > overall_stats['sites_count'] * 0.3:
            recommendations.append("High number of underperforming sites - consider centralized training")
        
        if overall_stats['avg_enrollment_rate'] < thresholds['enrollment_rate']:
            recommendations.append("Overall enrollment below target - review recruitment strategies")
        
        if overall_stats['avg_deviation_rate'] > thresholds['protocol_deviation_rate']:
            recommendations.append("Protocol deviations above threshold - additional site training needed")
        
        # Sort sites by performance score
        site_metrics.sort(key=lambda x: x['performance_score'], reverse=True)
        
        return {
            'success': True,
            'dashboard_data': {
                'generated_at': datetime.now().isoformat(),
                'time_period_days': time_period,
                'overall_statistics': overall_stats,
                'site_metrics': site_metrics,
                'recommendations': recommendations,
                'thresholds_used': thresholds
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error generating site performance dashboard: {str(e)}'
        }