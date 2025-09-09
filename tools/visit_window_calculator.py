"""
Visit Window Calculator Tool
Calculates protocol visit windows and validates visit compliance
Supports complex visit scheduling rules and deviation detection
"""

import csv
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from io import StringIO


def run(input_data: dict) -> dict:
    """
    Calculates visit windows and validates visit timing compliance
    
    Args:
        input_data: Dictionary containing:
            - visit_data: CSV data with visit information
            - protocol_schedule: Visit schedule definition
            - reference_date_field: Field to use as reference (default: 'enrollment_date')
            - window_type: 'strict' or 'flexible' (default: 'flexible')
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating if calculation succeeded
            - visit_windows: Calculated visit windows for each subject
            - compliance_report: Visit compliance analysis
            - errors: List of processing errors
            - warnings: List of processing warnings
            - statistics: Visit window statistics
    """
    try:
        visit_data = input_data.get('visit_data', '')
        protocol_schedule = input_data.get('protocol_schedule', {})
        reference_date_field = input_data.get('reference_date_field', 'enrollment_date')
        window_type = input_data.get('window_type', 'flexible')
        
        if not visit_data:
            return {
                'success': False,
                'visit_windows': {},
                'compliance_report': {},
                'errors': ['No visit data provided'],
                'warnings': [],
                'statistics': {}
            }
        
        if not protocol_schedule:
            return {
                'success': False,
                'visit_windows': {},
                'compliance_report': {},
                'errors': ['No protocol schedule provided'],
                'warnings': [],
                'statistics': {}
            }
        
        errors = []
        warnings = []
        
        # Parse visit data
        csv_reader = csv.DictReader(StringIO(visit_data))
        records = list(csv_reader)
        
        if not records:
            return {
                'success': False,
                'visit_windows': {},
                'compliance_report': {},
                'errors': ['Visit data is empty'],
                'warnings': [],
                'statistics': {}
            }
        
        # Group by subject
        subjects = {}
        for record in records:
            subject_id = record.get('subject_id', '').strip()
            if subject_id:
                if subject_id not in subjects:
                    subjects[subject_id] = []
                subjects[subject_id].append(record)
        
        # Calculate visit windows for each subject
        visit_windows = {}
        compliance_data = []
        
        for subject_id, subject_records in subjects.items():
            try:
                subject_windows = calculate_subject_windows(
                    subject_id, subject_records, protocol_schedule, 
                    reference_date_field, window_type
                )
                visit_windows[subject_id] = subject_windows
                
                # Analyze compliance
                compliance = analyze_visit_compliance(
                    subject_id, subject_records, subject_windows
                )
                compliance_data.append(compliance)
                
            except Exception as e:
                errors.append(f"Subject {subject_id}: {str(e)}")
        
        # Generate compliance report
        compliance_report = generate_compliance_report(compliance_data)
        
        # Generate statistics
        statistics = generate_statistics(visit_windows, compliance_data)
        
        return {
            'success': True,
            'visit_windows': visit_windows,
            'compliance_report': compliance_report,
            'errors': errors,
            'warnings': warnings,
            'statistics': statistics,
            'calculation_summary': {
                'total_subjects': len(subjects),
                'subjects_calculated': len(visit_windows),
                'window_type': window_type,
                'reference_field': reference_date_field
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'visit_windows': {},
            'compliance_report': {},
            'errors': [f"Visit window calculation failed: {str(e)}"],
            'warnings': [],
            'statistics': {}
        }


def calculate_subject_windows(subject_id: str, records: List[dict], 
                            protocol_schedule: dict, reference_date_field: str, 
                            window_type: str) -> dict:
    """Calculate visit windows for a single subject"""
    
    # Find reference date
    reference_date = None
    for record in records:
        if reference_date_field in record and record[reference_date_field]:
            try:
                reference_date = datetime.strptime(record[reference_date_field], '%Y-%m-%d')
                break
            except ValueError:
                try:
                    reference_date = datetime.strptime(record[reference_date_field], '%m/%d/%Y')
                    break
                except ValueError:
                    continue
    
    if not reference_date:
        raise ValueError(f"No valid reference date found in field '{reference_date_field}'")
    
    # Calculate windows for each visit
    windows = {}
    visits = protocol_schedule.get('visits', [])
    
    for visit in visits:
        visit_name = visit['name']
        day_offset = visit.get('day', 0)
        window_before = visit.get('window_before', 7)
        window_after = visit.get('window_after', 7)
        
        # Adjust windows based on type
        if window_type == 'strict':
            window_before = min(window_before, 3)
            window_after = min(window_after, 3)
        
        target_date = reference_date + timedelta(days=day_offset)
        earliest_date = target_date - timedelta(days=window_before)
        latest_date = target_date + timedelta(days=window_after)
        
        windows[visit_name] = {
            'target_date': target_date.strftime('%Y-%m-%d'),
            'earliest_date': earliest_date.strftime('%Y-%m-%d'),
            'latest_date': latest_date.strftime('%Y-%m-%d'),
            'window_days_before': window_before,
            'window_days_after': window_after,
            'protocol_day': day_offset
        }
    
    return {
        'reference_date': reference_date.strftime('%Y-%m-%d'),
        'windows': windows
    }


def analyze_visit_compliance(subject_id: str, records: List[dict], 
                           subject_windows: dict) -> dict:
    """Analyze visit compliance for a subject"""
    
    compliance = {
        'subject_id': subject_id,
        'total_visits_expected': len(subject_windows['windows']),
        'visits_completed': 0,
        'visits_on_time': 0,
        'visits_early': 0,
        'visits_late': 0,
        'visits_missed': 0,
        'visit_details': {},
        'overall_compliance_rate': 0.0
    }
    
    windows = subject_windows['windows']
    
    # Find actual visits
    actual_visits = {}
    for record in records:
        visit_name = record.get('visit_name', record.get('visit', '').strip())
        visit_date = record.get('visit_date', '').strip()
        if visit_name and visit_date:
            try:
                actual_visits[visit_name] = datetime.strptime(visit_date, '%Y-%m-%d')
            except ValueError:
                try:
                    actual_visits[visit_name] = datetime.strptime(visit_date, '%m/%d/%Y')
                except ValueError:
                    continue
    
    # Analyze each expected visit
    for visit_name, window in windows.items():
        target_date = datetime.strptime(window['target_date'], '%Y-%m-%d')
        earliest_date = datetime.strptime(window['earliest_date'], '%Y-%m-%d')
        latest_date = datetime.strptime(window['latest_date'], '%Y-%m-%d')
        
        visit_detail = {
            'expected': True,
            'completed': False,
            'compliance_status': 'missed',
            'days_deviation': None
        }
        
        if visit_name in actual_visits:
            actual_date = actual_visits[visit_name]
            visit_detail['completed'] = True
            visit_detail['actual_date'] = actual_date.strftime('%Y-%m-%d')
            compliance['visits_completed'] += 1
            
            # Calculate deviation
            deviation_days = (actual_date - target_date).days
            visit_detail['days_deviation'] = deviation_days
            
            # Determine compliance status
            if earliest_date <= actual_date <= latest_date:
                visit_detail['compliance_status'] = 'on_time'
                compliance['visits_on_time'] += 1
            elif actual_date < earliest_date:
                visit_detail['compliance_status'] = 'early'
                compliance['visits_early'] += 1
            else:
                visit_detail['compliance_status'] = 'late'
                compliance['visits_late'] += 1
        else:
            compliance['visits_missed'] += 1
        
        compliance['visit_details'][visit_name] = visit_detail
    
    # Calculate overall compliance rate
    if compliance['total_visits_expected'] > 0:
        compliance['overall_compliance_rate'] = (
            compliance['visits_on_time'] / compliance['total_visits_expected'] * 100
        )
    
    return compliance


def generate_compliance_report(compliance_data: List[dict]) -> dict:
    """Generate overall compliance report"""
    if not compliance_data:
        return {}
    
    total_subjects = len(compliance_data)
    
    # Aggregate statistics
    total_expected = sum(c['total_visits_expected'] for c in compliance_data)
    total_completed = sum(c['visits_completed'] for c in compliance_data)
    total_on_time = sum(c['visits_on_time'] for c in compliance_data)
    total_early = sum(c['visits_early'] for c in compliance_data)
    total_late = sum(c['visits_late'] for c in compliance_data)
    total_missed = sum(c['visits_missed'] for c in compliance_data)
    
    # Calculate rates
    completion_rate = (total_completed / total_expected * 100) if total_expected > 0 else 0
    on_time_rate = (total_on_time / total_expected * 100) if total_expected > 0 else 0
    
    # Subject-level analysis
    compliance_rates = [c['overall_compliance_rate'] for c in compliance_data]
    fully_compliant_subjects = sum(1 for rate in compliance_rates if rate >= 100)
    
    return {
        'summary': {
            'total_subjects': total_subjects,
            'total_visits_expected': total_expected,
            'total_visits_completed': total_completed,
            'completion_rate': round(completion_rate, 2),
            'on_time_rate': round(on_time_rate, 2)
        },
        'visit_status_counts': {
            'on_time': total_on_time,
            'early': total_early,
            'late': total_late,
            'missed': total_missed
        },
        'subject_compliance': {
            'fully_compliant': fully_compliant_subjects,
            'average_compliance_rate': round(sum(compliance_rates) / len(compliance_rates), 2) if compliance_rates else 0,
            'compliance_distribution': get_compliance_distribution(compliance_rates)
        }
    }


def get_compliance_distribution(rates: List[float]) -> dict:
    """Get distribution of compliance rates"""
    if not rates:
        return {}
    
    ranges = {
        '90-100%': sum(1 for r in rates if 90 <= r <= 100),
        '80-89%': sum(1 for r in rates if 80 <= r < 90),
        '70-79%': sum(1 for r in rates if 70 <= r < 80),
        '60-69%': sum(1 for r in rates if 60 <= r < 70),
        '<60%': sum(1 for r in rates if r < 60)
    }
    
    return ranges


def generate_statistics(visit_windows: dict, compliance_data: List[dict]) -> dict:
    """Generate visit window statistics"""
    if not visit_windows or not compliance_data:
        return {}
    
    # Window statistics
    all_windows = []
    for subject_windows in visit_windows.values():
        for window in subject_windows['windows'].values():
            all_windows.append({
                'window_before': window['window_days_before'],
                'window_after': window['window_days_after'],
                'total_window': window['window_days_before'] + window['window_days_after']
            })
    
    avg_window_before = sum(w['window_before'] for w in all_windows) / len(all_windows) if all_windows else 0
    avg_window_after = sum(w['window_after'] for w in all_windows) / len(all_windows) if all_windows else 0
    
    # Deviation statistics
    deviations = []
    for compliance in compliance_data:
        for visit_detail in compliance['visit_details'].values():
            if visit_detail['days_deviation'] is not None:
                deviations.append(abs(visit_detail['days_deviation']))
    
    avg_deviation = sum(deviations) / len(deviations) if deviations else 0
    
    return {
        'window_configuration': {
            'average_window_before_days': round(avg_window_before, 1),
            'average_window_after_days': round(avg_window_after, 1),
            'total_visit_windows_calculated': len(all_windows)
        },
        'compliance_performance': {
            'average_deviation_days': round(avg_deviation, 1),
            'subjects_with_deviations': sum(1 for c in compliance_data if c['visits_early'] + c['visits_late'] > 0),
            'total_protocol_deviations': sum(c['visits_early'] + c['visits_late'] for c in compliance_data)
        }
    }