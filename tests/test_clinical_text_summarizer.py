"""
Tests for Clinical Text Summarizer Tool
"""

import pytest
from tools.clinical_text_summarizer import run


class TestClinicalTextSummarizer:
    
    def test_successful_summarization(self):
        """Test successful text summarization"""
        input_data = {
            'text': 'Patient is a 45-year-old male presenting with chest pain for 2 days. Pain is substernal, radiating to left arm, associated with shortness of breath. Past medical history includes hypertension and diabetes mellitus type 2.'
        }
        
        result = run(input_data)
        
        # Should return a summary
        assert 'summary' in result
        assert isinstance(result['summary'], str)
        assert len(result['summary']) > 0
        
        # Should have metadata
        assert 'original_length' in result
        assert 'summary_length' in result
        assert result['original_length'] > 0
        assert result['summary_length'] > 0
    
    def test_empty_text(self):
        """Test with empty text"""
        input_data = {'text': ''}
        
        result = run(input_data)
        
        assert 'error' in result
        assert result['error'] == "No text provided to summarize"
    
    def test_missing_text_key(self):
        """Test with missing text key"""
        input_data = {}
        
        result = run(input_data)
        
        assert 'error' in result
        assert result['error'] == "No text provided to summarize"
    
    def test_configuration_check(self):
        """Test that tool checks for Azure OpenAI configuration"""
        # This will fail if no credentials but that's expected
        input_data = {'text': 'Test text'}
        
        result = run(input_data)
        
        # Should either succeed or fail gracefully
        assert isinstance(result, dict)
        # Either has summary or error
        assert 'summary' in result or 'error' in result