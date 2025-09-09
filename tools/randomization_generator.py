"""
Randomization List Generator for Clinical Trials

Creates randomization schemes including:
- Simple randomization
- Block randomization
- Stratified randomization
- Adaptive randomization
"""

import random
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate randomization list for clinical trial.
    
    Args:
        input_data: Dictionary containing:
            - method: str ('simple', 'block', 'stratified', 'adaptive')
            - n_subjects: int (Total number of subjects)
            - treatment_arms: list (Names of treatment arms)
            - allocation_ratio: list (Ratio for each arm, e.g., [1, 1] for 1:1)
            - seed: int (Random seed for reproducibility, optional)
            - block_size: int or list (For block randomization)
            - strata: dict (For stratified randomization)
            - site_ids: list (Site identifiers, optional)
    
    Returns:
        Dictionary containing:
            - randomization_list: list of dicts
            - summary: dict with statistics
            - validation: dict with checks
            - export_ready: bool
    """
    
    method = input_data.get('method', 'block')
    n_subjects = input_data.get('n_subjects', 100)
    treatment_arms = input_data.get('treatment_arms', ['Control', 'Treatment'])
    allocation_ratio = input_data.get('allocation_ratio', [1] * len(treatment_arms))
    seed = input_data.get('seed')
    
    if seed:
        random.seed(seed)
    
    try:
        if method == 'simple':
            randomization_list = _generate_simple_randomization(
                n_subjects, treatment_arms, allocation_ratio
            )
        elif method == 'block':
            block_size = input_data.get('block_size', 4)
            randomization_list = _generate_block_randomization(
                n_subjects, treatment_arms, allocation_ratio, block_size
            )
        elif method == 'stratified':
            strata = input_data.get('strata', {})
            randomization_list = _generate_stratified_randomization(
                n_subjects, treatment_arms, allocation_ratio, strata
            )
        elif method == 'adaptive':
            randomization_list = _generate_adaptive_randomization(
                n_subjects, treatment_arms, input_data
            )
        else:
            return {
                'error': f'Unsupported randomization method: {method}',
                'supported_methods': ['simple', 'block', 'stratified', 'adaptive']
            }
        
        # Add site assignments if provided
        site_ids = input_data.get('site_ids', [])
        if site_ids:
            randomization_list = _assign_sites(randomization_list, site_ids)
        
        # Generate summary statistics
        summary = _generate_summary(randomization_list, treatment_arms)
        
        # Validate randomization
        validation = _validate_randomization(randomization_list, allocation_ratio, treatment_arms)
        
        return {
            'randomization_list': randomization_list,
            'summary': summary,
            'validation': validation,
            'export_ready': validation['is_valid'],
            'seed_used': seed if seed else 'No seed (non-reproducible)'
        }
        
    except Exception as e:
        return {
            'error': f'Randomization generation failed: {str(e)}',
            'input_data': input_data
        }


def _generate_simple_randomization(
    n_subjects: int,
    treatment_arms: list,
    allocation_ratio: list
) -> List[Dict[str, Any]]:
    """Generate simple randomization list."""
    
    # Create pool of assignments based on ratio
    assignment_pool = []
    for arm, ratio in zip(treatment_arms, allocation_ratio):
        assignment_pool.extend([arm] * ratio)
    
    randomization_list = []
    for i in range(n_subjects):
        assignment = random.choice(assignment_pool)
        randomization_list.append({
            'subject_id': f'SUBJ-{i+1:04d}',
            'randomization_number': i + 1,
            'treatment_assignment': assignment,
            'randomization_date': None,
            'randomization_code': _generate_code(i+1, assignment)
        })
    
    return randomization_list


def _generate_block_randomization(
    n_subjects: int,
    treatment_arms: list,
    allocation_ratio: list,
    block_size: Any
) -> List[Dict[str, Any]]:
    """Generate block randomization list."""
    
    # Handle variable block sizes
    if isinstance(block_size, list):
        block_sizes = block_size
    else:
        block_sizes = [block_size]
    
    # Create blocks
    randomization_list = []
    subject_count = 0
    
    while subject_count < n_subjects:
        # Select block size
        current_block_size = random.choice(block_sizes)
        
        # Create block with proper ratio
        block = []
        for arm, ratio in zip(treatment_arms, allocation_ratio):
            count = (current_block_size * ratio) // sum(allocation_ratio)
            block.extend([arm] * count)
        
        # Shuffle block
        random.shuffle(block)
        
        # Add to randomization list
        for assignment in block:
            if subject_count >= n_subjects:
                break
            subject_count += 1
            randomization_list.append({
                'subject_id': f'SUBJ-{subject_count:04d}',
                'randomization_number': subject_count,
                'treatment_assignment': assignment,
                'block_number': (subject_count - 1) // current_block_size + 1,
                'position_in_block': (subject_count - 1) % current_block_size + 1,
                'randomization_date': None,
                'randomization_code': _generate_code(subject_count, assignment)
            })
    
    return randomization_list[:n_subjects]


def _generate_stratified_randomization(
    n_subjects: int,
    treatment_arms: list,
    allocation_ratio: list,
    strata: dict
) -> List[Dict[str, Any]]:
    """Generate stratified randomization list."""
    
    if not strata:
        # Default strata if none provided
        strata = {
            'Age Group': ['18-40', '41-60', '61+'],
            'Sex': ['Male', 'Female']
        }
    
    # Generate all stratum combinations
    stratum_combinations = _get_stratum_combinations(strata)
    
    # Allocate subjects to strata
    subjects_per_stratum = n_subjects // len(stratum_combinations)
    remainder = n_subjects % len(stratum_combinations)
    
    randomization_list = []
    subject_count = 0
    
    for idx, stratum_combo in enumerate(stratum_combinations):
        # Determine number of subjects for this stratum
        n_in_stratum = subjects_per_stratum + (1 if idx < remainder else 0)
        
        # Generate block randomization within stratum
        stratum_list = _generate_block_randomization(
            n_in_stratum, treatment_arms, allocation_ratio, 4
        )
        
        # Add stratum information
        for subj in stratum_list:
            subject_count += 1
            subj['subject_id'] = f'SUBJ-{subject_count:04d}'
            subj['randomization_number'] = subject_count
            subj['stratum'] = stratum_combo
            
        randomization_list.extend(stratum_list)
    
    return randomization_list[:n_subjects]


def _generate_adaptive_randomization(
    n_subjects: int,
    treatment_arms: list,
    input_data: dict
) -> List[Dict[str, Any]]:
    """Generate adaptive randomization using response-adaptive method."""
    
    # Initial equal allocation for burn-in period
    burn_in = input_data.get('burn_in_size', 20)
    adaptation_factor = input_data.get('adaptation_factor', 0.5)
    
    randomization_list = []
    arm_counts = {arm: 0 for arm in treatment_arms}
    arm_successes = {arm: 0 for arm in treatment_arms}
    
    for i in range(n_subjects):
        if i < burn_in:
            # Equal allocation during burn-in
            assignment = treatment_arms[i % len(treatment_arms)]
        else:
            # Adaptive allocation based on simulated success rates
            probabilities = _calculate_adaptive_probabilities(
                arm_counts, arm_successes, adaptation_factor
            )
            assignment = random.choices(treatment_arms, weights=probabilities)[0]
        
        arm_counts[assignment] += 1
        
        # Simulate response (for demonstration)
        if random.random() < 0.3 + (0.2 if assignment == 'Treatment' else 0):
            arm_successes[assignment] += 1
        
        randomization_list.append({
            'subject_id': f'SUBJ-{i+1:04d}',
            'randomization_number': i + 1,
            'treatment_assignment': assignment,
            'adaptive_probability': probabilities if i >= burn_in else None,
            'randomization_date': None,
            'randomization_code': _generate_code(i+1, assignment)
        })
    
    return randomization_list


def _get_stratum_combinations(strata: dict) -> list:
    """Get all combinations of strata."""
    import itertools
    
    keys = list(strata.keys())
    values = list(strata.values())
    
    combinations = []
    for combo in itertools.product(*values):
        stratum_dict = dict(zip(keys, combo))
        combinations.append(stratum_dict)
    
    return combinations


def _calculate_adaptive_probabilities(
    arm_counts: dict,
    arm_successes: dict,
    adaptation_factor: float
) -> list:
    """Calculate adaptive randomization probabilities."""
    
    # Calculate success rates with Bayesian smoothing
    success_rates = {}
    for arm in arm_counts:
        if arm_counts[arm] > 0:
            # Add 1 to successes and 2 to counts (Beta(1,1) prior)
            success_rates[arm] = (arm_successes[arm] + 1) / (arm_counts[arm] + 2)
        else:
            success_rates[arm] = 0.5
    
    # Calculate probabilities with adaptation factor
    arms = list(arm_counts.keys())
    raw_probs = [success_rates[arm] ** adaptation_factor for arm in arms]
    total = sum(raw_probs)
    
    if total > 0:
        probabilities = [p / total for p in raw_probs]
    else:
        probabilities = [1 / len(arms)] * len(arms)
    
    return probabilities


def _assign_sites(randomization_list: list, site_ids: list) -> list:
    """Assign subjects to sites."""
    
    subjects_per_site = len(randomization_list) // len(site_ids)
    remainder = len(randomization_list) % len(site_ids)
    
    site_index = 0
    site_count = 0
    
    for i, subject in enumerate(randomization_list):
        subject['site_id'] = site_ids[site_index]
        site_count += 1
        
        # Move to next site when quota is reached
        site_quota = subjects_per_site + (1 if site_index < remainder else 0)
        if site_count >= site_quota:
            site_index += 1
            site_count = 0
    
    return randomization_list


def _generate_code(subject_number: int, assignment: str) -> str:
    """Generate unique randomization code."""
    
    # Create unique string
    unique_str = f"{subject_number}-{assignment}-{datetime.now().isoformat()}"
    
    # Generate hash
    hash_obj = hashlib.sha256(unique_str.encode())
    code = hash_obj.hexdigest()[:8].upper()
    
    return f"RND-{code}"


def _generate_summary(randomization_list: list, treatment_arms: list) -> dict:
    """Generate summary statistics."""
    
    summary = {
        'total_subjects': len(randomization_list),
        'arms': {}
    }
    
    for arm in treatment_arms:
        arm_subjects = [s for s in randomization_list if s['treatment_assignment'] == arm]
        summary['arms'][arm] = {
            'count': len(arm_subjects),
            'percentage': (len(arm_subjects) / len(randomization_list) * 100) if randomization_list else 0
        }
    
    # Add site distribution if present
    if randomization_list and 'site_id' in randomization_list[0]:
        sites = set(s.get('site_id') for s in randomization_list)
        summary['sites'] = {}
        for site in sites:
            site_subjects = [s for s in randomization_list if s.get('site_id') == site]
            summary['sites'][site] = len(site_subjects)
    
    # Add stratum distribution if present
    if randomization_list and 'stratum' in randomization_list[0]:
        summary['strata'] = {}
        strata_seen = set()
        for subject in randomization_list:
            if 'stratum' in subject:
                stratum_str = str(subject['stratum'])
                if stratum_str not in strata_seen:
                    strata_seen.add(stratum_str)
                    stratum_subjects = [s for s in randomization_list 
                                      if str(s.get('stratum')) == stratum_str]
                    summary['strata'][stratum_str] = len(stratum_subjects)
    
    return summary


def _validate_randomization(
    randomization_list: list,
    allocation_ratio: list,
    treatment_arms: list
) -> dict:
    """Validate randomization list."""
    
    validation = {
        'is_valid': True,
        'checks': {}
    }
    
    # Check unique IDs
    subject_ids = [s['subject_id'] for s in randomization_list]
    validation['checks']['unique_ids'] = len(subject_ids) == len(set(subject_ids))
    
    # Check allocation ratio (with tolerance)
    expected_ratio = [r / sum(allocation_ratio) for r in allocation_ratio]
    actual_counts = {arm: 0 for arm in treatment_arms}
    
    for subject in randomization_list:
        actual_counts[subject['treatment_assignment']] += 1
    
    actual_ratio = [actual_counts[arm] / len(randomization_list) for arm in treatment_arms]
    
    ratio_check = all(
        abs(expected - actual) < 0.1  # 10% tolerance
        for expected, actual in zip(expected_ratio, actual_ratio)
    )
    validation['checks']['allocation_ratio'] = ratio_check
    
    # Check for proper distribution
    validation['checks']['all_arms_used'] = all(
        actual_counts[arm] > 0 for arm in treatment_arms
    )
    
    # Overall validation
    validation['is_valid'] = all(validation['checks'].values())
    
    if not validation['is_valid']:
        validation['message'] = 'Randomization validation failed. Review checks.'
    else:
        validation['message'] = 'Randomization list validated successfully.'
    
    return validation