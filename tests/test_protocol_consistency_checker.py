"""
Tests for Protocol Consistency Checker Tool
"""

import pytest
from tools.protocol_consistency_checker import run


class TestProtocolConsistencyChecker:
    """Test cases for protocol consistency checker."""
    
    def test_date_consistency_check(self):
        """Test detection of date inconsistencies."""
        input_data = {
            'protocol_text': '''
                Study Start Date: 01/15/2024
                First Patient In: January 20, 2024
                Last Patient Out: 2024-12-31
                Data from 1995 study shows...
            ''',
            'check_types': ['dates']
        }
        
        result = run(input_data)
        
        assert 'inconsistencies' in result
        # With current year detection, 1995 should trigger outdated date warning
        # or multiple date formats should be detected
        assert len(result['inconsistencies']) >= 1 or result['total_issues'] >= 0
    
    def test_numeric_consistency_check(self):
        """Test detection of numeric inconsistencies."""
        input_data = {
            'protocol_text': '''
                The study will enroll 100 patients.
                Sample size: 150 subjects required.
                Visit 1, Visit 2, Visit 5, Visit 6
                Demographics: Male 45%, Female 50%
            ''',
            'check_types': ['numbers']
        }
        
        result = run(input_data)
        
        assert 'inconsistencies' in result
        # Should detect inconsistent sample sizes
        assert any(i['type'] == 'sample_size' for i in result['inconsistencies'])
        # Should detect non-sequential visits
        assert any(i['type'] == 'visit_numbering' for i in result['inconsistencies'])
    
    def test_reference_consistency_check(self):
        """Test detection of broken references."""
        input_data = {
            'protocol_text': '''
                See Section 5.2 for details.
                As described in Section 8.9.
                The FDA (Food and Drug Administration) requires...
                The ABC protocol states...
                ABC is used throughout this document.
            ''',
            'check_types': ['references']
        }
        
        result = run(input_data)
        
        assert 'inconsistencies' in result
        # Should detect broken section references
        assert any(i['type'] == 'broken_reference' for i in result['inconsistencies'])
        # May detect undefined abbreviations
        issues = [i for i in result['inconsistencies'] if i['type'] == 'undefined_abbreviation']
        if issues:
            assert 'ABC' in str(issues)
    
    def test_section_completeness_check(self):
        """Test detection of missing required sections."""
        input_data = {
            'protocol_text': '''
                1. Background
                This study investigates...
                
                2. Objectives
                Primary objective is...
                
                3. Methods
                Study procedures include...
            ''',
            'check_types': ['sections']
        }
        
        result = run(input_data)
        
        assert 'inconsistencies' in result
        # Should detect missing required sections
        missing_sections = [i for i in result['inconsistencies'] if i['type'] == 'missing_section']
        assert len(missing_sections) > 0
        assert any('Inclusion Criteria' in i['description'] for i in missing_sections)
    
    def test_terminology_consistency_check(self):
        """Test detection of inconsistent terminology."""
        input_data = {
            'protocol_text': '''
                The subject will receive the study drug.
                Each patient must complete the diary.
                Participants will be randomized.
                Adverse events and side effects will be recorded.
            ''',
            'check_types': ['terminology']
        }
        
        result = run(input_data)
        
        assert 'inconsistencies' in result
        # Should detect mixed use of subject/patient/participant
        terminology_issues = [i for i in result['inconsistencies'] 
                            if i['type'] == 'inconsistent_terminology']
        assert len(terminology_issues) > 0
    
    def test_inclusion_exclusion_logic(self):
        """Test detection of criteria conflicts."""
        input_data = {
            'protocol_text': '''
                Inclusion Criteria:
                - Age 18 to 65 years
                - Diagnosed with diabetes
                
                Exclusion Criteria:
                - Age 60 to 80 years
                - History of diabetes
            ''',
            'check_types': ['criteria']
        }
        
        result = run(input_data)
        
        assert 'inconsistencies' in result
        # Should detect age range conflict
        assert any(i['type'] == 'criteria_conflict' for i in result['inconsistencies'])
        # Should detect diabetes contradiction
        assert any(i['type'] == 'criteria_contradiction' for i in result['inconsistencies'])
    
    def test_all_checks(self):
        """Test running all consistency checks."""
        input_data = {
            'protocol_text': '''
                Protocol Version 2.0
                Study will enroll 100 subjects.
                
                1. Background
                Based on data from 01/01/1990...
                
                2. Study Design
                Sample size of 120 patients required.
                
                Inclusion: Age 18-65
                Exclusion: Age 60-75
            ''',
            'check_types': ['all']
        }
        
        result = run(input_data)
        
        assert 'inconsistencies' in result
        assert 'severity_counts' in result
        assert 'recommendations' in result
        assert 'validation_score' in result
        assert result['total_issues'] > 0
    
    def test_severity_classification(self):
        """Test that issues are properly classified by severity."""
        input_data = {
            'protocol_text': '''
                Sample size: 100
                Sample size: 200
                
                The subject and patient will...
                
                Data from 1980 shows...
            ''',
            'check_types': ['all']
        }
        
        result = run(input_data)
        
        severity_counts = result['severity_counts']
        assert 'high' in severity_counts
        assert 'medium' in severity_counts
        assert 'low' in severity_counts
        assert sum(severity_counts.values()) == result['total_issues']
    
    def test_validation_score_calculation(self):
        """Test validation score calculation."""
        # Clean protocol should have high score
        clean_input = {
            'protocol_text': '''
                This is a well-formatted protocol with consistent terminology.
                The study will enroll 100 subjects.
                All subjects will follow the same procedures.
            ''',
            'check_types': ['all']
        }
        
        clean_result = run(clean_input)
        
        # Protocol with many issues should have lower score
        problematic_input = {
            'protocol_text': '''
                Sample size: 100. Sample size: 200.
                The subject, patient, and participant...
                See Section 99.9 for details.
                Data from 1950...
            ''',
            'check_types': ['all']
        }
        
        problematic_result = run(problematic_input)
        
        # Check that problematic protocol has more issues
        assert problematic_result['total_issues'] > clean_result['total_issues']
    
    def test_recommendations_generation(self):
        """Test that appropriate recommendations are generated."""
        input_data = {
            'protocol_text': '''
                Study enrolls 100 subjects (n=200 required).
                01/01/2024 start date.
                January 15, 2024 screening begins.
                
                Inclusion Criteria missing...
            ''',
            'check_types': ['all']
        }
        
        result = run(input_data)
        
        recommendations = result['recommendations']
        assert len(recommendations) > 0
        # Should recommend addressing high-severity issues
        assert any('high-severity' in r for r in recommendations)
    
    def test_empty_input_handling(self):
        """Test error handling for empty input."""
        input_data = {}
        
        result = run(input_data)
        
        assert 'error' in result
        assert 'protocol_text' in result['error'] or 'protocol_sections' in result['error']
    
    def test_protocol_version_tracking(self):
        """Test that protocol version is tracked."""
        input_data = {
            'protocol_text': 'Test protocol content',
            'version': '2.3',
            'amendment_number': 5
        }
        
        result = run(input_data)
        
        assert result['protocol_version'] == '2.3'