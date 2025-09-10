"""
Inclusion/Exclusion Logic Validator

Tests inclusion and exclusion criteria for logical consistency.
"""

import re
from typing import Dict, Any, List, Tuple


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate inclusion/exclusion criteria logic for consistency and conflicts.
    
    Example:
        Input: Lists of inclusion and exclusion criteria with optional patient test cases
        Output: Validation results showing conflicts, overlaps, gaps, and eligibility testing outcomes
    
    Parameters:
        inclusion_criteria : list
            List of inclusion criteria strings
        exclusion_criteria : list
            List of exclusion criteria strings
        test_cases : list, optional
            Patient profiles to test against the criteria
    """
    
    inclusion = input_data.get('inclusion_criteria', [])
    exclusion = input_data.get('exclusion_criteria', [])
    test_cases = input_data.get('test_cases', [])
    
    conflicts = _check_conflicts(inclusion, exclusion)
    overlaps = _check_overlaps(inclusion, exclusion)
    gaps = _check_gaps(inclusion, exclusion)
    test_results = _test_patient_cases(test_cases, inclusion, exclusion) if test_cases else []
    
    return {
        'conflicts': conflicts,
        'overlaps': overlaps,
        'gaps': gaps,
        'test_results': test_results,
        'is_valid': len(conflicts) == 0,
        'total_issues': len(conflicts) + len(overlaps) + len(gaps)
    }


def _check_conflicts(inclusion: List[str], exclusion: List[str]) -> List[Dict]:
    """Check for direct conflicts between criteria."""
    conflicts = []
    
    for inc in inclusion:
        for exc in exclusion:
            if _are_conflicting(inc, exc):
                conflicts.append({
                    'inclusion': inc,
                    'exclusion': exc,
                    'type': 'direct_conflict'
                })
    
    return conflicts


def _check_overlaps(inclusion: List[str], exclusion: List[str]) -> List[Dict]:
    """Check for overlapping criteria."""
    overlaps = []
    
    # Check age overlaps
    inc_ages = _extract_age_ranges(inclusion)
    exc_ages = _extract_age_ranges(exclusion)
    
    for inc_range in inc_ages:
        for exc_range in exc_ages:
            if _ranges_overlap(inc_range, exc_range):
                overlaps.append({
                    'type': 'age_overlap',
                    'inclusion_range': inc_range,
                    'exclusion_range': exc_range
                })
    
    return overlaps


def _check_gaps(inclusion: List[str], exclusion: List[str]) -> List[Dict]:
    """Check for gaps in criteria coverage."""
    gaps = []
    
    # Check for missing gender specification
    all_criteria = inclusion + exclusion
    has_gender = any('male' in c.lower() or 'female' in c.lower() for c in all_criteria)
    if not has_gender:
        gaps.append({
            'type': 'missing_gender_specification',
            'recommendation': 'Consider specifying gender requirements'
        })
    
    return gaps


def _test_patient_cases(test_cases: List[Dict], inclusion: List[str], exclusion: List[str]) -> List[Dict]:
    """Test specific patient profiles against criteria."""
    results = []
    
    for case in test_cases:
        eligible = _check_eligibility(case, inclusion, exclusion)
        results.append({
            'case': case,
            'eligible': eligible,
            'reason': 'Meets all criteria' if eligible else 'Failed criteria check'
        })
    
    return results


def _are_conflicting(inc: str, exc: str) -> bool:
    """Check if two criteria are conflicting."""
    inc_lower = inc.lower()
    exc_lower = exc.lower()
    
    # Check for same condition in both
    conditions = ['pregnancy', 'diabetes', 'hypertension', 'cancer', 'hiv']
    for condition in conditions:
        if condition in inc_lower and condition in exc_lower:
            return True
    
    return False


def _extract_age_ranges(criteria: List[str]) -> List[Tuple[int, int]]:
    """Extract age ranges from criteria."""
    ranges = []
    
    for criterion in criteria:
        # Match patterns like "18 to 65 years" or "18-65"
        matches = re.findall(r'(\d+)\s*(?:to|-)\s*(\d+)', criterion)
        for match in matches:
            ranges.append((int(match[0]), int(match[1])))
    
    return ranges


def _ranges_overlap(range1: Tuple[int, int], range2: Tuple[int, int]) -> bool:
    """Check if two ranges overlap."""
    return range1[0] <= range2[1] and range2[0] <= range1[1]


def _check_eligibility(patient: Dict, inclusion: List[str], exclusion: List[str]) -> bool:
    """Check if patient meets criteria."""
    # Simplified eligibility check
    age = patient.get('age')
    if age:
        # Check age against inclusion criteria
        inc_ages = _extract_age_ranges(inclusion)
        if inc_ages:
            age_eligible = any(r[0] <= age <= r[1] for r in inc_ages)
            if not age_eligible:
                return False
        
        # Check age against exclusion criteria
        exc_ages = _extract_age_ranges(exclusion)
        if exc_ages:
            age_excluded = any(r[0] <= age <= r[1] for r in exc_ages)
            if age_excluded:
                return False
    
    return True
