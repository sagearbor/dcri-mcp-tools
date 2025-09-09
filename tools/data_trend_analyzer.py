"""
Data Trend Analyzer Tool
Identifies unusual data patterns and trends in clinical trial data
Detects anomalies, outliers, and statistical deviations
"""

import csv
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from io import StringIO
import statistics as stats


def run(input_data: dict) -> dict:
    """
    Analyzes data trends and identifies unusual patterns
    
    Args:
        input_data: Dictionary containing:
            - data: CSV data to analyze
            - analysis_fields: List of fields to analyze for trends
            - sensitivity: 'low', 'medium', or 'high' (default: 'medium')
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating if analysis succeeded
            - trend_analysis: Detailed trend analysis results
            - anomalies_detected: List of detected anomalies
            - outliers: Statistical outliers identified
            - patterns: Identified patterns in the data
            - statistics: Trend analysis statistics
    """
    try:
        data = input_data.get('data', '')
        analysis_fields = input_data.get('analysis_fields', [])
        sensitivity = input_data.get('sensitivity', 'medium')
        
        if not data:
            return {
                'success': False,
                'trend_analysis': {},
                'anomalies_detected': [],
                'outliers': [],
                'patterns': {},
                'statistics': {}
            }
        
        # Parse data
        csv_reader = csv.DictReader(StringIO(data))
        records = list(csv_reader)
        
        if not records:
            return {
                'success': False,
                'trend_analysis': {},
                'anomalies_detected': [],
                'outliers': [],
                'patterns': {},
                'statistics': {}
            }
        
        # Auto-detect numeric fields if none specified
        if not analysis_fields:
            analysis_fields = detect_numeric_fields(records)
        
        # Analyze trends for each field
        trend_analysis = {}
        all_anomalies = []
        all_outliers = []
        
        for field in analysis_fields:
            if field in records[0]:
                field_analysis = analyze_field_trends(records, field, sensitivity)
                trend_analysis[field] = field_analysis
                all_anomalies.extend(field_analysis.get('anomalies', []))
                all_outliers.extend(field_analysis.get('outliers', []))
        
        # Identify patterns
        patterns = identify_patterns(records, analysis_fields)
        
        # Generate statistics
        statistics = generate_trend_statistics(trend_analysis, len(records))
        
        return {
            'success': True,
            'trend_analysis': trend_analysis,
            'anomalies_detected': all_anomalies[:100],
            'outliers': all_outliers[:100],
            'patterns': patterns,
            'statistics': statistics
        }
        
    except Exception as e:
        return {
            'success': False,
            'trend_analysis': {},
            'anomalies_detected': [],
            'outliers': [],
            'patterns': {},
            'statistics': {},
            'errors': [f"Trend analysis failed: {str(e)}"]
        }


def detect_numeric_fields(records: List[dict]) -> List[str]:
    """Auto-detect numeric fields in the data"""
    numeric_fields = []
    
    for field in records[0].keys():
        numeric_count = 0
        total_count = 0
        
        for record in records[:10]:  # Sample first 10 records
            value = record.get(field, '').strip()
            if value:
                total_count += 1
                try:
                    float(value)
                    numeric_count += 1
                except ValueError:
                    pass
        
        if total_count > 0 and (numeric_count / total_count) >= 0.8:
            numeric_fields.append(field)
    
    return numeric_fields[:10]  # Limit to 10 fields


def analyze_field_trends(records: List[dict], field: str, sensitivity: str) -> dict:
    """Analyze trends for a specific field"""
    
    # Extract numeric values
    values = []
    valid_records = []
    
    for i, record in enumerate(records):
        value = record.get(field, '').strip()
        if value:
            try:
                num_value = float(value)
                values.append(num_value)
                valid_records.append((i, record, num_value))
            except ValueError:
                pass
    
    if len(values) < 3:
        return {
            'field': field,
            'valid_values': len(values),
            'analysis': 'insufficient_data'
        }
    
    # Basic statistics
    mean_val = stats.mean(values)
    median_val = stats.median(values)
    std_dev = stats.stdev(values) if len(values) > 1 else 0
    
    # Set thresholds based on sensitivity
    if sensitivity == 'high':
        outlier_threshold = 2.0  # 2 standard deviations
        anomaly_threshold = 1.5
    elif sensitivity == 'low':
        outlier_threshold = 3.0  # 3 standard deviations
        anomaly_threshold = 2.5
    else:  # medium
        outlier_threshold = 2.5
        anomaly_threshold = 2.0
    
    # Identify outliers
    outliers = []
    anomalies = []
    
    if std_dev > 0:
        for i, record, value in valid_records:
            z_score = abs((value - mean_val) / std_dev)
            
            if z_score > outlier_threshold:
                outliers.append({
                    'record_index': i,
                    'field': field,
                    'value': value,
                    'z_score': round(z_score, 2),
                    'subject_id': record.get('subject_id', 'Unknown'),
                    'type': 'statistical_outlier'
                })
            elif z_score > anomaly_threshold:
                anomalies.append({
                    'record_index': i,
                    'field': field,
                    'value': value,
                    'z_score': round(z_score, 2),
                    'subject_id': record.get('subject_id', 'Unknown'),
                    'type': 'anomaly'
                })
    
    # Detect trends
    trend_analysis = detect_trend_pattern(values)
    
    return {
        'field': field,
        'valid_values': len(values),
        'statistics': {
            'mean': round(mean_val, 2),
            'median': round(median_val, 2),
            'std_dev': round(std_dev, 2),
            'min': min(values),
            'max': max(values),
            'range': max(values) - min(values)
        },
        'trend': trend_analysis,
        'outliers': outliers,
        'anomalies': anomalies,
        'distribution_analysis': analyze_distribution(values)
    }


def detect_trend_pattern(values: List[float]) -> dict:
    """Detect trend patterns in a series of values"""
    
    if len(values) < 3:
        return {'pattern': 'insufficient_data'}
    
    # Simple trend detection
    increases = 0
    decreases = 0
    stable = 0
    
    for i in range(1, len(values)):
        diff = values[i] - values[i-1]
        if abs(diff) < 0.001:  # Essentially the same
            stable += 1
        elif diff > 0:
            increases += 1
        else:
            decreases += 1
    
    total_changes = increases + decreases + stable
    
    if increases / total_changes > 0.7:
        pattern = 'increasing'
    elif decreases / total_changes > 0.7:
        pattern = 'decreasing'
    elif stable / total_changes > 0.7:
        pattern = 'stable'
    else:
        pattern = 'variable'
    
    # Calculate trend strength
    if pattern in ['increasing', 'decreasing']:
        first_half_mean = stats.mean(values[:len(values)//2])
        second_half_mean = stats.mean(values[len(values)//2:])
        trend_strength = abs(second_half_mean - first_half_mean) / first_half_mean if first_half_mean != 0 else 0
    else:
        trend_strength = 0
    
    return {
        'pattern': pattern,
        'strength': round(trend_strength, 3),
        'increases': increases,
        'decreases': decreases,
        'stable': stable
    }


def analyze_distribution(values: List[float]) -> dict:
    """Analyze the distribution of values"""
    
    if len(values) < 5:
        return {'analysis': 'insufficient_data'}
    
    sorted_values = sorted(values)
    n = len(values)
    
    # Quartiles
    q1_idx = n // 4
    q3_idx = 3 * n // 4
    q1 = sorted_values[q1_idx]
    q3 = sorted_values[q3_idx]
    iqr = q3 - q1
    
    # Check for skewness (simplified)
    mean_val = stats.mean(values)
    median_val = stats.median(values)
    
    if mean_val > median_val + (iqr * 0.2):
        skewness = 'right_skewed'
    elif mean_val < median_val - (iqr * 0.2):
        skewness = 'left_skewed'
    else:
        skewness = 'approximately_normal'
    
    return {
        'quartiles': {
            'q1': round(q1, 2),
            'q3': round(q3, 2),
            'iqr': round(iqr, 2)
        },
        'skewness': skewness,
        'distribution_type': classify_distribution(values)
    }


def classify_distribution(values: List[float]) -> str:
    """Classify the type of distribution"""
    
    # This is a simplified classification
    sorted_values = sorted(values)
    n = len(values)
    
    # Check for uniform distribution
    value_range = max(values) - min(values)
    expected_gap = value_range / (n - 1)
    actual_gaps = [sorted_values[i+1] - sorted_values[i] for i in range(n-1)]
    gap_variance = stats.variance(actual_gaps) if len(actual_gaps) > 1 else 0
    
    if gap_variance < (expected_gap * 0.1):
        return 'approximately_uniform'
    
    # Check for normal distribution (simplified)
    mean_val = stats.mean(values)
    std_dev = stats.stdev(values) if len(values) > 1 else 0
    
    if std_dev > 0:
        # Count values within 1 std dev
        within_1std = sum(1 for v in values if abs(v - mean_val) <= std_dev)
        within_1std_pct = within_1std / len(values)
        
        if 0.6 <= within_1std_pct <= 0.75:
            return 'approximately_normal'
    
    # Check for bimodal (very simplified)
    unique_values = list(set(values))
    if len(unique_values) < len(values) * 0.7:
        return 'clustered_or_bimodal'
    
    return 'unknown_distribution'


def identify_patterns(records: List[dict], analysis_fields: List[str]) -> dict:
    """Identify patterns across multiple fields"""
    
    patterns = {
        'correlations': [],
        'temporal_patterns': [],
        'categorical_patterns': []
    }
    
    # Simple correlation detection between numeric fields
    if len(analysis_fields) >= 2:
        for i, field1 in enumerate(analysis_fields):
            for field2 in analysis_fields[i+1:]:
                correlation = calculate_correlation(records, field1, field2)
                if abs(correlation) > 0.5:  # Moderate to strong correlation
                    patterns['correlations'].append({
                        'field1': field1,
                        'field2': field2,
                        'correlation': round(correlation, 3),
                        'strength': 'strong' if abs(correlation) > 0.7 else 'moderate'
                    })
    
    # Temporal patterns (if date fields exist)
    date_fields = ['date', 'visit_date', 'enrollment_date', 'created_date']
    for field in records[0].keys():
        if any(date_field in field.lower() for date_field in date_fields):
            temporal_pattern = analyze_temporal_pattern(records, field, analysis_fields)
            if temporal_pattern:
                patterns['temporal_patterns'].append(temporal_pattern)
            break  # Just analyze one date field for now
    
    return patterns


def calculate_correlation(records: List[dict], field1: str, field2: str) -> float:
    """Calculate correlation between two numeric fields"""
    
    pairs = []
    for record in records:
        try:
            val1 = float(record.get(field1, '').strip() or '0')
            val2 = float(record.get(field2, '').strip() or '0')
            pairs.append((val1, val2))
        except ValueError:
            continue
    
    if len(pairs) < 3:
        return 0.0
    
    # Calculate Pearson correlation
    x_values = [p[0] for p in pairs]
    y_values = [p[1] for p in pairs]
    
    if len(set(x_values)) <= 1 or len(set(y_values)) <= 1:
        return 0.0
    
    n = len(pairs)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in pairs)
    sum_x2 = sum(x * x for x in x_values)
    sum_y2 = sum(y * y for y in y_values)
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5
    
    return numerator / denominator if denominator != 0 else 0.0


def analyze_temporal_pattern(records: List[dict], date_field: str, analysis_fields: List[str]) -> Optional[dict]:
    """Analyze patterns over time"""
    
    # This is a simplified temporal analysis
    dated_records = []
    
    for record in records:
        date_str = record.get(date_field, '').strip()
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                dated_records.append((date_obj, record))
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_str, '%m/%d/%Y')
                    dated_records.append((date_obj, record))
                except ValueError:
                    continue
    
    if len(dated_records) < 5:
        return None
    
    # Sort by date
    dated_records.sort(key=lambda x: x[0])
    
    # Analyze trend over time for numeric fields
    temporal_trends = {}
    for field in analysis_fields:
        values_over_time = []
        for date_obj, record in dated_records:
            try:
                value = float(record.get(field, '').strip() or '0')
                values_over_time.append(value)
            except ValueError:
                values_over_time.append(None)
        
        # Remove None values for trend analysis
        clean_values = [v for v in values_over_time if v is not None]
        if len(clean_values) >= 3:
            trend = detect_trend_pattern(clean_values)
            temporal_trends[field] = trend
    
    return {
        'date_field': date_field,
        'date_range': {
            'start': dated_records[0][0].strftime('%Y-%m-%d'),
            'end': dated_records[-1][0].strftime('%Y-%m-%d')
        },
        'records_with_dates': len(dated_records),
        'temporal_trends': temporal_trends
    } if temporal_trends else None


def generate_trend_statistics(trend_analysis: dict, total_records: int) -> dict:
    """Generate overall trend analysis statistics"""
    
    if not trend_analysis:
        return {}
    
    total_outliers = sum(len(analysis.get('outliers', [])) for analysis in trend_analysis.values())
    total_anomalies = sum(len(analysis.get('anomalies', [])) for analysis in trend_analysis.values())
    
    fields_analyzed = len(trend_analysis)
    fields_with_outliers = sum(1 for analysis in trend_analysis.values() if analysis.get('outliers'))
    fields_with_trends = sum(1 for analysis in trend_analysis.values() 
                           if analysis.get('trend', {}).get('pattern') not in ['stable', 'variable'])
    
    return {
        'total_records': total_records,
        'fields_analyzed': fields_analyzed,
        'total_outliers': total_outliers,
        'total_anomalies': total_anomalies,
        'fields_with_outliers': fields_with_outliers,
        'fields_with_trends': fields_with_trends,
        'outlier_rate': round((total_outliers / total_records * 100), 2) if total_records > 0 else 0,
        'data_quality_indicators': {
            'high_variability_fields': fields_with_outliers,
            'trending_fields': fields_with_trends,
            'stable_fields': fields_analyzed - fields_with_trends
        }
    }