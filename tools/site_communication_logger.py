"""
Site Communication Logger Tool
Track site communications for clinical trials
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta

def run(input_data: Dict) -> Dict:
    """
    Track and analyze communications with clinical trial sites
    
    Args:
        input_data: Dictionary containing:
            - communication_records: List of communication records
            - sites: Site information for context
            - communication_types: Types of communications to track
            - analysis_period: Time period for analysis
            - escalation_rules: Rules for communication escalation
    
    Returns:
        Dictionary with communication tracking and analysis
    """
    try:
        communication_records = input_data.get('communication_records', [])
        sites = input_data.get('sites', [])
        communication_types = input_data.get('communication_types', [])
        analysis_period = input_data.get('analysis_period', 90)  # Default 90 days
        escalation_rules = input_data.get('escalation_rules', {})
        
        current_date = datetime.now()
        period_start = current_date - timedelta(days=analysis_period)
        
        # Create site lookup
        site_lookup = {site.get('site_id'): site for site in sites}
        
        # Default communication types
        default_comm_types = {
            'email': {'name': 'Email', 'urgency_weight': 1},
            'phone': {'name': 'Phone Call', 'urgency_weight': 2},
            'meeting': {'name': 'Meeting/Video Call', 'urgency_weight': 3},
            'formal_letter': {'name': 'Formal Letter', 'urgency_weight': 4},
            'site_visit': {'name': 'Site Visit', 'urgency_weight': 5},
            'regulatory_notice': {'name': 'Regulatory Notice', 'urgency_weight': 6}
        }
        
        # Merge with provided communication types
        for comm_type in communication_types:
            type_id = comm_type.get('type_id')
            if type_id:
                default_comm_types[type_id] = comm_type
        
        # Filter communications by analysis period
        relevant_communications = []
        for comm in communication_records:
            comm_date_str = comm.get('communication_date')
            if comm_date_str:
                try:
                    comm_date = datetime.fromisoformat(comm_date_str)
                    if comm_date >= period_start:
                        relevant_communications.append(comm)
                except ValueError:
                    continue
        
        if not relevant_communications:
            return {
                'success': False,
                'error': 'No communication records found for the specified analysis period'
            }
        
        # Initialize tracking data
        site_communications = {}
        communication_analysis = {
            'total_communications': len(relevant_communications),
            'by_type': {},
            'by_priority': {},
            'by_direction': {},
            'response_times': [],
            'escalation_events': []
        }
        
        # Process each communication
        for comm in relevant_communications:
            site_id = comm.get('site_id')
            comm_type = comm.get('communication_type', 'email')
            direction = comm.get('direction', 'outbound')  # outbound/inbound
            priority = comm.get('priority', 'normal')  # low/normal/high/urgent
            subject = comm.get('subject', '')
            status = comm.get('status', 'sent')  # sent/delivered/read/responded
            response_required = comm.get('response_required', False)
            response_deadline = comm.get('response_deadline')
            actual_response_date = comm.get('actual_response_date')
            
            # Initialize site tracking
            if site_id not in site_communications:
                site_info = site_lookup.get(site_id, {})
                site_communications[site_id] = {
                    'site_name': site_info.get('site_name', f'Site {site_id}'),
                    'total_communications': 0,
                    'outbound_communications': 0,
                    'inbound_communications': 0,
                    'by_type': {},
                    'by_priority': {},
                    'outstanding_responses': 0,
                    'average_response_time_hours': 0,
                    'response_times': [],
                    'escalations': [],
                    'communication_frequency_score': 0,
                    'responsiveness_score': 0
                }
            
            site_comm = site_communications[site_id]
            site_comm['total_communications'] += 1
            
            # Track direction
            if direction == 'outbound':
                site_comm['outbound_communications'] += 1
            else:
                site_comm['inbound_communications'] += 1
            
            # Track by type
            if comm_type not in site_comm['by_type']:
                site_comm['by_type'][comm_type] = 0
            site_comm['by_type'][comm_type] += 1
            
            # Track by priority
            if priority not in site_comm['by_priority']:
                site_comm['by_priority'][priority] = 0
            site_comm['by_priority'][priority] += 1
            
            # Overall analysis tracking
            communication_analysis['by_direction'][direction] = communication_analysis['by_direction'].get(direction, 0) + 1
            communication_analysis['by_type'][comm_type] = communication_analysis['by_type'].get(comm_type, 0) + 1
            communication_analysis['by_priority'][priority] = communication_analysis['by_priority'].get(priority, 0) + 1
            
            # Response time analysis
            if response_required and actual_response_date and direction == 'outbound':
                try:
                    comm_date = datetime.fromisoformat(comm.get('communication_date'))
                    response_date = datetime.fromisoformat(actual_response_date)
                    response_time_hours = (response_date - comm_date).total_seconds() / 3600
                    
                    site_comm['response_times'].append(response_time_hours)
                    communication_analysis['response_times'].append({
                        'site_id': site_id,
                        'response_time_hours': response_time_hours,
                        'priority': priority,
                        'communication_type': comm_type
                    })
                    
                except ValueError:
                    pass
            
            # Check for outstanding responses
            if response_required and not actual_response_date and direction == 'outbound':
                site_comm['outstanding_responses'] += 1
                
                # Check for escalation needed
                if response_deadline:
                    try:
                        deadline = datetime.fromisoformat(response_deadline)
                        if current_date > deadline:
                            days_overdue = (current_date - deadline).days
                            escalation_event = {
                                'site_id': site_id,
                                'communication_id': comm.get('communication_id'),
                                'subject': subject,
                                'days_overdue': days_overdue,
                                'priority': priority,
                                'escalation_level': _determine_escalation_level(days_overdue, priority, escalation_rules)
                            }
                            site_comm['escalations'].append(escalation_event)
                            communication_analysis['escalation_events'].append(escalation_event)
                    except ValueError:
                        pass
        
        # Calculate site-specific metrics
        for site_id, site_comm in site_communications.items():
            # Average response time
            if site_comm['response_times']:
                site_comm['average_response_time_hours'] = round(
                    sum(site_comm['response_times']) / len(site_comm['response_times']), 1
                )
            
            # Communication frequency score (communications per week)
            site_comm['communication_frequency_score'] = round(
                (site_comm['total_communications'] / analysis_period) * 7, 1
            )
            
            # Responsiveness score (0-100 based on response times and outstanding items)
            responsiveness_score = 100
            if site_comm['outstanding_responses'] > 0:
                responsiveness_score -= min(site_comm['outstanding_responses'] * 10, 50)
            
            if site_comm['average_response_time_hours'] > 48:  # > 2 days
                responsiveness_score -= 20
            elif site_comm['average_response_time_hours'] > 24:  # > 1 day
                responsiveness_score -= 10
            
            site_comm['responsiveness_score'] = max(0, responsiveness_score)
        
        # Generate communication insights
        insights = []
        
        # Overall response time analysis
        if communication_analysis['response_times']:
            avg_response_time = sum(rt['response_time_hours'] for rt in communication_analysis['response_times']) / len(communication_analysis['response_times'])
            if avg_response_time > 72:  # > 3 days
                insights.append({
                    'type': 'Response Time Concern',
                    'finding': f"Average response time is {avg_response_time:.1f} hours",
                    'impact': 'Delayed site communications may impact study timelines',
                    'recommendation': 'Implement response time targets and follow-up procedures'
                })
        
        # High-volume communication sites
        high_comm_sites = [
            site_id for site_id, data in site_communications.items()
            if data['communication_frequency_score'] > 10  # >10 per week
        ]
        
        if high_comm_sites:
            insights.append({
                'type': 'High Communication Volume',
                'finding': f"{len(high_comm_sites)} sites require frequent communication",
                'impact': 'High maintenance sites may need additional support',
                'recommendation': 'Review site training needs and provide targeted assistance'
            })
        
        # Low responsiveness sites
        low_response_sites = [
            site_id for site_id, data in site_communications.items()
            if data['responsiveness_score'] < 50
        ]
        
        if low_response_sites:
            insights.append({
                'type': 'Low Responsiveness',
                'finding': f"{len(low_response_sites)} sites have low responsiveness scores",
                'impact': 'Poor communication may lead to protocol deviations',
                'recommendation': 'Escalate communication concerns and provide additional support'
            })
        
        # Priority communication analysis
        urgent_comms = communication_analysis['by_priority'].get('urgent', 0)
        if urgent_comms > communication_analysis['total_communications'] * 0.1:  # >10% urgent
            insights.append({
                'type': 'High Urgent Communications',
                'finding': f"{urgent_comms} urgent communications sent ({(urgent_comms/communication_analysis['total_communications']*100):.1f}%)",
                'impact': 'High urgency rate may indicate systemic issues',
                'recommendation': 'Analyze root causes of urgent communications'
            })
        
        # Generate recommendations
        recommendations = []
        
        if len(communication_analysis['escalation_events']) > 0:
            recommendations.append(f"{len(communication_analysis['escalation_events'])} overdue responses require escalation")
        
        if communication_analysis['by_direction'].get('inbound', 0) < communication_analysis['by_direction'].get('outbound', 1) * 0.3:
            recommendations.append("Low inbound communication - sites may need encouragement to communicate proactively")
        
        # Site-specific recommendations
        for site_id, site_data in site_communications.items():
            if site_data['outstanding_responses'] > 5:
                recommendations.append(f"Site {site_id}: {site_data['outstanding_responses']} outstanding responses - immediate follow-up needed")
        
        # Communication trends (if enough historical data)
        communication_trends = _analyze_communication_trends(relevant_communications)
        
        return {
            'success': True,
            'communication_data': {
                'generated_at': current_date.isoformat(),
                'analysis_period': {
                    'start_date': period_start.isoformat(),
                    'end_date': current_date.isoformat(),
                    'days': analysis_period
                },
                'overall_analysis': communication_analysis,
                'site_communications': site_communications,
                'communication_trends': communication_trends,
                'insights': insights,
                'recommendations': recommendations,
                'escalation_alerts': [
                    event for event in communication_analysis['escalation_events']
                    if event['escalation_level'] in ['high', 'urgent']
                ]
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error tracking site communications: {str(e)}'
        }

def _determine_escalation_level(days_overdue: int, priority: str, escalation_rules: Dict) -> str:
    """Determine escalation level based on overdue days and priority"""
    # Default escalation rules
    default_rules = {
        'urgent': {'immediate': 1, 'high': 3, 'medium': 7},
        'high': {'immediate': 2, 'high': 5, 'medium': 10},
        'normal': {'immediate': 7, 'high': 14, 'medium': 21},
        'low': {'immediate': 14, 'high': 30, 'medium': 45}
    }
    
    rules = escalation_rules.get(priority, default_rules.get(priority, default_rules['normal']))
    
    if days_overdue >= rules.get('immediate', 7):
        return 'urgent'
    elif days_overdue >= rules.get('high', 5):
        return 'high'
    elif days_overdue >= rules.get('medium', 3):
        return 'medium'
    else:
        return 'low'

def _analyze_communication_trends(communications: List[Dict]) -> Dict:
    """Analyze communication trends over time"""
    trends = {
        'weekly_volume': {},
        'response_time_trend': 'stable',
        'priority_distribution_change': 'stable'
    }
    
    # Group communications by week
    for comm in communications:
        try:
            comm_date = datetime.fromisoformat(comm.get('communication_date'))
            week_key = comm_date.strftime('%Y-W%U')
            if week_key not in trends['weekly_volume']:
                trends['weekly_volume'][week_key] = 0
            trends['weekly_volume'][week_key] += 1
        except (ValueError, TypeError):
            continue
    
    # Simple trend analysis (more sophisticated analysis could be implemented)
    weekly_counts = list(trends['weekly_volume'].values())
    if len(weekly_counts) >= 4:
        recent_avg = sum(weekly_counts[-2:]) / 2
        earlier_avg = sum(weekly_counts[:2]) / 2
        
        if recent_avg > earlier_avg * 1.2:
            trends['volume_trend'] = 'increasing'
        elif recent_avg < earlier_avg * 0.8:
            trends['volume_trend'] = 'decreasing'
        else:
            trends['volume_trend'] = 'stable'
    
    return trends