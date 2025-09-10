"""
Patient Diary Compliance Checker Tool
AI-powered monitoring of electronic patient-reported outcome (ePRO) compliance
"""

from typing import Dict, List, Any
import re
from datetime import datetime, timedelta
from collections import Counter

def run(input_data: Dict) -> Dict:
    """
    Monitor and analyze patient diary compliance for ePRO data collection with AI-powered insights.
    
    Example:
        Input: Patient diary entries, completion schedule, and compliance thresholds
        Output: Compliance analysis with quality assessment, risk identification, and intervention recommendations
    
    Parameters:
        diary_data : list
            Patient diary entries and completion records
        study_schedule : dict
            Expected diary completion schedule and frequency
        compliance_thresholds : dict, optional
            Compliance rate thresholds for alert levels
        patient_population : list, optional
            Patient demographic and baseline data for analysis
        reminder_settings : dict, optional
            Reminder and notification configuration
        quality_criteria : dict, optional
            Data quality assessment criteria and standards
    """
    try:
        diary_data = input_data.get('diary_data', [])
        study_schedule = input_data.get('study_schedule', {})
        compliance_thresholds = input_data.get('compliance_thresholds', {
            'excellent': 95, 'good': 85, 'acceptable': 70, 'poor': 50
        })
        patient_population = input_data.get('patient_population', [])
        reminder_settings = input_data.get('reminder_settings', {})
        quality_criteria = input_data.get('quality_criteria', {})
        
        if not diary_data:
            return {
                'success': False,
                'error': 'No diary data provided for compliance analysis'
            }
        
        # Process and validate diary data
        processed_entries = process_diary_entries(diary_data)
        
        # Analyze compliance patterns
        compliance_analysis = analyze_compliance_patterns(
            processed_entries, study_schedule, compliance_thresholds
        )
        
        # Assess data quality
        quality_assessment = assess_diary_data_quality(
            processed_entries, quality_criteria
        )
        
        # Identify compliance issues and patterns
        compliance_issues = identify_compliance_issues(
            processed_entries, compliance_analysis, study_schedule
        )
        
        # Analyze patient behavior patterns
        behavior_patterns = analyze_patient_behavior_patterns(
            processed_entries, patient_population
        )
        
        # Generate compliance alerts
        alerts = generate_compliance_alerts(
            compliance_analysis, compliance_issues, compliance_thresholds
        )
        
        # Create intervention recommendations
        interventions = recommend_interventions(
            compliance_issues, behavior_patterns, reminder_settings
        )
        
        # Generate compliance metrics
        metrics = calculate_compliance_metrics(
            processed_entries, study_schedule, patient_population
        )
        
        # Trend analysis
        trend_analysis = analyze_compliance_trends(processed_entries, study_schedule)
        
        return {
            'success': True,
            'compliance_summary': {
                'total_patients': len(set(entry['patient_id'] for entry in processed_entries)),
                'total_diary_entries': len(processed_entries),
                'overall_compliance_rate': compliance_analysis['overall_compliance'],
                'data_quality_score': quality_assessment['overall_score'],
                'analysis_date': datetime.now().isoformat()
            },
            'compliance_analysis': compliance_analysis,
            'quality_assessment': quality_assessment,
            'compliance_issues': compliance_issues,
            'behavior_patterns': behavior_patterns,
            'alerts': alerts,
            'intervention_recommendations': interventions,
            'compliance_metrics': metrics,
            'trend_analysis': trend_analysis,
            'patient_segments': segment_patients_by_compliance(
                processed_entries, compliance_analysis, patient_population
            ),
            'reporting': {
                'compliance_dashboard_data': create_dashboard_data(compliance_analysis, metrics),
                'export_recommendations': generate_export_recommendations(compliance_analysis)
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error analyzing diary compliance: {str(e)}'
        }

def process_diary_entries(diary_data: List[Dict]) -> List[Dict]:
    """Process and standardize diary entry data."""
    processed_entries = []
    
    for entry in diary_data:
        if isinstance(entry, dict):
            processed_entry = {
                'patient_id': str(entry.get('patient_id', 'Unknown')),
                'entry_date': parse_date(entry.get('entry_date')),
                'completion_time': parse_time(entry.get('completion_time')),
                'diary_type': entry.get('diary_type', 'daily'),
                'questions_answered': entry.get('questions_answered', 0),
                'total_questions': entry.get('total_questions', 0),
                'completion_status': entry.get('completion_status', 'incomplete'),
                'data_quality_flags': entry.get('data_quality_flags', []),
                'response_time_minutes': entry.get('response_time_minutes', 0),
                'device_type': entry.get('device_type', 'unknown'),
                'location': entry.get('location', 'unknown'),
                'entry_method': entry.get('entry_method', 'manual'),
                'reminder_count': entry.get('reminder_count', 0),
                'late_entry': entry.get('late_entry', False),
                'partial_completion': entry.get('partial_completion', False),
                'symptom_scores': entry.get('symptom_scores', {}),
                'quality_of_life_scores': entry.get('quality_of_life_scores', {}),
                'medication_compliance': entry.get('medication_compliance', {}),
                'adverse_events_reported': entry.get('adverse_events_reported', []),
                'original_data': entry  # Keep original for reference
            }
            
            # Calculate completion percentage
            if processed_entry['total_questions'] > 0:
                processed_entry['completion_percentage'] = (
                    processed_entry['questions_answered'] / processed_entry['total_questions'] * 100
                )
            else:
                processed_entry['completion_percentage'] = 0
            
            # Determine if entry is timely
            processed_entry['timely_completion'] = not processed_entry['late_entry']
            
            processed_entries.append(processed_entry)
    
    # Sort by patient_id and entry_date
    processed_entries.sort(key=lambda x: (x['patient_id'], x['entry_date'] or datetime.min))
    
    return processed_entries

def parse_date(date_input: Any) -> datetime:
    """Parse date input into datetime object."""
    if isinstance(date_input, datetime):
        return date_input
    elif isinstance(date_input, str):
        # Try common date formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S']:
            try:
                return datetime.strptime(date_input, fmt)
            except ValueError:
                continue
    
    return None

def parse_time(time_input: Any) -> datetime:
    """Parse time input into datetime object."""
    if isinstance(time_input, datetime):
        return time_input
    elif isinstance(time_input, str):
        try:
            # Try to parse time string
            return datetime.strptime(time_input, '%H:%M:%S')
        except ValueError:
            try:
                return datetime.strptime(time_input, '%H:%M')
            except ValueError:
                pass
    
    return None

def analyze_compliance_patterns(processed_entries: List[Dict], study_schedule: Dict, 
                              thresholds: Dict) -> Dict:
    """Analyze overall compliance patterns across patients."""
    analysis = {
        'overall_compliance': 0.0,
        'patient_compliance_rates': {},
        'daily_compliance_rates': {},
        'weekly_compliance_rates': {},
        'monthly_compliance_rates': {},
        'compliance_by_diary_type': {},
        'compliance_distribution': {},
        'temporal_patterns': {}
    }
    
    if not processed_entries:
        return analysis
    
    # Group entries by patient
    patient_entries = {}
    for entry in processed_entries:
        patient_id = entry['patient_id']
        if patient_id not in patient_entries:
            patient_entries[patient_id] = []
        patient_entries[patient_id].append(entry)
    
    # Calculate patient-level compliance rates
    total_compliance = 0
    for patient_id, entries in patient_entries.items():
        complete_entries = sum(1 for entry in entries if entry['completion_status'] == 'complete')
        expected_entries = len(entries) if not study_schedule else calculate_expected_entries(
            patient_id, study_schedule, entries
        )
        
        if expected_entries > 0:
            compliance_rate = (complete_entries / expected_entries) * 100
            analysis['patient_compliance_rates'][patient_id] = compliance_rate
            total_compliance += compliance_rate
    
    # Overall compliance rate
    if patient_entries:
        analysis['overall_compliance'] = round(total_compliance / len(patient_entries), 2)
    
    # Daily compliance rates
    daily_entries = {}
    for entry in processed_entries:
        if entry['entry_date']:
            date_key = entry['entry_date'].strftime('%Y-%m-%d')
            if date_key not in daily_entries:
                daily_entries[date_key] = {'complete': 0, 'total': 0}
            daily_entries[date_key]['total'] += 1
            if entry['completion_status'] == 'complete':
                daily_entries[date_key]['complete'] += 1
    
    for date, counts in daily_entries.items():
        if counts['total'] > 0:
            analysis['daily_compliance_rates'][date] = round(
                (counts['complete'] / counts['total']) * 100, 2
            )
    
    # Compliance by diary type
    diary_type_compliance = {}
    for entry in processed_entries:
        diary_type = entry['diary_type']
        if diary_type not in diary_type_compliance:
            diary_type_compliance[diary_type] = {'complete': 0, 'total': 0}
        
        diary_type_compliance[diary_type]['total'] += 1
        if entry['completion_status'] == 'complete':
            diary_type_compliance[diary_type]['complete'] += 1
    
    for diary_type, counts in diary_type_compliance.items():
        if counts['total'] > 0:
            analysis['compliance_by_diary_type'][diary_type] = round(
                (counts['complete'] / counts['total']) * 100, 2
            )
    
    # Compliance distribution
    compliance_ranges = {
        'excellent': (thresholds.get('excellent', 95), 100),
        'good': (thresholds.get('good', 85), thresholds.get('excellent', 95)),
        'acceptable': (thresholds.get('acceptable', 70), thresholds.get('good', 85)),
        'poor': (0, thresholds.get('acceptable', 70))
    }
    
    distribution = {range_name: 0 for range_name in compliance_ranges.keys()}
    
    for patient_id, compliance_rate in analysis['patient_compliance_rates'].items():
        for range_name, (min_rate, max_rate) in compliance_ranges.items():
            if min_rate <= compliance_rate < max_rate:
                distribution[range_name] += 1
                break
    
    analysis['compliance_distribution'] = distribution
    
    # Temporal patterns (day of week, time of day)
    analysis['temporal_patterns'] = analyze_temporal_patterns(processed_entries)
    
    return analysis

def calculate_expected_entries(patient_id: str, study_schedule: Dict, entries: List[Dict]) -> int:
    """Calculate expected number of diary entries for a patient based on study schedule."""
    if not study_schedule or not entries:
        return len(entries)  # Default to actual entries if no schedule provided
    
    # Get patient's study period
    first_entry = min(entries, key=lambda x: x['entry_date'] or datetime.max)['entry_date']
    last_entry = max(entries, key=lambda x: x['entry_date'] or datetime.min)['entry_date']
    
    if not first_entry or not last_entry:
        return len(entries)
    
    # Calculate expected entries based on diary frequency
    diary_frequency = study_schedule.get('diary_frequency', 'daily')
    study_days = (last_entry - first_entry).days + 1
    
    if diary_frequency == 'daily':
        return study_days
    elif diary_frequency == 'weekly':
        return max(1, study_days // 7)
    elif diary_frequency == 'monthly':
        return max(1, study_days // 30)
    else:
        return len(entries)

def analyze_temporal_patterns(processed_entries: List[Dict]) -> Dict:
    """Analyze temporal patterns in diary completion."""
    patterns = {
        'day_of_week': {},
        'hour_of_day': {},
        'completion_time_distribution': {},
        'weekend_vs_weekday': {'weekday': 0, 'weekend': 0}
    }
    
    # Day of week analysis
    day_counts = {i: {'complete': 0, 'total': 0} for i in range(7)}  # 0=Monday, 6=Sunday
    
    for entry in processed_entries:
        if entry['entry_date']:
            day_of_week = entry['entry_date'].weekday()
            day_counts[day_of_week]['total'] += 1
            
            if entry['completion_status'] == 'complete':
                day_counts[day_of_week]['complete'] += 1
    
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i, day_name in enumerate(day_names):
        if day_counts[i]['total'] > 0:
            patterns['day_of_week'][day_name] = round(
                (day_counts[i]['complete'] / day_counts[i]['total']) * 100, 2
            )
    
    # Hour of day analysis (if completion time available)
    hour_counts = {i: {'complete': 0, 'total': 0} for i in range(24)}
    
    for entry in processed_entries:
        if entry['completion_time']:
            hour = entry['completion_time'].hour
            hour_counts[hour]['total'] += 1
            
            if entry['completion_status'] == 'complete':
                hour_counts[hour]['complete'] += 1
    
    for hour in range(24):
        if hour_counts[hour]['total'] > 0:
            patterns['hour_of_day'][f"{hour:02d}:00"] = round(
                (hour_counts[hour]['complete'] / hour_counts[hour]['total']) * 100, 2
            )
    
    # Weekend vs weekday
    for entry in processed_entries:
        if entry['entry_date']:
            is_weekend = entry['entry_date'].weekday() >= 5
            if is_weekend:
                patterns['weekend_vs_weekday']['weekend'] += 1
            else:
                patterns['weekend_vs_weekday']['weekday'] += 1
    
    return patterns

def assess_diary_data_quality(processed_entries: List[Dict], quality_criteria: Dict) -> Dict:
    """Assess the quality of diary data entries."""
    assessment = {
        'overall_score': 0.0,
        'completeness_score': 0.0,
        'timeliness_score': 0.0,
        'consistency_score': 0.0,
        'validity_score': 0.0,
        'quality_issues': [],
        'data_quality_by_patient': {},
        'improvement_areas': []
    }
    
    if not processed_entries:
        return assessment
    
    total_entries = len(processed_entries)
    quality_scores = []
    
    # Completeness assessment
    complete_entries = sum(1 for entry in processed_entries 
                          if entry['completion_status'] == 'complete')
    assessment['completeness_score'] = (complete_entries / total_entries) * 100 if total_entries > 0 else 0
    
    # Timeliness assessment
    timely_entries = sum(1 for entry in processed_entries 
                        if entry['timely_completion'])
    assessment['timeliness_score'] = (timely_entries / total_entries) * 100 if total_entries > 0 else 0
    
    # Consistency assessment (based on data quality flags)
    entries_without_flags = sum(1 for entry in processed_entries 
                               if not entry['data_quality_flags'])
    assessment['consistency_score'] = (entries_without_flags / total_entries) * 100 if total_entries > 0 else 0
    
    # Validity assessment (response time reasonableness)
    reasonable_response_times = sum(1 for entry in processed_entries 
                                   if 1 <= entry['response_time_minutes'] <= 60)  # 1-60 minutes reasonable
    assessment['validity_score'] = (reasonable_response_times / total_entries) * 100 if total_entries > 0 else 0
    
    # Overall score (weighted average)
    weights = {
        'completeness': 0.4,
        'timeliness': 0.3,
        'consistency': 0.2,
        'validity': 0.1
    }
    
    assessment['overall_score'] = (
        assessment['completeness_score'] * weights['completeness'] +
        assessment['timeliness_score'] * weights['timeliness'] +
        assessment['consistency_score'] * weights['consistency'] +
        assessment['validity_score'] * weights['validity']
    )
    
    # Identify quality issues
    if assessment['completeness_score'] < 80:
        assessment['quality_issues'].append("Low completion rate")
        assessment['improvement_areas'].append("Improve patient engagement and reminder systems")
    
    if assessment['timeliness_score'] < 70:
        assessment['quality_issues'].append("Frequent late entries")
        assessment['improvement_areas'].append("Enhance reminder timing and frequency")
    
    if assessment['consistency_score'] < 85:
        assessment['quality_issues'].append("Data consistency concerns")
        assessment['improvement_areas'].append("Implement additional data validation checks")
    
    # Patient-level quality assessment
    patient_entries = {}
    for entry in processed_entries:
        patient_id = entry['patient_id']
        if patient_id not in patient_entries:
            patient_entries[patient_id] = []
        patient_entries[patient_id].append(entry)
    
    for patient_id, entries in patient_entries.items():
        patient_complete = sum(1 for e in entries if e['completion_status'] == 'complete')
        patient_timely = sum(1 for e in entries if e['timely_completion'])
        
        patient_score = (
            (patient_complete / len(entries)) * 0.6 +
            (patient_timely / len(entries)) * 0.4
        ) * 100
        
        assessment['data_quality_by_patient'][patient_id] = round(patient_score, 2)
    
    return assessment

def identify_compliance_issues(processed_entries: List[Dict], compliance_analysis: Dict, 
                             study_schedule: Dict) -> List[Dict]:
    """Identify specific compliance issues and patterns."""
    issues = []
    
    # Low overall compliance
    if compliance_analysis['overall_compliance'] < 70:
        issues.append({
            'type': 'low_overall_compliance',
            'severity': 'high',
            'description': f"Overall compliance rate is {compliance_analysis['overall_compliance']:.1f}%",
            'affected_patients': len(compliance_analysis['patient_compliance_rates']),
            'recommendation': 'Implement comprehensive intervention strategy'
        })
    
    # Identify non-compliant patients
    non_compliant_patients = [
        patient_id for patient_id, rate in compliance_analysis['patient_compliance_rates'].items()
        if rate < 50
    ]
    
    if non_compliant_patients:
        issues.append({
            'type': 'non_compliant_patients',
            'severity': 'high',
            'description': f"{len(non_compliant_patients)} patients with <50% compliance",
            'affected_patients': non_compliant_patients,
            'recommendation': 'Individual patient outreach and intervention required'
        })
    
    # Declining compliance trends
    daily_rates = list(compliance_analysis['daily_compliance_rates'].values())
    if len(daily_rates) >= 7:
        recent_avg = sum(daily_rates[-7:]) / 7
        earlier_avg = sum(daily_rates[:7]) / 7
        
        if recent_avg < earlier_avg - 10:  # 10% decline
            issues.append({
                'type': 'declining_compliance',
                'severity': 'medium',
                'description': f"Compliance declined from {earlier_avg:.1f}% to {recent_avg:.1f}%",
                'affected_patients': 'all_active_patients',
                'recommendation': 'Review and enhance engagement strategies'
            })
    
    # Missing data patterns
    missing_entries = [entry for entry in processed_entries 
                      if entry['completion_status'] == 'incomplete']
    
    if len(missing_entries) > len(processed_entries) * 0.3:  # >30% missing
        issues.append({
            'type': 'high_missing_data',
            'severity': 'high',
            'description': f"{len(missing_entries)} incomplete entries ({len(missing_entries)/len(processed_entries)*100:.1f}%)",
            'affected_patients': len(set(entry['patient_id'] for entry in missing_entries)),
            'recommendation': 'Investigate barriers to diary completion'
        })
    
    # Late entry patterns
    late_entries = [entry for entry in processed_entries if entry['late_entry']]
    if len(late_entries) > len(processed_entries) * 0.4:  # >40% late
        issues.append({
            'type': 'frequent_late_entries',
            'severity': 'medium',
            'description': f"{len(late_entries)} late entries ({len(late_entries)/len(processed_entries)*100:.1f}%)",
            'affected_patients': len(set(entry['patient_id'] for entry in late_entries)),
            'recommendation': 'Optimize reminder timing and frequency'
        })
    
    # Device-related issues
    device_problems = [entry for entry in processed_entries 
                      if 'device_error' in entry['data_quality_flags']]
    if device_problems:
        issues.append({
            'type': 'device_technical_issues',
            'severity': 'medium',
            'description': f"{len(device_problems)} entries with device errors",
            'affected_patients': len(set(entry['patient_id'] for entry in device_problems)),
            'recommendation': 'Provide technical support and device troubleshooting'
        })
    
    return issues

def analyze_patient_behavior_patterns(processed_entries: List[Dict], 
                                    patient_population: List[Dict]) -> Dict:
    """Analyze patient behavior patterns related to diary compliance."""
    patterns = {
        'completion_time_patterns': {},
        'reminder_response_patterns': {},
        'compliance_by_demographics': {},
        'engagement_patterns': {},
        'dropout_risk_factors': []
    }
    
    # Group entries by patient
    patient_entries = {}
    for entry in processed_entries:
        patient_id = entry['patient_id']
        if patient_id not in patient_entries:
            patient_entries[patient_id] = []
        patient_entries[patient_id].append(entry)
    
    # Completion time patterns
    completion_times = []
    for entry in processed_entries:
        if entry['completion_time']:
            completion_times.append(entry['completion_time'].hour)
    
    if completion_times:
        time_counter = Counter(completion_times)
        patterns['completion_time_patterns'] = {
            'peak_hours': [hour for hour, count in time_counter.most_common(3)],
            'average_completion_hour': sum(completion_times) / len(completion_times),
            'completion_time_distribution': dict(time_counter)
        }
    
    # Reminder response patterns
    reminder_responses = []
    for entry in processed_entries:
        if entry['reminder_count'] > 0:
            reminder_responses.append({
                'reminders_needed': entry['reminder_count'],
                'completed': entry['completion_status'] == 'complete'
            })
    
    if reminder_responses:
        avg_reminders = sum(r['reminders_needed'] for r in reminder_responses) / len(reminder_responses)
        response_after_reminders = sum(1 for r in reminder_responses if r['completed']) / len(reminder_responses)
        
        patterns['reminder_response_patterns'] = {
            'average_reminders_needed': round(avg_reminders, 2),
            'response_rate_after_reminders': round(response_after_reminders * 100, 2),
            'patients_requiring_multiple_reminders': len([r for r in reminder_responses if r['reminders_needed'] > 1])
        }
    
    # Compliance by demographics (if demographic data available)
    if patient_population:
        demo_compliance = analyze_demographic_compliance(patient_entries, patient_population)
        patterns['compliance_by_demographics'] = demo_compliance
    
    # Engagement patterns
    engagement_metrics = {}
    for patient_id, entries in patient_entries.items():
        if entries:
            avg_response_time = sum(e['response_time_minutes'] for e in entries if e['response_time_minutes'] > 0)
            if avg_response_time > 0:
                avg_response_time /= len([e for e in entries if e['response_time_minutes'] > 0])
                engagement_metrics[patient_id] = {
                    'avg_response_time': round(avg_response_time, 2),
                    'completion_streak': calculate_completion_streak(entries),
                    'engagement_score': calculate_engagement_score(entries)
                }
    
    patterns['engagement_patterns'] = engagement_metrics
    
    # Dropout risk factors
    patterns['dropout_risk_factors'] = identify_dropout_risk_factors(patient_entries)
    
    return patterns

def analyze_demographic_compliance(patient_entries: Dict, patient_population: List[Dict]) -> Dict:
    """Analyze compliance patterns by demographic characteristics."""
    demographic_analysis = {}
    
    # Create patient demographic lookup
    demo_lookup = {}
    for patient in patient_population:
        demo_lookup[str(patient.get('patient_id', ''))] = patient
    
    # Analyze by age groups
    age_compliance = {'<30': [], '30-50': [], '50-65': [], '>65': []}
    
    for patient_id, entries in patient_entries.items():
        patient_demo = demo_lookup.get(patient_id, {})
        age = patient_demo.get('age', 0)
        
        if age > 0:
            compliance_rate = sum(1 for e in entries if e['completion_status'] == 'complete') / len(entries) * 100
            
            if age < 30:
                age_compliance['<30'].append(compliance_rate)
            elif age < 50:
                age_compliance['30-50'].append(compliance_rate)
            elif age < 65:
                age_compliance['50-65'].append(compliance_rate)
            else:
                age_compliance['>65'].append(compliance_rate)
    
    demographic_analysis['age_groups'] = {}
    for age_group, rates in age_compliance.items():
        if rates:
            demographic_analysis['age_groups'][age_group] = {
                'average_compliance': round(sum(rates) / len(rates), 2),
                'patient_count': len(rates)
            }
    
    # Analyze by gender
    gender_compliance = {'male': [], 'female': [], 'other': []}
    
    for patient_id, entries in patient_entries.items():
        patient_demo = demo_lookup.get(patient_id, {})
        gender = patient_demo.get('gender', 'unknown').lower()
        
        if gender in gender_compliance:
            compliance_rate = sum(1 for e in entries if e['completion_status'] == 'complete') / len(entries) * 100
            gender_compliance[gender].append(compliance_rate)
    
    demographic_analysis['gender'] = {}
    for gender, rates in gender_compliance.items():
        if rates:
            demographic_analysis['gender'][gender] = {
                'average_compliance': round(sum(rates) / len(rates), 2),
                'patient_count': len(rates)
            }
    
    return demographic_analysis

def calculate_completion_streak(entries: List[Dict]) -> int:
    """Calculate the current completion streak for a patient."""
    if not entries:
        return 0
    
    # Sort by date
    sorted_entries = sorted(entries, key=lambda x: x['entry_date'] or datetime.min, reverse=True)
    
    streak = 0
    for entry in sorted_entries:
        if entry['completion_status'] == 'complete':
            streak += 1
        else:
            break
    
    return streak

def calculate_engagement_score(entries: List[Dict]) -> float:
    """Calculate an engagement score based on multiple factors."""
    if not entries:
        return 0.0
    
    # Factors: completion rate, timeliness, response time, reminder dependency
    completion_rate = sum(1 for e in entries if e['completion_status'] == 'complete') / len(entries)
    timeliness_rate = sum(1 for e in entries if e['timely_completion']) / len(entries)
    
    # Response time score (faster is better, up to reasonable limit)
    response_times = [e['response_time_minutes'] for e in entries if e['response_time_minutes'] > 0]
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        response_time_score = max(0, min(1, (30 - avg_response_time) / 30))  # 30 min ideal
    else:
        response_time_score = 0.5  # neutral if no data
    
    # Reminder dependency (fewer reminders is better)
    reminder_counts = [e['reminder_count'] for e in entries]
    avg_reminders = sum(reminder_counts) / len(reminder_counts)
    reminder_score = max(0, min(1, (3 - avg_reminders) / 3))  # 0 reminders ideal
    
    # Weighted engagement score
    engagement_score = (
        completion_rate * 0.4 +
        timeliness_rate * 0.3 +
        response_time_score * 0.2 +
        reminder_score * 0.1
    ) * 100
    
    return round(engagement_score, 2)

def identify_dropout_risk_factors(patient_entries: Dict) -> List[Dict]:
    """Identify factors that may indicate dropout risk."""
    risk_factors = []
    
    for patient_id, entries in patient_entries.items():
        if len(entries) < 3:  # Too few entries to assess
            continue
        
        # Recent entries (last 7 days or last 25% of entries)
        sorted_entries = sorted(entries, key=lambda x: x['entry_date'] or datetime.min, reverse=True)
        recent_count = max(3, len(entries) // 4)
        recent_entries = sorted_entries[:recent_count]
        
        # Calculate recent compliance
        recent_compliance = sum(1 for e in recent_entries if e['completion_status'] == 'complete') / len(recent_entries)
        
        # Overall compliance
        overall_compliance = sum(1 for e in entries if e['completion_status'] == 'complete') / len(entries)
        
        # Check for declining pattern
        if recent_compliance < overall_compliance - 0.3:  # 30% decline
            risk_factors.append({
                'patient_id': patient_id,
                'risk_type': 'declining_compliance',
                'severity': 'high',
                'recent_compliance': round(recent_compliance * 100, 2),
                'overall_compliance': round(overall_compliance * 100, 2),
                'recommendation': 'Immediate intervention required'
            })
        
        # Check for increasing reminder dependency
        recent_avg_reminders = sum(e['reminder_count'] for e in recent_entries) / len(recent_entries)
        overall_avg_reminders = sum(e['reminder_count'] for e in entries) / len(entries)
        
        if recent_avg_reminders > overall_avg_reminders + 1:  # Needing more reminders
            risk_factors.append({
                'patient_id': patient_id,
                'risk_type': 'increasing_reminder_dependency',
                'severity': 'medium',
                'recent_avg_reminders': round(recent_avg_reminders, 2),
                'overall_avg_reminders': round(overall_avg_reminders, 2),
                'recommendation': 'Enhanced engagement strategy needed'
            })
        
        # Check for extended periods without entries
        gaps = calculate_entry_gaps(entries)
        long_gaps = [gap for gap in gaps if gap > 3]  # 3+ day gaps
        
        if len(long_gaps) > len(entries) * 0.2:  # >20% of periods have long gaps
            risk_factors.append({
                'patient_id': patient_id,
                'risk_type': 'frequent_long_gaps',
                'severity': 'medium',
                'long_gap_count': len(long_gaps),
                'max_gap_days': max(long_gaps) if long_gaps else 0,
                'recommendation': 'Investigate barriers to regular completion'
            })
    
    return risk_factors

def calculate_entry_gaps(entries: List[Dict]) -> List[int]:
    """Calculate gaps between consecutive diary entries."""
    if len(entries) < 2:
        return []
    
    sorted_entries = sorted([e for e in entries if e['entry_date']], 
                           key=lambda x: x['entry_date'])
    
    gaps = []
    for i in range(1, len(sorted_entries)):
        gap_days = (sorted_entries[i]['entry_date'] - sorted_entries[i-1]['entry_date']).days
        gaps.append(gap_days)
    
    return gaps

def generate_compliance_alerts(compliance_analysis: Dict, compliance_issues: List[Dict], 
                             thresholds: Dict) -> List[Dict]:
    """Generate compliance alerts based on analysis results."""
    alerts = []
    
    # Critical compliance alerts
    if compliance_analysis['overall_compliance'] < thresholds.get('poor', 50):
        alerts.append({
            'level': 'critical',
            'type': 'overall_compliance',
            'title': 'Critical: Overall Compliance Below Threshold',
            'message': f"Overall compliance rate of {compliance_analysis['overall_compliance']:.1f}% is below acceptable threshold",
            'action_required': True,
            'recommended_actions': [
                'Immediate study team review required',
                'Implement emergency intervention protocol',
                'Consider study design modifications'
            ]
        })
    
    # High-priority patient alerts
    poor_compliance_patients = [
        pid for pid, rate in compliance_analysis['patient_compliance_rates'].items()
        if rate < thresholds.get('acceptable', 70)
    ]
    
    if poor_compliance_patients:
        alerts.append({
            'level': 'high',
            'type': 'patient_compliance',
            'title': f'{len(poor_compliance_patients)} Patients Below Compliance Threshold',
            'message': f"Patients with <{thresholds.get('acceptable', 70)}% compliance require intervention",
            'action_required': True,
            'affected_patients': poor_compliance_patients,
            'recommended_actions': [
                'Individual patient outreach',
                'Review and address barriers',
                'Consider personalized intervention strategies'
            ]
        })
    
    # Quality-based alerts
    for issue in compliance_issues:
        if issue['severity'] == 'high':
            alerts.append({
                'level': 'high',
                'type': issue['type'],
                'title': f"Quality Issue: {issue['type'].replace('_', ' ').title()}",
                'message': issue['description'],
                'action_required': True,
                'recommended_actions': [issue['recommendation']]
            })
    
    # Trend-based alerts
    daily_rates = list(compliance_analysis['daily_compliance_rates'].values())
    if len(daily_rates) >= 7:
        recent_trend = sum(daily_rates[-3:]) / 3 - sum(daily_rates[-7:-3]) / 4
        if recent_trend < -5:  # 5% decline
            alerts.append({
                'level': 'medium',
                'type': 'declining_trend',
                'title': 'Declining Compliance Trend Detected',
                'message': f"Compliance has declined by {abs(recent_trend):.1f}% in recent days",
                'action_required': False,
                'recommended_actions': [
                    'Monitor trend closely',
                    'Review recent changes in study procedures',
                    'Consider proactive interventions'
                ]
            })
    
    return alerts

def recommend_interventions(compliance_issues: List[Dict], behavior_patterns: Dict, 
                          reminder_settings: Dict) -> List[Dict]:
    """Recommend specific interventions based on compliance analysis."""
    interventions = []
    
    # Technology-based interventions
    if any(issue['type'] == 'frequent_late_entries' for issue in compliance_issues):
        interventions.append({
            'category': 'technology',
            'intervention': 'Optimize Reminder System',
            'description': 'Adjust reminder timing and frequency based on patient behavior patterns',
            'implementation': [
                'Analyze peak completion times from behavior patterns',
                'Set personalized reminder schedules',
                'Implement progressive reminder escalation'
            ],
            'expected_impact': 'Reduce late entries by 20-30%',
            'priority': 'high'
        })
    
    # Personalized interventions
    if any(issue['type'] == 'non_compliant_patients' for issue in compliance_issues):
        interventions.append({
            'category': 'personalized',
            'intervention': 'Individual Patient Support',
            'description': 'Provide targeted support for patients with poor compliance',
            'implementation': [
                'Conduct one-on-one patient interviews',
                'Identify specific barriers to completion',
                'Develop personalized compliance strategies',
                'Provide additional training if needed'
            ],
            'expected_impact': 'Improve individual compliance by 40-50%',
            'priority': 'high'
        })
    
    # Educational interventions
    if behavior_patterns.get('engagement_patterns'):
        low_engagement_patients = [
            pid for pid, metrics in behavior_patterns['engagement_patterns'].items()
            if metrics['engagement_score'] < 50
        ]
        
        if low_engagement_patients:
            interventions.append({
                'category': 'educational',
                'intervention': 'Enhanced Patient Education',
                'description': 'Provide additional education on diary importance and completion',
                'implementation': [
                    'Develop patient education materials',
                    'Conduct webinar sessions on diary importance',
                    'Create video tutorials for diary completion',
                    'Implement gamification elements'
                ],
                'expected_impact': 'Increase engagement scores by 25-35%',
                'priority': 'medium'
            })
    
    # Process improvements
    if any(issue['type'] == 'device_technical_issues' for issue in compliance_issues):
        interventions.append({
            'category': 'process',
            'intervention': 'Technical Support Enhancement',
            'description': 'Improve technical support for patients experiencing device issues',
            'implementation': [
                'Establish dedicated technical support hotline',
                'Create troubleshooting guides',
                'Provide backup devices for critical patients',
                'Implement proactive device monitoring'
            ],
            'expected_impact': 'Reduce technical barriers by 60-70%',
            'priority': 'high'
        })
    
    # Communication interventions
    interventions.append({
        'category': 'communication',
        'intervention': 'Improved Patient Communication',
        'description': 'Enhance communication strategies to improve engagement',
        'implementation': [
            'Send personalized progress reports to patients',
            'Implement peer support groups',
            'Create patient success stories and testimonials',
            'Establish regular check-in calls'
        ],
        'expected_impact': 'Increase overall engagement by 15-25%',
        'priority': 'medium'
    })
    
    # Data-driven interventions
    completion_patterns = behavior_patterns.get('completion_time_patterns', {})
    if completion_patterns.get('peak_hours'):
        interventions.append({
            'category': 'data_driven',
            'intervention': 'Timing Optimization',
            'description': 'Optimize diary prompts based on patient completion patterns',
            'implementation': [
                f'Schedule reminders during peak hours: {completion_patterns["peak_hours"]}',
                'Avoid reminder times with low completion rates',
                'Implement adaptive scheduling based on individual patterns',
                'Test different reminder frequencies'
            ],
            'expected_impact': 'Improve completion rates by 10-20%',
            'priority': 'medium'
        })
    
    return interventions

def calculate_compliance_metrics(processed_entries: List[Dict], study_schedule: Dict, 
                               patient_population: List[Dict]) -> Dict:
    """Calculate comprehensive compliance metrics."""
    metrics = {
        'summary_metrics': {},
        'patient_metrics': {},
        'temporal_metrics': {},
        'quality_metrics': {},
        'comparative_metrics': {}
    }
    
    if not processed_entries:
        return metrics
    
    # Summary metrics
    total_patients = len(set(entry['patient_id'] for entry in processed_entries))
    total_entries = len(processed_entries)
    complete_entries = sum(1 for entry in processed_entries if entry['completion_status'] == 'complete')
    
    metrics['summary_metrics'] = {
        'total_patients': total_patients,
        'total_expected_entries': total_entries,  # Simplified
        'total_completed_entries': complete_entries,
        'overall_completion_rate': round((complete_entries / total_entries) * 100, 2) if total_entries > 0 else 0,
        'average_entries_per_patient': round(total_entries / total_patients, 2) if total_patients > 0 else 0
    }
    
    # Patient-level metrics
    patient_entries = {}
    for entry in processed_entries:
        patient_id = entry['patient_id']
        if patient_id not in patient_entries:
            patient_entries[patient_id] = []
        patient_entries[patient_id].append(entry)
    
    patient_metrics = {}
    for patient_id, entries in patient_entries.items():
        complete_count = sum(1 for e in entries if e['completion_status'] == 'complete')
        timely_count = sum(1 for e in entries if e['timely_completion'])
        
        patient_metrics[patient_id] = {
            'total_entries': len(entries),
            'completed_entries': complete_count,
            'completion_rate': round((complete_count / len(entries)) * 100, 2),
            'timeliness_rate': round((timely_count / len(entries)) * 100, 2),
            'avg_response_time': calculate_avg_response_time(entries),
            'current_streak': calculate_completion_streak(entries),
            'compliance_category': categorize_compliance(complete_count / len(entries) * 100)
        }
    
    metrics['patient_metrics'] = patient_metrics
    
    # Temporal metrics
    metrics['temporal_metrics'] = calculate_temporal_metrics(processed_entries)
    
    # Quality metrics
    metrics['quality_metrics'] = {
        'partial_completions': sum(1 for e in processed_entries if e['partial_completion']),
        'late_entries': sum(1 for e in processed_entries if e['late_entry']),
        'entries_with_quality_flags': sum(1 for e in processed_entries if e['data_quality_flags']),
        'avg_response_time_all': calculate_avg_response_time(processed_entries)
    }
    
    return metrics

def calculate_avg_response_time(entries: List[Dict]) -> float:
    """Calculate average response time for entries."""
    response_times = [e['response_time_minutes'] for e in entries if e['response_time_minutes'] > 0]
    return round(sum(response_times) / len(response_times), 2) if response_times else 0.0

def categorize_compliance(rate: float) -> str:
    """Categorize compliance rate."""
    if rate >= 95:
        return 'excellent'
    elif rate >= 85:
        return 'good'
    elif rate >= 70:
        return 'acceptable'
    else:
        return 'poor'

def calculate_temporal_metrics(processed_entries: List[Dict]) -> Dict:
    """Calculate temporal compliance metrics."""
    temporal_metrics = {}
    
    # Daily completion rates
    daily_data = {}
    for entry in processed_entries:
        if entry['entry_date']:
            date_key = entry['entry_date'].strftime('%Y-%m-%d')
            if date_key not in daily_data:
                daily_data[date_key] = {'total': 0, 'complete': 0}
            daily_data[date_key]['total'] += 1
            if entry['completion_status'] == 'complete':
                daily_data[date_key]['complete'] += 1
    
    daily_rates = [(counts['complete'] / counts['total']) * 100 
                  for counts in daily_data.values() if counts['total'] > 0]
    
    if daily_rates:
        temporal_metrics['daily_compliance'] = {
            'average': round(sum(daily_rates) / len(daily_rates), 2),
            'minimum': round(min(daily_rates), 2),
            'maximum': round(max(daily_rates), 2),
            'std_deviation': round(calculate_std_deviation(daily_rates), 2)
        }
    
    return temporal_metrics

def calculate_std_deviation(values: List[float]) -> float:
    """Calculate standard deviation."""
    if len(values) < 2:
        return 0.0
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return variance ** 0.5

def analyze_compliance_trends(processed_entries: List[Dict], study_schedule: Dict) -> Dict:
    """Analyze compliance trends over time."""
    trends = {
        'overall_trend': 'stable',
        'trend_analysis': {},
        'seasonal_patterns': {},
        'predictions': {}
    }
    
    # Group entries by week
    weekly_data = {}
    for entry in processed_entries:
        if entry['entry_date']:
            week_key = entry['entry_date'].strftime('%Y-W%U')
            if week_key not in weekly_data:
                weekly_data[week_key] = {'total': 0, 'complete': 0}
            weekly_data[week_key]['total'] += 1
            if entry['completion_status'] == 'complete':
                weekly_data[week_key]['complete'] += 1
    
    # Calculate weekly compliance rates
    weekly_rates = []
    sorted_weeks = sorted(weekly_data.keys())
    
    for week in sorted_weeks:
        if weekly_data[week]['total'] > 0:
            rate = (weekly_data[week]['complete'] / weekly_data[week]['total']) * 100
            weekly_rates.append(rate)
    
    if len(weekly_rates) >= 4:  # Need at least 4 weeks for trend analysis
        # Simple linear trend
        recent_avg = sum(weekly_rates[-4:]) / 4
        early_avg = sum(weekly_rates[:4]) / 4
        
        trend_change = recent_avg - early_avg
        
        if trend_change > 5:
            trends['overall_trend'] = 'improving'
        elif trend_change < -5:
            trends['overall_trend'] = 'declining'
        else:
            trends['overall_trend'] = 'stable'
        
        trends['trend_analysis'] = {
            'recent_4week_average': round(recent_avg, 2),
            'early_4week_average': round(early_avg, 2),
            'trend_change_percentage': round(trend_change, 2),
            'total_weeks_analyzed': len(weekly_rates)
        }
    
    return trends

def segment_patients_by_compliance(processed_entries: List[Dict], compliance_analysis: Dict, 
                                 patient_population: List[Dict]) -> Dict:
    """Segment patients based on compliance patterns."""
    segments = {
        'high_performers': [],
        'consistent_performers': [],
        'declining_performers': [],
        'low_performers': [],
        'at_risk_patients': []
    }
    
    # Segment based on compliance rates
    for patient_id, rate in compliance_analysis['patient_compliance_rates'].items():
        if rate >= 95:
            segments['high_performers'].append(patient_id)
        elif rate >= 80:
            segments['consistent_performers'].append(patient_id)
        elif rate >= 60:
            segments['declining_performers'].append(patient_id)
        else:
            segments['low_performers'].append(patient_id)
    
    # Identify at-risk patients (those showing declining patterns)
    patient_entries = {}
    for entry in processed_entries:
        patient_id = entry['patient_id']
        if patient_id not in patient_entries:
            patient_entries[patient_id] = []
        patient_entries[patient_id].append(entry)
    
    for patient_id, entries in patient_entries.items():
        if len(entries) >= 6:  # Need sufficient data
            sorted_entries = sorted(entries, key=lambda x: x['entry_date'] or datetime.min)
            recent_half = sorted_entries[len(sorted_entries)//2:]
            early_half = sorted_entries[:len(sorted_entries)//2]
            
            recent_compliance = sum(1 for e in recent_half if e['completion_status'] == 'complete') / len(recent_half)
            early_compliance = sum(1 for e in early_half if e['completion_status'] == 'complete') / len(early_half)
            
            if recent_compliance < early_compliance - 0.2:  # 20% decline
                segments['at_risk_patients'].append(patient_id)
    
    # Add segment metadata
    for segment_name, patient_list in segments.items():
        if patient_list:
            segment_rates = [compliance_analysis['patient_compliance_rates'].get(pid, 0) 
                           for pid in patient_list]
            segments[segment_name] = {
                'patient_ids': patient_list,
                'patient_count': len(patient_list),
                'average_compliance': round(sum(segment_rates) / len(segment_rates), 2),
                'compliance_range': f"{round(min(segment_rates), 1)}-{round(max(segment_rates), 1)}%"
            }
    
    return segments

def create_dashboard_data(compliance_analysis: Dict, metrics: Dict) -> Dict:
    """Create data structure for compliance dashboard."""
    dashboard_data = {
        'summary_cards': {
            'total_patients': metrics['summary_metrics']['total_patients'],
            'overall_compliance': compliance_analysis['overall_compliance'],
            'completed_entries': metrics['summary_metrics']['total_completed_entries'],
            'compliance_trend': 'stable'  # Would be calculated from trend analysis
        },
        'compliance_distribution': compliance_analysis['compliance_distribution'],
        'temporal_data': {
            'daily_rates': compliance_analysis['daily_compliance_rates'],
            'weekly_rates': compliance_analysis.get('weekly_compliance_rates', {}),
        },
        'patient_segments': {
            'excellent': compliance_analysis['compliance_distribution'].get('excellent', 0),
            'good': compliance_analysis['compliance_distribution'].get('good', 0),
            'acceptable': compliance_analysis['compliance_distribution'].get('acceptable', 0),
            'poor': compliance_analysis['compliance_distribution'].get('poor', 0)
        },
        'alerts_count': {
            'critical': 0,  # Would be calculated from alerts
            'high': 0,
            'medium': 0,
            'low': 0
        }
    }
    
    return dashboard_data

def generate_export_recommendations(compliance_analysis: Dict) -> List[str]:
    """Generate recommendations for data export and reporting."""
    recommendations = [
        "Export patient-level compliance data for detailed analysis",
        "Generate weekly compliance reports for study team review",
        "Create patient-specific compliance profiles for interventions",
        "Export temporal compliance data for trend analysis"
    ]
    
    if compliance_analysis['overall_compliance'] < 80:
        recommendations.extend([
            "Export non-compliant patient data for urgent intervention",
            "Generate compliance improvement tracking reports",
            "Create detailed analysis of compliance barriers"
        ])
    
    if compliance_analysis['compliance_distribution'].get('poor', 0) > 0:
        recommendations.append("Export individual patient compliance patterns for personalized interventions")
    
    return recommendations