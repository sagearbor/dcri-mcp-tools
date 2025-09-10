"""
Equipment Calibration Tracker Tool
Monitor equipment calibration status for clinical trial sites
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta

def run(input_data: Dict) -> Dict:
    """
    Monitors equipment calibration status and generates alerts for expiring calibrations across clinical sites.
    
    Example:
        Input: Equipment inventory with calibration dates and alert threshold settings
        Output: Calibration status dashboard with expiration alerts and compliance recommendations
    
    Parameters:
        equipment_inventory : list
            List of site equipment with calibration status data
        calibration_records : list
            Historical equipment calibration records
        equipment_types : dict
            Equipment type definitions and calibration requirements
        sites : list
            Site information for tracking context
        alert_thresholds : dict
            Days before expiry for different alert severity levels
    """
    try:
        equipment_inventory = input_data.get('equipment_inventory', [])
        calibration_records = input_data.get('calibration_records', [])
        equipment_types = input_data.get('equipment_types', {})
        sites = input_data.get('sites', [])
        alert_thresholds = input_data.get('alert_thresholds', {
            'critical': 7,   # 7 days before expiry
            'urgent': 30,    # 30 days before expiry
            'warning': 60,   # 60 days before expiry
            'notice': 90     # 90 days before expiry
        })
        
        if not equipment_inventory:
            return {
                'success': False,
                'error': 'No equipment inventory provided'
            }
        
        current_date = datetime.now()
        
        # Create site lookup
        site_lookup = {site.get('site_id'): site for site in sites}
        
        # Default equipment types with calibration requirements
        default_equipment_types = {
            'scale': {
                'name': 'Scale/Balance',
                'calibration_frequency_days': 365,
                'criticality': 'high',
                'regulatory_requirement': True
            },
            'centrifuge': {
                'name': 'Centrifuge',
                'calibration_frequency_days': 365,
                'criticality': 'high',
                'regulatory_requirement': True
            },
            'freezer': {
                'name': 'Freezer (-20°C/-80°C)',
                'calibration_frequency_days': 365,
                'criticality': 'critical',
                'regulatory_requirement': True
            },
            'refrigerator': {
                'name': 'Refrigerator (2-8°C)',
                'calibration_frequency_days': 365,
                'criticality': 'critical',
                'regulatory_requirement': True
            },
            'thermometer': {
                'name': 'Digital Thermometer',
                'calibration_frequency_days': 365,
                'criticality': 'medium',
                'regulatory_requirement': True
            },
            'bp_monitor': {
                'name': 'Blood Pressure Monitor',
                'calibration_frequency_days': 365,
                'criticality': 'high',
                'regulatory_requirement': True
            },
            'ecg_machine': {
                'name': 'ECG Machine',
                'calibration_frequency_days': 365,
                'criticality': 'high',
                'regulatory_requirement': True
            },
            'pipette': {
                'name': 'Pipette',
                'calibration_frequency_days': 365,
                'criticality': 'medium',
                'regulatory_requirement': True
            },
            'incubator': {
                'name': 'Incubator',
                'calibration_frequency_days': 365,
                'criticality': 'high',
                'regulatory_requirement': True
            },
            'microscope': {
                'name': 'Microscope',
                'calibration_frequency_days': 730,
                'criticality': 'medium',
                'regulatory_requirement': False
            }
        }
        
        # Merge with provided equipment types
        for equip_type_id, equip_config in equipment_types.items():
            # Ensure required fields have defaults
            merged_config = {
                'calibration_frequency_days': 365,
                'criticality': 'medium',
                'regulatory_requirement': True
            }
            merged_config.update(equip_config)
            default_equipment_types[equip_type_id] = merged_config
        
        # Process each piece of equipment
        calibration_alerts = []
        site_equipment_status = {}
        equipment_analysis = {
            'total_equipment': 0,  # Will count only active equipment
            'compliant_equipment': 0,
            'expiring_equipment': 0,
            'expired_equipment': 0,
            'by_criticality': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'by_type': {}
        }
        
        for equipment in equipment_inventory:
            site_id = equipment.get('site_id')
            equipment_id = equipment.get('equipment_id')
            equipment_type_id = equipment.get('equipment_type_id', 'unknown')
            serial_number = equipment.get('serial_number', 'Unknown')
            location = equipment.get('location', 'Unknown')
            status = equipment.get('status', 'active')
            
            # Skip inactive equipment
            if status != 'active':
                continue
            
            # Get equipment type configuration
            equipment_config = default_equipment_types.get(equipment_type_id, {
                'name': f'Unknown Equipment ({equipment_type_id})',
                'calibration_frequency_days': 365,
                'criticality': 'medium',
                'regulatory_requirement': True
            })
            
            # Find most recent calibration
            equipment_calibrations = [
                record for record in calibration_records
                if record.get('equipment_id') == equipment_id
            ]
            
            # Initialize site tracking
            if site_id not in site_equipment_status:
                site_info = site_lookup.get(site_id, {})
                site_equipment_status[site_id] = {
                    'site_name': site_info.get('site_name', f'Site {site_id}'),
                    'total_equipment': 0,
                    'compliant_equipment': 0,
                    'expired_equipment': 0,
                    'expiring_equipment': 0,
                    'equipment_details': [],
                    'compliance_percentage': 0
                }
            
            site_status = site_equipment_status[site_id]
            site_status['total_equipment'] += 1
            equipment_analysis['total_equipment'] += 1  # Count active equipment
            
            # Track by type
            equipment_type_name = equipment_config['name']
            if equipment_type_name not in equipment_analysis['by_type']:
                equipment_analysis['by_type'][equipment_type_name] = {
                    'total': 0,
                    'compliant': 0,
                    'expired': 0,
                    'expiring': 0
                }
            equipment_analysis['by_type'][equipment_type_name]['total'] += 1
            
            # Analyze calibration status
            calibration_status = 'No Calibration Record'
            last_calibration_date = None
            next_calibration_due = None
            days_until_expiry = None
            alert_level = None
            
            if equipment_calibrations:
                # Sort by calibration date
                equipment_calibrations.sort(
                    key=lambda x: datetime.fromisoformat(x.get('calibration_date', '1900-01-01')),
                    reverse=True
                )
                latest_calibration = equipment_calibrations[0]
                
                try:
                    last_calibration_date = datetime.fromisoformat(latest_calibration.get('calibration_date'))
                    calibration_frequency = equipment_config['calibration_frequency_days']
                    next_calibration_due = last_calibration_date + timedelta(days=calibration_frequency)
                    days_until_expiry = (next_calibration_due - current_date).days
                    
                    # Determine status and alert level
                    if days_until_expiry < 0:
                        calibration_status = 'Expired'
                        alert_level = 'expired'
                        site_status['expired_equipment'] += 1
                        equipment_analysis['expired_equipment'] += 1
                        equipment_analysis['by_type'][equipment_type_name]['expired'] += 1
                    elif days_until_expiry <= alert_thresholds['critical']:
                        calibration_status = 'Expiring Soon (Critical)'
                        alert_level = 'critical'
                        site_status['expiring_equipment'] += 1
                        equipment_analysis['expiring_equipment'] += 1
                        equipment_analysis['by_type'][equipment_type_name]['expiring'] += 1
                    elif days_until_expiry <= alert_thresholds['urgent']:
                        calibration_status = 'Expiring Soon (Urgent)'
                        alert_level = 'urgent'
                        site_status['expiring_equipment'] += 1
                        equipment_analysis['expiring_equipment'] += 1
                        equipment_analysis['by_type'][equipment_type_name]['expiring'] += 1
                    elif days_until_expiry <= alert_thresholds['warning']:
                        calibration_status = 'Expiring Soon (Warning)'
                        alert_level = 'warning'
                        site_status['expiring_equipment'] += 1
                        equipment_analysis['expiring_equipment'] += 1
                        equipment_analysis['by_type'][equipment_type_name]['expiring'] += 1
                    elif days_until_expiry <= alert_thresholds['notice']:
                        calibration_status = 'Expiring Soon (Notice)'
                        alert_level = 'notice'
                        site_status['expiring_equipment'] += 1
                        equipment_analysis['expiring_equipment'] += 1
                        equipment_analysis['by_type'][equipment_type_name]['expiring'] += 1
                    else:
                        calibration_status = 'Compliant'
                        site_status['compliant_equipment'] += 1
                        equipment_analysis['compliant_equipment'] += 1
                        equipment_analysis['by_type'][equipment_type_name]['compliant'] += 1
                        
                except ValueError:
                    calibration_status = 'Invalid Calibration Date'
            
            # Track by criticality
            criticality = equipment_config.get('criticality', 'medium')
            equipment_analysis['by_criticality'][criticality] = equipment_analysis['by_criticality'].get(criticality, 0) + 1
            
            # Equipment detail record
            equipment_detail = {
                'equipment_id': equipment_id,
                'equipment_type': equipment_type_name,
                'serial_number': serial_number,
                'location': location,
                'calibration_status': calibration_status,
                'last_calibration_date': last_calibration_date.isoformat() if last_calibration_date else None,
                'next_calibration_due': next_calibration_due.isoformat() if next_calibration_due else None,
                'days_until_expiry': days_until_expiry,
                'criticality': criticality,
                'regulatory_requirement': equipment_config.get('regulatory_requirement', True),
                'calibration_frequency_days': equipment_config['calibration_frequency_days']
            }
            
            site_status['equipment_details'].append(equipment_detail)
            
            # Create alert if needed
            if alert_level and alert_level != 'notice':  # Create alerts for critical, urgent, warning, and expired
                alert_priority = 'critical' if equipment_config.get('criticality') == 'critical' else 'high'
                if alert_level == 'expired':
                    alert_priority = 'critical'
                
                site_info = site_lookup.get(site_id, {})
                calibration_alerts.append({
                    'alert_id': f"{site_id}_{equipment_id}_{alert_level}",
                    'priority': alert_priority,
                    'alert_level': alert_level,
                    'site_id': site_id,
                    'site_name': site_info.get('site_name', f'Site {site_id}'),
                    'equipment_id': equipment_id,
                    'equipment_type': equipment_type_name,
                    'serial_number': serial_number,
                    'location': location,
                    'calibration_due_date': next_calibration_due.isoformat() if next_calibration_due else None,
                    'days_overdue_or_until_due': abs(days_until_expiry) if days_until_expiry is not None else None,
                    'criticality': criticality,
                    'regulatory_requirement': equipment_config.get('regulatory_requirement', True),
                    'action_required': _get_calibration_action(alert_level, days_until_expiry, criticality),
                    'created_at': current_date.isoformat()
                })
        
        # Calculate site compliance percentages
        for site_data in site_equipment_status.values():
            if site_data['total_equipment'] > 0:
                site_data['compliance_percentage'] = round(
                    (site_data['compliant_equipment'] / site_data['total_equipment']) * 100, 1
                )
        
        # Sort alerts by priority and urgency
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        calibration_alerts.sort(key=lambda x: (
            priority_order.get(x['priority'], 99),
            x['days_overdue_or_until_due'] or 0
        ))
        
        # Generate insights
        insights = []
        
        # Overall compliance analysis
        overall_compliance_rate = (equipment_analysis['compliant_equipment'] / max(equipment_analysis['total_equipment'], 1)) * 100
        if overall_compliance_rate < 80:
            insights.append({
                'type': 'Low Overall Compliance',
                'finding': f"Overall calibration compliance is {overall_compliance_rate:.1f}%",
                'impact': 'Regulatory compliance risk and data integrity concerns',
                'recommendation': 'Implement systematic calibration management program'
            })
        
        # Critical equipment analysis
        critical_expired = len([
            alert for alert in calibration_alerts
            if alert['criticality'] == 'critical' and alert['alert_level'] == 'expired'
        ])
        
        if critical_expired > 0:
            insights.append({
                'type': 'Critical Equipment Expired',
                'finding': f"{critical_expired} critical equipment items have expired calibrations",
                'impact': 'Immediate regulatory compliance risk - equipment must be removed from service',
                'recommendation': 'Immediately remove from service and schedule emergency calibration'
            })
        
        # Site performance variation
        site_compliance_rates = [site['compliance_percentage'] for site in site_equipment_status.values()]
        if site_compliance_rates:
            min_compliance = min(site_compliance_rates)
            max_compliance = max(site_compliance_rates)
            
            if max_compliance - min_compliance > 30:  # >30% variation
                insights.append({
                    'type': 'Site Performance Variation',
                    'finding': f"Calibration compliance varies from {min_compliance:.1f}% to {max_compliance:.1f}% across sites",
                    'impact': 'Inconsistent calibration management practices',
                    'recommendation': 'Standardize calibration procedures and provide site training'
                })
        
        # Generate recommendations
        recommendations = []
        
        if equipment_analysis['expired_equipment'] > 0:
            recommendations.append(f"{equipment_analysis['expired_equipment']} equipment items have expired calibrations - immediate action required")
        
        critical_alerts = len([a for a in calibration_alerts if a['priority'] == 'critical'])
        if critical_alerts > 0:
            recommendations.append(f"{critical_alerts} critical calibration alerts require immediate attention")
        
        # Equipment type specific recommendations
        for equip_type, type_data in equipment_analysis['by_type'].items():
            if type_data['expired'] > 0:
                recommendations.append(f"{equip_type}: {type_data['expired']} expired items need immediate calibration")
        
        # Regulatory compliance recommendations
        regulatory_expired = len([
            alert for alert in calibration_alerts
            if alert['regulatory_requirement'] and alert['alert_level'] == 'expired'
        ])
        
        if regulatory_expired > 0:
            recommendations.append(f"{regulatory_expired} regulatory-required equipment items expired - compliance risk")
        
        # Generate calibration schedule for next 6 months
        upcoming_calibrations = {}
        for equipment_detail in [item for sublist in [site['equipment_details'] for site in site_equipment_status.values()] for item in sublist]:
            if equipment_detail['next_calibration_due']:
                try:
                    due_date = datetime.fromisoformat(equipment_detail['next_calibration_due'])
                    if due_date <= current_date + timedelta(days=180):  # Next 6 months
                        month_key = due_date.strftime('%Y-%m')
                        if month_key not in upcoming_calibrations:
                            upcoming_calibrations[month_key] = []
                        upcoming_calibrations[month_key].append({
                            'equipment_id': equipment_detail['equipment_id'],
                            'equipment_type': equipment_detail['equipment_type'],
                            'due_date': equipment_detail['next_calibration_due']
                        })
                except ValueError:
                    continue
        
        return {
            'success': True,
            'calibration_data': {
                'generated_at': current_date.isoformat(),
                'alert_thresholds': alert_thresholds,
                'overall_analysis': equipment_analysis,
                'site_equipment_status': site_equipment_status,
                'calibration_alerts': calibration_alerts[:50],  # Limit to top 50 alerts
                'upcoming_calibrations_by_month': dict(sorted(upcoming_calibrations.items())[:6]),
                'insights': insights,
                'recommendations': recommendations
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error tracking equipment calibration: {str(e)}'
        }

def _get_calibration_action(alert_level: str, days_until_expiry: int, criticality: str) -> str:
    """Generate action required text based on calibration status"""
    if alert_level == 'expired':
        if criticality == 'critical':
            return f"REMOVE FROM SERVICE - Expired {abs(days_until_expiry) if days_until_expiry else 0} days ago"
        else:
            return f"Schedule immediate calibration - Expired {abs(days_until_expiry) if days_until_expiry else 0} days ago"
    elif alert_level == 'critical':
        return f"Schedule calibration within {days_until_expiry} days - critical priority"
    elif alert_level == 'urgent':
        return f"Schedule calibration within {days_until_expiry} days"
    elif alert_level == 'warning':
        return f"Plan calibration - due in {days_until_expiry} days"
    else:
        return f"Monitor - due in {days_until_expiry} days"