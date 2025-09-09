"""
Lab Range Validator Tool
Validates laboratory values against reference ranges and clinical thresholds
Supports age/gender-specific ranges and critical value detection
"""

import csv
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from io import StringIO


def run(input_data: dict) -> dict:
    """
    Validates lab values against reference ranges
    
    Args:
        input_data: Dictionary containing:
            - lab_data: CSV data with laboratory results
            - reference_ranges: Lab reference ranges configuration
            - validation_level: 'basic', 'standard', or 'comprehensive' (default: 'standard')
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating if validation succeeded
            - validation_results: Detailed validation results
            - out_of_range_values: Values outside reference ranges
            - critical_values: Values in critical ranges
            - errors: List of processing errors
            - warnings: List of processing warnings
            - statistics: Validation statistics
    """
    try:
        lab_data = input_data.get('lab_data', '')
        reference_ranges = input_data.get('reference_ranges', get_default_ranges())
        validation_level = input_data.get('validation_level', 'standard')
        
        if not lab_data:
            return {
                'success': False,
                'validation_results': [],
                'out_of_range_values': [],
                'critical_values': [],
                'errors': ['No lab data provided'],
                'warnings': [],
                'statistics': {}
            }
        
        errors = []
        warnings = []
        validation_results = []
        out_of_range_values = []
        critical_values = []
        
        # Parse lab data
        csv_reader = csv.DictReader(StringIO(lab_data))
        records = list(csv_reader)
        
        if not records:
            return {
                'success': False,
                'validation_results': [],
                'out_of_range_values': [],
                'critical_values': [],
                'errors': ['Lab data is empty'],
                'warnings': [],
                'statistics': {}
            }
        
        # Validate each record
        for i, record in enumerate(records):
            try:
                result = validate_lab_record(record, reference_ranges, validation_level, i)
                validation_results.append(result)
                
                # Collect out of range values
                if result['out_of_range_tests']:
                    out_of_range_values.extend(result['out_of_range_tests'])
                
                # Collect critical values
                if result['critical_tests']:
                    critical_values.extend(result['critical_tests'])
                    
            except Exception as e:
                errors.append(f"Record {i+1}: {str(e)}")
        
        # Generate statistics
        statistics = generate_lab_statistics(validation_results, len(records))
        
        return {
            'success': True,
            'validation_results': validation_results[:500],  # Limit output
            'out_of_range_values': out_of_range_values[:100],
            'critical_values': critical_values[:50],
            'errors': errors,
            'warnings': warnings,
            'statistics': statistics,
            'validation_summary': {
                'total_records': len(records),
                'records_validated': len(validation_results),
                'out_of_range_count': len(out_of_range_values),
                'critical_count': len(critical_values),
                'validation_level': validation_level
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'validation_results': [],
            'out_of_range_values': [],
            'critical_values': [],
            'errors': [f"Lab validation failed: {str(e)}"],
            'warnings': [],
            'statistics': {}
        }


def get_default_ranges() -> dict:
    """Get default laboratory reference ranges"""
    return {
        'glucose': {
            'normal_range': {'min': 70, 'max': 100, 'unit': 'mg/dL'},
            'critical_low': 40,
            'critical_high': 400,
            'age_specific': False
        },
        'hemoglobin': {
            'normal_range': {
                'male': {'min': 13.8, 'max': 17.2, 'unit': 'g/dL'},
                'female': {'min': 12.1, 'max': 15.1, 'unit': 'g/dL'}
            },
            'critical_low': 7.0,
            'critical_high': 20.0,
            'gender_specific': True
        },
        'creatinine': {
            'normal_range': {
                'male': {'min': 0.7, 'max': 1.3, 'unit': 'mg/dL'},
                'female': {'min': 0.6, 'max': 1.1, 'unit': 'mg/dL'}
            },
            'critical_high': 4.0,
            'gender_specific': True
        }
    }


def validate_lab_record(record: dict, reference_ranges: dict, 
                       validation_level: str, record_index: int) -> dict:
    """Validate a single lab record"""
    
    subject_id = record.get('subject_id', f'Unknown_{record_index}')
    age = record.get('age', '')
    gender = record.get('gender', record.get('sex', '')).lower()
    
    result = {
        'record_index': record_index,
        'subject_id': subject_id,
        'total_tests': 0,
        'valid_tests': 0,
        'out_of_range_tests': [],
        'critical_tests': [],
        'test_results': {}
    }
    
    # Check each lab test in the record
    for field, value in record.items():
        if field.lower() in reference_ranges and value and str(value).strip():
            try:
                numeric_value = float(str(value).strip())
                test_name = field.lower()
                range_config = reference_ranges[test_name]
                
                result['total_tests'] += 1
                
                # Get appropriate reference range
                ref_range = get_applicable_range(range_config, age, gender)
                
                # Validate the value
                test_result = validate_test_value(
                    test_name, numeric_value, ref_range, range_config, 
                    subject_id, record_index
                )
                
                result['test_results'][test_name] = test_result
                
                if test_result['status'] == 'normal':
                    result['valid_tests'] += 1
                elif test_result['status'] in ['low', 'high']:
                    result['out_of_range_tests'].append(test_result)
                elif test_result['status'] in ['critical_low', 'critical_high']:
                    result['critical_tests'].append(test_result)
                    result['out_of_range_tests'].append(test_result)
                    
            except (ValueError, TypeError):
                if validation_level in ['standard', 'comprehensive']:
                    result['test_results'][field] = {
                        'test_name': field,
                        'value': value,
                        'status': 'invalid',
                        'message': 'Non-numeric value'
                    }
    
    return result


def get_applicable_range(range_config: dict, age: str, gender: str) -> dict:
    """Get the applicable reference range based on age and gender"""
    
    normal_range = range_config.get('normal_range', {})
    
    # Gender-specific ranges
    if range_config.get('gender_specific') and gender in ['male', 'female', 'm', 'f']:
        gender_key = 'male' if gender.lower() in ['male', 'm'] else 'female'
        if gender_key in normal_range:
            return normal_range[gender_key]
    
    # Default range
    if isinstance(normal_range, dict) and 'min' in normal_range:
        return normal_range
    elif isinstance(normal_range, dict) and 'male' in normal_range:
        return normal_range['male']  # Default to male range if no gender specified
    
    return normal_range


def validate_test_value(test_name: str, value: float, ref_range: dict, 
                       range_config: dict, subject_id: str, record_index: int) -> dict:
    """Validate a single test value against reference range"""
    
    result = {
        'test_name': test_name,
        'subject_id': subject_id,
        'record_index': record_index,
        'value': value,
        'reference_range': ref_range,
        'status': 'normal',
        'message': 'Within normal range',
        'severity': 'normal'
    }
    
    if not ref_range or 'min' not in ref_range or 'max' not in ref_range:
        result['status'] = 'no_range'
        result['message'] = 'No reference range available'
        return result
    
    min_normal = ref_range['min']
    max_normal = ref_range['max']
    
    # Check critical values first
    critical_low = range_config.get('critical_low')
    critical_high = range_config.get('critical_high')
    
    if critical_low is not None and value < critical_low:
        result['status'] = 'critical_low'
        result['message'] = f'Critical low value: {value} < {critical_low}'
        result['severity'] = 'critical'
    elif critical_high is not None and value > critical_high:
        result['status'] = 'critical_high'
        result['message'] = f'Critical high value: {value} > {critical_high}'
        result['severity'] = 'critical'
    elif value < min_normal:
        result['status'] = 'low'
        result['message'] = f'Below normal range: {value} < {min_normal}'
        result['severity'] = 'abnormal'
    elif value > max_normal:
        result['status'] = 'high'
        result['message'] = f'Above normal range: {value} > {max_normal}'
        result['severity'] = 'abnormal'
    
    return result


def generate_lab_statistics(validation_results: List[dict], total_records: int) -> dict:
    """Generate laboratory validation statistics"""
    
    if not validation_results:
        return {}
    
    total_tests = sum(r['total_tests'] for r in validation_results)
    valid_tests = sum(r['valid_tests'] for r in validation_results)
    total_out_of_range = sum(len(r['out_of_range_tests']) for r in validation_results)
    total_critical = sum(len(r['critical_tests']) for r in validation_results)
    
    normal_rate = (valid_tests / total_tests * 100) if total_tests > 0 else 0
    
    return {
        'total_records': total_records,
        'total_lab_tests': total_tests,
        'normal_tests': valid_tests,
        'abnormal_tests': total_out_of_range,
        'critical_tests': total_critical,
        'normal_rate': round(normal_rate, 2),
        'subjects_with_abnormal_labs': sum(1 for r in validation_results if r['out_of_range_tests']),
        'subjects_with_critical_labs': sum(1 for r in validation_results if r['critical_tests'])
    }