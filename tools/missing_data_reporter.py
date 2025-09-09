"""
Missing Data Reporter Tool
Identifies and analyzes missing data patterns in clinical trial datasets
Provides detailed reporting on missingness by subject, visit, and field
"""

import csv
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from io import StringIO
import statistics as stats


def run(input_data: dict) -> dict:
    """
    Analyzes missing data patterns in clinical trial data
    
    Args:
        input_data: Dictionary containing:
            - data: CSV data as string to analyze
            - required_fields: List of fields that are required
            - visit_schedule: Optional visit schedule for completeness analysis
            - analysis_level: 'basic', 'detailed', or 'comprehensive' (default: 'detailed')
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating if analysis succeeded
            - missing_data_report: Comprehensive missing data analysis
            - errors: List of processing errors
            - warnings: List of processing warnings
            - statistics: Missing data statistics
            - recommendations: Data quality improvement recommendations
    """
    try:
        data = input_data.get('data', '')
        required_fields = input_data.get('required_fields', [])
        visit_schedule = input_data.get('visit_schedule', [])
        analysis_level = input_data.get('analysis_level', 'detailed')
        
        if not data:
            return {
                'success': False,
                'missing_data_report': {},
                'errors': ['No data provided'],
                'warnings': [],
                'statistics': {},
                'recommendations': []
            }
        
        errors = []
        warnings = []
        
        # Parse data
        csv_reader = csv.DictReader(StringIO(data))
        records = list(csv_reader)
        
        if not records:
            return {
                'success': False,
                'missing_data_report': {},
                'errors': ['Data is empty'],
                'warnings': [],
                'statistics': {},
                'recommendations': []
            }
        
        # Get all field names from data
        all_fields = list(records[0].keys()) if records else []
        
        # Group data by subject
        subjects = {}
        for record in records:
            subject_id = record.get('subject_id', '').strip()
            if subject_id:
                if subject_id not in subjects:
                    subjects[subject_id] = []
                subjects[subject_id].append(record)
        
        # Perform missing data analysis
        missing_data_report = {
            'overall_summary': analyze_overall_missingness(records, all_fields),
            'field_analysis': analyze_field_missingness(records, all_fields, required_fields),
            'subject_analysis': analyze_subject_missingness(subjects, all_fields, required_fields),
            'pattern_analysis': analyze_missing_patterns(records, all_fields),
            'temporal_analysis': {},
            'correlation_analysis': {}
        }
        
        # Add visit-based analysis if visit schedule provided
        if visit_schedule:
            missing_data_report['visit_analysis'] = analyze_visit_missingness(
                subjects, visit_schedule, all_fields
            )
            missing_data_report['temporal_analysis'] = analyze_temporal_patterns(
                subjects, visit_schedule, all_fields
            )
        
        # Comprehensive analysis includes correlations and advanced patterns
        if analysis_level == 'comprehensive':
            missing_data_report['correlation_analysis'] = analyze_missingness_correlations(
                records, all_fields
            )
            missing_data_report['advanced_patterns'] = analyze_advanced_patterns(
                subjects, all_fields
            )
        
        # Generate statistics
        statistics = generate_missing_data_statistics(missing_data_report, len(records), len(subjects))
        
        # Generate recommendations
        recommendations = generate_recommendations(missing_data_report, statistics)
        
        return {
            'success': True,
            'missing_data_report': missing_data_report,
            'errors': errors,
            'warnings': warnings,
            'statistics': statistics,
            'recommendations': recommendations,
            'analysis_summary': {
                'total_records': len(records),
                'total_subjects': len(subjects),
                'total_fields': len(all_fields),
                'required_fields': len(required_fields),
                'analysis_level': analysis_level,
                'overall_completeness': statistics.get('overall_completeness_rate', 0)
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'missing_data_report': {},
            'errors': [f"Missing data analysis failed: {str(e)}"],
            'warnings': [],
            'statistics': {},
            'recommendations': []
        }


def analyze_overall_missingness(records: List[dict], all_fields: List[str]) -> dict:
    """Analyze overall missing data patterns"""
    total_cells = len(records) * len(all_fields)
    missing_cells = 0
    
    field_missing_counts = {field: 0 for field in all_fields}
    
    for record in records:
        for field in all_fields:
            value = record.get(field, '').strip()
            if not value or value.upper() in ['NULL', 'N/A', 'NA', 'MISSING', '', ' ']:
                missing_cells += 1
                field_missing_counts[field] += 1
    
    completeness_rate = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0
    
    return {
        'total_cells': total_cells,
        'missing_cells': missing_cells,
        'completeness_rate': round(completeness_rate, 2),
        'missing_rate': round((missing_cells / total_cells * 100) if total_cells > 0 else 0, 2),
        'fields_with_missing_data': sum(1 for count in field_missing_counts.values() if count > 0),
        'completely_empty_fields': sum(1 for count in field_missing_counts.values() if count == len(records))
    }


def analyze_field_missingness(records: List[dict], all_fields: List[str], required_fields: List[str]) -> dict:
    """Analyze missing data by field"""
    field_analysis = {}
    
    for field in all_fields:
        missing_count = 0
        values = []
        
        for record in records:
            value = record.get(field, '').strip()
            if not value or value.upper() in ['NULL', 'N/A', 'NA', 'MISSING', '', ' ']:
                missing_count += 1
            else:
                values.append(value)
        
        completeness_rate = ((len(records) - missing_count) / len(records) * 100) if len(records) > 0 else 0
        
        field_analysis[field] = {
            'missing_count': missing_count,
            'total_records': len(records),
            'completeness_rate': round(completeness_rate, 2),
            'missing_rate': round((missing_count / len(records) * 100) if len(records) > 0 else 0, 2),
            'is_required': field in required_fields,
            'unique_values': len(set(values)),
            'severity': get_field_missing_severity(completeness_rate, field in required_fields)
        }
    
    # Sort by missing rate (highest first)
    sorted_fields = sorted(field_analysis.items(), key=lambda x: x[1]['missing_rate'], reverse=True)
    
    return {
        'field_details': field_analysis,
        'worst_fields': dict(sorted_fields[:10]),  # Top 10 worst fields
        'required_field_issues': {
            field: details for field, details in field_analysis.items() 
            if field in required_fields and details['missing_count'] > 0
        }
    }


def analyze_subject_missingness(subjects: dict, all_fields: List[str], required_fields: List[str]) -> dict:
    """Analyze missing data by subject"""
    subject_analysis = {}
    
    for subject_id, records in subjects.items():
        total_cells = len(records) * len(all_fields)
        missing_cells = 0
        required_missing = 0
        
        field_missing_counts = {field: 0 for field in all_fields}
        
        for record in records:
            for field in all_fields:
                value = record.get(field, '').strip()
                if not value or value.upper() in ['NULL', 'N/A', 'NA', 'MISSING', '', ' ']:
                    missing_cells += 1
                    field_missing_counts[field] += 1
                    if field in required_fields:
                        required_missing += 1
        
        completeness_rate = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0
        
        subject_analysis[subject_id] = {
            'total_records': len(records),
            'total_cells': total_cells,
            'missing_cells': missing_cells,
            'completeness_rate': round(completeness_rate, 2),
            'required_missing': required_missing,
            'fields_with_missing': sum(1 for count in field_missing_counts.values() if count > 0),
            'completely_missing_fields': sum(1 for count in field_missing_counts.values() if count == len(records)),
            'severity': get_subject_missing_severity(completeness_rate, required_missing)
        }
    
    # Sort by completeness rate (lowest first)
    sorted_subjects = sorted(subject_analysis.items(), key=lambda x: x[1]['completeness_rate'])
    
    return {
        'subject_details': subject_analysis,
        'worst_subjects': dict(sorted_subjects[:10]),  # Top 10 worst subjects
        'completeness_distribution': get_completeness_distribution(subject_analysis),
        'subjects_with_required_missing': sum(1 for details in subject_analysis.values() if details['required_missing'] > 0)
    }


def analyze_missing_patterns(records: List[dict], all_fields: List[str]) -> dict:
    """Analyze common missing data patterns"""
    patterns = {}
    
    for record in records:
        # Create a pattern string representing missing fields
        pattern_key = tuple(
            field for field in all_fields 
            if not record.get(field, '').strip() or 
               record.get(field, '').strip().upper() in ['NULL', 'N/A', 'NA', 'MISSING']
        )
        
        if pattern_key:
            pattern_str = ', '.join(pattern_key) if pattern_key else 'Complete'
            patterns[pattern_str] = patterns.get(pattern_str, 0) + 1
    
    # Sort patterns by frequency
    sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'common_patterns': dict(sorted_patterns[:20]),  # Top 20 patterns
        'total_patterns': len(patterns),
        'most_common_missing_combination': sorted_patterns[0] if sorted_patterns else ('None', 0),
        'records_with_no_missing': patterns.get('', 0)
    }


def analyze_visit_missingness(subjects: dict, visit_schedule: List[dict], all_fields: List[str]) -> dict:
    """Analyze missing data by visit"""
    visit_analysis = {}
    expected_visits = {visit['name']: visit for visit in visit_schedule}
    
    for visit_name in expected_visits.keys():
        visit_records = []
        
        # Collect all records for this visit across subjects
        for subject_records in subjects.values():
            for record in subject_records:
                if record.get('visit_name', '').strip() == visit_name or record.get('visit', '').strip() == visit_name:
                    visit_records.append(record)
        
        if visit_records:
            total_cells = len(visit_records) * len(all_fields)
            missing_cells = 0
            field_missing_counts = {field: 0 for field in all_fields}
            
            for record in visit_records:
                for field in all_fields:
                    value = record.get(field, '').strip()
                    if not value or value.upper() in ['NULL', 'N/A', 'NA', 'MISSING', '', ' ']:
                        missing_cells += 1
                        field_missing_counts[field] += 1
            
            completeness_rate = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0
            
            visit_analysis[visit_name] = {
                'total_records': len(visit_records),
                'expected_subjects': len(subjects),
                'actual_subjects': len(set(r.get('subject_id', '') for r in visit_records)),
                'visit_completion_rate': (len(set(r.get('subject_id', '') for r in visit_records)) / len(subjects) * 100) if subjects else 0,
                'data_completeness_rate': round(completeness_rate, 2),
                'missing_cells': missing_cells,
                'fields_missing_counts': field_missing_counts
            }
    
    return visit_analysis


def analyze_temporal_patterns(subjects: dict, visit_schedule: List[dict], all_fields: List[str]) -> dict:
    """Analyze temporal patterns in missing data"""
    temporal_analysis = {
        'missingness_by_visit_order': {},
        'progressive_missingness': {},
        'dropout_analysis': {}
    }
    
    # Analyze missingness by visit order
    visit_order = {visit['name']: i for i, visit in enumerate(visit_schedule)}
    
    for subject_id, records in subjects.items():
        # Sort records by visit order
        sorted_records = sorted(
            records,
            key=lambda r: visit_order.get(r.get('visit_name', r.get('visit', '')), 999)
        )
        
        # Track missingness progression
        for i, record in enumerate(sorted_records):
            visit_name = record.get('visit_name', record.get('visit', ''))
            if visit_name in visit_order:
                order_pos = visit_order[visit_name]
                
                if order_pos not in temporal_analysis['missingness_by_visit_order']:
                    temporal_analysis['missingness_by_visit_order'][order_pos] = {
                        'visit_name': visit_name,
                        'total_fields_missing': 0,
                        'total_records': 0
                    }
                
                missing_fields = sum(
                    1 for field in all_fields
                    if not record.get(field, '').strip() or 
                       record.get(field, '').strip().upper() in ['NULL', 'N/A', 'NA', 'MISSING']
                )
                
                temporal_analysis['missingness_by_visit_order'][order_pos]['total_fields_missing'] += missing_fields
                temporal_analysis['missingness_by_visit_order'][order_pos]['total_records'] += 1
    
    return temporal_analysis


def analyze_missingness_correlations(records: List[dict], all_fields: List[str]) -> dict:
    """Analyze correlations between missing fields"""
    correlations = {}
    
    # Create binary missing data matrix
    missing_matrix = []
    for record in records:
        row = []
        for field in all_fields:
            value = record.get(field, '').strip()
            is_missing = not value or value.upper() in ['NULL', 'N/A', 'NA', 'MISSING', '', ' ']
            row.append(1 if is_missing else 0)
        missing_matrix.append(row)
    
    # Calculate correlations between fields
    for i, field1 in enumerate(all_fields):
        for j, field2 in enumerate(all_fields[i+1:], i+1):
            # Calculate correlation coefficient for missing patterns
            field1_missing = [row[i] for row in missing_matrix]
            field2_missing = [row[j] for row in missing_matrix]
            
            if sum(field1_missing) > 0 and sum(field2_missing) > 0:  # Both fields have some missing data
                correlation = calculate_correlation(field1_missing, field2_missing)
                if abs(correlation) > 0.3:  # Only include meaningful correlations
                    correlations[f"{field1} vs {field2}"] = round(correlation, 3)
    
    # Sort by correlation strength
    sorted_correlations = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
    
    return {
        'significant_correlations': dict(sorted_correlations[:20]),
        'total_correlations_found': len(correlations),
        'strongest_correlation': sorted_correlations[0] if sorted_correlations else ('None', 0)
    }


def analyze_advanced_patterns(subjects: dict, all_fields: List[str]) -> dict:
    """Analyze advanced missing data patterns"""
    patterns = {
        'monotone_patterns': {},
        'intermittent_patterns': {},
        'block_patterns': {}
    }
    
    # This would implement more sophisticated pattern analysis
    # For now, return basic structure
    return patterns


def get_field_missing_severity(completeness_rate: float, is_required: bool) -> str:
    """Determine severity level for field missing data"""
    if is_required and completeness_rate < 95:
        return 'CRITICAL'
    elif completeness_rate < 70:
        return 'HIGH'
    elif completeness_rate < 85:
        return 'MEDIUM'
    else:
        return 'LOW'


def get_subject_missing_severity(completeness_rate: float, required_missing: int) -> str:
    """Determine severity level for subject missing data"""
    if required_missing > 0 or completeness_rate < 70:
        return 'HIGH'
    elif completeness_rate < 85:
        return 'MEDIUM'
    else:
        return 'LOW'


def get_completeness_distribution(subject_analysis: dict) -> dict:
    """Get distribution of completeness rates across subjects"""
    rates = [details['completeness_rate'] for details in subject_analysis.values()]
    
    if not rates:
        return {}
    
    return {
        'mean': round(stats.mean(rates), 2),
        'median': round(stats.median(rates), 2),
        'std_dev': round(stats.stdev(rates), 2) if len(rates) > 1 else 0,
        'min': min(rates),
        'max': max(rates),
        'quartiles': {
            'q25': round(stats.quantiles(rates, n=4)[0], 2) if len(rates) >= 4 else rates[0],
            'q50': round(stats.median(rates), 2),
            'q75': round(stats.quantiles(rates, n=4)[2], 2) if len(rates) >= 4 else rates[-1]
        }
    }


def calculate_correlation(x: List[int], y: List[int]) -> float:
    """Calculate Pearson correlation coefficient"""
    if len(x) != len(y) or len(x) == 0:
        return 0
    
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xx = sum(xi * xi for xi in x)
    sum_yy = sum(yi * yi for yi in y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_xx - sum_x * sum_x) * (n * sum_yy - sum_y * sum_y)) ** 0.5
    
    if denominator == 0:
        return 0
    
    return numerator / denominator


def generate_missing_data_statistics(report: dict, total_records: int, total_subjects: int) -> dict:
    """Generate comprehensive missing data statistics"""
    overall = report.get('overall_summary', {})
    field_analysis = report.get('field_analysis', {})
    subject_analysis = report.get('subject_analysis', {})
    
    return {
        'overall_completeness_rate': overall.get('completeness_rate', 0),
        'overall_missing_rate': overall.get('missing_rate', 0),
        'total_missing_cells': overall.get('missing_cells', 0),
        'fields_with_issues': overall.get('fields_with_missing_data', 0),
        'completely_empty_fields': overall.get('completely_empty_fields', 0),
        'required_fields_with_missing': len(field_analysis.get('required_field_issues', {})),
        'subjects_with_missing_required': subject_analysis.get('subjects_with_required_missing', 0),
        'worst_completeness_rate': min(
            (details['completeness_rate'] for details in subject_analysis.get('subject_details', {}).values()),
            default=100
        ),
        'best_completeness_rate': max(
            (details['completeness_rate'] for details in subject_analysis.get('subject_details', {}).values()),
            default=0
        ),
        'data_quality_score': calculate_data_quality_score(report)
    }


def calculate_data_quality_score(report: dict) -> float:
    """Calculate overall data quality score based on missing data patterns"""
    overall = report.get('overall_summary', {})
    field_analysis = report.get('field_analysis', {})
    
    base_score = overall.get('completeness_rate', 0)
    
    # Penalize for required field issues
    required_issues = len(field_analysis.get('required_field_issues', {}))
    required_penalty = min(required_issues * 10, 30)  # Max 30 point penalty
    
    # Penalize for completely empty fields
    empty_fields = overall.get('completely_empty_fields', 0)
    empty_penalty = min(empty_fields * 5, 20)  # Max 20 point penalty
    
    final_score = max(base_score - required_penalty - empty_penalty, 0)
    return round(final_score, 2)


def generate_recommendations(report: dict, statistics: dict) -> List[dict]:
    """Generate data quality improvement recommendations"""
    recommendations = []
    
    # Overall completeness recommendations
    if statistics['overall_completeness_rate'] < 85:
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Overall Data Quality',
            'issue': f"Overall completeness rate is {statistics['overall_completeness_rate']:.1f}%, below target of 85%",
            'recommendation': 'Implement comprehensive data collection training and monitoring procedures',
            'estimated_impact': 'High'
        })
    
    # Required field recommendations
    if statistics['required_fields_with_missing'] > 0:
        recommendations.append({
            'priority': 'CRITICAL',
            'category': 'Required Fields',
            'issue': f"{statistics['required_fields_with_missing']} required fields have missing data",
            'recommendation': 'Implement mandatory field validation and real-time data entry checks',
            'estimated_impact': 'Very High'
        })
    
    # Subject-level recommendations
    if statistics['subjects_with_missing_required'] > 0:
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Subject Data Quality',
            'issue': f"{statistics['subjects_with_missing_required']} subjects have missing required data",
            'recommendation': 'Review and follow up with sites for subject-specific data completion',
            'estimated_impact': 'High'
        })
    
    # Field-specific recommendations
    field_details = report.get('field_analysis', {}).get('field_details', {})
    high_missing_fields = [
        field for field, details in field_details.items()
        if details['missing_rate'] > 20 and details['is_required']
    ]
    
    if high_missing_fields:
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Field-Specific Issues',
            'issue': f"Fields with >20% missing data: {', '.join(high_missing_fields[:5])}",
            'recommendation': 'Review CRF design and data collection procedures for these fields',
            'estimated_impact': 'Medium'
        })
    
    # Pattern-based recommendations
    patterns = report.get('pattern_analysis', {})
    if patterns.get('total_patterns', 0) > 10:
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Missing Data Patterns',
            'issue': f"Multiple distinct missing data patterns detected ({patterns['total_patterns']})",
            'recommendation': 'Investigate systematic causes of missing data and implement targeted interventions',
            'estimated_impact': 'Medium'
        })
    
    # Data quality score recommendations
    if statistics['data_quality_score'] < 80:
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Overall Data Quality Score',
            'issue': f"Data quality score is {statistics['data_quality_score']:.1f}%, below acceptable threshold",
            'recommendation': 'Implement comprehensive data quality improvement program with regular monitoring',
            'estimated_impact': 'Very High'
        })
    
    return recommendations