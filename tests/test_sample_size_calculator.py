"""
Tests for Sample Size Calculator Tool
"""

import pytest
import math
from tools.sample_size_calculator import run


class TestSampleSizeCalculator:
    """Test cases for sample size calculator."""
    
    def test_continuous_superiority(self):
        """Test sample size calculation for continuous superiority trial."""
        input_data = {
            'design_type': 'superiority',
            'outcome_type': 'continuous',
            'mean_difference': 5.0,
            'std_dev': 10.0,
            'alpha': 0.05,
            'power': 0.8,
            'allocation_ratio': 1,
            'dropout_rate': 0.1
        }
        
        result = run(input_data)
        
        assert 'sample_size_per_arm' in result
        assert 'total_sample_size' in result
        assert result['total_sample_size'] > 0
        assert result['sample_size_per_arm']['control'] > 0
        assert result['sample_size_per_arm']['treatment'] > 0
        # With effect size of 0.5, expect around 64 per arm (unadjusted)
        assert 140 <= result['total_sample_size'] < 180
    
    def test_binary_superiority(self):
        """Test sample size calculation for binary superiority trial."""
        input_data = {
            'design_type': 'superiority',
            'outcome_type': 'binary',
            'control_rate': 0.2,
            'treatment_rate': 0.35,
            'alpha': 0.05,
            'power': 0.8,
            'allocation_ratio': 1,
            'dropout_rate': 0.15
        }
        
        result = run(input_data)
        
        assert 'sample_size_per_arm' in result
        assert 'total_sample_size' in result
        assert result['total_sample_size'] > 0
        # Binary outcome with 15% difference should need moderate sample
        assert 200 < result['total_sample_size'] < 350
    
    def test_non_inferiority_continuous(self):
        """Test sample size for non-inferiority trial with continuous outcome."""
        input_data = {
            'design_type': 'non_inferiority',
            'outcome_type': 'continuous',
            'mean_difference': 0,
            'std_dev': 15.0,
            'margin': 3.0,
            'alpha': 0.025,  # One-sided
            'power': 0.8,
            'allocation_ratio': 1,
            'dropout_rate': 0.1
        }
        
        result = run(input_data)
        
        assert 'sample_size_per_arm' in result
        assert result['calculation_details']['design_type'] == 'non_inferiority'
        assert result['total_sample_size'] > 0
    
    def test_time_to_event_outcome(self):
        """Test sample size for survival analysis."""
        input_data = {
            'design_type': 'superiority',
            'outcome_type': 'time_to_event',
            'hazard_ratio': 0.7,
            'median_survival_control': 12,
            'accrual_time': 24,
            'follow_up_time': 12,
            'alpha': 0.05,
            'power': 0.8,
            'allocation_ratio': 1,
            'dropout_rate': 0.2
        }
        
        result = run(input_data)
        
        assert 'sample_size_per_arm' in result
        assert 'total_sample_size' in result
        assert result['total_sample_size'] > 0
        assert result['calculation_details']['outcome_type'] == 'time_to_event'
    
    def test_unequal_allocation(self):
        """Test sample size with unequal allocation ratio."""
        input_data = {
            'design_type': 'superiority',
            'outcome_type': 'continuous',
            'mean_difference': 10.0,
            'std_dev': 15.0,
            'alpha': 0.05,
            'power': 0.9,
            'allocation_ratio': 2,  # 2:1 treatment:control
            'dropout_rate': 0.05
        }
        
        result = run(input_data)
        
        assert 'sample_size_per_arm' in result
        treatment_n = result['sample_size_per_arm']['treatment']
        control_n = result['sample_size_per_arm']['control']
        # Check 2:1 ratio is approximately maintained
        ratio = treatment_n / control_n
        assert 1.8 < ratio < 2.2
    
    def test_high_power(self):
        """Test sample size with high statistical power."""
        input_data = {
            'design_type': 'superiority',
            'outcome_type': 'continuous',
            'mean_difference': 3.0,
            'std_dev': 10.0,
            'alpha': 0.05,
            'power': 0.95,  # High power
            'allocation_ratio': 1,
            'dropout_rate': 0.1
        }
        
        result = run(input_data)
        
        assert result['total_sample_size'] > 0
        assert 'High statistical power' in ' '.join(result['recommendations'])
    
    def test_dropout_adjustment(self):
        """Test that dropout rate properly inflates sample size."""
        # Without dropout
        input_no_dropout = {
            'design_type': 'superiority',
            'outcome_type': 'continuous',
            'mean_difference': 5.0,
            'std_dev': 10.0,
            'alpha': 0.05,
            'power': 0.8,
            'allocation_ratio': 1,
            'dropout_rate': 0
        }
        
        # With 20% dropout
        input_with_dropout = input_no_dropout.copy()
        input_with_dropout['dropout_rate'] = 0.2
        
        result_no_dropout = run(input_no_dropout)
        result_with_dropout = run(input_with_dropout)
        
        # Sample size should be inflated by 1/(1-0.2) = 1.25
        ratio = result_with_dropout['total_sample_size'] / result_no_dropout['total_sample_size']
        assert 1.2 < ratio < 1.3
    
    def test_recommendations_large_sample(self):
        """Test recommendations for large sample size."""
        input_data = {
            'design_type': 'superiority',
            'outcome_type': 'binary',
            'control_rate': 0.5,
            'treatment_rate': 0.55,  # Small difference requires large sample
            'alpha': 0.05,
            'power': 0.8,
            'allocation_ratio': 1,
            'dropout_rate': 0.1
        }
        
        result = run(input_data)
        
        assert 'recommendations' in result
        assert len(result['recommendations']) > 0
        # Should recommend multi-site or feasibility consideration
        recommendations_text = ' '.join(result['recommendations'])
        assert 'Large sample' in recommendations_text or 'Multi-site' in recommendations_text
    
    def test_missing_required_parameters(self):
        """Test error handling for missing parameters."""
        input_data = {
            'design_type': 'superiority',
            'outcome_type': 'continuous',
            # Missing mean_difference and std_dev
            'alpha': 0.05,
            'power': 0.8
        }
        
        result = run(input_data)
        
        assert 'error' in result
        assert 'mean_difference' in result['error'] or 'std_dev' in result['error']
    
    def test_invalid_outcome_type(self):
        """Test error handling for invalid outcome type."""
        input_data = {
            'design_type': 'superiority',
            'outcome_type': 'invalid_type',
            'alpha': 0.05,
            'power': 0.8
        }
        
        result = run(input_data)
        
        assert 'error' in result
        assert 'supported_types' in result
        assert 'continuous' in result['supported_types']
    
    def test_interim_analysis_recommendation(self):
        """Test that interim analysis is recommended for larger studies."""
        input_data = {
            'design_type': 'superiority',
            'outcome_type': 'continuous',
            'mean_difference': 5.0,
            'std_dev': 15.0,
            'alpha': 0.05,
            'power': 0.8,
            'allocation_ratio': 1,
            'dropout_rate': 0.1
        }
        
        result = run(input_data)
        
        if result['total_sample_size'] > 200:
            recommendations_text = ' '.join(result['recommendations'])
            assert 'interim analysis' in recommendations_text.lower()
    
    def test_non_inferiority_recommendation(self):
        """Test specific recommendation for non-inferiority design."""
        input_data = {
            'design_type': 'non_inferiority',
            'outcome_type': 'binary',
            'control_rate': 0.8,
            'treatment_rate': 0.75,
            'margin': 0.1,
            'alpha': 0.025,
            'power': 0.8,
            'allocation_ratio': 1,
            'dropout_rate': 0.1
        }
        
        result = run(input_data)
        
        recommendations_text = ' '.join(result['recommendations'])
        assert 'non-inferiority' in recommendations_text.lower()
        assert 'margin' in recommendations_text.lower()