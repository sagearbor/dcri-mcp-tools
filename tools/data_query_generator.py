"""
Data Query Generator Tool
Creates data queries based on logic checks and validation rules
Supports automatic query generation for clinical trial data management
"""

import csv
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from io import StringIO


def run(input_data: dict) -> dict:
    """
    Generates data queries based on logic checks and validation rules
    
    Args:
        input_data: Dictionary containing:
            - data: CSV data as string to check
            - query_rules: Query generation rules and logic checks
            - severity_levels: Query severity configuration
            - auto_close_rules: Rules for automatic query closure
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating if query generation succeeded
            - queries: List of generated queries
            - errors: List of processing errors
            - warnings: List of processing warnings
            - statistics: Query generation statistics
            - summary: Query summary by type and severity
    """
    try:
        data = input_data.get('data', '')
        query_rules = input_data.get('query_rules', {})
        severity_levels = input_data.get('severity_levels', get_default_severity_levels())
        auto_close_rules = input_data.get('auto_close_rules', {})
        
        if not data:
            return {
                'success': False,
                'queries': [],
                'errors': ['No data provided'],
                'warnings': [],
                'statistics': {},
                'summary': {}
            }
        
        if not query_rules:
            return {
                'success': False,
                'queries': [],
                'errors': ['No query rules provided'],
                'warnings': [],
                'statistics': {},
                'summary': {}
            }
        
        errors = []
        warnings = []
        queries = []
        statistics = {
            'total_records_checked': 0,
            'queries_generated': 0,
            'auto_closed_queries': 0,
            'critical_queries': 0,
            'major_queries': 0,
            'minor_queries': 0,
            'info_queries': 0,
            'rules_triggered': {},
            'affected_subjects': set(),
            'processing_time': 0
        }
        
        start_time = datetime.now()
        
        # Parse data
        csv_reader = csv.DictReader(StringIO(data))
        records = list(csv_reader)
        statistics['total_records_checked'] = len(records)
        
        if not records:
            return {
                'success': False,
                'queries': [],
                'errors': ['Data is empty'],
                'warnings': [],
                'statistics': statistics,
                'summary': {}
            }
        
        # Group records by subject for cross-record checks
        subjects = {}
        for record in records:
            subject_id = record.get('subject_id', '').strip()
            if subject_id:
                if subject_id not in subjects:
                    subjects[subject_id] = []
                subjects[subject_id].append(record)
        
        # Apply query rules
        rule_categories = query_rules.get('categories', {})
        
        for category_name, category_rules in rule_categories.items():
            for rule in category_rules:
                rule_queries = apply_query_rule(
                    rule, records, subjects, severity_levels, category_name
                )
                queries.extend(rule_queries)
                
                if rule_queries:
                    rule_name = rule.get('name', 'Unknown')
                    statistics['rules_triggered'][rule_name] = len(rule_queries)
                    
                    # Track affected subjects
                    for query in rule_queries:
                        if query.get('subject_id'):
                            statistics['affected_subjects'].add(query['subject_id'])
        
        # Apply auto-close rules
        if auto_close_rules:
            auto_closed = apply_auto_close_rules(queries, auto_close_rules)
            statistics['auto_closed_queries'] = auto_closed
        
        # Update statistics
        statistics['queries_generated'] = len(queries)
        statistics['affected_subjects'] = len(statistics['affected_subjects'])
        
        # Count by severity
        for query in queries:
            severity = query.get('severity', 'INFO').upper()
            if severity == 'CRITICAL':
                statistics['critical_queries'] += 1
            elif severity == 'MAJOR':
                statistics['major_queries'] += 1
            elif severity == 'MINOR':
                statistics['minor_queries'] += 1
            else:
                statistics['info_queries'] += 1
        
        end_time = datetime.now()
        statistics['processing_time'] = (end_time - start_time).total_seconds()
        
        # Generate summary
        summary = generate_query_summary(queries, statistics)
        
        return {
            'success': True,
            'queries': queries[:1000],  # Limit to prevent huge responses
            'errors': errors,
            'warnings': warnings,
            'statistics': statistics,
            'summary': summary,
            'processing_info': {
                'total_queries': len(queries),
                'shown_queries': min(len(queries), 1000),
                'processing_time_seconds': statistics['processing_time']
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'queries': [],
            'errors': [f"Query generation failed: {str(e)}"],
            'warnings': [],
            'statistics': {},
            'summary': {}
        }


def get_default_severity_levels() -> dict:
    """Get default query severity levels"""
    return {
        'CRITICAL': {
            'description': 'Critical data issues that affect subject safety or primary endpoints',
            'priority': 1,
            'response_time_hours': 24,
            'escalation_required': True
        },
        'MAJOR': {
            'description': 'Important data issues that affect data quality or secondary endpoints',
            'priority': 2,
            'response_time_hours': 72,
            'escalation_required': False
        },
        'MINOR': {
            'description': 'Minor data issues or inconsistencies',
            'priority': 3,
            'response_time_hours': 168,  # 1 week
            'escalation_required': False
        },
        'INFO': {
            'description': 'Informational queries or data clarification requests',
            'priority': 4,
            'response_time_hours': 336,  # 2 weeks
            'escalation_required': False
        }
    }


def apply_query_rule(rule: dict, records: List[dict], subjects: dict, severity_levels: dict, category: str) -> List[dict]:
    """Apply a single query rule to the data"""
    queries = []
    rule_type = rule.get('type', '')
    rule_name = rule.get('name', 'Unknown Rule')
    severity = rule.get('severity', 'INFO').upper()
    message_template = rule.get('message', 'Data query generated')
    
    if rule_type == 'missing_required':
        queries.extend(check_missing_required(rule, records, severity, message_template, category))
    elif rule_type == 'range_check':
        queries.extend(check_range_violations(rule, records, severity, message_template, category))
    elif rule_type == 'logic_check':
        queries.extend(check_logic_violations(rule, records, severity, message_template, category))
    elif rule_type == 'consistency_check':
        queries.extend(check_consistency_violations(rule, subjects, severity, message_template, category))
    elif rule_type == 'date_logic':
        queries.extend(check_date_logic(rule, records, subjects, severity, message_template, category))
    elif rule_type == 'duplicate_check':
        queries.extend(check_duplicates(rule, records, severity, message_template, category))
    elif rule_type == 'pattern_match':
        queries.extend(check_pattern_violations(rule, records, severity, message_template, category))
    elif rule_type == 'cross_domain':
        queries.extend(check_cross_domain_logic(rule, subjects, severity, message_template, category))
    
    # Add rule metadata to queries
    for query in queries:
        query['rule_name'] = rule_name
        query['rule_category'] = category
        query['generated_date'] = datetime.now().isoformat()
        
        # Add severity details
        if severity in severity_levels:
            query['severity_details'] = severity_levels[severity]
    
    return queries


def check_missing_required(rule: dict, records: List[dict], severity: str, message_template: str, category: str) -> List[dict]:
    """Check for missing required fields"""
    queries = []
    required_fields = rule.get('fields', [])
    conditions = rule.get('conditions', {})
    
    for i, record in enumerate(records):
        # Check if conditions are met
        if not evaluate_conditions(record, conditions):
            continue
            
        for field in required_fields:
            if not record.get(field, '').strip():
                query = {
                    'query_id': f"MR_{i}_{field}_{hash(str(record))}"[-20:],
                    'subject_id': record.get('subject_id', 'Unknown'),
                    'visit': record.get('visit_name', record.get('visit', '')),
                    'field': field,
                    'severity': severity,
                    'message': message_template.format(field=field, **record),
                    'query_type': 'missing_required',
                    'status': 'OPEN',
                    'record_index': i
                }
                queries.append(query)
    
    return queries


def check_range_violations(rule: dict, records: List[dict], severity: str, message_template: str, category: str) -> List[dict]:
    """Check for values outside acceptable ranges"""
    queries = []
    field = rule.get('field', '')
    min_value = rule.get('min_value')
    max_value = rule.get('max_value')
    conditions = rule.get('conditions', {})
    
    for i, record in enumerate(records):
        if not evaluate_conditions(record, conditions):
            continue
            
        if field in record and record[field]:
            try:
                value = float(record[field])
                violation = False
                violation_details = []
                
                if min_value is not None and value < min_value:
                    violation = True
                    violation_details.append(f"below minimum {min_value}")
                
                if max_value is not None and value > max_value:
                    violation = True
                    violation_details.append(f"above maximum {max_value}")
                
                if violation:
                    query = {
                        'query_id': f"RV_{i}_{field}_{hash(str(record))}"[-20:],
                        'subject_id': record.get('subject_id', 'Unknown'),
                        'visit': record.get('visit_name', record.get('visit', '')),
                        'field': field,
                        'value': record[field],
                        'severity': severity,
                        'message': message_template.format(
                            field=field, 
                            value=value,
                            violation=', '.join(violation_details),
                            **record
                        ),
                        'query_type': 'range_violation',
                        'status': 'OPEN',
                        'record_index': i,
                        'violation_details': violation_details
                    }
                    queries.append(query)
                    
            except (ValueError, TypeError):
                # Value is not numeric
                if rule.get('check_numeric_format', False):
                    query = {
                        'query_id': f"NF_{i}_{field}_{hash(str(record))}"[-20:],
                        'subject_id': record.get('subject_id', 'Unknown'),
                        'visit': record.get('visit_name', record.get('visit', '')),
                        'field': field,
                        'value': record[field],
                        'severity': severity,
                        'message': f"Non-numeric value in numeric field {field}: '{record[field]}'",
                        'query_type': 'format_violation',
                        'status': 'OPEN',
                        'record_index': i
                    }
                    queries.append(query)
    
    return queries


def check_logic_violations(rule: dict, records: List[dict], severity: str, message_template: str, category: str) -> List[dict]:
    """Check for logical inconsistencies"""
    queries = []
    logic_expression = rule.get('expression', '')
    conditions = rule.get('conditions', {})
    
    for i, record in enumerate(records):
        if not evaluate_conditions(record, conditions):
            continue
            
        if evaluate_logic_expression(logic_expression, record):
            query = {
                'query_id': f"LC_{i}_{hash(logic_expression + str(record))}"[-20:],
                'subject_id': record.get('subject_id', 'Unknown'),
                'visit': record.get('visit_name', record.get('visit', '')),
                'severity': severity,
                'message': message_template.format(**record),
                'query_type': 'logic_violation',
                'status': 'OPEN',
                'record_index': i,
                'logic_expression': logic_expression
            }
            queries.append(query)
    
    return queries


def check_consistency_violations(rule: dict, subjects: dict, severity: str, message_template: str, category: str) -> List[dict]:
    """Check for consistency across records for same subject"""
    queries = []
    check_field = rule.get('field', '')
    consistency_type = rule.get('consistency_type', 'same_value')  # same_value, increasing, decreasing
    
    for subject_id, records in subjects.items():
        if len(records) < 2:
            continue
            
        values = []
        record_indices = []
        
        for i, record in enumerate(records):
            if check_field in record and record[check_field]:
                try:
                    if consistency_type in ['increasing', 'decreasing']:
                        values.append(float(record[check_field]))
                    else:
                        values.append(record[check_field])
                    record_indices.append(i)
                except ValueError:
                    values.append(record[check_field])
                    record_indices.append(i)
        
        if len(set(values)) > 1:  # Values are different
            violation = False
            
            if consistency_type == 'same_value':
                violation = True
                violation_msg = f"Inconsistent values for {check_field}: {values}"
            elif consistency_type == 'increasing' and len(values) > 1:
                if not all(values[i] <= values[i+1] for i in range(len(values)-1)):
                    violation = True
                    violation_msg = f"Values not increasing for {check_field}: {values}"
            elif consistency_type == 'decreasing' and len(values) > 1:
                if not all(values[i] >= values[i+1] for i in range(len(values)-1)):
                    violation = True
                    violation_msg = f"Values not decreasing for {check_field}: {values}"
            
            if violation:
                query = {
                    'query_id': f"CC_{subject_id}_{check_field}_{hash(str(values))}"[-20:],
                    'subject_id': subject_id,
                    'field': check_field,
                    'severity': severity,
                    'message': message_template.format(
                        field=check_field,
                        values=values,
                        subject_id=subject_id,
                        violation_msg=violation_msg
                    ),
                    'query_type': 'consistency_violation',
                    'status': 'OPEN',
                    'values': values,
                    'consistency_type': consistency_type
                }
                queries.append(query)
    
    return queries


def check_date_logic(rule: dict, records: List[dict], subjects: dict, severity: str, message_template: str, category: str) -> List[dict]:
    """Check date logic violations"""
    queries = []
    date_rule = rule.get('date_rule', '')
    
    if date_rule == 'chronological_order':
        date_fields = rule.get('date_fields', [])
        
        for subject_id, subject_records in subjects.items():
            for record in subject_records:
                dates = []
                field_names = []
                
                for field in date_fields:
                    if field in record and record[field]:
                        try:
                            date_obj = parse_date(record[field])
                            dates.append(date_obj)
                            field_names.append(field)
                        except ValueError:
                            continue
                
                # Check if dates are in chronological order
                if len(dates) > 1:
                    for i in range(len(dates) - 1):
                        if dates[i] > dates[i + 1]:
                            query = {
                                'query_id': f"DL_{subject_id}_{hash(str(dates))}"[-20:],
                                'subject_id': subject_id,
                                'severity': severity,
                                'message': message_template.format(
                                    field1=field_names[i],
                                    date1=record[field_names[i]],
                                    field2=field_names[i+1],
                                    date2=record[field_names[i+1]],
                                    **record
                                ),
                                'query_type': 'date_logic_violation',
                                'status': 'OPEN',
                                'violation_type': 'chronological_order'
                            }
                            queries.append(query)
    
    elif date_rule == 'future_date_check':
        date_field = rule.get('field', '')
        max_future_days = rule.get('max_future_days', 0)
        
        for i, record in enumerate(records):
            if date_field in record and record[date_field]:
                try:
                    date_obj = parse_date(record[date_field])
                    max_allowed = datetime.now() + timedelta(days=max_future_days)
                    
                    if date_obj > max_allowed:
                        query = {
                            'query_id': f"FD_{i}_{date_field}_{hash(str(record))}"[-20:],
                            'subject_id': record.get('subject_id', 'Unknown'),
                            'field': date_field,
                            'value': record[date_field],
                            'severity': severity,
                            'message': message_template.format(
                                field=date_field,
                                value=record[date_field],
                                **record
                            ),
                            'query_type': 'future_date_violation',
                            'status': 'OPEN',
                            'record_index': i
                        }
                        queries.append(query)
                        
                except ValueError:
                    continue
    
    return queries


def check_duplicates(rule: dict, records: List[dict], severity: str, message_template: str, category: str) -> List[dict]:
    """Check for duplicate records"""
    queries = []
    key_fields = rule.get('key_fields', [])
    
    if not key_fields:
        return queries
    
    seen_keys = {}
    
    for i, record in enumerate(records):
        key = tuple(record.get(field, '') for field in key_fields)
        
        if key in seen_keys:
            query = {
                'query_id': f"DUP_{i}_{hash(str(key))}"[-20:],
                'subject_id': record.get('subject_id', 'Unknown'),
                'severity': severity,
                'message': message_template.format(
                    key_fields=', '.join(key_fields),
                    key_values=', '.join(str(k) for k in key),
                    **record
                ),
                'query_type': 'duplicate_record',
                'status': 'OPEN',
                'record_index': i,
                'duplicate_of_index': seen_keys[key],
                'key_fields': key_fields
            }
            queries.append(query)
        else:
            seen_keys[key] = i
    
    return queries


def check_pattern_violations(rule: dict, records: List[dict], severity: str, message_template: str, category: str) -> List[dict]:
    """Check for pattern violations using regex"""
    queries = []
    field = rule.get('field', '')
    pattern = rule.get('pattern', '')
    pattern_type = rule.get('pattern_type', 'must_match')  # must_match or must_not_match
    
    if not pattern:
        return queries
    
    try:
        regex = re.compile(pattern)
    except re.error:
        return queries
    
    for i, record in enumerate(records):
        if field in record and record[field]:
            value = str(record[field])
            matches = bool(regex.match(value))
            
            violation = (pattern_type == 'must_match' and not matches) or \
                       (pattern_type == 'must_not_match' and matches)
            
            if violation:
                query = {
                    'query_id': f"PT_{i}_{field}_{hash(str(record))}"[-20:],
                    'subject_id': record.get('subject_id', 'Unknown'),
                    'field': field,
                    'value': record[field],
                    'severity': severity,
                    'message': message_template.format(
                        field=field,
                        value=record[field],
                        pattern=pattern,
                        **record
                    ),
                    'query_type': 'pattern_violation',
                    'status': 'OPEN',
                    'record_index': i,
                    'pattern': pattern,
                    'pattern_type': pattern_type
                }
                queries.append(query)
    
    return queries


def check_cross_domain_logic(rule: dict, subjects: dict, severity: str, message_template: str, category: str) -> List[dict]:
    """Check cross-domain logic violations"""
    queries = []
    # This would implement complex cross-domain checks
    # For now, return empty list as it requires more complex domain relationship definitions
    return queries


def evaluate_conditions(record: dict, conditions: dict) -> bool:
    """Evaluate whether conditions are met for applying a rule"""
    if not conditions:
        return True
    
    for field, condition in conditions.items():
        if field not in record:
            return False
            
        value = record[field]
        
        if isinstance(condition, str):
            if value != condition:
                return False
        elif isinstance(condition, list):
            if value not in condition:
                return False
        elif isinstance(condition, dict):
            if 'equals' in condition and value != condition['equals']:
                return False
            if 'not_equals' in condition and value == condition['not_equals']:
                return False
            if 'in' in condition and value not in condition['in']:
                return False
            if 'not_in' in condition and value in condition['not_in']:
                return False
    
    return True


def evaluate_logic_expression(expression: str, record: dict) -> bool:
    """Evaluate a logic expression against a record"""
    # This is a simplified implementation
    # In practice, you'd want a more robust expression evaluator
    
    # Replace field names with their values
    for field, value in record.items():
        expression = expression.replace(f'{{{field}}}', f'"{value}"')
    
    # Simple evaluations
    try:
        # This is potentially unsafe - in production use a safer expression evaluator
        return eval(expression)
    except:
        return False


def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats"""
    formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%d-%b-%Y']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def apply_auto_close_rules(queries: List[dict], auto_close_rules: dict) -> int:
    """Apply automatic query closure rules"""
    auto_closed = 0
    
    for rule_name, rule in auto_close_rules.items():
        conditions = rule.get('conditions', {})
        
        for query in queries:
            if query['status'] != 'OPEN':
                continue
                
            should_close = True
            
            # Check conditions for auto-closure
            for condition_type, condition_value in conditions.items():
                if condition_type == 'severity_below' and query.get('severity', 'INFO') not in condition_value:
                    should_close = False
                elif condition_type == 'query_type' and query.get('query_type', '') not in condition_value:
                    should_close = False
                elif condition_type == 'age_days' and 'generated_date' in query:
                    try:
                        gen_date = datetime.fromisoformat(query['generated_date'])
                        age_days = (datetime.now() - gen_date).days
                        if age_days < condition_value:
                            should_close = False
                    except:
                        should_close = False
            
            if should_close:
                query['status'] = 'AUTO_CLOSED'
                query['closure_reason'] = rule.get('reason', 'Auto-closed by system rule')
                query['closure_date'] = datetime.now().isoformat()
                auto_closed += 1
    
    return auto_closed


def generate_query_summary(queries: List[dict], statistics: dict) -> dict:
    """Generate summary of queries by type and severity"""
    summary = {
        'by_severity': {},
        'by_type': {},
        'by_status': {},
        'top_rules': {},
        'affected_subjects': statistics.get('affected_subjects', 0),
        'recommendation': ''
    }
    
    # Count by severity
    for query in queries:
        severity = query.get('severity', 'INFO')
        summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
    
    # Count by type
    for query in queries:
        query_type = query.get('query_type', 'unknown')
        summary['by_type'][query_type] = summary['by_type'].get(query_type, 0) + 1
    
    # Count by status
    for query in queries:
        status = query.get('status', 'UNKNOWN')
        summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
    
    # Top triggered rules
    summary['top_rules'] = dict(sorted(
        statistics.get('rules_triggered', {}).items(),
        key=lambda x: x[1],
        reverse=True
    )[:10])
    
    # Generate recommendation
    critical_count = summary['by_severity'].get('CRITICAL', 0)
    major_count = summary['by_severity'].get('MAJOR', 0)
    
    if critical_count > 0:
        summary['recommendation'] = f"Immediate attention required: {critical_count} critical queries need resolution within 24 hours."
    elif major_count > 5:
        summary['recommendation'] = f"High priority: {major_count} major queries require attention within 72 hours."
    elif len(queries) > 50:
        summary['recommendation'] = "Large number of queries generated. Consider reviewing data collection processes."
    else:
        summary['recommendation'] = "Query volume is manageable. Continue with routine data cleaning process."
    
    return summary