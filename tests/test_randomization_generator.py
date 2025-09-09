"""
Tests for Randomization List Generator Tool
"""

import pytest
from tools.randomization_generator import run


class TestRandomizationGenerator:
    """Test cases for randomization generator."""
    
    def test_simple_randomization(self):
        """Test simple randomization method."""
        input_data = {
            'method': 'simple',
            'n_subjects': 100,
            'treatment_arms': ['Control', 'Treatment'],
            'allocation_ratio': [1, 1],
            'seed': 42
        }
        
        result = run(input_data)
        
        assert 'randomization_list' in result
        assert len(result['randomization_list']) == 100
        assert 'summary' in result
        assert 'validation' in result
        assert result['validation']['is_valid']
    
    def test_block_randomization(self):
        """Test block randomization method."""
        input_data = {
            'method': 'block',
            'n_subjects': 80,
            'treatment_arms': ['Placebo', 'Drug A', 'Drug B'],
            'allocation_ratio': [1, 1, 1],
            'block_size': 6,
            'seed': 123
        }
        
        result = run(input_data)
        
        assert len(result['randomization_list']) == 80
        # Check block structure
        first_subject = result['randomization_list'][0]
        assert 'block_number' in first_subject
        assert 'position_in_block' in first_subject
    
    def test_variable_block_sizes(self):
        """Test block randomization with variable block sizes."""
        input_data = {
            'method': 'block',
            'n_subjects': 50,
            'treatment_arms': ['Control', 'Treatment'],
            'allocation_ratio': [1, 1],
            'block_size': [2, 4, 6],
            'seed': 456
        }
        
        result = run(input_data)
        
        assert len(result['randomization_list']) == 50
        assert result['validation']['is_valid']
    
    def test_stratified_randomization(self):
        """Test stratified randomization method."""
        input_data = {
            'method': 'stratified',
            'n_subjects': 120,
            'treatment_arms': ['Control', 'Treatment'],
            'allocation_ratio': [1, 1],
            'strata': {
                'Age Group': ['<50', '>=50'],
                'Risk': ['Low', 'High']
            },
            'seed': 789
        }
        
        result = run(input_data)
        
        assert len(result['randomization_list']) == 120
        # Check stratum assignment
        first_subject = result['randomization_list'][0]
        assert 'stratum' in first_subject
        assert 'Age Group' in first_subject['stratum']
        assert 'Risk' in first_subject['stratum']
    
    def test_adaptive_randomization(self):
        """Test adaptive randomization method."""
        input_data = {
            'method': 'adaptive',
            'n_subjects': 100,
            'treatment_arms': ['Control', 'Treatment'],
            'burn_in_size': 20,
            'adaptation_factor': 0.5,
            'seed': 999
        }
        
        result = run(input_data)
        
        assert len(result['randomization_list']) == 100
        # Check adaptive features after burn-in
        later_subject = result['randomization_list'][25]
        assert 'adaptive_probability' in later_subject
    
    def test_unequal_allocation(self):
        """Test unequal allocation ratio."""
        input_data = {
            'method': 'block',
            'n_subjects': 90,
            'treatment_arms': ['Control', 'Treatment'],
            'allocation_ratio': [1, 2],  # 1:2 ratio
            'block_size': 6,
            'seed': 111
        }
        
        result = run(input_data)
        
        summary = result['summary']
        control_count = summary['arms']['Control']['count']
        treatment_count = summary['arms']['Treatment']['count']
        
        # Check ratio is approximately 1:2
        ratio = treatment_count / control_count if control_count > 0 else 0
        assert 1.5 < ratio < 2.5
    
    def test_site_assignment(self):
        """Test assignment of subjects to sites."""
        input_data = {
            'method': 'simple',
            'n_subjects': 100,
            'treatment_arms': ['Control', 'Treatment'],
            'allocation_ratio': [1, 1],
            'site_ids': ['Site01', 'Site02', 'Site03', 'Site04'],
            'seed': 222
        }
        
        result = run(input_data)
        
        # Check site assignments
        first_subject = result['randomization_list'][0]
        assert 'site_id' in first_subject
        
        # Check site distribution in summary
        assert 'sites' in result['summary']
        assert len(result['summary']['sites']) == 4
    
    def test_randomization_codes(self):
        """Test that unique randomization codes are generated."""
        input_data = {
            'method': 'simple',
            'n_subjects': 50,
            'treatment_arms': ['Control', 'Treatment'],
            'allocation_ratio': [1, 1],
            'seed': 333
        }
        
        result = run(input_data)
        
        # Check all subjects have codes
        codes = [s['randomization_code'] for s in result['randomization_list']]
        assert len(codes) == 50
        assert all(code.startswith('RND-') for code in codes)
        # Codes should be unique
        assert len(set(codes)) == len(codes)
    
    def test_validation_checks(self):
        """Test validation of randomization list."""
        input_data = {
            'method': 'block',
            'n_subjects': 100,
            'treatment_arms': ['A', 'B', 'C'],
            'allocation_ratio': [1, 1, 1],
            'block_size': 6,
            'seed': 444
        }
        
        result = run(input_data)
        
        validation = result['validation']
        assert validation['is_valid']
        assert validation['checks']['unique_ids']
        assert validation['checks']['allocation_ratio']
        assert validation['checks']['all_arms_used']
    
    def test_reproducibility_with_seed(self):
        """Test that same seed produces same randomization."""
        input_data = {
            'method': 'simple',
            'n_subjects': 30,
            'treatment_arms': ['Control', 'Treatment'],
            'allocation_ratio': [1, 1],
            'seed': 555
        }
        
        result1 = run(input_data)
        result2 = run(input_data)
        
        # Same seed should produce same assignments
        assignments1 = [s['treatment_assignment'] for s in result1['randomization_list']]
        assignments2 = [s['treatment_assignment'] for s in result2['randomization_list']]
        assert assignments1 == assignments2
    
    def test_export_ready_flag(self):
        """Test export ready flag based on validation."""
        input_data = {
            'method': 'block',
            'n_subjects': 60,
            'treatment_arms': ['Control', 'Treatment'],
            'allocation_ratio': [1, 1],
            'block_size': 4,
            'seed': 666
        }
        
        result = run(input_data)
        
        assert 'export_ready' in result
        assert result['export_ready'] == result['validation']['is_valid']
    
    def test_invalid_method(self):
        """Test error handling for invalid method."""
        input_data = {
            'method': 'invalid_method',
            'n_subjects': 50,
            'treatment_arms': ['Control', 'Treatment']
        }
        
        result = run(input_data)
        
        assert 'error' in result
        assert 'supported_methods' in result