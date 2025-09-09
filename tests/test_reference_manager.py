"""
Tests for Reference Manager Tool
"""

import pytest
import json
from tools.reference_manager import run


class TestReferenceManager:
    
    def test_add_single_reference(self):
        """Test adding a single reference"""
        reference = {
            'title': 'Clinical Trial Design and Analysis',
            'authors': ['Smith J', 'Johnson M'],
            'year': '2023',
            'journal': 'New England Journal of Medicine',
            'volume': '388',
            'pages': '123-130',
            'doi': '10.1056/example'
        }
        
        input_data = {
            'action': 'add',
            'references': [reference]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'added_references' in result
        assert len(result['added_references']) == 1
        
        added_ref = result['added_references'][0]
        assert added_ref['title'] == reference['title']
        assert added_ref['authors'] == reference['authors']
        assert 'date_added' in added_ref
        assert added_ref['type'] == 'article'
    
    def test_add_multiple_references(self):
        """Test adding multiple references"""
        references = [
            {
                'title': 'Randomized Controlled Trials',
                'authors': ['Brown A'],
                'year': '2022',
                'journal': 'Lancet'
            },
            {
                'title': 'Statistical Methods in Clinical Research',
                'authors': ['Davis C', 'Wilson R'],
                'year': '2023',
                'journal': 'JAMA',
                'type': 'review'
            }
        ]
        
        input_data = {
            'action': 'add',
            'references': references
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert result['added_count'] == 2
        assert len(result['added_references']) == 2
        assert result['summary'].startswith('Successfully added 2 references')
    
    def test_format_references_apa_style(self):
        """Test formatting references in APA style"""
        references = [
            {
                'title': 'Clinical Trial Methodology',
                'authors': ['Smith, J.', 'Johnson, M. K.'],
                'year': '2023',
                'journal': 'Clinical Research Journal',
                'volume': '45',
                'pages': '15-28'
            }
        ]
        
        input_data = {
            'action': 'format',
            'references': references,
            'citation_style': 'apa'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'formatted_references' in result
        
        formatted_ref = result['formatted_references'][0]
        assert 'in_text_citation' in formatted_ref
        assert 'bibliography_entry' in formatted_ref
        
        # Check APA format characteristics
        in_text = formatted_ref['in_text_citation']
        assert '(Smith, 2023)' in in_text or '(Smith & Johnson, 2023)' in in_text
        
        bibliography = formatted_ref['bibliography_entry']
        assert '(2023)' in bibliography
        assert 'Clinical Trial Methodology' in bibliography
    
    def test_format_references_vancouver_style(self):
        """Test formatting references in Vancouver style"""
        references = [
            {
                'id': 'ref1',
                'title': 'Evidence-Based Medicine',
                'authors': ['Anderson P', 'Brown K'],
                'year': '2024',
                'journal': 'BMJ',
                'volume': '380',
                'pages': 'e001234'
            }
        ]
        
        input_data = {
            'action': 'format',
            'references': references,
            'citation_style': 'vancouver'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        
        formatted_ref = result['formatted_references'][0]
        
        # Vancouver uses numbered citations
        in_text = formatted_ref['in_text_citation']
        assert '(' in in_text and ')' in in_text
        
        # Vancouver bibliography format
        bibliography = formatted_ref['bibliography_entry']
        assert 'Anderson P' in bibliography or 'Anderson' in bibliography
        assert 'Evidence-Based Medicine' in bibliography
    
    def test_validate_references_comprehensive(self):
        """Test comprehensive reference validation"""
        references = [
            {
                'title': 'Complete Reference',
                'authors': ['Complete A'],
                'year': '2023',
                'journal': 'Complete Journal',
                'doi': '10.1234/complete',
                'pmid': '12345678'
            },
            {
                'title': 'Incomplete Reference',
                # Missing required fields
                'year': 'invalid_year',
                'doi': 'invalid_doi',
                'pmid': 'invalid_pmid'
            }
        ]
        
        input_data = {
            'action': 'validate',
            'references': references
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        validation_results = result['validation_results']
        
        assert len(validation_results) == 2
        
        # First reference should score well
        complete_ref = validation_results[0]
        assert complete_ref['percentage_score'] > 80
        assert len(complete_ref['issues']) == 0
        
        # Second reference should have issues
        incomplete_ref = validation_results[1]
        assert incomplete_ref['percentage_score'] < 50
        assert len(incomplete_ref['issues']) > 0
        
        # Check summary
        summary = result['summary']
        assert summary['total_issues'] > 0
        assert 'quality_rating' in summary
    
    def test_search_references(self):
        """Test searching through references"""
        references = [
            {
                'title': 'Clinical Trial Design',
                'authors': ['Smith J'],
                'journal': 'Clinical Research',
                'keywords': ['randomized', 'controlled', 'trial']
            },
            {
                'title': 'Statistical Analysis Methods',
                'authors': ['Jones M'],
                'journal': 'Statistics in Medicine',
                'abstract': 'This paper discusses statistical methods for clinical trials'
            },
            {
                'title': 'Patient Safety in Trials',
                'authors': ['Brown K'],
                'journal': 'Safety Journal'
            }
        ]
        
        input_data = {
            'action': 'search',
            'references': references,
            'search_query': 'clinical'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'search_results' in result
        
        # Should find references containing 'clinical'
        search_results = result['search_results']
        assert len(search_results) >= 2  # At least 2 should match
        
        # Results should be sorted by relevance
        assert all('relevance_score' in res for res in search_results)
        
        # First result should have highest relevance
        if len(search_results) > 1:
            assert search_results[0]['relevance_score'] >= search_results[1]['relevance_score']
    
    def test_export_references_bibtex(self):
        """Test exporting references as BibTeX"""
        references = [
            {
                'id': 'smith2023',
                'type': 'article',
                'title': 'Clinical Trial Methods',
                'authors': ['Smith, John', 'Doe, Jane'],
                'journal': 'Research Journal',
                'year': '2023',
                'volume': '10',
                'pages': '1-15'
            }
        ]
        
        input_data = {
            'action': 'export',
            'references': references,
            'export_format': 'bibtex'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'exported_data' in result
        
        bibtex_data = result['exported_data']
        
        # Check BibTeX format
        assert '@article{smith2023,' in bibtex_data
        assert 'title={Clinical Trial Methods}' in bibtex_data
        assert 'author={Smith, John and Doe, Jane}' in bibtex_data
        assert 'year={2023}' in bibtex_data
        assert '}' in bibtex_data
    
    def test_export_references_json(self):
        """Test exporting references as JSON"""
        references = [
            {
                'title': 'Test Reference',
                'authors': ['Test Author'],
                'year': '2024'
            }
        ]
        
        input_data = {
            'action': 'export',
            'references': references,
            'export_format': 'json'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        
        # Should be valid JSON
        exported_data = result['exported_data']
        parsed_json = json.loads(exported_data)
        assert isinstance(parsed_json, list)
        assert len(parsed_json) == 1
        assert parsed_json[0]['title'] == 'Test Reference'
    
    def test_import_references_json(self):
        """Test importing references from JSON"""
        json_data = json.dumps([
            {
                'title': 'Imported Reference 1',
                'authors': ['Import Author A'],
                'year': '2023'
            },
            {
                'title': 'Imported Reference 2',
                'authors': ['Import Author B'],
                'year': '2024'
            }
        ])
        
        input_data = {
            'action': 'import',
            'import_data': json_data
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'imported_references' in result
        assert result['import_count'] == 2
        assert result['detected_format'] == 'json'
        
        imported_refs = result['imported_references']
        titles = [ref['title'] for ref in imported_refs]
        assert 'Imported Reference 1' in titles
        assert 'Imported Reference 2' in titles
    
    def test_import_references_bibtex(self):
        """Test importing references from BibTeX"""
        bibtex_data = """
        @article{test2023,
            title={Test BibTeX Import},
            author={Test Author and Second Author},
            journal={Test Journal},
            year={2023},
            volume={1},
            pages={1-10}
        }
        """
        
        input_data = {
            'action': 'import',
            'import_data': bibtex_data
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert result['detected_format'] == 'bibtex'
        assert result['import_count'] == 1
        
        imported_ref = result['imported_references'][0]
        assert imported_ref['title'] == 'Test BibTeX Import'
        assert 'Test Author' in imported_ref['authors']
        assert imported_ref['year'] == '2023'
    
    def test_custom_validation_rules(self):
        """Test validation with custom rules"""
        references = [
            {
                'title': 'Valid Reference',
                'authors': ['Smith J'],
                'year': '2023',
                'journal': 'Test Journal',
                'custom_field': 'VALID-123'
            },
            {
                'title': 'Invalid Reference',
                'authors': ['Jones M'],
                'year': '2023',
                'journal': 'Test Journal',
                'custom_field': 'INVALID'
            }
        ]
        
        validation_rules = {
            'custom_id_format': {
                'field': 'custom_field',
                'pattern': r'^VALID-\d{3}$',
                'required': True,
                'severity': 'error'
            }
        }
        
        input_data = {
            'action': 'validate',
            'references': references,
            'validation_rules': validation_rules
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        validation_results = result['validation_results']
        
        # First reference should pass custom validation
        valid_ref = validation_results[0]
        assert len(valid_ref['issues']) == 0
        
        # Second reference should fail custom validation
        invalid_ref = validation_results[1]
        custom_issues = [issue for issue in invalid_ref['issues'] if 'custom_field' in issue]
        assert len(custom_issues) > 0
    
    def test_comprehensive_reference_workflow(self):
        """Test comprehensive reference management workflow"""
        # Step 1: Add references
        references = [
            {
                'title': 'Primary Clinical Trial',
                'authors': ['Lead Author', 'Co Author'],
                'year': '2023',
                'journal': 'Primary Journal',
                'type': 'article',
                'doi': '10.1000/primary'
            },
            {
                'title': 'Secondary Analysis',
                'authors': ['Second Author'],
                'year': '2024',
                'journal': 'Analysis Journal',
                'type': 'article'
            }
        ]
        
        # Add references
        add_input = {
            'action': 'add',
            'references': references
        }
        add_result = run(add_input)
        assert add_result['success'] is True
        
        added_refs = add_result['added_references']
        
        # Step 2: Validate references
        validate_input = {
            'action': 'validate',
            'references': added_refs
        }
        validate_result = run(validate_input)
        assert validate_result['success'] is True
        
        # Step 3: Format references
        format_input = {
            'action': 'format',
            'references': added_refs,
            'citation_style': 'apa'
        }
        format_result = run(format_input)
        assert format_result['success'] is True
        
        # Step 4: Search references
        search_input = {
            'action': 'search',
            'references': added_refs,
            'search_query': 'clinical'
        }
        search_result = run(search_input)
        assert search_result['success'] is True
        
        # Step 5: Export references
        export_input = {
            'action': 'export',
            'references': added_refs,
            'export_format': 'bibtex'
        }
        export_result = run(export_input)
        assert export_result['success'] is True
        
        # Verify workflow completed successfully
        assert len(format_result['formatted_references']) == 2
        assert search_result['result_count'] > 0
        assert '@article' in export_result['exported_data']
    
    def test_error_handling_invalid_action(self):
        """Test error handling for invalid action"""
        input_data = {
            'action': 'invalid_action',
            'references': []
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'Unknown action' in result['error']
        assert 'valid_actions' in result
    
    def test_error_handling_missing_action(self):
        """Test error handling for missing action"""
        input_data = {
            'references': []
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'action is required' in result['error']
    
    def test_different_reference_types(self):
        """Test handling different types of references"""
        references = [
            {
                'type': 'book',
                'title': 'Clinical Research Handbook',
                'authors': ['Book Author'],
                'year': '2023',
                'publisher': 'Academic Press'
            },
            {
                'type': 'conference',
                'title': 'Advances in Clinical Trials',
                'authors': ['Conference Author'],
                'year': '2023',
                'conference_name': 'International Clinical Research Conference'
            },
            {
                'type': 'thesis',
                'title': 'Novel Methods in Clinical Research',
                'authors': ['Thesis Author'],
                'year': '2024',
                'institution': 'University of Research'
            }
        ]
        
        input_data = {
            'action': 'add',
            'references': references
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        added_refs = result['added_references']
        
        # Check that different types are handled
        types_found = [ref['type'] for ref in added_refs]
        assert 'book' in types_found
        assert 'conference' in types_found
        assert 'thesis' in types_found