"""
Tests for FAQ Generator Tool
"""

import pytest
import json
from tools.faq_generator import run


class TestFAQGenerator:
    
    def test_generate_faqs_from_simple_questions(self):
        """Test generating FAQs from simple question list"""
        questions = [
            "Am I eligible for this study?",
            "How long will the study last?",
            "What are the risks involved?",
            "Can I withdraw from the study?",
            "Will I be compensated?"
        ]
        
        input_data = {
            'action': 'generate',
            'questions': questions,
            'source_type': 'queries',
            'target_audience': 'participants'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'generated_faqs' in result
        
        faqs = result['generated_faqs']
        assert len(faqs) >= 3  # Should generate multiple FAQs
        
        # Check FAQ structure
        faq = faqs[0]
        assert 'question' in faq
        assert 'answer' in faq
        assert 'category' in faq
        assert 'priority' in faq
        
        # Check categories are appropriate
        categories = [f['category'] for f in faqs]
        assert 'Eligibility' in categories
        assert 'Time Commitment' in categories or 'General' in categories
        
        # Check statistics
        stats = result['statistics']
        assert 'total_faqs' in stats
        assert stats['total_faqs'] > 0
    
    def test_generate_faqs_from_detailed_questions(self):
        """Test generating FAQs from detailed question objects"""
        questions = [
            {
                'id': 'q1',
                'question': 'What are the inclusion criteria for this study?',
                'source': 'participant_feedback',
                'frequency': 5,
                'priority': 'high',
                'category': 'eligibility'
            },
            {
                'id': 'q2',
                'question': 'How often do I need to come for visits?',
                'source': 'investigator_query',
                'frequency': 3,
                'priority': 'medium'
            },
            {
                'id': 'q3',
                'question': 'Are there any side effects I should know about?',
                'source': 'safety_concern',
                'frequency': 8,
                'priority': 'high'
            }
        ]
        
        input_data = {
            'action': 'generate',
            'questions': questions,
            'categorization': True,
            'format_style': 'detailed',
            'priority_threshold': 2
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        faqs = result['generated_faqs']
        
        # Should include high frequency questions
        high_freq_faqs = [f for f in faqs if f.get('frequency', 0) >= 5]
        assert len(high_freq_faqs) >= 2
        
        # Check priority assignment
        high_priority_faqs = [f for f in faqs if f.get('priority') == 'high']
        assert len(high_priority_faqs) > 0
        
        # Check categorization worked
        categories = set(f['category'] for f in faqs)
        assert len(categories) > 1  # Multiple categories should be identified
    
    def test_categorize_questions_automatically(self):
        """Test automatic question categorization"""
        questions = [
            "Am I eligible to participate?",
            "What tests will be performed?",
            "Is this study safe?",
            "How long does each visit take?",
            "Will I be paid for participation?",
            "Can I stop participating anytime?",
            "Who will see my information?"
        ]
        
        input_data = {
            'action': 'categorize',
            'questions': questions
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'categorized_questions' in result
        
        categorized = result['categorized_questions']
        assert len(categorized) == len(questions)
        
        # Check categories are assigned
        categories_found = set(q['category'] for q in categorized)
        expected_categories = ['Eligibility', 'Study Procedures', 'Safety', 'Time Commitment', 
                             'Compensation', 'Withdrawal', 'Confidentiality']
        
        # Should find at least 4 different categories
        assert len(categories_found) >= 4
        
        # Check category statistics
        category_stats = result['category_statistics']
        assert len(category_stats) > 0
        assert sum(category_stats.values()) == len(questions)
    
    def test_update_existing_faqs(self):
        """Test updating existing FAQs with new questions"""
        existing_faqs = [
            {
                'id': 'faq_1',
                'question': 'How do I enroll in the study?',
                'answer': 'Contact the study team at...',
                'category': 'Enrollment',
                'frequency': 3
            }
        ]
        
        new_questions = [
            {
                'question': 'How do I sign up for the study?',  # Similar to existing
                'frequency': 2
            },
            {
                'question': 'What happens during screening?',    # New question
                'frequency': 4
            }
        ]
        
        input_data = {
            'action': 'update',
            'existing_faqs': existing_faqs,
            'questions': new_questions
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'updated_faqs' in result
        
        updated_faqs = result['updated_faqs']
        
        # Should have updated existing FAQ and added new one
        assert len(updated_faqs) >= 2
        
        # Check that similar question updated existing FAQ
        enrollment_faqs = [f for f in updated_faqs if f.get('category') == 'Enrollment']
        if enrollment_faqs:
            enrollment_faq = enrollment_faqs[0]
            assert enrollment_faq['frequency'] > 3  # Should be increased
        
        # Check summary
        summary = result['summary']
        assert 'new_faqs_added' in summary
        assert 'existing_faqs_updated' in summary
    
    def test_format_faqs_html(self):
        """Test formatting FAQs as HTML"""
        faqs = [
            {
                'question': 'What is this study about?',
                'answer': 'This study investigates new treatment approaches.',
                'category': 'General',
                'priority': 'high'
            },
            {
                'question': 'Am I eligible?',
                'answer': 'Eligibility depends on specific criteria.',
                'category': 'Eligibility',
                'priority': 'medium'
            }
        ]
        
        input_data = {
            'action': 'format',
            'existing_faqs': faqs,
            'format_style': 'detailed',
            'target_audience': 'participants'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'formatted_faqs' in result
        
        formatted_output = result['formatted_faqs']
        
        # Check HTML format
        html_output = formatted_output['html']
        assert '<!DOCTYPE html>' in html_output
        assert 'What is this study about?' in html_output
        assert 'This study investigates' in html_output
        assert 'priority-high' in html_output or 'high' in html_output
        
        # Check Markdown format
        markdown_output = formatted_output['markdown']
        assert '# Frequently Asked Questions' in markdown_output
        assert '## General' in markdown_output
        assert '**What is this study about?**' in markdown_output
    
    def test_analyze_question_patterns(self):
        """Test analyzing question patterns and trends"""
        questions = [
            {
                'question': 'What are the inclusion criteria?',
                'timestamp': '2024-01-01T10:00:00',
                'source': 'participant'
            },
            {
                'question': 'How do I qualify for this study?',
                'timestamp': '2024-01-02T14:30:00',
                'source': 'participant'
            },
            {
                'question': 'What tests will be performed during the study?',
                'timestamp': '2024-01-03T09:15:00',
                'source': 'investigator'
            },
            {
                'question': 'URGENT: What are the emergency procedures?',
                'timestamp': '2024-01-04T16:45:00',
                'source': 'safety_concern'
            }
        ]
        
        input_data = {
            'action': 'analyze',
            'questions': questions
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'analysis' in result
        
        analysis = result['analysis']
        
        # Check question types analysis
        question_types = analysis['question_types']
        assert 'what' in question_types
        assert question_types['what'] >= 2
        
        # Check common topics
        common_topics = analysis['common_topics']
        assert len(common_topics) > 0
        
        topic_names = [topic['topic'] for topic in common_topics]
        assert 'eligibility' in topic_names
        
        # Check urgency analysis
        urgency_analysis = analysis['urgency_analysis']
        assert urgency_analysis['urgent_question_count'] >= 1
        
        # Check insights
        insights = result['insights']
        assert len(insights) > 0
        assert any('question type' in insight for insight in insights)
    
    def test_faq_structure_generation(self):
        """Test comprehensive FAQ structure generation"""
        questions = [
            'How do I enroll in the study?',
            'What are the side effects?',
            'How long will it take?',
            'Am I eligible?',
            'Can I withdraw?',
            'Will I be compensated?',
            'Who can I contact for questions?'
        ]
        
        input_data = {
            'action': 'generate',
            'questions': questions,
            'source_type': 'mixed',
            'format_style': 'clinical',
            'target_audience': 'all'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        
        # Check FAQ structure
        faq_structure = result['faq_structure']
        assert 'title' in faq_structure
        assert 'introduction' in faq_structure
        assert 'categories' in faq_structure
        
        categories = faq_structure['categories']
        assert len(categories) > 0
        
        # Categories should be in logical order
        category_names = [cat['name'] for cat in categories]
        assert 'Eligibility' in category_names or 'General' in category_names
        
        # Each category should have FAQs
        for category in categories:
            assert 'faqs' in category
            assert 'count' in category
            assert len(category['faqs']) == category['count']
    
    def test_different_target_audiences(self):
        """Test FAQ generation for different target audiences"""
        questions = [
            'What is the protocol number for this study?',
            'How should I report adverse events?',
            'What are the inclusion criteria?'
        ]
        
        # Test for investigators
        investigator_input = {
            'action': 'generate',
            'questions': questions,
            'target_audience': 'investigators',
            'format_style': 'clinical'
        }
        
        investigator_result = run(investigator_input)
        assert investigator_result['success'] is True
        
        # Test for participants
        participant_input = {
            'action': 'generate',
            'questions': questions,
            'target_audience': 'participants',
            'format_style': 'friendly'
        }
        
        participant_result = run(participant_input)
        assert participant_result['success'] is True
        
        # Answers should be different for different audiences
        inv_faqs = investigator_result['generated_faqs']
        part_faqs = participant_result['generated_faqs']
        
        # Investigator FAQs should be more clinical
        inv_answers = [faq['answer'] for faq in inv_faqs]
        clinical_terms = any('protocol' in answer.lower() or 'regulatory' in answer.lower() 
                           for answer in inv_answers)
        
        # Participant FAQs should be more friendly
        part_answers = [faq['answer'] for faq in part_faqs]
        friendly_terms = any('we' in answer.lower() or 'you' in answer.lower() 
                           for answer in part_answers)
        
        assert clinical_terms or friendly_terms  # At least one should be appropriate
    
    def test_priority_threshold_filtering(self):
        """Test filtering by priority threshold"""
        questions = [
            {
                'question': 'Low priority question',
                'frequency': 1,
                'priority': 'low'
            },
            {
                'question': 'Medium priority question',
                'frequency': 3,
                'priority': 'medium'
            },
            {
                'question': 'High priority question',
                'frequency': 7,
                'priority': 'high'
            }
        ]
        
        # Test with high threshold (should only include high priority)
        high_threshold_input = {
            'action': 'generate',
            'questions': questions,
            'priority_threshold': 5
        }
        
        high_result = run(high_threshold_input)
        assert high_result['success'] is True
        
        # Should only include high frequency/priority questions
        high_faqs = high_result['generated_faqs']
        high_freq_faqs = [f for f in high_faqs if f.get('frequency', 0) >= 5]
        
        # Most FAQs should meet the threshold
        assert len(high_freq_faqs) >= len(high_faqs) // 2
    
    def test_comprehensive_faq_workflow(self):
        """Test comprehensive FAQ generation workflow"""
        # Step 1: Generate FAQs
        questions = [
            {'question': 'How do I enroll?', 'frequency': 5, 'source': 'participant_feedback'},
            {'question': 'What are the risks?', 'frequency': 8, 'source': 'safety_concern'},
            {'question': 'How long is the study?', 'frequency': 3, 'source': 'general_inquiry'},
            {'question': 'Can I bring a family member?', 'frequency': 2, 'source': 'participant_feedback'},
            {'question': 'What compensation is provided?', 'frequency': 6, 'source': 'enrollment_question'}
        ]
        
        generate_input = {
            'action': 'generate',
            'questions': questions,
            'categorization': True,
            'format_style': 'detailed',
            'target_audience': 'participants',
            'priority_threshold': 2
        }
        
        generate_result = run(generate_input)
        assert generate_result['success'] is True
        
        generated_faqs = generate_result['generated_faqs']
        
        # Step 2: Analyze the questions
        analyze_input = {
            'action': 'analyze',
            'questions': questions
        }
        
        analyze_result = run(analyze_input)
        assert analyze_result['success'] is True
        
        # Step 3: Format the FAQs
        format_input = {
            'action': 'format',
            'existing_faqs': generated_faqs,
            'format_style': 'detailed',
            'target_audience': 'participants'
        }
        
        format_result = run(format_input)
        assert format_result['success'] is True
        
        # Verify workflow results
        assert len(generated_faqs) >= 3
        assert 'analysis' in analyze_result
        assert 'formatted_faqs' in format_result
        
        # Check that high-priority items were included
        high_priority_faqs = [f for f in generated_faqs if f.get('priority') == 'high']
        assert len(high_priority_faqs) > 0
        
        # Check formatting quality
        formatted_output = format_result['formatted_faqs']
        assert 'html' in formatted_output
        assert 'markdown' in formatted_output
        assert len(formatted_output['html']) > 500  # Should be substantial
    
    def test_error_handling_invalid_action(self):
        """Test error handling for invalid action"""
        input_data = {
            'action': 'invalid_action',
            'questions': []
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'Unknown action' in result['error']
        assert 'valid_actions' in result
    
    def test_error_handling_empty_questions(self):
        """Test handling of empty questions list"""
        input_data = {
            'action': 'generate',
            'questions': []
        }
        
        result = run(input_data)
        
        # Should handle gracefully
        assert result['success'] is True
        assert result['statistics']['total_faqs'] == 0