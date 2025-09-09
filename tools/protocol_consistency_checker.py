"""
Protocol Consistency Checker Tool

Finds inconsistencies in clinical trial protocols including:
- Conflicting information
- Missing required sections
- Formatting issues
- Reference errors
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check protocol document for consistency issues.
    
    Args:
        input_data: Dictionary containing:
            - protocol_text: str (Protocol document text)
            - protocol_sections: dict (Optional structured sections)
            - check_types: list (Types of checks to perform)
            - version: str (Protocol version)
            - amendment_number: int (Amendment number if applicable)
    
    Returns:
        Dictionary containing:
            - inconsistencies: list of found issues
            - severity_counts: dict counting issues by severity
            - recommendations: list of recommendations
            - validation_score: float (0-100)
    """
    
    protocol_text = input_data.get('protocol_text', '')
    protocol_sections = input_data.get('protocol_sections', {})
    check_types = input_data.get('check_types', ['all'])
    version = input_data.get('version', '1.0')
    
    if not protocol_text and not protocol_sections:
        return {
            'error': 'Either protocol_text or protocol_sections must be provided',
            'input_provided': list(input_data.keys())
        }
    
    try:
        inconsistencies = []
        
        # Perform various consistency checks
        if 'all' in check_types or 'dates' in check_types:
            inconsistencies.extend(_check_date_consistency(protocol_text))
        
        if 'all' in check_types or 'numbers' in check_types:
            inconsistencies.extend(_check_numeric_consistency(protocol_text))
        
        if 'all' in check_types or 'references' in check_types:
            inconsistencies.extend(_check_reference_consistency(protocol_text))
        
        if 'all' in check_types or 'sections' in check_types:
            inconsistencies.extend(_check_section_completeness(protocol_text, protocol_sections))
        
        if 'all' in check_types or 'terminology' in check_types:
            inconsistencies.extend(_check_terminology_consistency(protocol_text))
        
        if 'all' in check_types or 'criteria' in check_types:
            inconsistencies.extend(_check_inclusion_exclusion_logic(protocol_text))
        
        # Calculate severity counts
        severity_counts = _calculate_severity_counts(inconsistencies)
        
        # Generate recommendations
        recommendations = _generate_recommendations(inconsistencies, severity_counts)
        
        # Calculate validation score
        validation_score = _calculate_validation_score(inconsistencies, len(protocol_text))
        
        return {
            'inconsistencies': inconsistencies,
            'severity_counts': severity_counts,
            'recommendations': recommendations,
            'validation_score': validation_score,
            'protocol_version': version,
            'total_issues': len(inconsistencies)
        }
        
    except Exception as e:
        return {
            'error': f'Protocol consistency check failed: {str(e)}',
            'input_data': input_data
        }


def _check_date_consistency(text: str) -> List[Dict[str, Any]]:
    """Check for date-related inconsistencies."""
    
    issues = []
    
    # Find all dates in various formats
    date_patterns = [
        r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b',
        r'\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b',
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b'
    ]
    
    dates_found = []
    for pattern in date_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            dates_found.append({
                'date_str': match.group(),
                'position': match.start()
            })
    
    # Check for inconsistent date formats
    if len(set(len(d['date_str']) for d in dates_found)) > 2:
        issues.append({
            'type': 'date_format',
            'severity': 'medium',
            'description': 'Inconsistent date formats found throughout document',
            'recommendation': 'Use consistent date format (e.g., DD-MMM-YYYY)'
        })
    
    # Check for dates in the past (for new protocols)
    current_year = datetime.now().year
    for date_info in dates_found:
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', date_info['date_str'])
        if year_match:
            year = int(year_match.group())
            if year < current_year - 5:
                issues.append({
                    'type': 'outdated_date',
                    'severity': 'high',
                    'description': f'Potentially outdated date found: {date_info["date_str"]}',
                    'location': f'Position {date_info["position"]}'
                })
    
    return issues


def _check_numeric_consistency(text: str) -> List[Dict[str, Any]]:
    """Check for numeric inconsistencies."""
    
    issues = []
    
    # Check sample size consistency
    sample_size_matches = re.findall(r'(?:sample size|n\s*=|enroll)\s*[:=]?\s*(\d+)', text, re.IGNORECASE)
    if sample_size_matches:
        unique_sizes = set(sample_size_matches)
        if len(unique_sizes) > 1:
            issues.append({
                'type': 'sample_size',
                'severity': 'high',
                'description': f'Inconsistent sample sizes found: {unique_sizes}',
                'recommendation': 'Verify and use consistent sample size throughout'
            })
    
    # Check visit numbers
    visit_patterns = re.findall(r'visit\s+(\d+)', text, re.IGNORECASE)
    if visit_patterns:
        visit_numbers = sorted(set(int(v) for v in visit_patterns))
        expected = list(range(1, len(visit_numbers) + 1))
        if visit_numbers != expected[:len(visit_numbers)]:
            issues.append({
                'type': 'visit_numbering',
                'severity': 'medium',
                'description': 'Non-sequential or missing visit numbers detected',
                'found_visits': visit_numbers
            })
    
    # Check percentage totals
    percentage_sections = re.findall(r'((?:\d+(?:\.\d+)?%[^.]*){2,})', text)
    for section in percentage_sections:
        percentages = re.findall(r'(\d+(?:\.\d+)?)%', section)
        total = sum(float(p) for p in percentages)
        if 95 <= total <= 105 and total != 100:
            issues.append({
                'type': 'percentage_total',
                'severity': 'low',
                'description': f'Percentages may not sum to 100% (found {total:.1f}%)',
                'context': section[:100]
            })
    
    return issues


def _check_reference_consistency(text: str) -> List[Dict[str, Any]]:
    """Check for reference and citation consistency."""
    
    issues = []
    
    # Find all section references
    section_refs = re.findall(r'(?:see |refer to |in )section\s+([\d.]+)', text, re.IGNORECASE)
    
    # Find all actual section numbers
    section_headers = re.findall(r'^([\d.]+)\s+[A-Z]', text, re.MULTILINE)
    
    # Check for broken references
    for ref in section_refs:
        if ref not in section_headers:
            issues.append({
                'type': 'broken_reference',
                'severity': 'medium',
                'description': f'Reference to non-existent section {ref}',
                'recommendation': 'Update section reference or add missing section'
            })
    
    # Check for undefined abbreviations
    abbreviations = re.findall(r'\b([A-Z]{2,})\b', text)
    abbrev_counts = {}
    for abbrev in abbreviations:
        if abbrev not in abbrev_counts:
            abbrev_counts[abbrev] = 0
        abbrev_counts[abbrev] += 1
    
    # Common medical abbreviations to exclude
    common_abbrevs = {'FDA', 'ICH', 'GCP', 'SAE', 'AE', 'IRB', 'EC', 'IV', 'PO', 'BID', 'QD', 'PRN'}
    
    for abbrev, count in abbrev_counts.items():
        if count > 2 and abbrev not in common_abbrevs:
            # Check if defined
            definition_pattern = f'{abbrev}\\s*\\([^)]+\\)|\\([^)]*{abbrev}[^)]*\\)'
            if not re.search(definition_pattern, text):
                issues.append({
                    'type': 'undefined_abbreviation',
                    'severity': 'low',
                    'description': f'Abbreviation "{abbrev}" used {count} times but may not be defined',
                    'recommendation': 'Define abbreviation at first use'
                })
    
    return issues


def _check_section_completeness(text: str, sections: dict) -> List[Dict[str, Any]]:
    """Check for missing required sections."""
    
    issues = []
    
    # Required sections per ICH E6
    required_sections = [
        'Background',
        'Objectives',
        'Study Design',
        'Study Population',
        'Inclusion Criteria',
        'Exclusion Criteria',
        'Study Procedures',
        'Safety',
        'Statistical',
        'Ethics',
        'Data Management'
    ]
    
    text_lower = text.lower()
    
    for section in required_sections:
        section_lower = section.lower()
        if section_lower not in text_lower:
            issues.append({
                'type': 'missing_section',
                'severity': 'high',
                'description': f'Required section "{section}" appears to be missing',
                'recommendation': f'Add {section} section per ICH E6 guidelines'
            })
    
    return issues


def _check_terminology_consistency(text: str) -> List[Dict[str, Any]]:
    """Check for inconsistent terminology."""
    
    issues = []
    
    # Common terminology variations
    term_variations = [
        ('subject', 'patient', 'participant'),
        ('investigational product', 'study drug', 'test article'),
        ('adverse event', 'side effect', 'adverse reaction'),
        ('washout', 'wash-out', 'wash out'),
        ('follow-up', 'followup', 'follow up')
    ]
    
    for term_group in term_variations:
        counts = {}
        for term in term_group:
            counts[term] = len(re.findall(r'\b' + term + r'\b', text, re.IGNORECASE))
        
        # If multiple variations are used
        used_terms = [term for term, count in counts.items() if count > 0]
        if len(used_terms) > 1:
            issues.append({
                'type': 'inconsistent_terminology',
                'severity': 'low',
                'description': f'Inconsistent use of terms: {used_terms}',
                'counts': counts,
                'recommendation': f'Use consistent terminology, preferably "{max(counts, key=counts.get)}"'
            })
    
    return issues


def _check_inclusion_exclusion_logic(text: str) -> List[Dict[str, Any]]:
    """Check inclusion/exclusion criteria for logical issues."""
    
    issues = []
    
    # Extract inclusion and exclusion sections
    inclusion_match = re.search(r'inclusion criteria(.*?)(?:exclusion|$)', text, re.IGNORECASE | re.DOTALL)
    exclusion_match = re.search(r'exclusion criteria(.*?)(?:study procedures|$)', text, re.IGNORECASE | re.DOTALL)
    
    if inclusion_match and exclusion_match:
        inclusion_text = inclusion_match.group(1)
        exclusion_text = exclusion_match.group(1)
        
        # Check for age conflicts
        inc_ages = re.findall(r'(\d+)\s*(?:to|-)\s*(\d+)\s*years', inclusion_text, re.IGNORECASE)
        exc_ages = re.findall(r'(\d+)\s*(?:to|-)\s*(\d+)\s*years', exclusion_text, re.IGNORECASE)
        
        if inc_ages and exc_ages:
            # Check for overlapping age ranges
            for inc_min, inc_max in inc_ages:
                for exc_min, exc_max in exc_ages:
                    if int(inc_min) <= int(exc_max) and int(exc_min) <= int(inc_max):
                        issues.append({
                            'type': 'criteria_conflict',
                            'severity': 'high',
                            'description': 'Potential age range conflict between inclusion and exclusion criteria',
                            'recommendation': 'Review and clarify age requirements'
                        })
        
        # Check for contradictory conditions
        conditions = ['pregnancy', 'diabetes', 'hypertension', 'cancer']
        for condition in conditions:
            if condition in inclusion_text.lower() and condition in exclusion_text.lower():
                issues.append({
                    'type': 'criteria_contradiction',
                    'severity': 'high',
                    'description': f'Condition "{condition}" appears in both inclusion and exclusion criteria',
                    'recommendation': 'Clarify criteria to avoid contradiction'
                })
    
    return issues


def _calculate_severity_counts(inconsistencies: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate counts by severity level."""
    
    counts = {'high': 0, 'medium': 0, 'low': 0}
    
    for issue in inconsistencies:
        severity = issue.get('severity', 'low')
        counts[severity] += 1
    
    return counts


def _generate_recommendations(inconsistencies: List[Dict[str, Any]], severity_counts: Dict[str, int]) -> List[str]:
    """Generate recommendations based on found issues."""
    
    recommendations = []
    
    if severity_counts['high'] > 0:
        recommendations.append(
            f"Address {severity_counts['high']} high-severity issues before protocol finalization"
        )
    
    if severity_counts['medium'] > 3:
        recommendations.append(
            "Consider systematic review of document structure and references"
        )
    
    # Type-specific recommendations
    issue_types = set(issue['type'] for issue in inconsistencies)
    
    if 'date_format' in issue_types:
        recommendations.append(
            "Standardize date format throughout document (recommend DD-MMM-YYYY)"
        )
    
    if 'sample_size' in issue_types:
        recommendations.append(
            "Reconcile sample size discrepancies with statistician"
        )
    
    if 'missing_section' in issue_types:
        recommendations.append(
            "Add missing required sections per ICH E6 guidelines"
        )
    
    if 'undefined_abbreviation' in issue_types:
        recommendations.append(
            "Create abbreviations list and define all at first use"
        )
    
    if not recommendations:
        recommendations.append(
            "Protocol shows good consistency. Perform final review before approval."
        )
    
    return recommendations


def _calculate_validation_score(inconsistencies: List[Dict[str, Any]], text_length: int) -> float:
    """Calculate overall validation score."""
    
    if text_length == 0:
        return 0.0
    
    # Weight by severity
    severity_weights = {'high': 10, 'medium': 5, 'low': 2}
    
    total_penalty = 0
    for issue in inconsistencies:
        severity = issue.get('severity', 'low')
        total_penalty += severity_weights[severity]
    
    # Normalize based on document length
    normalized_penalty = (total_penalty * 1000) / text_length
    
    # Convert to score (0-100)
    score = max(0, 100 - normalized_penalty)
    
    return round(score, 1)