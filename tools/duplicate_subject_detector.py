"""
Duplicate Subject Detector Tool
Identifies potential duplicate enrollments in clinical trial data
Uses multiple matching algorithms and fuzzy matching techniques
"""

import csv
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from io import StringIO
import hashlib


def run(input_data: dict) -> dict:
    """
    Detects potential duplicate subjects in clinical trial data
    
    Args:
        input_data: Dictionary containing:
            - data: CSV data as string containing subject information
            - matching_fields: List of fields to use for matching
            - matching_algorithm: 'exact', 'fuzzy', or 'comprehensive' (default: 'comprehensive')
            - similarity_threshold: Minimum similarity score for fuzzy matching (0-100, default: 85)
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating if detection succeeded
            - duplicates_found: List of potential duplicate groups
            - errors: List of processing errors
            - warnings: List of processing warnings
            - statistics: Duplicate detection statistics
            - recommendations: Actions to resolve duplicates
    """
    try:
        data = input_data.get('data', '')
        matching_fields = input_data.get('matching_fields', get_default_matching_fields())
        matching_algorithm = input_data.get('matching_algorithm', 'comprehensive')
        similarity_threshold = input_data.get('similarity_threshold', 85)
        
        if not data:
            return {
                'success': False,
                'duplicates_found': [],
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
                'duplicates_found': [],
                'errors': ['Data is empty'],
                'warnings': [],
                'statistics': {},
                'recommendations': []
            }
        
        # Validate matching fields
        available_fields = set(records[0].keys()) if records else set()
        valid_matching_fields = [field for field in matching_fields if field in available_fields]
        
        if not valid_matching_fields:
            warnings.append('No specified matching fields found in data, using default fields')
            valid_matching_fields = list(available_fields)[:5]  # Use first 5 fields
        
        # Detect duplicates based on algorithm
        if matching_algorithm == 'exact':
            duplicate_groups = detect_exact_duplicates(records, valid_matching_fields)
        elif matching_algorithm == 'fuzzy':
            duplicate_groups = detect_fuzzy_duplicates(records, valid_matching_fields, similarity_threshold)
        else:  # comprehensive
            duplicate_groups = detect_comprehensive_duplicates(records, valid_matching_fields, similarity_threshold)
        
        # Generate statistics
        statistics = generate_duplicate_statistics(records, duplicate_groups, valid_matching_fields)
        
        # Generate recommendations
        recommendations = generate_recommendations(duplicate_groups, statistics)
        
        return {
            'success': True,
            'duplicates_found': duplicate_groups[:100],  # Limit to prevent huge responses
            'errors': errors,
            'warnings': warnings,
            'statistics': statistics,
            'recommendations': recommendations,
            'detection_summary': {
                'total_records': len(records),
                'duplicate_groups': len(duplicate_groups),
                'potentially_duplicate_records': sum(len(group['records']) for group in duplicate_groups),
                'matching_algorithm': matching_algorithm,
                'matching_fields': valid_matching_fields,
                'similarity_threshold': similarity_threshold
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'duplicates_found': [],
            'errors': [f"Duplicate detection failed: {str(e)}"],
            'warnings': [],
            'statistics': {},
            'recommendations': []
        }


def get_default_matching_fields() -> List[str]:
    """Get default fields for duplicate matching"""
    return [
        'first_name', 'last_name', 'date_of_birth', 'dob',
        'gender', 'sex', 'phone_number', 'phone', 'email',
        'address', 'zip_code', 'postal_code', 'ssn', 
        'medical_record_number', 'mrn', 'initials'
    ]


def detect_exact_duplicates(records: List[dict], matching_fields: List[str]) -> List[dict]:
    """Detect exact duplicate matches"""
    duplicate_groups = []
    processed = set()
    
    for i, record1 in enumerate(records):
        if i in processed:
            continue
            
        matches = [{'record': record1, 'index': i, 'similarity_score': 100.0}]
        
        for j, record2 in enumerate(records[i+1:], i+1):
            if j in processed:
                continue
                
            if is_exact_match(record1, record2, matching_fields):
                matches.append({'record': record2, 'index': j, 'similarity_score': 100.0})
                processed.add(j)
        
        if len(matches) > 1:
            duplicate_groups.append({
                'group_id': f"exact_{len(duplicate_groups)+1}",
                'match_type': 'exact',
                'confidence': 'high',
                'records': matches,
                'matching_criteria': get_matching_criteria(matches[0]['record'], matches[1]['record'], matching_fields),
                'recommended_action': 'immediate_review'
            })
            processed.add(i)
    
    return duplicate_groups


def detect_fuzzy_duplicates(records: List[dict], matching_fields: List[str], threshold: float) -> List[dict]:
    """Detect fuzzy duplicate matches"""
    duplicate_groups = []
    processed = set()
    
    for i, record1 in enumerate(records):
        if i in processed:
            continue
            
        matches = [{'record': record1, 'index': i, 'similarity_score': 100.0}]
        
        for j, record2 in enumerate(records[i+1:], i+1):
            if j in processed:
                continue
                
            similarity = calculate_similarity(record1, record2, matching_fields)
            if similarity >= threshold:
                matches.append({'record': record2, 'index': j, 'similarity_score': similarity})
        
        if len(matches) > 1:
            # Sort by similarity score
            matches.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            confidence = 'high' if matches[1]['similarity_score'] >= 95 else 'medium' if matches[1]['similarity_score'] >= 90 else 'low'
            
            duplicate_groups.append({
                'group_id': f"fuzzy_{len(duplicate_groups)+1}",
                'match_type': 'fuzzy',
                'confidence': confidence,
                'records': matches,
                'matching_criteria': get_matching_criteria(matches[0]['record'], matches[1]['record'], matching_fields),
                'recommended_action': 'detailed_review' if confidence == 'low' else 'priority_review'
            })
            
            for match in matches[1:]:
                processed.add(match['index'])
            processed.add(i)
    
    return duplicate_groups


def detect_comprehensive_duplicates(records: List[dict], matching_fields: List[str], threshold: float) -> List[dict]:
    """Detect duplicates using comprehensive matching approach"""
    duplicate_groups = []
    
    # First, detect exact matches
    exact_groups = detect_exact_duplicates(records, matching_fields)
    duplicate_groups.extend(exact_groups)
    
    # Track records already in exact duplicate groups
    exact_processed = set()
    for group in exact_groups:
        for match in group['records']:
            exact_processed.add(match['index'])
    
    # Then, detect fuzzy matches among remaining records
    remaining_records = [(i, record) for i, record in enumerate(records) if i not in exact_processed]
    
    if remaining_records:
        fuzzy_groups = detect_fuzzy_duplicates_from_subset(remaining_records, matching_fields, threshold)
        duplicate_groups.extend(fuzzy_groups)
    
    # Finally, detect potential matches using alternative criteria
    phonetic_groups = detect_phonetic_duplicates(records, matching_fields, exact_processed)
    duplicate_groups.extend(phonetic_groups)
    
    return duplicate_groups


def detect_fuzzy_duplicates_from_subset(indexed_records: List[Tuple[int, dict]], matching_fields: List[str], threshold: float) -> List[dict]:
    """Detect fuzzy duplicates from a subset of records"""
    duplicate_groups = []
    processed = set()
    
    for i, (idx1, record1) in enumerate(indexed_records):
        if idx1 in processed:
            continue
            
        matches = [{'record': record1, 'index': idx1, 'similarity_score': 100.0}]
        
        for j, (idx2, record2) in enumerate(indexed_records[i+1:], i+1):
            if idx2 in processed:
                continue
                
            similarity = calculate_similarity(record1, record2, matching_fields)
            if similarity >= threshold:
                matches.append({'record': record2, 'index': idx2, 'similarity_score': similarity})
        
        if len(matches) > 1:
            matches.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            confidence = 'high' if matches[1]['similarity_score'] >= 95 else 'medium' if matches[1]['similarity_score'] >= 90 else 'low'
            
            duplicate_groups.append({
                'group_id': f"comprehensive_{len(duplicate_groups)+1}",
                'match_type': 'comprehensive_fuzzy',
                'confidence': confidence,
                'records': matches,
                'matching_criteria': get_matching_criteria(matches[0]['record'], matches[1]['record'], matching_fields),
                'recommended_action': 'detailed_review' if confidence == 'low' else 'priority_review'
            })
            
            for match in matches[1:]:
                processed.add(match['index'])
            processed.add(idx1)
    
    return duplicate_groups


def detect_phonetic_duplicates(records: List[dict], matching_fields: List[str], exclude_indices: set) -> List[dict]:
    """Detect duplicates using phonetic matching for names"""
    duplicate_groups = []
    
    # Focus on name fields
    name_fields = [field for field in matching_fields if 'name' in field.lower()]
    
    if not name_fields:
        return duplicate_groups
    
    processed = set()
    
    for i, record1 in enumerate(records):
        if i in processed or i in exclude_indices:
            continue
            
        matches = [{'record': record1, 'index': i, 'similarity_score': 100.0}]
        
        for j, record2 in enumerate(records[i+1:], i+1):
            if j in processed or j in exclude_indices:
                continue
                
            if has_phonetic_match(record1, record2, name_fields):
                # Calculate additional similarity
                similarity = calculate_similarity(record1, record2, matching_fields)
                if similarity >= 70:  # Lower threshold for phonetic matches
                    matches.append({'record': record2, 'index': j, 'similarity_score': similarity})
        
        if len(matches) > 1:
            duplicate_groups.append({
                'group_id': f"phonetic_{len(duplicate_groups)+1}",
                'match_type': 'phonetic',
                'confidence': 'low',
                'records': matches,
                'matching_criteria': get_matching_criteria(matches[0]['record'], matches[1]['record'], matching_fields),
                'recommended_action': 'manual_review'
            })
            
            for match in matches[1:]:
                processed.add(match['index'])
            processed.add(i)
    
    return duplicate_groups


def is_exact_match(record1: dict, record2: dict, matching_fields: List[str]) -> bool:
    """Check if two records are exact matches"""
    matches = 0
    total_fields = 0
    
    for field in matching_fields:
        value1 = normalize_value(record1.get(field, ''))
        value2 = normalize_value(record2.get(field, ''))
        
        if value1 and value2:  # Both have values
            total_fields += 1
            if value1 == value2:
                matches += 1
        elif value1 or value2:  # One has value, other doesn't
            total_fields += 1
    
    # Require at least 2 matching fields and 100% match rate
    return matches >= 2 and total_fields > 0 and matches == total_fields


def calculate_similarity(record1: dict, record2: dict, matching_fields: List[str]) -> float:
    """Calculate similarity score between two records"""
    total_score = 0.0
    field_count = 0
    weights = get_field_weights()
    
    for field in matching_fields:
        value1 = normalize_value(record1.get(field, ''))
        value2 = normalize_value(record2.get(field, ''))
        
        if value1 and value2:  # Both have values
            field_weight = weights.get(field, 1.0)
            
            if field in ['date_of_birth', 'dob']:
                score = calculate_date_similarity(value1, value2)
            elif field in ['phone_number', 'phone']:
                score = calculate_phone_similarity(value1, value2)
            elif field in ['first_name', 'last_name']:
                score = calculate_name_similarity(value1, value2)
            else:
                score = calculate_string_similarity(value1, value2)
            
            total_score += score * field_weight
            field_count += field_weight
    
    return (total_score / field_count) if field_count > 0 else 0.0


def get_field_weights() -> dict:
    """Get weights for different fields in similarity calculation"""
    return {
        'first_name': 2.0,
        'last_name': 2.5,
        'date_of_birth': 3.0,
        'dob': 3.0,
        'ssn': 4.0,
        'medical_record_number': 4.0,
        'mrn': 4.0,
        'email': 2.0,
        'phone_number': 2.0,
        'phone': 2.0,
        'address': 1.5,
        'gender': 1.0,
        'sex': 1.0
    }


def calculate_date_similarity(date1: str, date2: str) -> float:
    """Calculate similarity between two dates"""
    try:
        # Try to parse dates
        d1 = parse_date(date1)
        d2 = parse_date(date2)
        
        if d1 == d2:
            return 100.0
        
        # Calculate difference in days
        diff_days = abs((d1 - d2).days)
        
        if diff_days == 0:
            return 100.0
        elif diff_days <= 1:
            return 95.0
        elif diff_days <= 7:
            return 80.0
        elif diff_days <= 30:
            return 60.0
        elif diff_days <= 365:
            return 30.0
        else:
            return 0.0
            
    except:
        # Fall back to string similarity if date parsing fails
        return calculate_string_similarity(date1, date2)


def calculate_phone_similarity(phone1: str, phone2: str) -> float:
    """Calculate similarity between phone numbers"""
    # Normalize phone numbers (remove formatting)
    norm1 = re.sub(r'[^\d]', '', phone1)
    norm2 = re.sub(r'[^\d]', '', phone2)
    
    if norm1 == norm2:
        return 100.0
    
    # Check if one is a subset of the other (different formatting)
    if norm1 in norm2 or norm2 in norm1:
        return 90.0
    
    # Check last 7 digits (local number)
    if len(norm1) >= 7 and len(norm2) >= 7:
        if norm1[-7:] == norm2[-7:]:
            return 85.0
    
    return calculate_string_similarity(phone1, phone2)


def calculate_name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity between names"""
    # Check exact match
    if name1 == name2:
        return 100.0
    
    # Check if one is nickname of the other
    if is_nickname_match(name1, name2):
        return 95.0
    
    # Check phonetic similarity
    if soundex(name1) == soundex(name2):
        return 90.0
    
    # Fall back to string similarity
    return calculate_string_similarity(name1, name2)


def calculate_string_similarity(str1: str, str2: str) -> float:
    """Calculate Levenshtein distance-based similarity"""
    if str1 == str2:
        return 100.0
    
    if not str1 or not str2:
        return 0.0
    
    # Levenshtein distance
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    distance = dp[m][n]
    max_len = max(len(str1), len(str2))
    
    return ((max_len - distance) / max_len) * 100.0


def has_phonetic_match(record1: dict, record2: dict, name_fields: List[str]) -> bool:
    """Check if records have phonetic name matches"""
    for field in name_fields:
        name1 = normalize_value(record1.get(field, ''))
        name2 = normalize_value(record2.get(field, ''))
        
        if name1 and name2:
            if soundex(name1) == soundex(name2) and name1 != name2:
                return True
    
    return False


def soundex(name: str) -> str:
    """Generate Soundex code for phonetic matching"""
    if not name:
        return "0000"
    
    name = name.upper()
    soundex_code = name[0]
    
    # Mapping for consonants
    mapping = {
        'BFPV': '1', 'CGJKQSXZ': '2', 'DT': '3',
        'L': '4', 'MN': '5', 'R': '6'
    }
    
    for char in name[1:]:
        for key, value in mapping.items():
            if char in key:
                soundex_code += value
                break
        else:
            if char not in 'AEIOUY':
                soundex_code += '0'
    
    # Remove consecutive duplicates
    result = soundex_code[0]
    for i in range(1, len(soundex_code)):
        if soundex_code[i] != soundex_code[i-1]:
            result += soundex_code[i]
    
    # Remove zeros and pad/truncate to 4 characters
    result = result.replace('0', '')
    result = (result + '000')[:4]
    
    return result


def is_nickname_match(name1: str, name2: str) -> bool:
    """Check if one name is a common nickname for the other"""
    nickname_pairs = {
        ('james', 'jim'), ('james', 'jimmy'), ('william', 'bill'), ('william', 'will'),
        ('robert', 'bob'), ('robert', 'rob'), ('michael', 'mike'), ('david', 'dave'),
        ('richard', 'rick'), ('richard', 'dick'), ('thomas', 'tom'), ('christopher', 'chris'),
        ('matthew', 'matt'), ('anthony', 'tony'), ('elizabeth', 'liz'), ('elizabeth', 'beth'),
        ('patricia', 'pat'), ('jennifer', 'jen'), ('linda', 'lynn'), ('barbara', 'barb'),
        ('susan', 'sue'), ('jessica', 'jess'), ('sarah', 'sara'), ('karen', 'kay'),
        ('nancy', 'nan'), ('lisa', 'lee'), ('betty', 'beth'), ('helen', 'nell'),
        ('sandra', 'sandy'), ('donna', 'don'), ('carol', 'carrie'), ('ruth', 'rue'),
        ('sharon', 'shari'), ('michelle', 'shelly'), ('laura', 'laurie'), ('sarah', 'sally'),
        ('kimberly', 'kim'), ('deborah', 'deb'), ('dorothy', 'dot'), ('lisa', 'lis'),
        ('nancy', 'nance'), ('karen', 'carrie'), ('betty', 'bette'), ('helen', 'ellie')
    }
    
    name1_lower = name1.lower()
    name2_lower = name2.lower()
    
    return (name1_lower, name2_lower) in nickname_pairs or (name2_lower, name1_lower) in nickname_pairs


def normalize_value(value: str) -> str:
    """Normalize a value for comparison"""
    if not value:
        return ''
    
    # Convert to lowercase and strip whitespace
    normalized = str(value).lower().strip()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove common punctuation
    normalized = re.sub(r'[.,\-_()]', '', normalized)
    
    return normalized


def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats"""
    formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%m-%d-%Y', '%d-%m-%Y']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def get_matching_criteria(record1: dict, record2: dict, matching_fields: List[str]) -> dict:
    """Get detailed matching criteria for two records"""
    criteria = {}
    
    for field in matching_fields:
        value1 = record1.get(field, '')
        value2 = record2.get(field, '')
        
        if value1 and value2:
            if field in ['date_of_birth', 'dob']:
                similarity = calculate_date_similarity(value1, value2)
            elif field in ['phone_number', 'phone']:
                similarity = calculate_phone_similarity(value1, value2)
            elif field in ['first_name', 'last_name']:
                similarity = calculate_name_similarity(value1, value2)
            else:
                similarity = calculate_string_similarity(value1, value2)
            
            criteria[field] = {
                'value1': value1,
                'value2': value2,
                'similarity': round(similarity, 2),
                'match_type': 'exact' if similarity == 100 else 'partial' if similarity >= 80 else 'weak'
            }
    
    return criteria


def generate_duplicate_statistics(records: List[dict], duplicate_groups: List[dict], matching_fields: List[str]) -> dict:
    """Generate statistics about duplicate detection"""
    total_duplicates = sum(len(group['records']) for group in duplicate_groups)
    
    confidence_counts = {'high': 0, 'medium': 0, 'low': 0}
    match_type_counts = {'exact': 0, 'fuzzy': 0, 'phonetic': 0, 'comprehensive_fuzzy': 0}
    
    for group in duplicate_groups:
        confidence_counts[group['confidence']] += 1
        match_type_counts[group['match_type']] += 1
    
    return {
        'total_records': len(records),
        'duplicate_groups': len(duplicate_groups),
        'total_duplicate_records': total_duplicates,
        'unique_records': len(records) - total_duplicates + len(duplicate_groups),  # Count each group as one
        'duplication_rate': round((total_duplicates / len(records) * 100), 2) if records else 0,
        'confidence_distribution': confidence_counts,
        'match_type_distribution': match_type_counts,
        'matching_fields_used': matching_fields,
        'largest_duplicate_group': max((len(group['records']) for group in duplicate_groups), default=0),
        'avg_group_size': round(sum(len(group['records']) for group in duplicate_groups) / len(duplicate_groups), 2) if duplicate_groups else 0
    }


def generate_recommendations(duplicate_groups: List[dict], statistics: dict) -> List[dict]:
    """Generate recommendations for handling duplicates"""
    recommendations = []
    
    # High confidence duplicates
    high_conf_groups = [g for g in duplicate_groups if g['confidence'] == 'high']
    if high_conf_groups:
        recommendations.append({
            'priority': 'HIGH',
            'category': 'High Confidence Duplicates',
            'issue': f"{len(high_conf_groups)} high-confidence duplicate groups detected",
            'recommendation': 'Review and merge or exclude duplicate records immediately',
            'estimated_impact': 'Critical - affects data integrity'
        })
    
    # Overall duplication rate
    if statistics['duplication_rate'] > 5:
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Duplication Rate',
            'issue': f"Duplication rate is {statistics['duplication_rate']:.1f}%, above acceptable threshold",
            'recommendation': 'Implement stronger enrollment screening procedures and real-time duplicate checking',
            'estimated_impact': 'High - reduces study efficiency'
        })
    
    # Large duplicate groups
    if statistics['largest_duplicate_group'] > 2:
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Large Duplicate Groups',
            'issue': f"Largest duplicate group contains {statistics['largest_duplicate_group']} records",
            'recommendation': 'Investigate potential systematic enrollment issues or data entry problems',
            'estimated_impact': 'Medium - may indicate process issues'
        })
    
    # Low confidence matches
    low_conf_groups = [g for g in duplicate_groups if g['confidence'] == 'low']
    if low_conf_groups:
        recommendations.append({
            'priority': 'LOW',
            'category': 'Low Confidence Matches',
            'issue': f"{len(low_conf_groups)} low-confidence potential duplicates found",
            'recommendation': 'Schedule manual review of potential duplicates to verify false positives',
            'estimated_impact': 'Low - primarily for verification'
        })
    
    # Phonetic matches
    phonetic_groups = [g for g in duplicate_groups if g['match_type'] == 'phonetic']
    if phonetic_groups:
        recommendations.append({
            'priority': 'LOW',
            'category': 'Phonetic Matches',
            'issue': f"{len(phonetic_groups)} phonetic name matches detected",
            'recommendation': 'Review phonetic matches for potential name variations or spelling errors',
            'estimated_impact': 'Low - may help identify clerical errors'
        })
    
    return recommendations