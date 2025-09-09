"""
Training Compliance Tracker Tool
Monitor staff training completion and compliance for clinical trial sites
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta

def run(input_data: Dict) -> Dict:
    """
    Track training compliance for site staff members
    
    Args:
        input_data: Dictionary containing:
            - site_staff: List of staff members and their training records
            - required_trainings: List of mandatory training requirements
            - training_records: Historical training completion data
            - compliance_period: Time period for compliance checking
            - reminder_thresholds: Days before expiry to send reminders
    
    Returns:
        Dictionary with training compliance status and recommendations
    """
    try:
        site_staff = input_data.get('site_staff', [])
        required_trainings = input_data.get('required_trainings', [])
        training_records = input_data.get('training_records', [])
        compliance_period = input_data.get('compliance_period', 365)  # Default 1 year
        reminder_thresholds = input_data.get('reminder_thresholds', {
            'urgent': 7,    # 7 days before expiry
            'warning': 30,  # 30 days before expiry
            'notice': 60    # 60 days before expiry
        })
        
        if not site_staff:
            return {
                'success': False,
                'error': 'No site staff data provided'
            }
        
        current_date = datetime.now()
        
        # Process training requirements
        training_requirements = {}
        for training in required_trainings:
            training_id = training.get('training_id')
            training_requirements[training_id] = {
                'name': training.get('training_name'),
                'validity_period_days': training.get('validity_period_days', 365),
                'mandatory_roles': training.get('mandatory_roles', []),
                'category': training.get('category', 'General'),
                'renewal_required': training.get('renewal_required', True)
            }
        
        # Track compliance for each staff member
        staff_compliance = []
        overall_stats = {
            'total_staff': len(site_staff),
            'fully_compliant': 0,
            'partially_compliant': 0,
            'non_compliant': 0,
            'pending_renewals': 0
        }
        
        compliance_alerts = []
        upcoming_expirations = []
        
        for staff_member in site_staff:
            staff_id = staff_member.get('staff_id')
            staff_name = staff_member.get('name', f'Staff {staff_id}')
            role = staff_member.get('role', 'Unknown')
            status = staff_member.get('status', 'active')
            
            # Skip inactive staff
            if status != 'active':
                continue
            
            # Get training records for this staff member
            staff_training_records = [
                record for record in training_records
                if record.get('staff_id') == staff_id
            ]
            
            # Determine required trainings for this role
            role_required_trainings = []
            for training_id, req in training_requirements.items():
                if not req['mandatory_roles'] or role in req['mandatory_roles']:
                    role_required_trainings.append(training_id)
            
            # Check compliance for each required training
            training_status = []
            compliant_count = 0
            
            for training_id in role_required_trainings:
                req = training_requirements[training_id]
                
                # Find most recent completion
                recent_completions = [
                    record for record in staff_training_records
                    if record.get('training_id') == training_id
                ]
                
                if recent_completions:
                    # Sort by completion date
                    recent_completions.sort(
                        key=lambda x: datetime.fromisoformat(x.get('completion_date', '1900-01-01')),
                        reverse=True
                    )
                    latest_completion = recent_completions[0]
                    completion_date = datetime.fromisoformat(latest_completion.get('completion_date'))
                    
                    # Calculate expiry date
                    validity_days = req['validity_period_days']
                    expiry_date = completion_date + timedelta(days=validity_days)
                    days_until_expiry = (expiry_date - current_date).days
                    
                    # Determine compliance status
                    if days_until_expiry > 0:
                        if days_until_expiry <= reminder_thresholds['urgent']:
                            compliance_status = 'Expiring Soon (Urgent)'
                            upcoming_expirations.append({
                                'staff_id': staff_id,
                                'staff_name': staff_name,
                                'training': req['name'],
                                'expiry_date': expiry_date.isoformat(),
                                'days_until_expiry': days_until_expiry,
                                'priority': 'urgent'
                            })
                        elif days_until_expiry <= reminder_thresholds['warning']:
                            compliance_status = 'Expiring Soon (Warning)'
                            upcoming_expirations.append({
                                'staff_id': staff_id,
                                'staff_name': staff_name,
                                'training': req['name'],
                                'expiry_date': expiry_date.isoformat(),
                                'days_until_expiry': days_until_expiry,
                                'priority': 'warning'
                            })
                        elif days_until_expiry <= reminder_thresholds['notice']:
                            compliance_status = 'Expiring Soon (Notice)'
                            upcoming_expirations.append({
                                'staff_id': staff_id,
                                'staff_name': staff_name,
                                'training': req['name'],
                                'expiry_date': expiry_date.isoformat(),
                                'days_until_expiry': days_until_expiry,
                                'priority': 'notice'
                            })
                        else:
                            compliance_status = 'Compliant'
                            compliant_count += 1
                    else:
                        compliance_status = 'Expired'
                        compliance_alerts.append({
                            'type': 'Expired Training',
                            'staff_id': staff_id,
                            'staff_name': staff_name,
                            'training': req['name'],
                            'expired_days': abs(days_until_expiry)
                        })
                    
                    training_status.append({
                        'training_id': training_id,
                        'training_name': req['name'],
                        'category': req['category'],
                        'completion_date': completion_date.isoformat(),
                        'expiry_date': expiry_date.isoformat(),
                        'days_until_expiry': days_until_expiry,
                        'status': compliance_status,
                        'score': latest_completion.get('score', 'N/A'),
                        'certificate_id': latest_completion.get('certificate_id')
                    })
                else:
                    # No training record found
                    compliance_status = 'Not Completed'
                    compliance_alerts.append({
                        'type': 'Missing Training',
                        'staff_id': staff_id,
                        'staff_name': staff_name,
                        'training': req['name']
                    })
                    
                    training_status.append({
                        'training_id': training_id,
                        'training_name': req['name'],
                        'category': req['category'],
                        'completion_date': None,
                        'expiry_date': None,
                        'days_until_expiry': None,
                        'status': compliance_status,
                        'score': None,
                        'certificate_id': None
                    })
            
            # Calculate overall compliance for this staff member
            total_required = len(role_required_trainings)
            compliance_percentage = (compliant_count / max(total_required, 1)) * 100
            
            if compliance_percentage == 100:
                overall_compliance_status = 'Fully Compliant'
                overall_stats['fully_compliant'] += 1
            elif compliance_percentage >= 50:
                overall_compliance_status = 'Partially Compliant'
                overall_stats['partially_compliant'] += 1
            else:
                overall_compliance_status = 'Non-Compliant'
                overall_stats['non_compliant'] += 1
            
            staff_compliance.append({
                'staff_id': staff_id,
                'staff_name': staff_name,
                'role': role,
                'compliance_percentage': round(compliance_percentage, 1),
                'overall_status': overall_compliance_status,
                'required_trainings_count': total_required,
                'compliant_trainings_count': compliant_count,
                'training_details': training_status,
                'last_updated': current_date.isoformat()
            })
        
        # Sort upcoming expirations by urgency and date
        upcoming_expirations.sort(key=lambda x: (
            {'urgent': 0, 'warning': 1, 'notice': 2}[x['priority']],
            x['days_until_expiry']
        ))
        
        # Generate compliance summary by training category
        category_compliance = {}
        for training_id, req in training_requirements.items():
            category = req['category']
            if category not in category_compliance:
                category_compliance[category] = {
                    'total_required': 0,
                    'total_compliant': 0,
                    'compliance_rate': 0
                }
            
            # Count compliance for this training across all staff
            for staff in staff_compliance:
                training_detail = next(
                    (t for t in staff['training_details'] if t['training_id'] == training_id),
                    None
                )
                if training_detail:
                    category_compliance[category]['total_required'] += 1
                    if training_detail['status'] == 'Compliant':
                        category_compliance[category]['total_compliant'] += 1
        
        # Calculate compliance rates
        for category_data in category_compliance.values():
            if category_data['total_required'] > 0:
                category_data['compliance_rate'] = round(
                    (category_data['total_compliant'] / category_data['total_required']) * 100, 1
                )
        
        # Generate recommendations
        recommendations = []
        
        if overall_stats['non_compliant'] > 0:
            recommendations.append(f"{overall_stats['non_compliant']} staff members are non-compliant - immediate action required")
        
        urgent_expirations = len([e for e in upcoming_expirations if e['priority'] == 'urgent'])
        if urgent_expirations > 0:
            recommendations.append(f"{urgent_expirations} trainings expire within 7 days - schedule renewals immediately")
        
        if len(compliance_alerts) > overall_stats['total_staff'] * 0.1:
            recommendations.append("High number of training issues - consider centralized training coordination")
        
        # Training efficiency recommendations
        missing_trainings = [alert for alert in compliance_alerts if alert['type'] == 'Missing Training']
        if len(missing_trainings) > 5:
            recommendations.append("Multiple staff missing same trainings - schedule group training sessions")
        
        return {
            'success': True,
            'compliance_data': {
                'generated_at': current_date.isoformat(),
                'compliance_period_days': compliance_period,
                'overall_statistics': overall_stats,
                'staff_compliance': staff_compliance,
                'upcoming_expirations': upcoming_expirations[:10],  # Show next 10 expirations
                'compliance_alerts': compliance_alerts[:20],  # Show top 20 alerts
                'category_compliance': category_compliance,
                'reminder_thresholds': reminder_thresholds,
                'recommendations': recommendations
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error tracking training compliance: {str(e)}'
        }