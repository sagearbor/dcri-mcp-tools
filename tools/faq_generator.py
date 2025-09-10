"""
FAQ Generator Tool for Clinical Studies
Generates FAQs from study queries, issues, and common questions
"""

import re
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
from collections import Counter


def run(input_data: Dict) -> Dict:
    """
    Generate FAQs from study queries and issues.
    
    Example:
        Input: List of participant questions where "Am I eligible?" was asked 15 times and "How long does it take?" was asked 12 times
        Output: Categorized FAQ document with answers in participant-friendly format
    
    Parameters:
        action : str
            'generate', 'categorize', 'update', 'format', or 'analyze'
        questions : list
            List of questions/issues with frequency counts
        target_audience : str
            'participants', 'investigators', 'staff', or 'all'
        format_style : str
            'simple', 'detailed', 'clinical', or 'participant'
        source_type : str, optional
            'queries', 'issues', 'feedback', or 'mixed'
        categorization : bool, optional
            Auto-categorize questions (default: True)
        priority_threshold : int, optional
            Minimum frequency for inclusion (default: 2)
        existing_faqs : list, optional
            Current FAQ list for updates
    """
    try:
        action = input_data.get('action', 'generate').lower()
        questions = input_data.get('questions', [])
        existing_faqs = input_data.get('existing_faqs', [])
        source_type = input_data.get('source_type', 'mixed')
        categorization = input_data.get('categorization', True)
        format_style = input_data.get('format_style', 'simple')
        priority_threshold = input_data.get('priority_threshold', 2)
        target_audience = input_data.get('target_audience', 'all')
        
        result = {'success': True, 'action': action}
        
        if action == 'generate':
            result.update(_generate_faqs(questions, source_type, categorization, 
                                       format_style, priority_threshold, target_audience))
        elif action == 'categorize':
            result.update(_categorize_questions(questions))
        elif action == 'update':
            result.update(_update_existing_faqs(existing_faqs, questions))
        elif action == 'format':
            result.update(_format_faqs(existing_faqs, format_style, target_audience))
        elif action == 'analyze':
            result.update(_analyze_questions(questions))
        else:
            return {
                'success': False,
                'error': f'Unknown action: {action}',
                'valid_actions': ['generate', 'categorize', 'update', 'format', 'analyze']
            }
        
        # Add metadata
        result['metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'source_type': source_type,
            'target_audience': target_audience,
            'questions_processed': len(questions)
        }
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error generating FAQs: {str(e)}'
        }


def _generate_faqs(questions: List[Dict], source_type: str, categorization: bool,
                  format_style: str, priority_threshold: int, target_audience: str) -> Dict:
    """Generate FAQs from questions and issues."""
    # Process input questions
    processed_questions = _process_input_questions(questions)
    
    # Group similar questions
    grouped_questions = _group_similar_questions(processed_questions, priority_threshold)
    
    # Generate answers for each group
    faq_items = []
    for group in grouped_questions:
        faq_item = _generate_faq_item(group, format_style, target_audience)
        if faq_item:
            faq_items.append(faq_item)
    
    # Categorize if requested
    if categorization:
        faq_items = _add_categories_to_faqs(faq_items)
    
    # Sort by priority and category
    faq_items = _sort_faqs(faq_items)
    
    # Generate FAQ structure
    faq_structure = _create_faq_structure(faq_items, format_style, target_audience)
    
    return {
        'generated_faqs': faq_items,
        'faq_structure': faq_structure,
        'statistics': {
            'total_faqs': len(faq_items),
            'categories_created': len(set(faq.get('category', 'General') for faq in faq_items)),
            'questions_grouped': len(processed_questions),
            'priority_questions': len([faq for faq in faq_items if faq.get('priority', 'medium') == 'high'])
        },
        'recommendations': _generate_faq_recommendations(faq_items, source_type)
    }


def _categorize_questions(questions: List[Dict]) -> Dict:
    """Categorize questions automatically."""
    categorized = []
    category_stats = {}
    
    for question in questions:
        question_text = _extract_question_text(question)
        category = _determine_question_category(question_text)
        
        categorized_question = question.copy() if isinstance(question, dict) else {'question': question}
        categorized_question['category'] = category
        categorized_question['confidence'] = _calculate_categorization_confidence(question_text, category)
        
        categorized.append(categorized_question)
        
        category_stats[category] = category_stats.get(category, 0) + 1
    
    return {
        'categorized_questions': categorized,
        'category_statistics': category_stats,
        'categorization_summary': _generate_categorization_summary(category_stats)
    }


def _update_existing_faqs(existing_faqs: List[Dict], new_questions: List[Dict]) -> Dict:
    """Update existing FAQs with new questions."""
    updated_faqs = existing_faqs.copy()
    new_faq_items = []
    updated_items = []
    
    # Process new questions
    processed_questions = _process_input_questions(new_questions)
    
    for question_data in processed_questions:
        question_text = question_data['text']
        
        # Check if question matches existing FAQ
        matching_faq = _find_matching_faq(question_text, existing_faqs)
        
        if matching_faq:
            # Update existing FAQ
            updated_faq = _update_faq_item(matching_faq, question_data)
            # Replace in list
            for i, faq in enumerate(updated_faqs):
                if faq.get('id') == matching_faq.get('id'):
                    updated_faqs[i] = updated_faq
                    updated_items.append(updated_faq)
                    break
        else:
            # Create new FAQ
            new_faq = _create_new_faq_from_question(question_data)
            updated_faqs.append(new_faq)
            new_faq_items.append(new_faq)
    
    return {
        'updated_faqs': updated_faqs,
        'new_items': new_faq_items,
        'updated_items': updated_items,
        'summary': {
            'total_faqs': len(updated_faqs),
            'new_faqs_added': len(new_faq_items),
            'existing_faqs_updated': len(updated_items)
        }
    }


def _format_faqs(faqs: List[Dict], format_style: str, target_audience: str) -> Dict:
    """Format FAQs in specified style."""
    formatted_output = {
        'html': _format_faqs_html(faqs, target_audience),
        'markdown': _format_faqs_markdown(faqs, target_audience),
        'json': _format_faqs_json(faqs),
        'text': _format_faqs_text(faqs, target_audience),
        'pdf_ready': _format_faqs_pdf_ready(faqs, target_audience)
    }
    
    return {
        'formatted_faqs': formatted_output,
        'format_style': format_style,
        'target_audience': target_audience,
        'formatting_notes': _get_formatting_notes(format_style, target_audience)
    }


def _analyze_questions(questions: List[Dict]) -> Dict:
    """Analyze question patterns and trends."""
    processed_questions = _process_input_questions(questions)
    
    analysis = {
        'question_types': _analyze_question_types(processed_questions),
        'common_topics': _identify_common_topics(processed_questions),
        'complexity_analysis': _analyze_question_complexity(processed_questions),
        'temporal_patterns': _analyze_temporal_patterns(processed_questions),
        'urgency_analysis': _analyze_question_urgency(processed_questions)
    }
    
    insights = _generate_analysis_insights(analysis)
    recommendations = _generate_analysis_recommendations(analysis)
    
    return {
        'analysis': analysis,
        'insights': insights,
        'recommendations': recommendations,
        'summary': _create_analysis_summary(analysis)
    }


def _process_input_questions(questions: List) -> List[Dict]:
    """Process and standardize input questions."""
    processed = []
    
    for i, question in enumerate(questions):
        if isinstance(question, str):
            # Simple string question
            processed_q = {
                'id': f'q_{i+1}',
                'text': question,
                'source': 'unknown',
                'timestamp': datetime.now().isoformat(),
                'frequency': 1
            }
        elif isinstance(question, dict):
            # Dictionary question with metadata
            processed_q = {
                'id': question.get('id', f'q_{i+1}'),
                'text': question.get('question', question.get('text', '')),
                'source': question.get('source', 'unknown'),
                'timestamp': question.get('timestamp', datetime.now().isoformat()),
                'frequency': question.get('frequency', question.get('count', 1)),
                'category': question.get('category', ''),
                'priority': question.get('priority', 'medium'),
                'metadata': question.get('metadata', {})
            }
        else:
            continue
        
        if processed_q['text']:  # Only add if there's actual question text
            processed.append(processed_q)
    
    return processed


def _group_similar_questions(questions: List[Dict], threshold: int) -> List[List[Dict]]:
    """Group similar questions together."""
    from difflib import SequenceMatcher
    
    groups = []
    ungrouped_questions = questions.copy()
    
    while ungrouped_questions:
        current_question = ungrouped_questions.pop(0)
        current_group = [current_question]
        
        # Find similar questions
        to_remove = []
        for i, question in enumerate(ungrouped_questions):
            similarity = SequenceMatcher(
                None, 
                current_question['text'].lower(), 
                question['text'].lower()
            ).ratio()
            
            if similarity > 0.7:  # 70% similarity threshold
                current_group.append(question)
                to_remove.append(i)
        
        # Remove grouped questions
        for i in reversed(to_remove):
            ungrouped_questions.pop(i)
        
        # Only include groups that meet frequency threshold
        total_frequency = sum(q['frequency'] for q in current_group)
        if total_frequency >= threshold:
            groups.append(current_group)
    
    return groups


def _generate_faq_item(question_group: List[Dict], format_style: str, target_audience: str) -> Dict:
    """Generate a single FAQ item from a group of questions."""
    # Select the most representative question
    main_question = max(question_group, key=lambda x: x['frequency'])
    
    # Generate comprehensive answer
    answer = _generate_answer_for_question(main_question['text'], format_style, target_audience)
    
    # Calculate priority
    total_frequency = sum(q['frequency'] for q in question_group)
    priority = _calculate_faq_priority(total_frequency, main_question.get('source', ''))
    
    # Determine category
    category = _determine_question_category(main_question['text'])
    
    faq_item = {
        'id': f"faq_{main_question['id']}",
        'question': _refine_question_text(main_question['text']),
        'answer': answer,
        'category': category,
        'priority': priority,
        'frequency': total_frequency,
        'related_questions': [q['text'] for q in question_group if q != main_question],
        'sources': list(set(q['source'] for q in question_group)),
        'last_updated': datetime.now().isoformat(),
        'target_audience': _determine_faq_audience(main_question['text'], target_audience),
        'tags': _extract_question_tags(main_question['text'])
    }
    
    return faq_item


def _determine_question_category(question_text: str) -> str:
    """Determine the category of a question based on its content."""
    question_lower = question_text.lower()
    
    # Define category patterns
    categories = {
        'Eligibility': [
            'eligible', 'qualify', 'inclusion', 'exclusion', 'criteria', 'requirements',
            'can i participate', 'am i eligible', 'do i qualify'
        ],
        'Study Procedures': [
            'procedures', 'visits', 'tests', 'examinations', 'blood draw', 'scan',
            'what happens', 'what will', 'during the study', 'appointment'
        ],
        'Safety': [
            'safe', 'safety', 'risk', 'side effect', 'adverse', 'harm', 'danger',
            'what are the risks', 'is it safe'
        ],
        'Time Commitment': [
            'time', 'duration', 'how long', 'schedule', 'frequency', 'visits',
            'commitment', 'hours', 'days', 'weeks', 'months'
        ],
        'Compensation': [
            'compensation', 'payment', 'reimbursement', 'money', 'paid',
            'travel expenses', 'parking'
        ],
        'Withdrawal': [
            'withdraw', 'quit', 'stop', 'leave', 'drop out', 'discontinue',
            'can i stop', 'what if i want to quit'
        ],
        'Confidentiality': [
            'confidential', 'privacy', 'personal information', 'data', 'records',
            'who will know', 'information shared'
        ],
        'Results': [
            'results', 'findings', 'outcomes', 'will i know', 'get results',
            'what happens to the data'
        ],
        'Contact Information': [
            'contact', 'questions', 'who do i call', 'phone number', 'email',
            'how to reach', 'need help'
        ]
    }
    
    # Score each category
    category_scores = {}
    for category, keywords in categories.items():
        score = sum(1 for keyword in keywords if keyword in question_lower)
        if score > 0:
            category_scores[category] = score
    
    if category_scores:
        return max(category_scores, key=category_scores.get)
    else:
        return 'General'


def _generate_answer_for_question(question: str, format_style: str, target_audience: str) -> str:
    """Generate an answer for a question based on common patterns."""
    question_lower = question.lower()
    
    # Template answers based on question patterns
    answer_templates = {
        'eligibility': {
            'simple': "To participate in this study, you must meet specific criteria. Please contact the study team to discuss your eligibility in detail.",
            'detailed': "Study participation requires meeting inclusion and exclusion criteria designed to ensure participant safety and study validity. Eligibility is determined through screening procedures that may include medical history review, physical examination, and laboratory tests.",
            'clinical': "Refer to the protocol inclusion/exclusion criteria. Screening procedures will determine eligibility based on medical history, current medications, and relevant clinical parameters.",
            'participant': "We'd be happy to discuss whether this study might be right for you. Our study team will review your medical history and current health status to determine if you meet the study requirements."
        },
        'safety': {
            'simple': "All study procedures are designed with participant safety as the top priority. Any potential risks will be explained to you in detail.",
            'detailed': "Study safety is ensured through rigorous protocol design, regular safety monitoring, and immediate reporting of any adverse events. All procedures follow established medical standards and regulatory guidelines.",
            'clinical': "Safety monitoring includes regular assessment of vital signs, laboratory values, and adverse event reporting per protocol specifications and regulatory requirements.",
            'participant': "Your safety is our highest priority. We carefully monitor all participants throughout the study and will explain any potential risks before you decide to participate."
        },
        'procedures': {
            'simple': "The study involves regular visits where we'll perform various assessments. The exact procedures will be explained during your consent process.",
            'detailed': "Study procedures are specified in the protocol and may include medical examinations, laboratory tests, imaging studies, questionnaires, and other assessments relevant to the study objectives.",
            'clinical': "Refer to the protocol schedule of events for specific procedures, timing, and visit windows. All procedures should be performed according to protocol specifications.",
            'participant': "During your study visits, we'll perform various tests and assessments. Everything will be explained to you step-by-step, and you can ask questions at any time."
        },
        'time_commitment': {
            'simple': "The time commitment varies by study. We'll provide you with a detailed schedule of all required visits and procedures.",
            'detailed': "Study duration and visit frequency are specified in the protocol. Participants should plan for the full study duration including follow-up periods as outlined in the consent form.",
            'clinical': "Refer to protocol schedule of events for visit timing, duration, and required procedures. Ensure participants understand the full time commitment before enrollment.",
            'participant': "We understand your time is valuable. We'll work with you to schedule visits at convenient times and provide clear information about the time commitment involved."
        },
        'compensation': {
            'simple': "Information about compensation for your time and any study-related expenses will be provided during the consent process.",
            'detailed': "Compensation policies vary by institution and study. Participants may receive reimbursement for time, travel, parking, and other study-related expenses as outlined in the informed consent.",
            'clinical': "Refer to institutional policies and informed consent form for specific compensation amounts and reimbursement procedures.",
            'participant': "We appreciate the time you're volunteering for research. Details about any compensation or reimbursement for study-related expenses will be explained before you enroll."
        },
        'withdrawal': {
            'simple': "You can withdraw from the study at any time for any reason without penalty or loss of benefits.",
            'detailed': "Withdrawal from research is a fundamental right. Participants may discontinue at any time without affecting their medical care or legal rights, though safety follow-up may be required.",
            'clinical': "Document all withdrawals appropriately, ensure proper safety follow-up as per protocol, and maintain participant confidentiality per regulatory requirements.",
            'participant': "Participating in this study is completely voluntary. You can change your mind and stop participating at any time, for any reason, without any negative consequences to your medical care."
        }
    }
    
    # Determine answer type based on question content
    if any(word in question_lower for word in ['eligible', 'qualify', 'criteria']):
        answer_type = 'eligibility'
    elif any(word in question_lower for word in ['safe', 'risk', 'side effect']):
        answer_type = 'safety'
    elif any(word in question_lower for word in ['procedures', 'tests', 'what happens']):
        answer_type = 'procedures'
    elif any(word in question_lower for word in ['time', 'how long', 'duration']):
        answer_type = 'time_commitment'
    elif any(word in question_lower for word in ['compensation', 'paid', 'reimbursement']):
        answer_type = 'compensation'
    elif any(word in question_lower for word in ['withdraw', 'quit', 'stop']):
        answer_type = 'withdrawal'
    else:
        # Default answer
        return "Thank you for your question. Please contact the study team for detailed information specific to your situation."
    
    # Get appropriate answer template
    if answer_type in answer_templates and format_style in answer_templates[answer_type]:
        base_answer = answer_templates[answer_type][format_style]
    else:
        base_answer = answer_templates[answer_type]['simple']
    
    # Add contact information footer
    if target_audience in ['participants', 'all']:
        base_answer += "\n\nIf you have additional questions, please contact the study team at [CONTACT_INFORMATION]."
    
    return base_answer


def _calculate_faq_priority(frequency: int, source: str) -> str:
    """Calculate priority level for FAQ."""
    base_score = frequency
    
    # Adjust based on source
    source_weights = {
        'participant_feedback': 1.5,
        'investigator_query': 1.3,
        'regulatory_question': 1.8,
        'safety_concern': 2.0,
        'enrollment_issue': 1.4
    }
    
    weighted_score = base_score * source_weights.get(source, 1.0)
    
    if weighted_score >= 10:
        return 'high'
    elif weighted_score >= 5:
        return 'medium'
    else:
        return 'low'


def _refine_question_text(question: str) -> str:
    """Refine question text for better readability."""
    # Clean up question
    refined = question.strip()
    
    # Ensure it ends with question mark
    if not refined.endswith('?'):
        refined += '?'
    
    # Capitalize first letter
    if refined:
        refined = refined[0].upper() + refined[1:]
    
    # Remove redundant spaces
    refined = re.sub(r'\s+', ' ', refined)
    
    return refined


def _add_categories_to_faqs(faq_items: List[Dict]) -> List[Dict]:
    """Add categories to FAQ items if not already present."""
    for faq in faq_items:
        if not faq.get('category'):
            faq['category'] = _determine_question_category(faq['question'])
    return faq_items


def _sort_faqs(faq_items: List[Dict]) -> List[Dict]:
    """Sort FAQs by priority and category."""
    priority_order = {'high': 3, 'medium': 2, 'low': 1}
    
    return sorted(faq_items, key=lambda x: (
        priority_order.get(x.get('priority', 'medium'), 2),
        x.get('category', 'General'),
        -x.get('frequency', 1)
    ), reverse=True)


def _create_faq_structure(faq_items: List[Dict], format_style: str, target_audience: str) -> Dict:
    """Create structured FAQ organization."""
    # Group by category
    categories = {}
    for faq in faq_items:
        category = faq.get('category', 'General')
        if category not in categories:
            categories[category] = []
        categories[category].append(faq)
    
    # Create structure
    structure = {
        'title': _get_faq_title(target_audience),
        'introduction': _get_faq_introduction(target_audience),
        'categories': []
    }
    
    # Order categories by importance
    category_order = [
        'Eligibility', 'Study Procedures', 'Safety', 'Time Commitment',
        'Compensation', 'Withdrawal', 'Confidentiality', 'Results',
        'Contact Information', 'General'
    ]
    
    for category in category_order:
        if category in categories:
            structure['categories'].append({
                'name': category,
                'faqs': categories[category],
                'count': len(categories[category])
            })
    
    # Add any remaining categories
    for category, faqs in categories.items():
        if category not in category_order:
            structure['categories'].append({
                'name': category,
                'faqs': faqs,
                'count': len(faqs)
            })
    
    return structure


def _find_matching_faq(question: str, existing_faqs: List[Dict]) -> Optional[Dict]:
    """Find existing FAQ that matches the question."""
    from difflib import SequenceMatcher
    
    best_match = None
    best_similarity = 0.0
    
    for faq in existing_faqs:
        existing_question = faq.get('question', '')
        similarity = SequenceMatcher(None, question.lower(), existing_question.lower()).ratio()
        
        if similarity > best_similarity and similarity > 0.8:  # 80% similarity threshold
            best_similarity = similarity
            best_match = faq
    
    return best_match


def _update_faq_item(existing_faq: Dict, new_question: Dict) -> Dict:
    """Update existing FAQ with new question data."""
    updated_faq = existing_faq.copy()
    
    # Increase frequency
    updated_faq['frequency'] = updated_faq.get('frequency', 1) + new_question.get('frequency', 1)
    
    # Add to related questions if different
    if new_question['text'] not in updated_faq.get('related_questions', []):
        if 'related_questions' not in updated_faq:
            updated_faq['related_questions'] = []
        updated_faq['related_questions'].append(new_question['text'])
    
    # Update timestamp
    updated_faq['last_updated'] = datetime.now().isoformat()
    
    # Add new sources
    if 'sources' not in updated_faq:
        updated_faq['sources'] = []
    if new_question['source'] not in updated_faq['sources']:
        updated_faq['sources'].append(new_question['source'])
    
    return updated_faq


def _create_new_faq_from_question(question_data: Dict) -> Dict:
    """Create new FAQ from question data."""
    return {
        'id': f"faq_{question_data['id']}",
        'question': _refine_question_text(question_data['text']),
        'answer': _generate_answer_for_question(question_data['text'], 'simple', 'all'),
        'category': _determine_question_category(question_data['text']),
        'priority': _calculate_faq_priority(question_data.get('frequency', 1), question_data.get('source', 'unknown')),
        'frequency': question_data.get('frequency', 1),
        'sources': [question_data.get('source', 'unknown')],
        'last_updated': datetime.now().isoformat(),
        'tags': _extract_question_tags(question_data['text'])
    }


def _format_faqs_html(faqs: List[Dict], target_audience: str) -> str:
    """Format FAQs as HTML."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{_get_faq_title(target_audience)}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            .faq-section {{ margin-bottom: 30px; }}
            .category {{ background-color: #f8f9fa; padding: 15px; margin-bottom: 20px; border-left: 4px solid #007cba; }}
            .category-title {{ font-size: 1.3em; font-weight: bold; color: #007cba; margin-bottom: 10px; }}
            .faq-item {{ margin-bottom: 15px; padding: 10px; border: 1px solid #e0e0e0; border-radius: 5px; }}
            .question {{ font-weight: bold; color: #333; margin-bottom: 8px; }}
            .answer {{ color: #555; }}
            .priority-high {{ border-left: 4px solid #dc3545; }}
            .priority-medium {{ border-left: 4px solid #ffc107; }}
            .priority-low {{ border-left: 4px solid #28a745; }}
        </style>
    </head>
    <body>
        <h1>{_get_faq_title(target_audience)}</h1>
        <div class="introduction">{_get_faq_introduction(target_audience)}</div>
    """
    
    # Group by category
    categories = {}
    for faq in faqs:
        category = faq.get('category', 'General')
        if category not in categories:
            categories[category] = []
        categories[category].append(faq)
    
    # Generate HTML for each category
    for category, category_faqs in categories.items():
        html += f"""
        <div class="faq-section">
            <div class="category">
                <div class="category-title">{category}</div>
        """
        
        for faq in category_faqs:
            priority_class = f"priority-{faq.get('priority', 'medium')}"
            html += f"""
                <div class="faq-item {priority_class}">
                    <div class="question">{faq.get('question', '')}</div>
                    <div class="answer">{faq.get('answer', '')}</div>
                </div>
            """
        
        html += "</div></div>"
    
    html += """
    </body>
    </html>
    """
    
    return html


def _format_faqs_markdown(faqs: List[Dict], target_audience: str) -> str:
    """Format FAQs as Markdown."""
    markdown = f"# {_get_faq_title(target_audience)}\n\n"
    markdown += f"{_get_faq_introduction(target_audience)}\n\n"
    
    # Group by category
    categories = {}
    for faq in faqs:
        category = faq.get('category', 'General')
        if category not in categories:
            categories[category] = []
        categories[category].append(faq)
    
    # Generate Markdown for each category
    for category, category_faqs in categories.items():
        markdown += f"## {category}\n\n"
        
        for i, faq in enumerate(category_faqs, 1):
            priority_indicator = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(faq.get('priority', 'medium'), '🟡')
            
            markdown += f"{i}. **{faq.get('question', '')}** {priority_indicator}\n\n"
            markdown += f"   {faq.get('answer', '')}\n\n"
    
    return markdown


def _format_faqs_json(faqs: List[Dict]) -> str:
    """Format FAQs as JSON."""
    return json.dumps(faqs, indent=2, default=str)


def _format_faqs_text(faqs: List[Dict], target_audience: str) -> str:
    """Format FAQs as plain text."""
    text = f"{_get_faq_title(target_audience)}\n"
    text += "=" * len(_get_faq_title(target_audience)) + "\n\n"
    text += f"{_get_faq_introduction(target_audience)}\n\n"
    
    # Group by category
    categories = {}
    for faq in faqs:
        category = faq.get('category', 'General')
        if category not in categories:
            categories[category] = []
        categories[category].append(faq)
    
    # Generate text for each category
    for category, category_faqs in categories.items():
        text += f"{category}\n"
        text += "-" * len(category) + "\n\n"
        
        for i, faq in enumerate(category_faqs, 1):
            text += f"Q{i}: {faq.get('question', '')}\n"
            text += f"A{i}: {faq.get('answer', '')}\n\n"
    
    return text


def _format_faqs_pdf_ready(faqs: List[Dict], target_audience: str) -> str:
    """Format FAQs ready for PDF conversion."""
    # This returns HTML that's optimized for PDF conversion
    return _format_faqs_html(faqs, target_audience).replace(
        '<style>',
        '<style>@media print { .no-print { display: none; } } '
    )


def _analyze_question_types(questions: List[Dict]) -> Dict:
    """Analyze types of questions."""
    question_types = {
        'yes_no': 0,
        'what': 0,
        'how': 0,
        'when': 0,
        'where': 0,
        'why': 0,
        'who': 0,
        'other': 0
    }
    
    for q in questions:
        text = q['text'].lower()
        if any(word in text for word in ['can i', 'will i', 'do i', 'am i', 'is it']):
            question_types['yes_no'] += 1
        elif text.startswith('what'):
            question_types['what'] += 1
        elif text.startswith('how'):
            question_types['how'] += 1
        elif text.startswith('when'):
            question_types['when'] += 1
        elif text.startswith('where'):
            question_types['where'] += 1
        elif text.startswith('why'):
            question_types['why'] += 1
        elif text.startswith('who'):
            question_types['who'] += 1
        else:
            question_types['other'] += 1
    
    return question_types


def _identify_common_topics(questions: List[Dict]) -> List[Dict]:
    """Identify common topics in questions."""
    # Extract keywords from all questions
    all_text = ' '.join([q['text'].lower() for q in questions])
    
    # Define topic keywords
    topics = {
        'eligibility': ['eligible', 'qualify', 'criteria', 'inclusion', 'exclusion'],
        'safety': ['safe', 'risk', 'side effect', 'adverse', 'harm'],
        'procedures': ['procedure', 'test', 'visit', 'examination', 'blood'],
        'time': ['time', 'duration', 'long', 'schedule', 'appointment'],
        'compensation': ['pay', 'compensation', 'reimbursement', 'money'],
        'withdrawal': ['withdraw', 'quit', 'stop', 'leave', 'drop out'],
        'confidentiality': ['confidential', 'privacy', 'information', 'data']
    }
    
    topic_scores = []
    for topic, keywords in topics.items():
        score = sum(all_text.count(keyword) for keyword in keywords)
        if score > 0:
            topic_scores.append({
                'topic': topic,
                'frequency': score,
                'keywords': keywords
            })
    
    return sorted(topic_scores, key=lambda x: x['frequency'], reverse=True)


def _analyze_question_complexity(questions: List[Dict]) -> Dict:
    """Analyze complexity of questions."""
    complexity_scores = []
    
    for q in questions:
        text = q['text']
        
        # Simple complexity metrics
        word_count = len(text.split())
        sentence_count = text.count('.') + text.count('?') + text.count('!')
        avg_word_length = sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0
        
        # Complexity indicators
        complex_indicators = len(re.findall(r'\b(however|moreover|furthermore|nevertheless|specifically|particularly)\b', text.lower()))
        
        complexity_score = word_count * 0.3 + avg_word_length * 0.5 + complex_indicators * 2
        
        complexity_scores.append({
            'question_id': q['id'],
            'complexity_score': complexity_score,
            'word_count': word_count,
            'sentence_count': sentence_count
        })
    
    # Categorize complexity
    avg_complexity = sum(c['complexity_score'] for c in complexity_scores) / len(complexity_scores)
    
    return {
        'average_complexity': avg_complexity,
        'simple_questions': len([c for c in complexity_scores if c['complexity_score'] < avg_complexity * 0.7]),
        'moderate_questions': len([c for c in complexity_scores if avg_complexity * 0.7 <= c['complexity_score'] <= avg_complexity * 1.3]),
        'complex_questions': len([c for c in complexity_scores if c['complexity_score'] > avg_complexity * 1.3]),
        'complexity_details': complexity_scores
    }


def _analyze_temporal_patterns(questions: List[Dict]) -> Dict:
    """Analyze temporal patterns in questions."""
    # This is simplified - in practice you'd analyze actual timestamps
    return {
        'peak_question_periods': ['enrollment_phase', 'mid_study'],
        'question_volume_trend': 'increasing',
        'seasonal_patterns': 'none_detected'
    }


def _analyze_question_urgency(questions: List[Dict]) -> Dict:
    """Analyze urgency indicators in questions."""
    urgent_keywords = ['urgent', 'emergency', 'immediate', 'asap', 'quickly', 'right away']
    
    urgent_questions = []
    for q in questions:
        urgency_score = sum(1 for keyword in urgent_keywords if keyword in q['text'].lower())
        if urgency_score > 0:
            urgent_questions.append({
                'question_id': q['id'],
                'urgency_score': urgency_score,
                'text': q['text']
            })
    
    return {
        'urgent_question_count': len(urgent_questions),
        'urgent_questions': urgent_questions,
        'urgency_percentage': len(urgent_questions) / len(questions) * 100 if questions else 0
    }


def _extract_question_text(question) -> str:
    """Extract question text from various input formats."""
    if isinstance(question, str):
        return question
    elif isinstance(question, dict):
        return question.get('question', question.get('text', ''))
    else:
        return str(question)


def _calculate_categorization_confidence(question_text: str, category: str) -> float:
    """Calculate confidence in categorization."""
    # This would be more sophisticated in practice
    return 0.85  # Placeholder confidence score


def _determine_faq_audience(question_text: str, default_audience: str) -> str:
    """Determine target audience for FAQ."""
    question_lower = question_text.lower()
    
    if any(term in question_lower for term in ['protocol', 'regulatory', 'irb', 'compliance']):
        return 'investigators'
    elif any(term in question_lower for term in ['can i', 'will i', 'my experience']):
        return 'participants'
    else:
        return default_audience


def _extract_question_tags(question_text: str) -> List[str]:
    """Extract tags from question text."""
    tags = []
    question_lower = question_text.lower()
    
    tag_keywords = {
        'safety': ['safe', 'risk', 'side effect'],
        'eligibility': ['eligible', 'qualify', 'criteria'],
        'procedures': ['procedure', 'test', 'visit'],
        'time': ['time', 'duration', 'schedule'],
        'compensation': ['pay', 'compensation', 'money']
    }
    
    for tag, keywords in tag_keywords.items():
        if any(keyword in question_lower for keyword in keywords):
            tags.append(tag)
    
    return tags


def _generate_faq_recommendations(faq_items: List[Dict], source_type: str) -> List[str]:
    """Generate recommendations for FAQ management."""
    recommendations = []
    
    if len(faq_items) > 20:
        recommendations.append("Consider organizing FAQs into subcategories for better navigation")
    
    high_priority_count = len([faq for faq in faq_items if faq.get('priority') == 'high'])
    if high_priority_count > 5:
        recommendations.append(f"Address {high_priority_count} high-priority questions promptly")
    
    if source_type == 'participant_feedback':
        recommendations.append("Consider participant-friendly language and clear explanations")
    
    categories = set(faq.get('category', 'General') for faq in faq_items)
    if len(categories) < 3:
        recommendations.append("Review question categorization to ensure comprehensive coverage")
    
    return recommendations


def _generate_categorization_summary(category_stats: Dict) -> str:
    """Generate summary of categorization results."""
    total_questions = sum(category_stats.values())
    most_common = max(category_stats.items(), key=lambda x: x[1])
    
    return f"Categorized {total_questions} questions across {len(category_stats)} categories. Most common category: {most_common[0]} ({most_common[1]} questions)"


def _generate_analysis_insights(analysis: Dict) -> List[str]:
    """Generate insights from question analysis."""
    insights = []
    
    question_types = analysis.get('question_types', {})
    most_common_type = max(question_types.items(), key=lambda x: x[1]) if question_types else ('unknown', 0)
    insights.append(f"Most common question type: {most_common_type[0]} ({most_common_type[1]} questions)")
    
    common_topics = analysis.get('common_topics', [])
    if common_topics:
        top_topic = common_topics[0]
        insights.append(f"Top concern: {top_topic['topic']} (mentioned {top_topic['frequency']} times)")
    
    complexity = analysis.get('complexity_analysis', {})
    complex_count = complexity.get('complex_questions', 0)
    if complex_count > 0:
        insights.append(f"{complex_count} questions identified as complex, may need detailed responses")
    
    urgency = analysis.get('urgency_analysis', {})
    urgent_count = urgency.get('urgent_question_count', 0)
    if urgent_count > 0:
        insights.append(f"{urgent_count} questions contain urgency indicators, prioritize for response")
    
    return insights


def _generate_analysis_recommendations(analysis: Dict) -> List[str]:
    """Generate recommendations from question analysis."""
    recommendations = []
    
    question_types = analysis.get('question_types', {})
    yes_no_count = question_types.get('yes_no', 0)
    if yes_no_count > len(question_types) * 0.4:  # More than 40% are yes/no
        recommendations.append("Many yes/no questions suggest need for clearer eligibility information")
    
    common_topics = analysis.get('common_topics', [])
    if common_topics:
        top_topics = [topic['topic'] for topic in common_topics[:3]]
        recommendations.append(f"Focus FAQ development on: {', '.join(top_topics)}")
    
    urgency = analysis.get('urgency_analysis', {})
    if urgency.get('urgency_percentage', 0) > 10:
        recommendations.append("High urgency question rate suggests need for faster response protocols")
    
    return recommendations


def _create_analysis_summary(analysis: Dict) -> str:
    """Create summary of question analysis."""
    question_types = analysis.get('question_types', {})
    total_questions = sum(question_types.values())
    
    common_topics = analysis.get('common_topics', [])
    top_topic = common_topics[0]['topic'] if common_topics else 'none identified'
    
    return f"Analyzed {total_questions} questions. Top concern: {top_topic}. Complexity: varied. Urgency: {analysis.get('urgency_analysis', {}).get('urgent_question_count', 0)} urgent questions identified."


def _get_faq_title(target_audience: str) -> str:
    """Get appropriate title for FAQ."""
    titles = {
        'participants': 'Frequently Asked Questions for Study Participants',
        'investigators': 'Investigator FAQ - Study Protocol Questions',
        'staff': 'Study Staff FAQ - Operational Questions',
        'all': 'Study FAQ - Common Questions and Answers'
    }
    return titles.get(target_audience, titles['all'])


def _get_faq_introduction(target_audience: str) -> str:
    """Get appropriate introduction for FAQ."""
    introductions = {
        'participants': 'This document answers common questions from study participants. If you have additional questions, please contact the study team.',
        'investigators': 'This FAQ addresses common protocol and operational questions from study investigators and site staff.',
        'staff': 'This document provides answers to frequently asked operational questions from study staff.',
        'all': 'This FAQ addresses common questions about the study. Please contact the study team if you need additional information.'
    }
    return introductions.get(target_audience, introductions['all'])


def _get_formatting_notes(format_style: str, target_audience: str) -> List[str]:
    """Get formatting notes."""
    notes = []
    
    if format_style == 'clinical':
        notes.append("Formatted with clinical terminology for medical professionals")
    elif format_style == 'participant':
        notes.append("Formatted with plain language for study participants")
    
    if target_audience == 'participants':
        notes.append("Content tailored for participant understanding")
    
    notes.append("Review all answers for accuracy and completeness before distribution")
    
    return notes