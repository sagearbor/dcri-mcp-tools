"""
EDC Data Validator Tool
Validates EDC (Electronic Data Capture) exports against study specifications
Checks for protocol compliance, visit schedules, and data completeness
"""

import csv
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from io import StringIO


def run(input_data: dict) -> dict:
    """
    Validates EDC export data against study specifications to ensure protocol compliance and data completeness.
    
    Example:
        Input: EDC export data with subject records and corresponding study specification requirements
        Output: Validation report with protocol compliance metrics and deviation identification
    
    Parameters:
        edc_data : str
            CSV data string from EDC export
        study_spec : dict
            Study specification with protocol requirements and criteria
        validation_level : str
            Validation intensity ('basic', 'standard', 'strict', default 'standard')
    """
    try:
        edc_data = input_data.get('edc_data', '')
        study_spec = input_data.get('study_spec', {})
        validation_level = input_data.get('validation_level', 'standard')
        
        if not edc_data:
            return {
                'valid': False,
                'errors': ['No EDC data provided'],
                'warnings': [],
                'statistics': {},
                'protocol_compliance': {}
            }
        
        if not study_spec:
            return {
                'valid': False,
                'errors': ['No study specification provided'],
                'warnings': [],
                'statistics': {},
                'protocol_compliance': {}
            }
        
        errors = []
        warnings = []
        statistics = {
            'total_subjects': 0,
            'total_visits': 0,
            'complete_visits': 0,
            'incomplete_visits': 0,
            'overdue_visits': 0,
            'protocol_deviations': 0,
            'missing_required_fields': 0,
            'data_quality_score': 0.0,
            'subject_statistics': {}
        }
        
        protocol_compliance = {
            'enrollment_criteria': {'met': 0, 'failed': 0, 'details': []},
            'visit_schedule': {'compliant': 0, 'deviations': 0, 'details': []},
            'inclusion_exclusion': {'compliant': 0, 'violations': 0, 'details': []},
            'required_assessments': {'complete': 0, 'missing': 0, 'details': []}
        }
        
        # Parse EDC data
        csv_reader = csv.DictReader(StringIO(edc_data))
        rows = list(csv_reader)
        
        if not rows:
            return {
                'valid': False,
                'errors': ['EDC data is empty'],
                'warnings': [],
                'statistics': statistics,
                'protocol_compliance': protocol_compliance
            }
        
        # Group data by subject
        subjects = {}
        for row in rows:
            subject_id = row.get('subject_id', '').strip()
            if not subject_id:
                errors.append('Row missing subject_id')
                continue
                
            if subject_id not in subjects:
                subjects[subject_id] = {'visits': [], 'demographics': {}}
            
            # Determine if this is a demographic row or visit row
            visit_name = row.get('visit_name', '').strip()
            if visit_name:
                subjects[subject_id]['visits'].append(row)
                # Also extract demographics from visit rows if they exist
                for demo_field in study_spec.get('required_demographics', []):
                    if demo_field in row and row[demo_field]:
                        subjects[subject_id]['demographics'][demo_field] = row[demo_field]
            else:
                # This is demographic data
                subjects[subject_id]['demographics'].update(row)
        
        statistics['total_subjects'] = len(subjects)
        
        # Validate each subject
        for subject_id, subject_data in subjects.items():
            subject_errors = validate_subject(
                subject_id, subject_data, study_spec, validation_level
            )
            
            # Update statistics
            subject_visits = len(subject_data['visits'])
            statistics['total_visits'] += subject_visits
            statistics['subject_statistics'][subject_id] = {
                'visits': subject_visits,
                'complete_visits': 0,
                'protocol_deviations': 0,
                'compliance_score': 0.0
            }
            
            # Process subject validation results
            for error in subject_errors:
                if error['type'] == 'error':
                    errors.append(f"Subject {subject_id}: {error['message']}")
                    if 'protocol_deviation' in error['category']:
                        statistics['protocol_deviations'] += 1
                        statistics['subject_statistics'][subject_id]['protocol_deviations'] += 1
                elif error['type'] == 'warning':
                    warnings.append(f"Subject {subject_id}: {error['message']}")
            
            # Validate enrollment criteria
            enrollment_result = validate_enrollment_criteria(
                subject_data['demographics'], study_spec.get('enrollment_criteria', {})
            )
            if enrollment_result['compliant']:
                protocol_compliance['enrollment_criteria']['met'] += 1
            else:
                protocol_compliance['enrollment_criteria']['failed'] += 1
                protocol_compliance['enrollment_criteria']['details'].extend(
                    [f"Subject {subject_id}: {detail}" for detail in enrollment_result['violations']]
                )
            
            # Validate visit schedule
            visit_compliance = validate_visit_schedule(
                subject_data['visits'], study_spec.get('visit_schedule', [])
            )
            statistics['complete_visits'] += visit_compliance['complete_visits']
            statistics['incomplete_visits'] += visit_compliance['incomplete_visits']
            statistics['overdue_visits'] += visit_compliance['overdue_visits']
            statistics['subject_statistics'][subject_id]['complete_visits'] = visit_compliance['complete_visits']
            
            if visit_compliance['deviations']:
                protocol_compliance['visit_schedule']['deviations'] += len(visit_compliance['deviations'])
                protocol_compliance['visit_schedule']['details'].extend(
                    [f"Subject {subject_id}: {dev}" for dev in visit_compliance['deviations']]
                )
            else:
                protocol_compliance['visit_schedule']['compliant'] += 1
            
            # Calculate subject compliance score
            total_checks = 4  # enrollment, visit schedule, assessments, data quality
            passed_checks = 0
            
            if enrollment_result['compliant']:
                passed_checks += 1
            if not visit_compliance['deviations']:
                passed_checks += 1
            if visit_compliance['complete_visits'] > 0:
                passed_checks += 1
            if len(subject_errors) == 0:
                passed_checks += 1
                
            statistics['subject_statistics'][subject_id]['compliance_score'] = (passed_checks / total_checks) * 100
        
        # Validate required assessments across all subjects
        assessment_compliance = validate_required_assessments(
            subjects, study_spec.get('required_assessments', [])
        )
        protocol_compliance['required_assessments'] = assessment_compliance
        
        # Calculate overall data quality score
        total_possible_score = len(subjects) * 100
        actual_score = sum(stats['compliance_score'] for stats in statistics['subject_statistics'].values())
        statistics['data_quality_score'] = (actual_score / total_possible_score * 100) if total_possible_score > 0 else 0
        
        # Determine validity based on validation level
        if validation_level == 'basic':
            valid = len(errors) == 0
        elif validation_level == 'standard':
            valid = len(errors) == 0 and statistics['data_quality_score'] >= 80
        else:  # strict
            valid = len(errors) == 0 and len(warnings) == 0 and statistics['data_quality_score'] >= 95
        
        return {
            'valid': valid,
            'errors': errors[:100],  # Limit to prevent huge responses
            'warnings': warnings[:50],
            'statistics': statistics,
            'protocol_compliance': protocol_compliance,
            'validation_summary': {
                'total_errors': len(errors),
                'total_warnings': len(warnings),
                'compliance_rate': f"{statistics['data_quality_score']:.2f}%",
                'subjects_compliant': sum(1 for stats in statistics['subject_statistics'].values() if stats['compliance_score'] >= 80),
                'total_subjects': statistics['total_subjects']
            }
        }
        
    except Exception as e:
        return {
            'valid': False,
            'errors': [f"EDC validation failed: {str(e)}"],
            'warnings': [],
            'statistics': {},
            'protocol_compliance': {}
        }


def validate_subject(subject_id: str, subject_data: dict, study_spec: dict, validation_level: str) -> List[dict]:
    """Validate individual subject data"""
    errors = []
    
    demographics = subject_data.get('demographics', {})
    visits = subject_data.get('visits', [])
    
    # Check required demographic fields
    required_demo_fields = study_spec.get('required_demographics', [])
    for field in required_demo_fields:
        if not demographics.get(field):
            errors.append({
                'type': 'error',
                'category': 'missing_data',
                'message': f"Missing required demographic field: {field}"
            })
    
    # Check age eligibility
    age_criteria = study_spec.get('enrollment_criteria', {}).get('age', {})
    if 'age' in demographics:
        try:
            age = int(demographics['age'])
            min_age = age_criteria.get('minimum', 0)
            max_age = age_criteria.get('maximum', 200)
            if age < min_age or age > max_age:
                errors.append({
                    'type': 'error',
                    'category': 'protocol_deviation',
                    'message': f"Age {age} outside protocol range ({min_age}-{max_age})"
                })
        except (ValueError, TypeError):
            errors.append({
                'type': 'error',
                'category': 'data_quality',
                'message': f"Invalid age value: {demographics.get('age')}"
            })
    
    # Check visit data quality
    for visit in visits:
        visit_name = visit.get('visit_name', '')
        visit_date = visit.get('visit_date', '')
        
        if not visit_date:
            errors.append({
                'type': 'warning',
                'category': 'missing_data',
                'message': f"Missing visit date for {visit_name}"
            })
        else:
            # Validate date format
            try:
                datetime.strptime(visit_date, '%Y-%m-%d')
            except ValueError:
                try:
                    datetime.strptime(visit_date, '%m/%d/%Y')
                except ValueError:
                    errors.append({
                        'type': 'error',
                        'category': 'data_quality',
                        'message': f"Invalid date format for {visit_name}: {visit_date}"
                    })
        
        # Check for required visit fields
        required_visit_fields = study_spec.get('required_visit_fields', [])
        for field in required_visit_fields:
            if not visit.get(field):
                if validation_level == 'strict':
                    errors.append({
                        'type': 'error',
                        'category': 'missing_data',
                        'message': f"Missing required field '{field}' in {visit_name}"
                    })
                else:
                    errors.append({
                        'type': 'warning',
                        'category': 'missing_data',
                        'message': f"Missing field '{field}' in {visit_name}"
                    })
    
    return errors


def validate_enrollment_criteria(demographics: dict, criteria: dict) -> dict:
    """Validate subject against enrollment criteria"""
    violations = []
    
    # Age criteria
    if 'age' in criteria and 'age' in demographics:
        try:
            age = int(demographics['age'])
            min_age = criteria['age'].get('minimum', 0)
            max_age = criteria['age'].get('maximum', 200)
            if age < min_age:
                violations.append(f"Age {age} below minimum {min_age}")
            elif age > max_age:
                violations.append(f"Age {age} above maximum {max_age}")
        except (ValueError, TypeError):
            violations.append(f"Invalid age value: {demographics.get('age')}")
    
    # Gender criteria
    if 'gender' in criteria and 'gender' in demographics:
        allowed_genders = criteria['gender']
        if demographics['gender'] not in allowed_genders:
            violations.append(f"Gender '{demographics['gender']}' not in allowed values: {allowed_genders}")
    
    # Medical history exclusions
    if 'exclusions' in criteria:
        for exclusion in criteria['exclusions']:
            field_name = exclusion.get('field')
            excluded_values = exclusion.get('values', [])
            if field_name in demographics and demographics[field_name] in excluded_values:
                violations.append(f"Exclusion criteria violated: {field_name} = {demographics[field_name]}")
    
    return {
        'compliant': len(violations) == 0,
        'violations': violations
    }


def validate_visit_schedule(visits: List[dict], schedule: List[dict]) -> dict:
    """Validate visit schedule compliance"""
    result = {
        'complete_visits': 0,
        'incomplete_visits': 0,
        'overdue_visits': 0,
        'deviations': []
    }
    
    if not schedule:
        return result
    
    # Create lookup for expected visits
    expected_visits = {visit['name']: visit for visit in schedule}
    actual_visits = {visit.get('visit_name'): visit for visit in visits if visit.get('visit_name')}
    
    # Check for missing required visits
    for visit_name, visit_spec in expected_visits.items():
        if visit_spec.get('required', True) and visit_name not in actual_visits:
            result['deviations'].append(f"Missing required visit: {visit_name}")
            result['incomplete_visits'] += 1
        elif visit_name in actual_visits:
            # Visit exists, check timing and completeness
            actual_visit = actual_visits[visit_name]
            
            # Check visit timing (if baseline date is available)
            if 'visit_date' in actual_visit and visit_spec.get('day_range'):
                try:
                    visit_date = datetime.strptime(actual_visit['visit_date'], '%Y-%m-%d')
                    # This would need baseline date to calculate properly
                    # For now, just mark as complete if date exists
                    result['complete_visits'] += 1
                except ValueError:
                    result['deviations'].append(f"Invalid date format for {visit_name}")
                    result['incomplete_visits'] += 1
            else:
                result['complete_visits'] += 1
    
    # Check for unexpected visits
    for visit_name in actual_visits:
        if visit_name not in expected_visits:
            result['deviations'].append(f"Unexpected visit: {visit_name}")
    
    return result


def validate_required_assessments(subjects: dict, assessments: List[dict]) -> dict:
    """Validate required assessments across all subjects"""
    result = {
        'complete': 0,
        'missing': 0,
        'details': []
    }
    
    if not assessments:
        return result
    
    for subject_id, subject_data in subjects.items():
        visits = subject_data.get('visits', [])
        
        for assessment in assessments:
            assessment_name = assessment.get('name')
            required_visits = assessment.get('required_at_visits', [])
            
            for visit_name in required_visits:
                # Find the visit
                visit_data = None
                for visit in visits:
                    if visit.get('visit_name') == visit_name:
                        visit_data = visit
                        break
                
                if not visit_data:
                    result['missing'] += 1
                    result['details'].append(f"Subject {subject_id}: Missing {assessment_name} at {visit_name}")
                elif not visit_data.get(assessment_name):
                    result['missing'] += 1
                    result['details'].append(f"Subject {subject_id}: {assessment_name} not completed at {visit_name}")
                else:
                    result['complete'] += 1
    
    return result