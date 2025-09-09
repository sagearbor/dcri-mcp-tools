"""
Tests for Newsletter Creator Tool
"""

import pytest
import json
from tools.newsletter_creator import run


class TestNewsletterCreator:
    
    def test_create_participant_newsletter(self):
        """Test creating participant newsletter"""
        content_items = [
            {
                'title': 'Study Progress Update',
                'content': 'We have successfully enrolled 150 participants in our study.',
                'type': 'enrollment_update',
                'priority': 'high'
            },
            {
                'title': 'Important Safety Information',
                'content': 'Please report any side effects immediately to the study team.',
                'type': 'safety_update',
                'priority': 'high'
            },
            {
                'title': 'Upcoming Events',
                'content': 'Join us for a participant appreciation event next month.',
                'type': 'event_announcement',
                'priority': 'medium'
            }
        ]
        
        study_info = {
            'name': 'Cardiac Health Study',
            'id': 'CHS-2024-001',
            'start_date': '2024-01-01'
        }
        
        input_data = {
            'action': 'create',
            'newsletter_type': 'participant',
            'content_items': content_items,
            'template_style': 'friendly',
            'frequency': 'monthly',
            'study_info': study_info
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'newsletter_content' in result
        
        newsletter = result['newsletter_content']
        
        # Check header information
        header = newsletter['header']
        assert header['study_name'] == 'Cardiac Health Study'
        assert 'Monthly' in header['newsletter_title'] or 'Participant' in header['newsletter_title']
        
        # Check sections are organized
        sections = newsletter['sections']
        assert len(sections) > 0
        
        # Should have study updates section
        section_names = list(sections.keys())
        assert any('Study Updates' in name or 'Update' in name for name in section_names)
        
        # Check formatted outputs
        formatted_versions = result['formatted_versions']
        assert 'html' in formatted_versions
        assert 'text' in formatted_versions
        assert 'markdown' in formatted_versions
        
        # HTML should contain study name
        html_output = formatted_versions['html']
        assert 'Cardiac Health Study' in html_output
        assert 'Study Progress Update' in html_output
    
    def test_create_investigator_newsletter(self):
        """Test creating investigator newsletter"""
        content_items = [
            {
                'title': 'Protocol Amendment #3',
                'content': 'New eligibility criteria have been added to the protocol.',
                'type': 'protocol_update',
                'priority': 'high',
                'target_audience': 'investigator'
            },
            {
                'title': 'Enrollment Status',
                'content': 'Current enrollment stands at 75% of target.',
                'type': 'enrollment_update',
                'priority': 'medium'
            },
            {
                'title': 'Upcoming Training',
                'content': 'Mandatory training on new procedures scheduled for next week.',
                'type': 'training_update',
                'priority': 'high'
            }
        ]
        
        input_data = {
            'action': 'create',
            'newsletter_type': 'investigator',
            'content_items': content_items,
            'template_style': 'clinical',
            'frequency': 'quarterly'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        
        newsletter = result['newsletter_content']
        sections = newsletter['sections']
        
        # Should have investigator-specific sections
        section_names = list(sections.keys())
        assert any('Protocol' in name for name in section_names)
        assert any('Enrollment' in name for name in section_names)
        
        # Check priority handling
        high_priority_content = []
        for section_data in sections.values():
            content = section_data.get('content', [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('priority') == 'high':
                        high_priority_content.append(item)
        
        assert len(high_priority_content) > 0  # Should have high priority items
    
    def test_generate_newsletter_template(self):
        """Test generating newsletter template"""
        input_data = {
            'action': 'template',
            'newsletter_type': 'participant',
            'template_style': 'friendly',
            'frequency': 'monthly'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'template' in result
        
        template = result['template']
        
        # Check template structure
        assert 'structure' in template
        assert 'style_guide' in template
        assert 'content_guidelines' in template
        assert 'frequency_recommendations' in template
        
        # Check usage notes
        assert 'usage_notes' in result
        usage_notes = result['usage_notes']
        assert len(usage_notes) > 0
        assert any('participant' in note.lower() for note in usage_notes)
    
    def test_format_newsletter_content(self):
        """Test formatting newsletter content"""
        content_items = [
            {
                'id': 'item1',
                'title': 'Study Milestone Reached',
                'content': 'We have reached our primary enrollment milestone.',
                'type': 'milestone',
                'priority': 'high'
            },
            {
                'id': 'item2',
                'title': 'Safety Update',
                'content': 'No new safety signals have been identified.',
                'type': 'safety_update',
                'priority': 'medium'
            }
        ]
        
        format_options = {
            'include_images': True,
            'use_brand_colors': True,
            'responsive_design': True
        }
        
        input_data = {
            'action': 'format',
            'content_items': content_items,
            'format_options': format_options
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'formatted_content' in result
        
        formatted_content = result['formatted_content']
        
        # Check that both items are formatted
        assert 'item1' in formatted_content
        assert 'item2' in formatted_content
        
        # Check formatting includes different output types
        item1_formats = formatted_content['item1']
        assert 'html' in item1_formats
        assert 'text' in item1_formats
        assert 'markdown' in item1_formats
        
        # Check formatting notes
        assert 'formatting_notes' in result
    
    def test_create_newsletter_schedule(self):
        """Test creating newsletter publication schedule"""
        study_info = {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        }
        
        input_data = {
            'action': 'schedule',
            'frequency': 'monthly',
            'study_info': study_info
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'publication_schedule' in result
        
        schedule = result['publication_schedule']
        
        # Should have multiple issues planned
        assert len(schedule) >= 10  # At least 10 monthly issues for a year
        
        # Check schedule structure
        first_issue = schedule[0]
        assert 'issue_number' in first_issue
        assert 'publication_date' in first_issue
        assert 'theme' in first_issue
        assert 'suggested_content' in first_issue
        assert 'deadline' in first_issue
        
        # Themes should be meaningful
        themes = [issue['theme'] for issue in schedule]
        assert any('Welcome' in theme or 'Launch' in theme for theme in themes)
        
        # Check schedule summary
        assert 'schedule_summary' in result
        assert result['total_issues_planned'] == len(schedule)
    
    def test_analyze_newsletter_performance(self):
        """Test newsletter performance analysis"""
        content_items = [
            {
                'title': 'Enrollment Update',
                'content': 'Short update about enrollment progress.',
                'type': 'enrollment_update',
                'priority': 'high',
                'word_count': 25
            },
            {
                'title': 'Detailed Protocol Review',
                'content': 'This is a very detailed and comprehensive review of the protocol changes that have been implemented in the study. It covers all aspects of the modifications and their implications for participants and investigators.',
                'type': 'protocol_update',
                'priority': 'high',
                'word_count': 150
            },
            {
                'title': 'Safety Information',
                'content': 'Important safety information for all participants.',
                'type': 'safety_update',
                'priority': 'high'
            },
            {
                'title': 'Administrative Update',
                'content': 'Minor administrative changes.',
                'type': 'administrative',
                'priority': 'low'
            }
        ]
        
        input_data = {
            'action': 'analyze',
            'content_items': content_items
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'analysis' in result
        
        analysis = result['analysis']
        
        # Check content analysis
        content_analysis = analysis['content_analysis']
        assert 'type_distribution' in content_analysis
        assert 'most_common_type' in content_analysis
        
        # Check engagement metrics
        engagement_metrics = analysis['engagement_metrics']
        assert 'estimated_open_rate' in engagement_metrics
        
        # Check readability analysis
        readability = analysis['readability_analysis']
        assert 'readability_level' in readability
        assert 'total_word_count' in readability
        
        # Check recommendations
        assert 'recommendations' in result
        recommendations = result['recommendations']
        assert len(recommendations) > 0
        
        # Check performance score
        assert 'performance_score' in result
        assert 0 <= result['performance_score'] <= 100
    
    def test_different_template_styles(self):
        """Test different newsletter template styles"""
        content_items = [
            {
                'title': 'Study Update',
                'content': 'Important update about the study progress.',
                'type': 'general_update'
            }
        ]
        
        styles = ['formal', 'friendly', 'clinical', 'brief']
        
        for style in styles:
            input_data = {
                'action': 'create',
                'newsletter_type': 'general',
                'content_items': content_items,
                'template_style': style,
                'frequency': 'monthly'
            }
            
            result = run(input_data)
            
            assert result['success'] is True
            newsletter = result['newsletter_content']
            
            # Check that style affects content
            greeting = newsletter.get('greeting', '')
            
            if style == 'friendly':
                assert 'Dear Friends' in greeting or 'friendly' in greeting.lower()
            elif style == 'formal':
                assert 'Dear Recipients' in greeting or 'formal' in greeting.lower()
            elif style == 'brief':
                assert len(greeting) < 50  # Brief should be short
    
    def test_multiple_newsletter_types(self):
        """Test creating different types of newsletters"""
        content_items = [
            {
                'title': 'Executive Summary',
                'content': 'High-level summary of study progress and key metrics.',
                'type': 'executive_summary'
            }
        ]
        
        newsletter_types = ['participant', 'investigator', 'sponsor', 'general']
        
        for newsletter_type in newsletter_types:
            input_data = {
                'action': 'create',
                'newsletter_type': newsletter_type,
                'content_items': content_items,
                'template_style': 'formal'
            }
            
            result = run(input_data)
            
            assert result['success'] is True
            
            newsletter = result['newsletter_content']
            sections = newsletter['sections']
            
            # Different types should have different section organizations
            if newsletter_type == 'sponsor':
                section_names = list(sections.keys())
                assert any('Executive' in name or 'Metrics' in name for name in section_names)
            elif newsletter_type == 'participant':
                section_names = list(sections.keys())
                assert any('Resources' in name or 'Updates' in name for name in section_names)
    
    def test_comprehensive_newsletter_creation(self):
        """Test comprehensive newsletter creation with all features"""
        content_items = [
            {
                'title': 'Major Milestone Achieved',
                'content': 'We are proud to announce that we have reached our primary enrollment goal.',
                'type': 'milestone',
                'priority': 'high',
                'target_audience': 'all'
            },
            {
                'title': 'Safety Review Complete',
                'content': 'The quarterly safety review has been completed with no new concerns identified.',
                'type': 'safety_update',
                'priority': 'medium',
                'target_audience': 'investigator'
            },
            {
                'title': 'Participant Appreciation Event',
                'content': 'Join us for our annual participant appreciation dinner on March 15th.',
                'type': 'event_announcement',
                'priority': 'medium',
                'target_audience': 'participants'
            },
            {
                'title': 'Training Session Scheduled',
                'content': 'Mandatory training on updated procedures scheduled for all sites.',
                'type': 'training_update',
                'priority': 'high',
                'target_audience': 'investigator'
            }
        ]
        
        study_info = {
            'name': 'Comprehensive Clinical Trial',
            'id': 'CCT-2024-001',
            'start_date': '2024-01-01',
            'contact_info': {
                'phone': '555-STUDY-1',
                'email': 'info@comprehensivetrial.com',
                'website': 'https://comprehensivetrial.com'
            }
        }
        
        format_options = {
            'include_toc': True,
            'include_metrics': True,
            'use_templates': True,
            'responsive': True
        }
        
        input_data = {
            'action': 'create',
            'newsletter_type': 'general',
            'content_items': content_items,
            'template_style': 'detailed',
            'frequency': 'quarterly',
            'study_info': study_info,
            'format_options': format_options
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        
        newsletter = result['newsletter_content']
        
        # Check comprehensive structure
        assert 'header' in newsletter
        assert 'greeting' in newsletter
        assert 'introduction' in newsletter
        assert 'sections' in newsletter
        assert 'conclusion' in newsletter
        assert 'footer' in newsletter
        
        # Check metadata
        metadata = newsletter['metadata']
        assert 'total_word_count' in metadata
        assert 'estimated_read_time' in metadata
        assert 'section_count' in metadata
        
        # Check statistics
        statistics = result['statistics']
        assert 'total_word_count' in statistics
        assert 'content_type_breakdown' in statistics
        assert 'priority_breakdown' in statistics
        
        # Check formatted versions quality
        formatted_versions = result['formatted_versions']
        html_output = formatted_versions['html']
        
        # HTML should be substantial and well-formed
        assert len(html_output) > 2000
        assert '<!DOCTYPE html>' in html_output
        assert 'Comprehensive Clinical Trial' in html_output
        assert 'Major Milestone Achieved' in html_output
        
        # Should include contact information
        footer_info = newsletter['footer']['contact_information']
        assert footer_info['phone'] == '555-STUDY-1'
        assert footer_info['email'] == 'info@comprehensivetrial.com'
        
        # Check recommendations
        recommendations = result['recommendations']
        assert len(recommendations) > 0
    
    def test_newsletter_frequency_variations(self):
        """Test different newsletter frequencies"""
        study_info = {
            'start_date': '2024-01-01',
            'end_date': '2025-12-31'
        }
        
        frequencies = ['weekly', 'monthly', 'quarterly', 'milestone']
        
        for frequency in frequencies:
            input_data = {
                'action': 'schedule',
                'frequency': frequency,
                'study_info': study_info
            }
            
            result = run(input_data)
            
            assert result['success'] is True
            
            schedule = result['publication_schedule']
            
            # Check frequency-appropriate number of issues
            if frequency == 'weekly':
                assert len(schedule) > 50  # More than 50 weekly issues
            elif frequency == 'monthly':
                assert 20 <= len(schedule) <= 30  # About 2 years of monthly
            elif frequency == 'quarterly':
                assert 6 <= len(schedule) <= 10  # About 2 years of quarterly
            
            # Check themes are appropriate for frequency
            themes = [issue['theme'] for issue in schedule]
            if frequency == 'quarterly':
                assert any('Year-End' in theme or 'Review' in theme for theme in themes)
    
    def test_error_handling_invalid_action(self):
        """Test error handling for invalid action"""
        input_data = {
            'action': 'invalid_action',
            'newsletter_type': 'participant'
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'Unknown action' in result['error']
        assert 'valid_actions' in result
    
    def test_error_handling_missing_content(self):
        """Test handling of missing content items"""
        input_data = {
            'action': 'create',
            'newsletter_type': 'participant',
            'content_items': [],  # Empty content
            'template_style': 'friendly'
        }
        
        result = run(input_data)
        
        # Should handle gracefully
        assert result['success'] is True
        
        # Should still create basic structure
        newsletter = result['newsletter_content']
        assert 'header' in newsletter
        assert 'sections' in newsletter
        
        # Statistics should reflect empty content
        statistics = result['statistics']
        assert statistics['content_item_count'] == 0