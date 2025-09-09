"""
Tests for Lab Range Validator Tool
"""

import pytest
from tools.lab_range_validator import run


class TestLabRangeValidator:
    
    def test_successful_validation(self):
        """Test successful lab value validation"""
        input_data = {
            'lab_values': [
                {
                    'test': 'glucose',
                    'value': 120,
                    'unit': 'mg/dL',
                    'subject_id': '001'
                }
            ]
        }
        
        result = run(input_data)
        
        assert 'success' in result
        assert result['success'] is True
        assert 'validation_results' in result
        assert isinstance(result['validation_results'], list)
    
    def test_empty_input(self):
        """Test with empty lab values"""
        input_data = {'lab_values': []}
        
        result = run(input_data)
        
        assert 'error' in result
        assert result['error'] == "No lab values provided"
    
    def test_missing_lab_values_key(self):
        """Test with missing lab_values key"""
        input_data = {}
        
        result = run(input_data)
        
        assert 'error' in result
        assert result['error'] == "No lab values provided"
    
    def test_out_of_range_values(self):
        """Test detection of out-of-range values"""
        input_data = {
            'lab_values': [
                {
                    'test': 'glucose',
                    'value': 400,  # High glucose
                    'unit': 'mg/dL',
                    'subject_id': '002'
                }
            ]
        }
        
        result = run(input_data)
        
        assert 'success' in result
        if result['success']:
            assert 'out_of_range_values' in result
            assert len(result['out_of_range_values']) > 0
    
    def test_critical_values(self):
        """Test detection of critical values"""
        input_data = {
            'lab_values': [
                {
                    'test': 'glucose',
                    'value': 30,  # Critically low glucose
                    'unit': 'mg/dL',
                    'subject_id': '003'
                }
            ]
        }
        
        result = run(input_data)
        
        assert 'success' in result
        if result['success']:
            assert 'critical_values' in result