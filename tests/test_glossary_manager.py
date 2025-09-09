"""
Tests for Glossary Manager Tool
"""

import pytest
import json
from tools.glossary_manager import run


class TestGlossaryManager:
    
    def test_create_glossary_from_simple_terms(self):
        """Test creating glossary from simple term list"""
        terms = [
            'adverse event',
            'clinical trial',
            'informed consent'
        ]
        
        input_data = {
            'action': 'create',
            'terms': terms
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'glossary' in result
        
        glossary = result['glossary']
        assert len(glossary) == 3
        
        # Check that terms were properly processed
        term_ids = list(glossary.keys())
        assert any('adverse_event' in term_id for term_id in term_ids)
        assert any('clinical_trial' in term_id for term_id in term_ids)
        
        # Check standardized structure
        first_term = list(glossary.values())[0]
        assert 'term' in first_term
        assert 'definition' in first_term
        assert 'category' in first_term
        assert 'date_added' in first_term
    
    def test_create_glossary_from_detailed_terms(self):
        """Test creating glossary from detailed term dictionaries"""
        terms = [
            {
                'term': 'Adverse Event',
                'definition': 'Any untoward medical occurrence in a patient or clinical investigation subject',
                'category': 'safety',
                'synonyms': ['AE', 'undesirable event'],
                'examples': ['Headache after treatment', 'Nausea during study']
            },
            {
                'term': 'Serious Adverse Event',
                'definition': 'An adverse event that results in death, is life-threatening, requires hospitalization',
                'category': 'safety',
                'abbreviations': ['SAE'],
                'related_terms': ['adverse event', 'hospitalization']
            }
        ]
        
        input_data = {
            'action': 'create',
            'terms': terms
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        glossary = result['glossary']
        
        # Should have 2 terms
        assert len(glossary) == 2
        
        # Check detailed structure
        ae_term = None
        for term_data in glossary.values():
            if term_data['term'] == 'Adverse Event':
                ae_term = term_data
                break
        
        assert ae_term is not None
        assert ae_term['definition'] == 'Any untoward medical occurrence in a patient or clinical investigation subject'
        assert ae_term['category'] == 'safety'
        assert 'AE' in ae_term['synonyms']
        assert len(ae_term['examples']) == 2
    
    def test_add_terms_to_existing_glossary(self):
        """Test adding terms to existing glossary"""
        existing_glossary = {
            'term_ae': {
                'term': 'Adverse Event',
                'definition': 'Existing definition',
                'category': 'safety'
            }
        }
        
        new_terms = [
            {
                'term': 'Clinical Trial',
                'definition': 'A research study to test new treatments',
                'category': 'research'
            },
            {
                'term': 'Adverse Event',  # Update existing
                'definition': 'Updated definition for adverse event',
                'synonyms': ['AE']
            }
        ]
        
        input_data = {
            'action': 'add_terms',
            'glossary': existing_glossary,
            'terms': new_terms
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert result['new_term_count'] == 1  # One new term
        assert result['updated_term_count'] == 1  # One updated term
        
        updated_glossary = result['updated_glossary']
        assert len(updated_glossary) == 2
        
        # Check that existing term was updated
        ae_term = None
        for term_data in updated_glossary.values():
            if term_data['term'] == 'Adverse Event':
                ae_term = term_data
                break
        
        assert ae_term is not None
        assert 'Updated definition' in ae_term['definition']
        assert 'AE' in ae_term.get('synonyms', [])
    
    def test_validate_document_terminology(self):
        """Test validating document against glossary"""
        glossary = {
            'term_ae': {
                'term': 'adverse event',
                'definition': 'Any untoward medical occurrence',
                'category': 'safety'
            },
            'term_sae': {
                'term': 'serious adverse event',
                'definition': 'An adverse event that is life-threatening',
                'category': 'safety',
                'synonyms': ['SAE']
            },
            'term_consent': {
                'term': 'informed consent',
                'definition': 'Process of learning key facts about a clinical trial',
                'category': 'regulatory'
            }
        }
        
        document_text = """
        The clinical trial protocol requires informed consent from all participants.
        Any adverse event must be reported within 24 hours.
        Serious adverse events require immediate notification.
        Undefined technical terms may appear in the document.
        """
        
        input_data = {
            'action': 'validate_document',
            'document_text': document_text,
            'glossary': glossary,
            'validation_options': {
                'case_sensitive': False,
                'highlight_undefined': True,
                'min_term_length': 4
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        validation_results = result['validation_results']
        
        # Should find defined terms
        defined_terms = validation_results['defined_terms_found']
        assert len(defined_terms) >= 3
        
        term_names = [term['term'] for term in defined_terms]
        assert any('adverse event' in term.lower() for term in term_names)
        assert any('informed consent' in term.lower() for term in term_names)
        
        # Should find undefined terms
        undefined_terms = validation_results['undefined_terms_found']
        undefined_term_names = [term['term'] for term in undefined_terms]
        assert any('technical' in term.lower() for term in undefined_term_names)
        
        # Check statistics
        statistics = result['statistics']
        assert 'validation_score' in statistics
        assert statistics['validation_score'] > 0
        assert 'terminology_coverage' in statistics
    
    def test_search_glossary(self):
        """Test searching through glossary"""
        glossary = {
            'term_ae': {
                'term': 'Adverse Event',
                'definition': 'Medical occurrence in clinical trial',
                'category': 'safety',
                'keywords': ['safety', 'medical']
            },
            'term_consent': {
                'term': 'Informed Consent',
                'definition': 'Process of learning about clinical trial',
                'category': 'regulatory',
                'keywords': ['regulatory', 'ethics']
            },
            'term_endpoint': {
                'term': 'Primary Endpoint',
                'definition': 'Main outcome measure in clinical trial',
                'category': 'statistics'
            }
        }
        
        input_data = {
            'action': 'search',
            'glossary': glossary,
            'search_query': 'clinical trial'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'search_results' in result
        
        search_results = result['search_results']
        assert len(search_results) >= 2  # At least 2 should match
        
        # Results should have relevance scores
        assert all('relevance_score' in res for res in search_results)
        
        # Should be sorted by relevance (highest first)
        if len(search_results) > 1:
            assert search_results[0]['relevance_score'] >= search_results[1]['relevance_score']
    
    def test_export_glossary_json(self):
        """Test exporting glossary as JSON"""
        glossary = {
            'term_1': {
                'term': 'Test Term',
                'definition': 'Test definition',
                'category': 'test'
            }
        }
        
        input_data = {
            'action': 'export',
            'glossary': glossary,
            'export_format': 'json'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'exported_data' in result
        
        # Should be valid JSON
        exported_data = result['exported_data']
        parsed_json = json.loads(exported_data)
        
        assert 'term_1' in parsed_json
        assert parsed_json['term_1']['term'] == 'Test Term'
    
    def test_export_glossary_html(self):
        """Test exporting glossary as HTML"""
        glossary = {
            'term_ae': {
                'term': 'Adverse Event',
                'definition': 'Any untoward medical occurrence',
                'category': 'safety',
                'synonyms': ['AE'],
                'examples': ['Headache', 'Nausea']
            }
        }
        
        input_data = {
            'action': 'export',
            'glossary': glossary,
            'export_format': 'html'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        
        html_data = result['exported_data']
        
        # Should contain HTML structure
        assert '<!DOCTYPE html>' in html_data
        assert '<html>' in html_data
        assert 'Adverse Event' in html_data
        assert 'Any untoward medical occurrence' in html_data
        assert 'Synonyms:' in html_data
        assert 'Examples:' in html_data
    
    def test_export_glossary_markdown(self):
        """Test exporting glossary as Markdown"""
        glossary = {
            'term_consent': {
                'term': 'Informed Consent',
                'definition': 'Process of learning about clinical trial',
                'category': 'regulatory',
                'usage_notes': 'Required before any study procedures'
            }
        }
        
        input_data = {
            'action': 'export',
            'glossary': glossary,
            'export_format': 'markdown'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        
        markdown_data = result['exported_data']
        
        # Should contain Markdown formatting
        assert '# Study Glossary' in markdown_data
        assert '## Informed Consent' in markdown_data
        assert 'Process of learning about clinical trial' in markdown_data
        assert '**Category:**' in markdown_data
        assert '**Usage Notes:**' in markdown_data
    
    def test_merge_glossaries(self):
        """Test merging multiple glossaries"""
        glossary1 = {
            'term_ae': {
                'term': 'Adverse Event',
                'definition': 'Definition from glossary 1',
                'category': 'safety'
            },
            'term_unique1': {
                'term': 'Unique Term 1',
                'definition': 'Only in glossary 1',
                'category': 'unique'
            }
        }
        
        glossary2 = {
            'term_ae': {  # Conflict - same term
                'term': 'Adverse Event',
                'definition': 'Definition from glossary 2',
                'category': 'safety',
                'synonyms': ['AE']  # Additional info
            },
            'term_unique2': {
                'term': 'Unique Term 2',
                'definition': 'Only in glossary 2',
                'category': 'unique'
            }
        }
        
        input_data = {
            'action': 'merge',
            'merge_glossaries': [glossary1, glossary2]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        
        merged_glossary = result['merged_glossary']
        merge_statistics = result['merge_statistics']
        
        # Should contain all unique terms
        assert len(merged_glossary) == 3  # 2 unique + 1 merged conflict
        
        # Check merge statistics
        assert merge_statistics['total_input_glossaries'] == 2
        assert merge_statistics['conflicts_resolved'] == 1
        
        # Check conflict resolution
        conflicts = result['merge_conflicts']
        assert len(conflicts) == 1
        
        conflict = conflicts[0]
        assert conflict['term_id'] == 'term_ae'
        assert 'existing_term' in conflict
        assert 'new_term' in conflict
        assert 'resolved_term' in conflict
    
    def test_comprehensive_validation_workflow(self):
        """Test comprehensive document validation workflow"""
        # Create comprehensive glossary
        terms = [
            {
                'term': 'clinical trial',
                'definition': 'A research study to test new treatments',
                'category': 'research',
                'synonyms': ['clinical study', 'research study']
            },
            {
                'term': 'adverse event',
                'definition': 'Any untoward medical occurrence',
                'category': 'safety',
                'abbreviations': ['AE']
            },
            {
                'term': 'randomization',
                'definition': 'Process of randomly assigning participants',
                'category': 'methodology'
            }
        ]
        
        create_input = {
            'action': 'create',
            'terms': terms
        }
        create_result = run(create_input)
        assert create_result['success'] is True
        
        glossary = create_result['glossary']
        
        # Validate complex document
        document_text = """
        This clinical trial protocol describes a randomized controlled study.
        Participants will be randomly assigned to treatment groups through randomization.
        Any adverse event must be reported immediately.
        The clinical study will follow Good Clinical Practice guidelines.
        Undefined medical terminology should be flagged for review.
        """
        
        validate_input = {
            'action': 'validate_document',
            'document_text': document_text,
            'glossary': glossary,
            'validation_options': {
                'case_sensitive': False,
                'check_definitions': True,
                'check_consistency': True,
                'highlight_undefined': True
            }
        }
        
        validate_result = run(validate_input)
        assert validate_result['success'] is True
        
        validation_results = validate_result['validation_results']
        
        # Should identify defined terms
        defined_terms = validation_results['defined_terms_found']
        assert len(defined_terms) >= 3
        
        # Should identify consistency issues if any
        assert 'inconsistent_usage' in validation_results
        
        # Should provide suggestions for undefined terms
        suggestions = validation_results['suggestions']
        assert len(suggestions) > 0
        
        # Check comprehensive statistics
        statistics = validate_result['statistics']
        assert 'validation_score' in statistics
        assert 'defined_terms' in statistics
        assert 'undefined_terms' in statistics
    
    def test_error_handling_invalid_action(self):
        """Test error handling for invalid action"""
        input_data = {
            'action': 'invalid_action',
            'glossary': {}
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'Unknown action' in result['error']
        assert 'valid_actions' in result
    
    def test_error_handling_missing_document_text(self):
        """Test error handling for document validation without text"""
        input_data = {
            'action': 'validate_document',
            'glossary': {'term1': {'term': 'test', 'definition': 'test'}}
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'document_text is required' in result['error']
    
    def test_error_handling_missing_glossary(self):
        """Test error handling for validation without glossary"""
        input_data = {
            'action': 'validate_document',
            'document_text': 'Some text to validate'
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'glossary is required' in result['error']
    
    def test_advanced_search_features(self):
        """Test advanced search features"""
        glossary = {
            'term_1': {
                'term': 'Primary Endpoint',
                'definition': 'Main outcome measure in clinical trial',
                'category': 'statistics',
                'synonyms': ['primary outcome'],
                'examples': ['Overall survival', 'Response rate']
            },
            'term_2': {
                'term': 'Secondary Endpoint',
                'definition': 'Additional outcome measure',
                'category': 'statistics',
                'related_terms': ['primary endpoint']
            }
        }
        
        # Search for empty query (should return all)
        search_all_input = {
            'action': 'search',
            'glossary': glossary,
            'search_query': ''
        }
        
        search_all_result = run(search_all_input)
        assert search_all_result['success'] is True
        assert len(search_all_result['search_results']) == 2
        assert search_all_result['query'] == 'all terms'
        
        # Search for specific term
        search_specific_input = {
            'action': 'search',
            'glossary': glossary,
            'search_query': 'endpoint'
        }
        
        search_specific_result = run(search_specific_input)
        assert search_specific_result['success'] is True
        assert len(search_specific_result['search_results']) == 2
        
        # Both should match with relevance scores
        results = search_specific_result['search_results']
        assert all('relevance_score' in r for r in results)
        assert all(r['relevance_score'] > 0 for r in results)