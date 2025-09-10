"""
Data Dictionary Validator Tool
Validates CSV data against JSON schema definitions for clinical trial data integrity
"""

import csv
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from io import StringIO


def run(input_data: dict) -> dict:
    """
    Validates CSV clinical trial data against JSON schema definitions to ensure data integrity.
    
    Example:
        Input: CSV data with subject records and corresponding JSON schema with field definitions
        Output: Validation report showing conformance status and detailed error descriptions
    
    Parameters:
        csv_data : str
            CSV data content as string
        schema : dict
            JSON schema definition for data validation
        strict_mode : bool
            Enable strict validation mode (optional, default True)
    """
    try:
        csv_data = input_data.get('csv_data', '')
        schema = input_data.get('schema', {})
        strict_mode = input_data.get('strict_mode', True)
        
        if not csv_data:
            return {
                'valid': False,
                'errors': ['No CSV data provided'],
                'warnings': [],
                'statistics': {}
            }
        
        if not schema:
            return {
                'valid': False,
                'errors': ['No schema provided'],
                'warnings': [],
                'statistics': {}
            }
        
        errors = []
        warnings = []
        statistics = {
            'total_rows': 0,
            'valid_rows': 0,
            'invalid_rows': 0,
            'missing_values': 0,
            'type_mismatches': 0,
            'constraint_violations': 0,
            'field_statistics': {}
        }
        
        # Parse CSV data
        csv_reader = csv.DictReader(StringIO(csv_data))
        rows = list(csv_reader)
        statistics['total_rows'] = len(rows)
        
        # Get schema fields
        schema_fields = schema.get('fields', {})
        required_fields = schema.get('required_fields', [])
        
        # Validate headers
        if rows:
            csv_headers = rows[0].keys()
            schema_headers = set(schema_fields.keys())
            
            # Check for missing required fields
            missing_required = set(required_fields) - set(csv_headers)
            if missing_required:
                errors.append(f"Missing required fields: {', '.join(missing_required)}")
            
            # Check for extra fields not in schema
            extra_fields = set(csv_headers) - schema_headers
            if extra_fields and strict_mode:
                errors.append(f"Extra fields not in schema: {', '.join(extra_fields)}")
            elif extra_fields:
                warnings.append(f"Extra fields not in schema: {', '.join(extra_fields)}")
        
        # Validate each row
        for row_num, row in enumerate(rows, start=1):
            row_errors = []
            
            for field_name, field_schema in schema_fields.items():
                value = row.get(field_name, '').strip()
                
                # Initialize field statistics
                if field_name not in statistics['field_statistics']:
                    statistics['field_statistics'][field_name] = {
                        'missing': 0,
                        'valid': 0,
                        'invalid': 0,
                        'unique_values': set()
                    }
                
                field_stats = statistics['field_statistics'][field_name]
                
                # Check required fields
                if field_name in required_fields and not value:
                    row_errors.append(f"Field '{field_name}' is required but missing")
                    field_stats['missing'] += 1
                    statistics['missing_values'] += 1
                    continue
                
                # Skip validation for empty optional fields
                if not value and field_name not in required_fields:
                    field_stats['missing'] += 1
                    statistics['missing_values'] += 1
                    continue
                
                # Validate data type
                data_type = field_schema.get('type', 'string')
                if not validate_type(value, data_type):
                    row_errors.append(f"Field '{field_name}' type mismatch: expected {data_type}, got '{value}'")
                    field_stats['invalid'] += 1
                    statistics['type_mismatches'] += 1
                    continue
                
                # Validate constraints
                constraint_errors = validate_constraints(value, field_schema, field_name)
                if constraint_errors:
                    row_errors.extend(constraint_errors)
                    field_stats['invalid'] += 1
                    statistics['constraint_violations'] += len(constraint_errors)
                else:
                    field_stats['valid'] += 1
                    field_stats['unique_values'].add(value)
            
            if row_errors:
                for error in row_errors:
                    errors.append(f"Row {row_num}: {error}")
                statistics['invalid_rows'] += 1
            else:
                statistics['valid_rows'] += 1
        
        # Convert sets to counts for JSON serialization
        for field_name in statistics['field_statistics']:
            unique_values = statistics['field_statistics'][field_name].pop('unique_values')
            statistics['field_statistics'][field_name]['unique_count'] = len(unique_values)
        
        # Determine overall validity
        valid = len(errors) == 0 if strict_mode else statistics['invalid_rows'] == 0
        
        return {
            'valid': valid,
            'errors': errors[:100],  # Limit errors to prevent huge responses
            'warnings': warnings,
            'statistics': statistics,
            'validation_summary': {
                'total_errors': len(errors),
                'total_warnings': len(warnings),
                'validation_rate': f"{(statistics['valid_rows'] / statistics['total_rows'] * 100):.2f}%" if statistics['total_rows'] > 0 else "N/A"
            }
        }
        
    except Exception as e:
        return {
            'valid': False,
            'errors': [f"Validation failed: {str(e)}"],
            'warnings': [],
            'statistics': {}
        }


def validate_type(value: str, expected_type: str) -> bool:
    """
    Validates if a value matches the expected data type
    
    Args:
        value: String value to validate
        expected_type: Expected data type
    
    Returns:
        Boolean indicating if value matches expected type
    """
    if expected_type == 'string':
        return True
    elif expected_type == 'integer':
        try:
            int(value)
            return True
        except ValueError:
            return False
    elif expected_type == 'float' or expected_type == 'number':
        try:
            float(value)
            return True
        except ValueError:
            return False
    elif expected_type == 'boolean':
        return value.lower() in ['true', 'false', '1', '0', 'yes', 'no', 'y', 'n']
    elif expected_type == 'date':
        return validate_date(value)
    elif expected_type == 'datetime':
        return validate_datetime(value)
    else:
        return True


def validate_date(value: str) -> bool:
    """
    Validates if a value is a valid date
    
    Args:
        value: String value to validate
    
    Returns:
        Boolean indicating if value is a valid date
    """
    date_formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%d-%b-%Y',
        '%d-%B-%Y'
    ]
    
    for fmt in date_formats:
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue
    return False


def validate_datetime(value: str) -> bool:
    """
    Validates if a value is a valid datetime
    
    Args:
        value: String value to validate
    
    Returns:
        Boolean indicating if value is a valid datetime
    """
    datetime_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%m/%d/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ'
    ]
    
    for fmt in datetime_formats:
        try:
            datetime.strptime(value, fmt)
            return True
        except ValueError:
            continue
    return False


def validate_constraints(value: str, field_schema: dict, field_name: str) -> List[str]:
    """
    Validates value against field constraints
    
    Args:
        value: Value to validate
        field_schema: Field schema with constraints
        field_name: Name of the field
    
    Returns:
        List of constraint violation errors
    """
    errors = []
    
    # Min/max length for strings
    if 'min_length' in field_schema and len(value) < field_schema['min_length']:
        errors.append(f"Field '{field_name}' length {len(value)} is less than minimum {field_schema['min_length']}")
    
    if 'max_length' in field_schema and len(value) > field_schema['max_length']:
        errors.append(f"Field '{field_name}' length {len(value)} exceeds maximum {field_schema['max_length']}")
    
    # Min/max values for numbers
    if field_schema.get('type') in ['integer', 'float', 'number']:
        try:
            num_value = float(value)
            if 'minimum' in field_schema and num_value < field_schema['minimum']:
                errors.append(f"Field '{field_name}' value {num_value} is less than minimum {field_schema['minimum']}")
            
            if 'maximum' in field_schema and num_value > field_schema['maximum']:
                errors.append(f"Field '{field_name}' value {num_value} exceeds maximum {field_schema['maximum']}")
        except ValueError:
            pass
    
    # Pattern matching
    if 'pattern' in field_schema:
        pattern = field_schema['pattern']
        if not re.match(pattern, value):
            errors.append(f"Field '{field_name}' value '{value}' does not match pattern '{pattern}'")
    
    # Enumerated values
    if 'enum' in field_schema:
        allowed_values = field_schema['enum']
        if value not in allowed_values:
            errors.append(f"Field '{field_name}' value '{value}' not in allowed values: {allowed_values}")
    
    # Custom validation rules
    if 'custom_rules' in field_schema:
        for rule in field_schema['custom_rules']:
            rule_type = rule.get('type')
            
            if rule_type == 'unique':
                # This would need to be handled at a higher level with all values
                pass
            elif rule_type == 'not_null':
                if not value or value.lower() in ['null', 'none', 'n/a']:
                    errors.append(f"Field '{field_name}' cannot be null or empty")
            elif rule_type == 'future_date':
                try:
                    date_value = datetime.strptime(value, '%Y-%m-%d')
                    if date_value <= datetime.now():
                        errors.append(f"Field '{field_name}' must be a future date")
                except ValueError:
                    pass
            elif rule_type == 'past_date':
                try:
                    date_value = datetime.strptime(value, '%Y-%m-%d')
                    if date_value >= datetime.now():
                        errors.append(f"Field '{field_name}' must be a past date")
                except ValueError:
                    pass
    
    return errors