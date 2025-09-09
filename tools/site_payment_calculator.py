"""
Site Payment Calculator Tool
Calculate site payments based on milestones and performance metrics
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta

def run(input_data: Dict) -> Dict:
    """
    Calculate site payments based on milestones, enrollment, and quality metrics
    
    Args:
        input_data: Dictionary containing:
            - site_id: Site identifier
            - payment_schedule: Payment milestone definitions
            - site_activities: Completed activities and metrics
            - quality_metrics: Quality performance data
            - bonus_criteria: Optional performance bonus criteria
            - payment_period: Calculation period (start_date, end_date)
    
    Returns:
        Dictionary with payment calculations and breakdown
    """
    try:
        site_id = input_data.get('site_id')
        payment_schedule = input_data.get('payment_schedule', {})
        site_activities = input_data.get('site_activities', {})
        quality_metrics = input_data.get('quality_metrics', {})
        bonus_criteria = input_data.get('bonus_criteria', {})
        payment_period = input_data.get('payment_period', {})
        
        if not site_id:
            return {
                'success': False,
                'error': 'Site ID is required'
            }
        
        current_date = datetime.now()
        period_start = datetime.fromisoformat(payment_period.get('start_date', 
                                                               (current_date - timedelta(days=30)).isoformat()))
        period_end = datetime.fromisoformat(payment_period.get('end_date', current_date.isoformat()))
        
        # Initialize payment calculation
        payment_breakdown = {
            'site_id': site_id,
            'calculation_period': {
                'start_date': period_start.isoformat(),
                'end_date': period_end.isoformat()
            },
            'base_payments': [],
            'milestone_payments': [],
            'performance_bonuses': [],
            'quality_adjustments': [],
            'deductions': [],
            'total_amount': 0
        }
        
        # Calculate base payments (per-subject, per-visit fees)
        base_rates = payment_schedule.get('base_rates', {})
        
        # Enrollment payments
        enrolled_subjects = site_activities.get('enrolled_subjects', 0)
        enrollment_rate = base_rates.get('per_subject_enrollment', 0)
        if enrolled_subjects > 0 and enrollment_rate > 0:
            enrollment_payment = enrolled_subjects * enrollment_rate
            payment_breakdown['base_payments'].append({
                'type': 'Subject Enrollment',
                'quantity': enrolled_subjects,
                'rate': enrollment_rate,
                'amount': enrollment_payment
            })
            payment_breakdown['total_amount'] += enrollment_payment
        
        # Visit payments
        completed_visits = site_activities.get('completed_visits', 0)
        visit_rate = base_rates.get('per_visit', 0)
        if completed_visits > 0 and visit_rate > 0:
            visit_payment = completed_visits * visit_rate
            payment_breakdown['base_payments'].append({
                'type': 'Completed Visits',
                'quantity': completed_visits,
                'rate': visit_rate,
                'amount': visit_payment
            })
            payment_breakdown['total_amount'] += visit_payment
        
        # Procedure-specific payments
        procedures = site_activities.get('procedures', {})
        procedure_rates = base_rates.get('procedures', {})
        for procedure_name, count in procedures.items():
            if count > 0 and procedure_name in procedure_rates:
                procedure_payment = count * procedure_rates[procedure_name]
                payment_breakdown['base_payments'].append({
                    'type': f'Procedure: {procedure_name}',
                    'quantity': count,
                    'rate': procedure_rates[procedure_name],
                    'amount': procedure_payment
                })
                payment_breakdown['total_amount'] += procedure_payment
        
        # Calculate milestone payments
        milestones = payment_schedule.get('milestones', [])
        completed_milestones = site_activities.get('completed_milestones', [])
        
        for milestone in milestones:
            milestone_id = milestone.get('id')
            if milestone_id in completed_milestones:
                milestone_payment = milestone.get('amount', 0)
                payment_breakdown['milestone_payments'].append({
                    'milestone_id': milestone_id,
                    'description': milestone.get('description', ''),
                    'amount': milestone_payment,
                    'completion_date': 'Completed'  # Since completed_milestones is a list
                })
                payment_breakdown['total_amount'] += milestone_payment
        
        # Calculate performance bonuses
        if bonus_criteria:
            # Enrollment performance bonus
            enrollment_target = bonus_criteria.get('enrollment_target', 0)
            enrollment_bonus_rate = bonus_criteria.get('enrollment_bonus_percent', 0)
            if enrolled_subjects >= enrollment_target and enrollment_bonus_rate > 0:
                current_base = sum(payment['amount'] for payment in payment_breakdown['base_payments'])
                enrollment_bonus = current_base * (enrollment_bonus_rate / 100)
                payment_breakdown['performance_bonuses'].append({
                    'type': 'Enrollment Target Bonus',
                    'criteria': f'≥{enrollment_target} subjects',
                    'achieved': enrolled_subjects,
                    'bonus_rate': f'{enrollment_bonus_rate}%',
                    'amount': enrollment_bonus
                })
                payment_breakdown['total_amount'] += enrollment_bonus
            
            # Quality performance bonus
            quality_threshold = bonus_criteria.get('quality_threshold', 95)
            quality_bonus_amount = bonus_criteria.get('quality_bonus_amount', 0)
            overall_quality_score = quality_metrics.get('overall_score', 0)
            if overall_quality_score >= quality_threshold and quality_bonus_amount > 0:
                payment_breakdown['performance_bonuses'].append({
                    'type': 'Quality Performance Bonus',
                    'criteria': f'≥{quality_threshold}% quality score',
                    'achieved': f'{overall_quality_score}%',
                    'amount': quality_bonus_amount
                })
                payment_breakdown['total_amount'] += quality_bonus_amount
            
            # Timeline adherence bonus
            timeline_adherence = site_activities.get('timeline_adherence_percent', 0)
            timeline_threshold = bonus_criteria.get('timeline_threshold', 90)
            timeline_bonus = bonus_criteria.get('timeline_bonus_amount', 0)
            if timeline_adherence >= timeline_threshold and timeline_bonus > 0:
                payment_breakdown['performance_bonuses'].append({
                    'type': 'Timeline Adherence Bonus',
                    'criteria': f'≥{timeline_threshold}% on-time completion',
                    'achieved': f'{timeline_adherence}%',
                    'amount': timeline_bonus
                })
                payment_breakdown['total_amount'] += timeline_bonus
        
        # Quality adjustments and deductions
        protocol_deviations = quality_metrics.get('protocol_deviations', 0)
        deviation_penalty = payment_schedule.get('deviation_penalty_per_incident', 0)
        if protocol_deviations > 0 and deviation_penalty > 0:
            total_deviation_penalty = protocol_deviations * deviation_penalty
            payment_breakdown['deductions'].append({
                'type': 'Protocol Deviation Penalty',
                'quantity': protocol_deviations,
                'penalty_per_incident': deviation_penalty,
                'amount': -total_deviation_penalty
            })
            payment_breakdown['total_amount'] -= total_deviation_penalty
        
        # Data query penalties
        outstanding_queries = quality_metrics.get('outstanding_queries', 0)
        query_penalty = payment_schedule.get('query_penalty_per_outstanding', 0)
        if outstanding_queries > 0 and query_penalty > 0:
            total_query_penalty = outstanding_queries * query_penalty
            payment_breakdown['deductions'].append({
                'type': 'Outstanding Query Penalty',
                'quantity': outstanding_queries,
                'penalty_per_query': query_penalty,
                'amount': -total_query_penalty
            })
            payment_breakdown['total_amount'] -= total_query_penalty
        
        # Late submission penalties
        late_submissions = site_activities.get('late_submissions', 0)
        late_penalty = payment_schedule.get('late_submission_penalty', 0)
        if late_submissions > 0 and late_penalty > 0:
            total_late_penalty = late_submissions * late_penalty
            payment_breakdown['deductions'].append({
                'type': 'Late Submission Penalty',
                'quantity': late_submissions,
                'penalty_per_incident': late_penalty,
                'amount': -total_late_penalty
            })
            payment_breakdown['total_amount'] -= total_late_penalty
        
        # Ensure minimum payment
        minimum_payment = payment_schedule.get('minimum_payment', 0)
        if payment_breakdown['total_amount'] < minimum_payment:
            adjustment = minimum_payment - payment_breakdown['total_amount']
            payment_breakdown['quality_adjustments'].append({
                'type': 'Minimum Payment Adjustment',
                'amount': adjustment
            })
            payment_breakdown['total_amount'] = minimum_payment
        
        # Calculate summary statistics
        total_base = sum(payment['amount'] for payment in payment_breakdown['base_payments'])
        total_milestones = sum(payment['amount'] for payment in payment_breakdown['milestone_payments'])
        total_bonuses = sum(payment['amount'] for payment in payment_breakdown['performance_bonuses'])
        total_adjustments = sum(payment['amount'] for payment in payment_breakdown['quality_adjustments'])
        total_deductions = sum(abs(payment['amount']) for payment in payment_breakdown['deductions'])
        
        payment_summary = {
            'base_payments_total': total_base,
            'milestone_payments_total': total_milestones,
            'performance_bonuses_total': total_bonuses,
            'quality_adjustments_total': total_adjustments,
            'total_deductions': total_deductions,
            'net_payment_amount': payment_breakdown['total_amount']
        }
        
        # Generate payment recommendations
        recommendations = []
        
        if total_deductions > total_base * 0.1:
            recommendations.append("High penalty amount - review site performance and provide additional support")
        
        if total_bonuses == 0 and enrolled_subjects > 0:
            recommendations.append("No performance bonuses earned - consider additional incentives")
        
        if outstanding_queries > 10:
            recommendations.append("High number of outstanding queries - prioritize data cleaning")
        
        # Payment schedule recommendations
        next_milestones = []
        for milestone in milestones:
            if milestone.get('id') not in completed_milestones:
                next_milestones.append({
                    'id': milestone.get('id'),
                    'description': milestone.get('description'),
                    'amount': milestone.get('amount'),
                    'due_date': milestone.get('due_date')
                })
        
        return {
            'success': True,
            'payment_data': {
                'calculation_date': current_date.isoformat(),
                'site_id': site_id,
                'payment_breakdown': payment_breakdown,
                'payment_summary': payment_summary,
                'next_milestones': next_milestones[:3],  # Show next 3 milestones
                'recommendations': recommendations
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error calculating site payments: {str(e)}'
        }