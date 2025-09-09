"""
Meeting Minutes Generator Tool for Clinical Studies
Generates structured meeting minutes from notes, recordings, and agenda items
"""

import re
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime, timedelta
from collections import Counter


def run(input_data: Dict) -> Dict:
    """
    Generate structured meeting minutes from notes and recordings.
    
    Args:
        input_data: Dictionary containing:
            - action: 'generate', 'template', 'format', 'summarize', 'extract_actions'
            - meeting_type: 'investigator', 'safety', 'steering_committee', 'site_initiation', 'closeout'
            - meeting_info: Basic meeting information (date, attendees, etc.)
            - notes: Raw meeting notes or transcript
            - agenda: Meeting agenda items
            - previous_minutes: Previous meeting minutes for follow-up
            - format_style: 'formal', 'detailed', 'executive_summary', 'action_focused'
            - output_format: 'html', 'pdf', 'docx', 'markdown'
    
    Returns:
        Dictionary with generated meeting minutes and metadata
    """
    try:
        action = input_data.get('action', 'generate').lower()
        meeting_type = input_data.get('meeting_type', 'investigator')
        meeting_info = input_data.get('meeting_info', {})
        notes = input_data.get('notes', '')
        agenda = input_data.get('agenda', [])
        previous_minutes = input_data.get('previous_minutes', {})
        format_style = input_data.get('format_style', 'formal')
        output_format = input_data.get('output_format', 'html')
        
        result = {'success': True, 'action': action}
        
        if action == 'generate':
            result.update(_generate_meeting_minutes(
                meeting_type, meeting_info, notes, agenda, previous_minutes, format_style
            ))
        elif action == 'template':
            result.update(_generate_minutes_template(meeting_type, format_style))
        elif action == 'format':
            result.update(_format_minutes(meeting_info, output_format))
        elif action == 'summarize':
            result.update(_summarize_meeting_content(notes, agenda, meeting_type))
        elif action == 'extract_actions':
            result.update(_extract_action_items(notes, meeting_info))
        else:
            return {
                'success': False,
                'error': f'Unknown action: {action}',
                'valid_actions': ['generate', 'template', 'format', 'summarize', 'extract_actions']
            }
        
        # Add metadata
        result['metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'meeting_type': meeting_type,
            'format_style': format_style,
            'output_format': output_format
        }
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error generating meeting minutes: {str(e)}'
        }


def _generate_meeting_minutes(meeting_type: str, meeting_info: Dict, notes: str,
                             agenda: List[Dict], previous_minutes: Dict, format_style: str) -> Dict:
    """Generate complete meeting minutes."""
    
    # Process meeting information
    processed_info = _process_meeting_info(meeting_info, meeting_type)
    
    # Process agenda and notes
    structured_content = _structure_meeting_content(notes, agenda, meeting_type)
    
    # Extract key elements
    action_items = _extract_action_items_from_content(structured_content, meeting_info)
    decisions = _extract_decisions(structured_content)
    follow_ups = _identify_follow_ups(previous_minutes, structured_content)
    
    # Create minutes sections
    minutes_sections = _create_minutes_sections(
        structured_content, action_items, decisions, follow_ups, meeting_type, format_style
    )
    
    # Generate complete minutes document
    minutes_document = {
        'header': _create_minutes_header(processed_info, meeting_type),
        'attendees': _format_attendee_list(processed_info.get('attendees', [])),
        'agenda_review': _create_agenda_review(agenda, structured_content),
        'content_sections': minutes_sections,
        'action_items': action_items,
        'decisions_made': decisions,
        'next_steps': _generate_next_steps(action_items, meeting_info),
        'footer': _create_minutes_footer(processed_info)
    }
    
    # Format in different outputs
    formatted_outputs = {
        'html': _format_minutes_html(minutes_document, format_style),
        'markdown': _format_minutes_markdown(minutes_document),
        'text': _format_minutes_text(minutes_document),
        'structured_json': json.dumps(minutes_document, indent=2, default=str)
    }
    
    # Calculate statistics
    statistics = _calculate_minutes_statistics(minutes_document, notes)
    
    return {
        'meeting_minutes': minutes_document,
        'formatted_outputs': formatted_outputs,
        'statistics': statistics,
        'recommendations': _generate_minutes_recommendations(minutes_document, statistics),
        'follow_up_items': _create_follow_up_summary(action_items)
    }


def _generate_minutes_template(meeting_type: str, format_style: str) -> Dict:
    """Generate a meeting minutes template."""
    
    template = {
        'structure': _get_minutes_structure(meeting_type),
        'required_sections': _get_required_sections(meeting_type),
        'optional_sections': _get_optional_sections(meeting_type, format_style),
        'formatting_guidelines': _get_formatting_guidelines(format_style),
        'sample_content': _get_sample_minutes_content(meeting_type)
    }
    
    return {
        'template': template,
        'meeting_type': meeting_type,
        'format_style': format_style,
        'usage_instructions': _get_template_usage_instructions(meeting_type),
        'customization_options': _get_customization_options(meeting_type, format_style)
    }


def _format_minutes(minutes_content: Dict, output_format: str) -> Dict:
    """Format meeting minutes in specified format."""
    
    format_functions = {
        'html': _format_minutes_html,
        'markdown': _format_minutes_markdown,
        'text': _format_minutes_text,
        'pdf_ready': _format_minutes_pdf_ready,
        'docx_structure': _format_minutes_docx_structure
    }
    
    if output_format not in format_functions:
        return {
            'error': f'Unsupported output format: {output_format}',
            'supported_formats': list(format_functions.keys())
        }
    
    try:
        formatted_content = format_functions[output_format](minutes_content, 'formal')
        return {
            'formatted_minutes': formatted_content,
            'output_format': output_format,
            'formatting_notes': _get_format_specific_notes(output_format)
        }
    except Exception as e:
        return {
            'error': f'Formatting failed: {str(e)}',
            'output_format': output_format
        }


def _summarize_meeting_content(notes: str, agenda: List[Dict], meeting_type: str) -> Dict:
    """Create a summary of meeting content."""
    
    # Extract key topics and discussions
    key_topics = _extract_key_topics(notes, agenda)
    main_discussions = _identify_main_discussions(notes, meeting_type)
    
    # Create summary sections
    executive_summary = _create_executive_summary(key_topics, main_discussions, meeting_type)
    key_points = _extract_key_points(notes, agenda)
    outcomes = _identify_meeting_outcomes(notes, main_discussions)
    
    summary = {
        'executive_summary': executive_summary,
        'key_topics_discussed': key_topics,
        'main_discussions': main_discussions,
        'key_points': key_points,
        'meeting_outcomes': outcomes,
        'attendance_summary': _analyze_participation(notes),
        'time_allocation': _analyze_time_spent_on_topics(notes, agenda)
    }
    
    return {
        'meeting_summary': summary,
        'summary_statistics': _calculate_summary_statistics(summary),
        'insights': _generate_meeting_insights(summary, meeting_type)
    }


def _extract_action_items(notes: str, meeting_info: Dict) -> Dict:
    """Extract action items from meeting notes."""
    
    action_items = _extract_action_items_from_content(notes, meeting_info)
    
    # Categorize and prioritize actions
    categorized_actions = _categorize_action_items(action_items)
    prioritized_actions = _prioritize_action_items(action_items, meeting_info.get('meeting_type', 'general'))
    
    # Generate action tracking information
    action_tracking = _create_action_tracking_info(action_items)
    
    return {
        'action_items': action_items,
        'categorized_actions': categorized_actions,
        'prioritized_actions': prioritized_actions,
        'action_tracking': action_tracking,
        'recommendations': _generate_action_item_recommendations(action_items)
    }


def _process_meeting_info(meeting_info: Dict, meeting_type: str) -> Dict:
    """Process and standardize meeting information."""
    
    processed = {
        'meeting_title': meeting_info.get('title', _get_default_meeting_title(meeting_type)),
        'meeting_type': meeting_type,
        'date': meeting_info.get('date', datetime.now().strftime('%Y-%m-%d')),
        'time': meeting_info.get('time', meeting_info.get('start_time', 'TBD')),
        'duration': meeting_info.get('duration', 'TBD'),
        'location': meeting_info.get('location', meeting_info.get('venue', 'Virtual')),
        'meeting_id': meeting_info.get('id', meeting_info.get('meeting_number', f'MTG-{datetime.now().strftime("%Y%m%d")}')),
        'chair': meeting_info.get('chair', meeting_info.get('chairperson', 'TBD')),
        'secretary': meeting_info.get('secretary', meeting_info.get('minute_taker', 'TBD')),
        'attendees': meeting_info.get('attendees', []),
        'apologies': meeting_info.get('apologies', meeting_info.get('absentees', [])),
        'study_info': meeting_info.get('study_info', {}),
        'recording_info': meeting_info.get('recording_info', {})
    }
    
    # Standardize attendees format
    processed['attendees'] = _standardize_attendee_list(processed['attendees'])
    
    return processed


def _structure_meeting_content(notes: str, agenda: List[Dict], meeting_type: str) -> Dict:
    """Structure meeting content based on notes and agenda."""
    
    # Parse agenda items
    processed_agenda = _process_agenda_items(agenda)
    
    # Extract content for each agenda item
    agenda_content = {}
    for agenda_item in processed_agenda:
        item_id = agenda_item.get('id', f"item_{len(agenda_content)}")
        agenda_content[item_id] = {
            'agenda_item': agenda_item,
            'discussion': _extract_discussion_for_agenda_item(notes, agenda_item),
            'outcomes': _extract_outcomes_for_agenda_item(notes, agenda_item),
            'action_items': _extract_actions_for_agenda_item(notes, agenda_item)
        }
    
    # Extract unstructured content (not tied to specific agenda items)
    unstructured_content = _extract_unstructured_content(notes, processed_agenda)
    
    return {
        'agenda_based_content': agenda_content,
        'unstructured_content': unstructured_content,
        'meeting_flow': _analyze_meeting_flow(notes),
        'key_themes': _identify_key_themes(notes, meeting_type)
    }


def _create_minutes_sections(structured_content: Dict, action_items: List[Dict],
                           decisions: List[Dict], follow_ups: List[Dict], 
                           meeting_type: str, format_style: str) -> Dict:
    """Create organized sections for meeting minutes."""
    
    sections = {}
    
    # Main content sections based on agenda
    agenda_content = structured_content.get('agenda_based_content', {})
    for item_id, content in agenda_content.items():
        agenda_item = content.get('agenda_item', {})
        section_name = agenda_item.get('title', f'Agenda Item {item_id}')
        
        sections[section_name] = {
            'agenda_reference': agenda_item.get('reference', ''),
            'presenter': agenda_item.get('presenter', 'TBD'),
            'time_allocated': agenda_item.get('time_allocated', 'TBD'),
            'discussion_summary': content.get('discussion', 'No discussion recorded'),
            'key_points': _extract_key_points_from_discussion(content.get('discussion', '')),
            'outcomes': content.get('outcomes', []),
            'related_actions': [action for action in action_items 
                              if action.get('agenda_item_id') == item_id]
        }
    
    # Add special sections based on meeting type
    if meeting_type == 'safety':
        sections = _add_safety_meeting_sections(sections, structured_content)
    elif meeting_type == 'steering_committee':
        sections = _add_steering_committee_sections(sections, structured_content)
    elif meeting_type == 'investigator':
        sections = _add_investigator_meeting_sections(sections, structured_content)
    
    # Add standard closing sections
    sections['Decisions Made'] = {
        'content': decisions,
        'total_decisions': len(decisions)
    }
    
    sections['Action Items Summary'] = {
        'content': action_items,
        'total_actions': len(action_items),
        'high_priority_actions': len([a for a in action_items if a.get('priority') == 'high'])
    }
    
    if follow_ups:
        sections['Follow-up from Previous Meeting'] = {
            'content': follow_ups,
            'completed_items': len([f for f in follow_ups if f.get('status') == 'completed']),
            'pending_items': len([f for f in follow_ups if f.get('status') == 'pending'])
        }
    
    return sections


def _extract_action_items_from_content(content, meeting_info: Dict) -> List[Dict]:
    """Extract action items from meeting content."""
    
    if isinstance(content, str):
        notes = content
    else:
        # Extract from structured content
        notes = ""
        if isinstance(content, dict):
            agenda_content = content.get('agenda_based_content', {})
            for item_content in agenda_content.values():
                notes += item_content.get('discussion', '') + " "
            notes += content.get('unstructured_content', '')
    
    action_items = []
    
    # Common action item patterns
    action_patterns = [
        r'(?:action|todo|task)[:\s]*(.+?)(?:\.|$)',
        r'(?:will|to|should|must)\s+(.+?)(?:\.|$)',
        r'(?:responsible|assigned to|owner)[:\s]*(.+?)(?:\.|$)',
        r'(?:by|due|deadline)[:\s]*(.+?)(?:\.|$)',
        r'(?:follow.?up|follow up)[:\s]*(.+?)(?:\.|$)'
    ]
    
    # Extract potential action items
    for pattern in action_patterns:
        matches = re.finditer(pattern, notes, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            action_text = match.group(1).strip()
            if len(action_text) > 10:  # Filter out very short matches
                action_item = _create_action_item(action_text, notes, meeting_info)
                if action_item:
                    action_items.append(action_item)
    
    # Extract explicit action items (numbered lists, bullet points)
    explicit_actions = _extract_explicit_actions(notes)
    action_items.extend(explicit_actions)
    
    # Deduplicate and clean up
    action_items = _deduplicate_action_items(action_items)
    
    # Add IDs and sequence numbers
    for i, action in enumerate(action_items):
        action['id'] = f"action_{i+1}"
        action['sequence'] = i + 1
    
    return action_items


def _create_action_item(action_text: str, full_notes: str, meeting_info: Dict) -> Optional[Dict]:
    """Create structured action item from text."""
    
    # Extract components
    assignee = _extract_assignee(action_text, full_notes)
    due_date = _extract_due_date(action_text)
    priority = _determine_action_priority(action_text, full_notes)
    category = _categorize_action(action_text)
    
    # Clean up action description
    cleaned_action = _clean_action_description(action_text)
    
    if len(cleaned_action) < 5:  # Too short to be meaningful
        return None
    
    return {
        'description': cleaned_action,
        'assignee': assignee,
        'due_date': due_date,
        'priority': priority,
        'category': category,
        'status': 'open',
        'created_date': datetime.now().strftime('%Y-%m-%d'),
        'meeting_reference': meeting_info.get('id', 'TBD'),
        'agenda_item_id': _find_related_agenda_item(action_text, meeting_info.get('agenda', []))
    }


def _extract_decisions(structured_content: Dict) -> List[Dict]:
    """Extract decisions made during the meeting."""
    
    decisions = []
    
    # Extract from agenda-based content
    agenda_content = structured_content.get('agenda_based_content', {})
    for item_id, content in agenda_content.items():
        outcomes = content.get('outcomes', [])
        for outcome in outcomes:
            if _is_decision(outcome):
                decision = {
                    'decision': outcome,
                    'agenda_item': content.get('agenda_item', {}).get('title', 'Unknown'),
                    'context': content.get('discussion', ''),
                    'type': _classify_decision_type(outcome),
                    'impact_level': _assess_decision_impact(outcome)
                }
                decisions.append(decision)
    
    # Extract from unstructured content
    unstructured = structured_content.get('unstructured_content', '')
    decision_patterns = [
        r'(?:decided|agreed|resolved|concluded)[:\s]*(.+?)(?:\.|$)',
        r'(?:decision|resolution)[:\s]*(.+?)(?:\.|$)',
        r'(?:it was agreed|consensus reached)[:\s]*(.+?)(?:\.|$)'
    ]
    
    for pattern in decision_patterns:
        matches = re.finditer(pattern, unstructured, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            decision_text = match.group(1).strip()
            if len(decision_text) > 10:
                decisions.append({
                    'decision': decision_text,
                    'agenda_item': 'General Discussion',
                    'context': 'From general meeting discussion',
                    'type': _classify_decision_type(decision_text),
                    'impact_level': _assess_decision_impact(decision_text)
                })
    
    # Add IDs
    for i, decision in enumerate(decisions):
        decision['id'] = f"decision_{i+1}"
    
    return decisions


def _identify_follow_ups(previous_minutes: Dict, current_content: Dict) -> List[Dict]:
    """Identify follow-up items from previous meeting."""
    
    follow_ups = []
    
    if not previous_minutes:
        return follow_ups
    
    previous_actions = previous_minutes.get('action_items', [])
    
    for prev_action in previous_actions:
        # Check if this action is mentioned in current meeting
        action_desc = prev_action.get('description', '')
        follow_up_status = _check_action_status_in_current_meeting(
            action_desc, current_content
        )
        
        follow_up = {
            'original_action': prev_action,
            'current_status': follow_up_status,
            'follow_up_discussion': _extract_follow_up_discussion(action_desc, current_content),
            'updated_due_date': _extract_updated_due_date(action_desc, current_content)
        }
        
        follow_ups.append(follow_up)
    
    return follow_ups


def _create_minutes_header(meeting_info: Dict, meeting_type: str) -> Dict:
    """Create meeting minutes header."""
    
    return {
        'document_title': f"{meeting_info.get('meeting_title', 'Meeting')} - Minutes",
        'meeting_type': meeting_type.title().replace('_', ' '),
        'meeting_id': meeting_info.get('meeting_id', 'TBD'),
        'date': meeting_info.get('date', 'TBD'),
        'time': meeting_info.get('time', 'TBD'),
        'duration': meeting_info.get('duration', 'TBD'),
        'location': meeting_info.get('location', 'TBD'),
        'chairperson': meeting_info.get('chair', 'TBD'),
        'minute_taker': meeting_info.get('secretary', 'TBD'),
        'study_reference': meeting_info.get('study_info', {}).get('name', 'TBD'),
        'distribution': _get_distribution_list(meeting_type)
    }


def _format_attendee_list(attendees: List) -> Dict:
    """Format attendee information."""
    
    formatted_attendees = {
        'present': [],
        'absent_with_apology': [],
        'total_attendees': 0
    }
    
    for attendee in attendees:
        if isinstance(attendee, str):
            formatted_attendees['present'].append({
                'name': attendee,
                'role': 'TBD',
                'organization': 'TBD'
            })
        elif isinstance(attendee, dict):
            attendee_info = {
                'name': attendee.get('name', 'TBD'),
                'role': attendee.get('role', attendee.get('title', 'TBD')),
                'organization': attendee.get('organization', attendee.get('institution', 'TBD')),
                'status': attendee.get('status', 'present')
            }
            
            if attendee_info['status'] in ['present', 'attended']:
                formatted_attendees['present'].append(attendee_info)
            else:
                formatted_attendees['absent_with_apology'].append(attendee_info)
    
    formatted_attendees['total_attendees'] = len(formatted_attendees['present'])
    
    return formatted_attendees


def _create_agenda_review(agenda: List[Dict], structured_content: Dict) -> Dict:
    """Create agenda review section."""
    
    agenda_review = {
        'agenda_items': [],
        'agenda_changes': [],
        'time_summary': {}
    }
    
    for item in agenda:
        item_review = {
            'item_number': item.get('number', item.get('id', 'TBD')),
            'title': item.get('title', 'TBD'),
            'presenter': item.get('presenter', 'TBD'),
            'time_allocated': item.get('time_allocated', 'TBD'),
            'status': _determine_agenda_item_status(item, structured_content),
            'summary': _get_agenda_item_summary(item, structured_content)
        }
        agenda_review['agenda_items'].append(item_review)
    
    return agenda_review


def _generate_next_steps(action_items: List[Dict], meeting_info: Dict) -> Dict:
    """Generate next steps summary."""
    
    # Categorize actions by urgency and type
    immediate_actions = [a for a in action_items if a.get('priority') == 'high']
    upcoming_actions = [a for a in action_items if a.get('priority') in ['medium', 'normal']]
    
    # Determine next meeting info
    next_meeting = _determine_next_meeting_info(meeting_info)
    
    return {
        'immediate_actions': immediate_actions,
        'upcoming_actions': upcoming_actions,
        'next_meeting': next_meeting,
        'follow_up_requirements': _identify_follow_up_requirements(action_items),
        'reporting_deadlines': _extract_reporting_deadlines(action_items, meeting_info)
    }


def _create_minutes_footer(meeting_info: Dict) -> Dict:
    """Create meeting minutes footer."""
    
    return {
        'minutes_prepared_by': meeting_info.get('secretary', 'TBD'),
        'minutes_prepared_date': datetime.now().strftime('%Y-%m-%d'),
        'approved_by': meeting_info.get('chair', 'TBD'),
        'approval_date': 'Pending approval',
        'next_meeting_date': 'TBD',
        'distribution_list': _get_distribution_list(meeting_info.get('meeting_type', 'general')),
        'document_version': '1.0',
        'confidentiality_notice': _get_confidentiality_notice(meeting_info.get('meeting_type', 'general'))
    }


def _format_minutes_html(minutes: Dict, format_style: str) -> str:
    """Format meeting minutes as HTML."""
    
    header = minutes.get('header', {})
    sections = minutes.get('content_sections', {})
    action_items = minutes.get('action_items', [])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{header.get('document_title', 'Meeting Minutes')}</title>
        <style>
            {_get_minutes_html_styles(format_style)}
        </style>
    </head>
    <body>
        <!-- Header -->
        <div class="header">
            <h1>{header.get('document_title', 'Meeting Minutes')}</h1>
            <div class="meeting-info">
                <p><strong>Meeting Type:</strong> {header.get('meeting_type', 'TBD')}</p>
                <p><strong>Date:</strong> {header.get('date', 'TBD')}</p>
                <p><strong>Time:</strong> {header.get('time', 'TBD')}</p>
                <p><strong>Location:</strong> {header.get('location', 'TBD')}</p>
                <p><strong>Chairperson:</strong> {header.get('chairperson', 'TBD')}</p>
            </div>
        </div>
        
        <!-- Attendees -->
        <div class="section">
            <h2>Attendees</h2>
            {_format_attendees_html(minutes.get('attendees', {}))}
        </div>
        
        <!-- Agenda Review -->
        <div class="section">
            <h2>Agenda Review</h2>
            {_format_agenda_review_html(minutes.get('agenda_review', {}))}
        </div>
        
        <!-- Content Sections -->
        <div class="content">
    """
    
    # Add content sections
    for section_name, section_data in sections.items():
        html += f"""
        <div class="section">
            <h2>{section_name}</h2>
        """
        
        if isinstance(section_data, dict):
            if 'discussion_summary' in section_data:
                html += f"<div class='discussion'>{section_data['discussion_summary']}</div>"
            
            if 'key_points' in section_data and section_data['key_points']:
                html += "<h3>Key Points:</h3><ul>"
                for point in section_data['key_points']:
                    html += f"<li>{point}</li>"
                html += "</ul>"
            
            if 'outcomes' in section_data and section_data['outcomes']:
                html += "<h3>Outcomes:</h3><ul>"
                for outcome in section_data['outcomes']:
                    html += f"<li>{outcome}</li>"
                html += "</ul>"
            
            if 'related_actions' in section_data and section_data['related_actions']:
                html += "<h3>Related Actions:</h3><ul>"
                for action in section_data['related_actions']:
                    html += f"<li>{action.get('description', 'TBD')} (Assigned to: {action.get('assignee', 'TBD')})</li>"
                html += "</ul>"
        
        html += "</div>"
    
    # Add action items summary
    if action_items:
        html += """
        <div class="section">
            <h2>Action Items Summary</h2>
            <table class="action-items-table">
                <thead>
                    <tr>
                        <th>Action</th>
                        <th>Assigned To</th>
                        <th>Due Date</th>
                        <th>Priority</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for action in action_items:
            priority_class = f"priority-{action.get('priority', 'medium')}"
            html += f"""
                    <tr class="{priority_class}">
                        <td>{action.get('description', 'TBD')}</td>
                        <td>{action.get('assignee', 'TBD')}</td>
                        <td>{action.get('due_date', 'TBD')}</td>
                        <td>{action.get('priority', 'Medium').title()}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
    
    # Add footer
    footer = minutes.get('footer', {})
    html += f"""
        <!-- Footer -->
        <div class="footer">
            <p><strong>Minutes prepared by:</strong> {footer.get('minutes_prepared_by', 'TBD')}</p>
            <p><strong>Date prepared:</strong> {footer.get('minutes_prepared_date', 'TBD')}</p>
            <p><strong>Next meeting:</strong> {footer.get('next_meeting_date', 'TBD')}</p>
            <div class="confidentiality">
                {footer.get('confidentiality_notice', '')}
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def _format_minutes_markdown(minutes: Dict) -> str:
    """Format meeting minutes as Markdown."""
    
    header = minutes.get('header', {})
    sections = minutes.get('content_sections', {})
    action_items = minutes.get('action_items', [])
    
    markdown = f"""
# {header.get('document_title', 'Meeting Minutes')}

**Meeting Type:** {header.get('meeting_type', 'TBD')}  
**Date:** {header.get('date', 'TBD')}  
**Time:** {header.get('time', 'TBD')}  
**Location:** {header.get('location', 'TBD')}  
**Chairperson:** {header.get('chairperson', 'TBD')}

## Attendees

{_format_attendees_markdown(minutes.get('attendees', {}))}

## Agenda Review

{_format_agenda_review_markdown(minutes.get('agenda_review', {}))}

"""
    
    # Add content sections
    for section_name, section_data in sections.items():
        markdown += f"\n## {section_name}\n\n"
        
        if isinstance(section_data, dict):
            if 'discussion_summary' in section_data:
                markdown += f"{section_data['discussion_summary']}\n\n"
            
            if 'key_points' in section_data and section_data['key_points']:
                markdown += "### Key Points:\n\n"
                for point in section_data['key_points']:
                    markdown += f"- {point}\n"
                markdown += "\n"
            
            if 'outcomes' in section_data and section_data['outcomes']:
                markdown += "### Outcomes:\n\n"
                for outcome in section_data['outcomes']:
                    markdown += f"- {outcome}\n"
                markdown += "\n"
    
    # Add action items
    if action_items:
        markdown += "\n## Action Items Summary\n\n"
        markdown += "| Action | Assigned To | Due Date | Priority |\n"
        markdown += "|--------|-------------|----------|----------|\n"
        
        for action in action_items:
            markdown += f"| {action.get('description', 'TBD')} | {action.get('assignee', 'TBD')} | {action.get('due_date', 'TBD')} | {action.get('priority', 'Medium').title()} |\n"
        
        markdown += "\n"
    
    # Add footer
    footer = minutes.get('footer', {})
    markdown += f"""
---

**Minutes prepared by:** {footer.get('minutes_prepared_by', 'TBD')}  
**Date prepared:** {footer.get('minutes_prepared_date', 'TBD')}  
**Next meeting:** {footer.get('next_meeting_date', 'TBD')}

{footer.get('confidentiality_notice', '')}
"""
    
    return markdown


def _format_minutes_text(minutes: Dict) -> str:
    """Format meeting minutes as plain text."""
    
    header = minutes.get('header', {})
    sections = minutes.get('content_sections', {})
    action_items = minutes.get('action_items', [])
    
    text = f"""
{header.get('document_title', 'MEETING MINUTES').upper()}
{'=' * len(header.get('document_title', 'MEETING MINUTES'))}

Meeting Type: {header.get('meeting_type', 'TBD')}
Date: {header.get('date', 'TBD')}
Time: {header.get('time', 'TBD')}
Location: {header.get('location', 'TBD')}
Chairperson: {header.get('chairperson', 'TBD')}

ATTENDEES
=========

{_format_attendees_text(minutes.get('attendees', {}))}

AGENDA REVIEW
=============

{_format_agenda_review_text(minutes.get('agenda_review', {}))}

"""
    
    # Add content sections
    for section_name, section_data in sections.items():
        text += f"\n{section_name.upper()}\n"
        text += "=" * len(section_name) + "\n\n"
        
        if isinstance(section_data, dict):
            if 'discussion_summary' in section_data:
                text += f"{section_data['discussion_summary']}\n\n"
            
            if 'key_points' in section_data and section_data['key_points']:
                text += "Key Points:\n"
                for point in section_data['key_points']:
                    text += f"- {point}\n"
                text += "\n"
    
    # Add action items
    if action_items:
        text += "\nACTION ITEMS SUMMARY\n"
        text += "====================\n\n"
        
        for i, action in enumerate(action_items, 1):
            text += f"{i}. {action.get('description', 'TBD')}\n"
            text += f"   Assigned to: {action.get('assignee', 'TBD')}\n"
            text += f"   Due date: {action.get('due_date', 'TBD')}\n"
            text += f"   Priority: {action.get('priority', 'Medium').title()}\n\n"
    
    # Add footer
    footer = minutes.get('footer', {})
    text += f"""
{'=' * 50}

Minutes prepared by: {footer.get('minutes_prepared_by', 'TBD')}
Date prepared: {footer.get('minutes_prepared_date', 'TBD')}
Next meeting: {footer.get('next_meeting_date', 'TBD')}

{footer.get('confidentiality_notice', '')}
"""
    
    return text


# Helper functions for processing and analysis

def _get_default_meeting_title(meeting_type: str) -> str:
    """Get default meeting title based on type."""
    titles = {
        'investigator': 'Investigator Meeting',
        'safety': 'Safety Review Meeting',
        'steering_committee': 'Steering Committee Meeting',
        'site_initiation': 'Site Initiation Visit',
        'closeout': 'Study Closeout Meeting'
    }
    return titles.get(meeting_type, 'Clinical Study Meeting')


def _standardize_attendee_list(attendees: List) -> List[Dict]:
    """Standardize attendee list format."""
    standardized = []
    
    for attendee in attendees:
        if isinstance(attendee, str):
            standardized.append({
                'name': attendee,
                'role': 'TBD',
                'organization': 'TBD',
                'status': 'present'
            })
        elif isinstance(attendee, dict):
            standardized.append({
                'name': attendee.get('name', 'TBD'),
                'role': attendee.get('role', attendee.get('title', 'TBD')),
                'organization': attendee.get('organization', attendee.get('institution', 'TBD')),
                'status': attendee.get('status', 'present')
            })
    
    return standardized


def _process_agenda_items(agenda: List[Dict]) -> List[Dict]:
    """Process and standardize agenda items."""
    processed = []
    
    for i, item in enumerate(agenda):
        if isinstance(item, str):
            processed_item = {
                'id': f'item_{i+1}',
                'number': i + 1,
                'title': item,
                'presenter': 'TBD',
                'time_allocated': 'TBD'
            }
        elif isinstance(item, dict):
            processed_item = {
                'id': item.get('id', f'item_{i+1}'),
                'number': item.get('number', i + 1),
                'title': item.get('title', item.get('topic', f'Agenda Item {i+1}')),
                'presenter': item.get('presenter', item.get('lead', 'TBD')),
                'time_allocated': item.get('time_allocated', item.get('duration', 'TBD')),
                'description': item.get('description', ''),
                'objectives': item.get('objectives', [])
            }
        
        processed.append(processed_item)
    
    return processed


def _extract_discussion_for_agenda_item(notes: str, agenda_item: Dict) -> str:
    """Extract discussion content for specific agenda item."""
    item_title = agenda_item.get('title', '')
    
    # Simple approach - look for sections mentioning the agenda item title
    if item_title and item_title.lower() in notes.lower():
        # Find content around mentions of the agenda item
        lines = notes.split('\n')
        relevant_lines = []
        
        for i, line in enumerate(lines):
            if item_title.lower() in line.lower():
                # Include surrounding context
                start = max(0, i - 2)
                end = min(len(lines), i + 5)
                relevant_lines.extend(lines[start:end])
        
        return '\n'.join(relevant_lines) if relevant_lines else 'No specific discussion recorded'
    
    return 'No specific discussion recorded'


def _extract_outcomes_for_agenda_item(notes: str, agenda_item: Dict) -> List[str]:
    """Extract outcomes for specific agenda item."""
    discussion = _extract_discussion_for_agenda_item(notes, agenda_item)
    
    # Look for outcome indicators
    outcome_patterns = [
        r'(?:outcome|result|conclusion)[:\s]*(.+?)(?:\.|$)',
        r'(?:decided|agreed|resolved)[:\s]*(.+?)(?:\.|$)',
        r'(?:next steps?|follow.?up)[:\s]*(.+?)(?:\.|$)'
    ]
    
    outcomes = []
    for pattern in outcome_patterns:
        matches = re.finditer(pattern, discussion, re.IGNORECASE)
        for match in matches:
            outcome_text = match.group(1).strip()
            if len(outcome_text) > 5:
                outcomes.append(outcome_text)
    
    return outcomes


def _extract_actions_for_agenda_item(notes: str, agenda_item: Dict) -> List[str]:
    """Extract actions for specific agenda item."""
    discussion = _extract_discussion_for_agenda_item(notes, agenda_item)
    
    # Simple action extraction
    action_patterns = [
        r'(?:action|task)[:\s]*(.+?)(?:\.|$)',
        r'(?:will|to)\s+(.+?)(?:\.|$)'
    ]
    
    actions = []
    for pattern in action_patterns:
        matches = re.finditer(pattern, discussion, re.IGNORECASE)
        for match in matches:
            action_text = match.group(1).strip()
            if len(action_text) > 5:
                actions.append(action_text)
    
    return actions


def _extract_unstructured_content(notes: str, processed_agenda: List[Dict]) -> str:
    """Extract content not tied to specific agenda items."""
    # This is a simplified approach - in practice would be more sophisticated
    agenda_titles = [item.get('title', '').lower() for item in processed_agenda]
    
    # Remove agenda-specific content
    remaining_content = notes
    for title in agenda_titles:
        if title:
            # Simple removal - could be more sophisticated
            remaining_content = remaining_content.replace(title, '')
    
    return remaining_content


def _analyze_meeting_flow(notes: str) -> Dict:
    """Analyze the flow of the meeting."""
    return {
        'estimated_duration': 'Based on content volume',
        'discussion_intensity': 'Moderate',  # Could analyze based on content
        'participation_level': 'Active',     # Could analyze based on indicators
        'time_management': 'On track'        # Could analyze based on agenda vs content
    }


def _identify_key_themes(notes: str, meeting_type: str) -> List[str]:
    """Identify key themes from meeting notes."""
    # Common themes by meeting type
    theme_keywords = {
        'safety': ['adverse', 'safety', 'risk', 'side effect', 'monitoring'],
        'investigator': ['enrollment', 'protocol', 'training', 'site', 'compliance'],
        'steering_committee': ['strategy', 'oversight', 'governance', 'decision', 'direction'],
        'general': ['progress', 'update', 'issues', 'next steps', 'timeline']
    }
    
    keywords = theme_keywords.get(meeting_type, theme_keywords['general'])
    notes_lower = notes.lower()
    
    themes = []
    for keyword in keywords:
        if keyword in notes_lower:
            themes.append(keyword.title())
    
    return themes


def _extract_assignee(action_text: str, full_notes: str) -> str:
    """Extract assignee from action text."""
    # Look for assignment patterns
    assignment_patterns = [
        r'(?:assigned to|responsible|owner)[:\s]*([A-Za-z\s]+)',
        r'([A-Za-z\s]+)\s+(?:will|to|should)',
        r'(?:by|from)\s+([A-Za-z\s]+)'
    ]
    
    for pattern in assignment_patterns:
        match = re.search(pattern, action_text, re.IGNORECASE)
        if match:
            assignee = match.group(1).strip()
            if len(assignee) > 2 and len(assignee) < 50:  # Reasonable name length
                return assignee
    
    return 'TBD'


def _extract_due_date(action_text: str) -> str:
    """Extract due date from action text."""
    # Look for date patterns
    date_patterns = [
        r'(?:by|due|deadline)[:\s]*(\d{1,2}/\d{1,2}/\d{4})',
        r'(?:by|due|deadline)[:\s]*(\w+\s+\d{1,2},?\s+\d{4})',
        r'(?:next\s+week|next\s+meeting|end\s+of\s+week)'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, action_text, re.IGNORECASE)
        if match:
            return match.group(1) if match.groups() else match.group(0)
    
    return 'TBD'


def _determine_action_priority(action_text: str, full_notes: str) -> str:
    """Determine priority of action item."""
    urgent_keywords = ['urgent', 'asap', 'immediately', 'critical', 'high priority']
    low_keywords = ['when time permits', 'low priority', 'nice to have']
    
    action_lower = action_text.lower()
    
    if any(keyword in action_lower for keyword in urgent_keywords):
        return 'high'
    elif any(keyword in action_lower for keyword in low_keywords):
        return 'low'
    else:
        return 'medium'


def _categorize_action(action_text: str) -> str:
    """Categorize action item."""
    categories = {
        'communication': ['email', 'call', 'contact', 'notify', 'inform'],
        'documentation': ['document', 'report', 'write', 'prepare', 'draft'],
        'meeting': ['schedule', 'meet', 'arrange', 'convene'],
        'review': ['review', 'check', 'verify', 'validate', 'audit'],
        'training': ['train', 'education', 'teach', 'instruct'],
        'administrative': ['update', 'file', 'submit', 'process']
    }
    
    action_lower = action_text.lower()
    
    for category, keywords in categories.items():
        if any(keyword in action_lower for keyword in keywords):
            return category
    
    return 'general'


def _clean_action_description(action_text: str) -> str:
    """Clean up action description."""
    # Remove common prefixes and clean up
    cleaned = re.sub(r'^(action|task|todo)[:\s]*', '', action_text, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Capitalize first letter
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    
    return cleaned


def _find_related_agenda_item(action_text: str, agenda: List[Dict]) -> Optional[str]:
    """Find which agenda item an action relates to."""
    for item in agenda:
        item_title = item.get('title', '').lower()
        if item_title and item_title in action_text.lower():
            return item.get('id', 'TBD')
    return None


def _extract_explicit_actions(notes: str) -> List[Dict]:
    """Extract explicitly formatted action items."""
    explicit_actions = []
    
    # Look for numbered action items
    numbered_pattern = r'(?:action|task)\s*\d+[:\.]?\s*(.+?)(?:\n|$)'
    matches = re.finditer(numbered_pattern, notes, re.IGNORECASE | re.MULTILINE)
    
    for match in matches:
        action_text = match.group(1).strip()
        if len(action_text) > 5:
            explicit_actions.append({
                'description': action_text,
                'assignee': 'TBD',
                'due_date': 'TBD',
                'priority': 'medium',
                'category': 'general',
                'status': 'open',
                'created_date': datetime.now().strftime('%Y-%m-%d')
            })
    
    return explicit_actions


def _deduplicate_action_items(action_items: List[Dict]) -> List[Dict]:
    """Remove duplicate action items."""
    seen = set()
    unique_actions = []
    
    for action in action_items:
        description = action.get('description', '').lower().strip()
        if description and description not in seen:
            seen.add(description)
            unique_actions.append(action)
    
    return unique_actions


def _is_decision(text: str) -> bool:
    """Determine if text represents a decision."""
    decision_indicators = [
        'decided', 'agreed', 'resolved', 'approved', 'rejected', 
        'consensus', 'voted', 'determined', 'concluded'
    ]
    
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in decision_indicators)


def _classify_decision_type(decision_text: str) -> str:
    """Classify the type of decision."""
    text_lower = decision_text.lower()
    
    if any(word in text_lower for word in ['approve', 'accept', 'yes']):
        return 'approval'
    elif any(word in text_lower for word in ['reject', 'deny', 'no']):
        return 'rejection'
    elif any(word in text_lower for word in ['defer', 'postpone', 'delay']):
        return 'deferral'
    else:
        return 'resolution'


def _assess_decision_impact(decision_text: str) -> str:
    """Assess the impact level of a decision."""
    high_impact_words = ['critical', 'major', 'significant', 'important', 'key']
    low_impact_words = ['minor', 'small', 'administrative', 'routine']
    
    text_lower = decision_text.lower()
    
    if any(word in text_lower for word in high_impact_words):
        return 'high'
    elif any(word in text_lower for word in low_impact_words):
        return 'low'
    else:
        return 'medium'


def _check_action_status_in_current_meeting(action_desc: str, current_content: Dict) -> str:
    """Check if previous action is mentioned in current meeting."""
    # Simple check - look for action description in current content
    all_current_content = ""
    
    agenda_content = current_content.get('agenda_based_content', {})
    for content in agenda_content.values():
        all_current_content += content.get('discussion', '') + " "
    all_current_content += current_content.get('unstructured_content', '')
    
    if action_desc.lower() in all_current_content.lower():
        # Look for completion indicators
        completion_indicators = ['completed', 'done', 'finished', 'resolved']
        if any(indicator in all_current_content.lower() for indicator in completion_indicators):
            return 'completed'
        else:
            return 'in_progress'
    else:
        return 'not_mentioned'


def _extract_follow_up_discussion(action_desc: str, current_content: Dict) -> str:
    """Extract discussion about follow-up item."""
    # Simplified implementation
    all_content = ""
    agenda_content = current_content.get('agenda_based_content', {})
    for content in agenda_content.values():
        all_content += content.get('discussion', '') + " "
    
    # Find sentences mentioning the action
    sentences = all_content.split('.')
    relevant_sentences = [s.strip() for s in sentences if action_desc.lower()[:20] in s.lower()]
    
    return '. '.join(relevant_sentences) if relevant_sentences else 'No specific discussion found'


def _extract_updated_due_date(action_desc: str, current_content: Dict) -> str:
    """Extract updated due date for follow-up item."""
    discussion = _extract_follow_up_discussion(action_desc, current_content)
    return _extract_due_date(discussion) if discussion != 'No specific discussion found' else 'No update'


# Additional helper functions for formatting and analysis

def _get_minutes_structure(meeting_type: str) -> List[str]:
    """Get recommended structure for meeting minutes."""
    structures = {
        'investigator': [
            'header', 'attendees', 'agenda_review', 'protocol_updates', 
            'enrollment_status', 'safety_updates', 'training_items', 
            'action_items', 'next_meeting', 'footer'
        ],
        'safety': [
            'header', 'attendees', 'safety_review', 'adverse_events',
            'risk_assessment', 'recommendations', 'action_items', 'footer'
        ],
        'steering_committee': [
            'header', 'attendees', 'executive_summary', 'strategic_updates',
            'governance_items', 'decisions', 'action_items', 'footer'
        ]
    }
    
    return structures.get(meeting_type, [
        'header', 'attendees', 'agenda_review', 'content_sections',
        'action_items', 'decisions', 'next_steps', 'footer'
    ])


def _get_required_sections(meeting_type: str) -> List[str]:
    """Get required sections for meeting type."""
    return [
        'header',
        'attendees', 
        'action_items',
        'footer'
    ]


def _get_optional_sections(meeting_type: str, format_style: str) -> List[str]:
    """Get optional sections."""
    optional = [
        'agenda_review',
        'decisions_made',
        'follow_ups',
        'next_meeting_info'
    ]
    
    if format_style == 'detailed':
        optional.extend(['discussion_details', 'time_tracking', 'participant_comments'])
    
    return optional


def _get_formatting_guidelines(format_style: str) -> Dict:
    """Get formatting guidelines."""
    return {
        'formal': {
            'tone': 'Professional and structured',
            'detail_level': 'Comprehensive',
            'language': 'Formal business language'
        },
        'detailed': {
            'tone': 'Thorough and analytical',
            'detail_level': 'Extensive with analysis',
            'language': 'Technical and precise'
        },
        'executive_summary': {
            'tone': 'Concise and strategic',
            'detail_level': 'High-level overview',
            'language': 'Executive-level communication'
        },
        'action_focused': {
            'tone': 'Direct and actionable',
            'detail_level': 'Focus on outcomes and actions',
            'language': 'Clear and action-oriented'
        }
    }


def _get_sample_minutes_content(meeting_type: str) -> Dict:
    """Get sample content for meeting type."""
    return {
        'investigator': {
            'sample_agenda_item': 'Protocol Amendment Review',
            'sample_discussion': 'The team reviewed the proposed protocol amendment...',
            'sample_action': 'Site coordinator to update screening procedures by [date]'
        },
        'safety': {
            'sample_agenda_item': 'Adverse Event Review',
            'sample_discussion': 'Review of recent safety reports showed...',
            'sample_action': 'Safety officer to investigate reported event within 48 hours'
        }
    }


def _calculate_minutes_statistics(minutes_doc: Dict, original_notes: str) -> Dict:
    """Calculate statistics for meeting minutes."""
    
    action_items = minutes_doc.get('action_items', [])
    decisions = minutes_doc.get('decisions_made', [])
    sections = minutes_doc.get('content_sections', {})
    
    return {
        'total_action_items': len(action_items),
        'high_priority_actions': len([a for a in action_items if a.get('priority') == 'high']),
        'total_decisions': len(decisions),
        'content_sections': len(sections),
        'original_notes_word_count': len(original_notes.split()) if original_notes else 0,
        'minutes_word_count': _calculate_minutes_word_count(minutes_doc),
        'processing_efficiency': _calculate_processing_efficiency(original_notes, minutes_doc)
    }


def _calculate_minutes_word_count(minutes_doc: Dict) -> int:
    """Calculate word count in meeting minutes."""
    word_count = 0
    
    sections = minutes_doc.get('content_sections', {})
    for section_data in sections.values():
        if isinstance(section_data, dict):
            if 'discussion_summary' in section_data:
                word_count += len(section_data['discussion_summary'].split())
    
    action_items = minutes_doc.get('action_items', [])
    for action in action_items:
        word_count += len(action.get('description', '').split())
    
    return word_count


def _calculate_processing_efficiency(original_notes: str, minutes_doc: Dict) -> str:
    """Calculate how efficiently notes were processed."""
    if not original_notes:
        return 'N/A'
    
    original_words = len(original_notes.split())
    minutes_words = _calculate_minutes_word_count(minutes_doc)
    
    if original_words == 0:
        return 'N/A'
    
    ratio = minutes_words / original_words
    
    if ratio > 0.8:
        return 'Low compression - consider summarizing more'
    elif ratio > 0.4:
        return 'Good compression - well summarized'
    else:
        return 'High compression - ensure no important details lost'


def _generate_minutes_recommendations(minutes_doc: Dict, statistics: Dict) -> List[str]:
    """Generate recommendations for meeting minutes improvement."""
    recommendations = []
    
    action_count = statistics.get('total_action_items', 0)
    if action_count == 0:
        recommendations.append("Consider identifying specific action items and assignments")
    elif action_count > 20:
        recommendations.append("Large number of action items - consider prioritization")
    
    decision_count = statistics.get('total_decisions', 0)
    if decision_count == 0:
        recommendations.append("No formal decisions recorded - verify if any were made")
    
    processing_efficiency = statistics.get('processing_efficiency', '')
    if 'Low compression' in processing_efficiency:
        recommendations.append("Consider more concise summarization of discussions")
    
    recommendations.append("Review all action items for clear ownership and deadlines")
    recommendations.append("Ensure all decisions are clearly documented with rationale")
    
    return recommendations


def _create_follow_up_summary(action_items: List[Dict]) -> Dict:
    """Create summary of follow-up items needed."""
    
    return {
        'immediate_follow_ups': [
            a for a in action_items 
            if a.get('priority') == 'high' or 'urgent' in a.get('description', '').lower()
        ],
        'weekly_follow_ups': [
            a for a in action_items 
            if 'week' in a.get('due_date', '').lower()
        ],
        'monthly_follow_ups': [
            a for a in action_items 
            if 'month' in a.get('due_date', '').lower()
        ],
        'follow_up_recommendations': [
            'Schedule follow-up meetings as needed',
            'Send action item reminders to assignees',
            'Track progress on key deliverables'
        ]
    }


def _get_distribution_list(meeting_type: str) -> List[str]:
    """Get typical distribution list for meeting type."""
    distributions = {
        'investigator': ['All Principal Investigators', 'Study Coordinators', 'Sponsor Representatives'],
        'safety': ['Safety Committee Members', 'Medical Monitor', 'Regulatory Team'],
        'steering_committee': ['Steering Committee Members', 'Study Leadership', 'Key Stakeholders'],
        'general': ['Meeting Attendees', 'Study Team', 'Relevant Stakeholders']
    }
    
    return distributions.get(meeting_type, distributions['general'])


def _get_confidentiality_notice(meeting_type: str) -> str:
    """Get confidentiality notice for meeting type."""
    if meeting_type == 'safety':
        return "CONFIDENTIAL: This document contains safety information subject to regulatory requirements."
    elif meeting_type == 'steering_committee':
        return "CONFIDENTIAL: This document contains strategic information for authorized personnel only."
    else:
        return "CONFIDENTIAL: This document contains study information for authorized personnel only."


def _get_minutes_html_styles(format_style: str) -> str:
    """Get HTML styles for meeting minutes."""
    
    base_styles = """
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        margin: 20px;
        color: #333;
    }
    .header {
        border-bottom: 2px solid #007cba;
        padding-bottom: 20px;
        margin-bottom: 20px;
    }
    .section {
        margin-bottom: 25px;
        padding: 15px;
        border-left: 3px solid #007cba;
        background-color: #f9f9f9;
    }
    .action-items-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
    }
    .action-items-table th,
    .action-items-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    .action-items-table th {
        background-color: #007cba;
        color: white;
    }
    .priority-high {
        background-color: #ffebee;
    }
    .priority-medium {
        background-color: #fff3e0;
    }
    .priority-low {
        background-color: #e8f5e8;
    }
    .footer {
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #ccc;
        font-size: 0.9em;
        color: #666;
    }
    """
    
    style_variants = {
        'formal': """
        h1, h2 { color: #333; }
        .header { background-color: #f8f9fa; padding: 20px; }
        """,
        'detailed': """
        .section { background-color: #ffffff; border: 1px solid #ddd; }
        .discussion { font-style: italic; margin: 10px 0; }
        """,
        'executive_summary': """
        .section { padding: 10px; }
        h2 { color: #007cba; }
        """,
        'action_focused': """
        .action-items-table { border: 2px solid #007cba; }
        .priority-high { font-weight: bold; }
        """
    }
    
    return base_styles + style_variants.get(format_style, '')


# Additional formatting helper functions

def _format_attendees_html(attendees: Dict) -> str:
    """Format attendees section as HTML."""
    html = "<h3>Present:</h3><ul>"
    
    for attendee in attendees.get('present', []):
        html += f"<li>{attendee.get('name', 'TBD')} - {attendee.get('role', 'TBD')}"
        if attendee.get('organization', 'TBD') != 'TBD':
            html += f" ({attendee['organization']})"
        html += "</li>"
    
    html += "</ul>"
    
    if attendees.get('absent_with_apology'):
        html += "<h3>Apologies:</h3><ul>"
        for attendee in attendees['absent_with_apology']:
            html += f"<li>{attendee.get('name', 'TBD')} - {attendee.get('role', 'TBD')}</li>"
        html += "</ul>"
    
    return html


def _format_agenda_review_html(agenda_review: Dict) -> str:
    """Format agenda review section as HTML."""
    html = "<table><thead><tr><th>Item</th><th>Title</th><th>Presenter</th><th>Status</th></tr></thead><tbody>"
    
    for item in agenda_review.get('agenda_items', []):
        html += f"""
        <tr>
            <td>{item.get('item_number', 'TBD')}</td>
            <td>{item.get('title', 'TBD')}</td>
            <td>{item.get('presenter', 'TBD')}</td>
            <td>{item.get('status', 'Discussed')}</td>
        </tr>
        """
    
    html += "</tbody></table>"
    return html


def _format_attendees_markdown(attendees: Dict) -> str:
    """Format attendees section as Markdown."""
    markdown = "### Present:\n\n"
    
    for attendee in attendees.get('present', []):
        markdown += f"- {attendee.get('name', 'TBD')} - {attendee.get('role', 'TBD')}"
        if attendee.get('organization', 'TBD') != 'TBD':
            markdown += f" ({attendee['organization']})"
        markdown += "\n"
    
    if attendees.get('absent_with_apology'):
        markdown += "\n### Apologies:\n\n"
        for attendee in attendees['absent_with_apology']:
            markdown += f"- {attendee.get('name', 'TBD')} - {attendee.get('role', 'TBD')}\n"
    
    return markdown


def _format_agenda_review_markdown(agenda_review: Dict) -> str:
    """Format agenda review section as Markdown."""
    markdown = "| Item | Title | Presenter | Status |\n|------|-------|-----------|--------|\n"
    
    for item in agenda_review.get('agenda_items', []):
        markdown += f"| {item.get('item_number', 'TBD')} | {item.get('title', 'TBD')} | {item.get('presenter', 'TBD')} | {item.get('status', 'Discussed')} |\n"
    
    return markdown


def _format_attendees_text(attendees: Dict) -> str:
    """Format attendees section as text."""
    text = "Present:\n"
    
    for attendee in attendees.get('present', []):
        text += f"- {attendee.get('name', 'TBD')} - {attendee.get('role', 'TBD')}"
        if attendee.get('organization', 'TBD') != 'TBD':
            text += f" ({attendee['organization']})"
        text += "\n"
    
    if attendees.get('absent_with_apology'):
        text += "\nApologies:\n"
        for attendee in attendees['absent_with_apology']:
            text += f"- {attendee.get('name', 'TBD')} - {attendee.get('role', 'TBD')}\n"
    
    return text


def _format_agenda_review_text(agenda_review: Dict) -> str:
    """Format agenda review section as text."""
    text = ""
    
    for i, item in enumerate(agenda_review.get('agenda_items', []), 1):
        text += f"{i}. {item.get('title', 'TBD')}\n"
        text += f"   Presenter: {item.get('presenter', 'TBD')}\n"
        text += f"   Status: {item.get('status', 'Discussed')}\n\n"
    
    return text


# Additional analysis and extraction functions

def _extract_key_topics(notes: str, agenda: List[Dict]) -> List[str]:
    """Extract key topics discussed."""
    topics = []
    
    # Add agenda items as topics
    for item in agenda:
        topic = item.get('title', item.get('topic', ''))
        if topic:
            topics.append(topic)
    
    # Extract additional topics from notes
    topic_indicators = [
        r'(?:topic|subject|discuss(?:ed|ing)?)[:\s]*(.+?)(?:\.|$)',
        r'(?:regarding|about|concerning)[:\s]*(.+?)(?:\.|$)'
    ]
    
    for pattern in topic_indicators:
        matches = re.finditer(pattern, notes, re.IGNORECASE)
        for match in matches:
            topic = match.group(1).strip()
            if len(topic) > 3 and len(topic) < 100:
                topics.append(topic)
    
    # Remove duplicates and return
    return list(set(topics))


def _identify_main_discussions(notes: str, meeting_type: str) -> List[Dict]:
    """Identify main discussions from notes."""
    # This is a simplified implementation
    discussions = []
    
    # Split notes into potential discussion blocks
    blocks = notes.split('\n\n')
    
    for i, block in enumerate(blocks):
        if len(block.strip()) > 100:  # Substantial content
            discussions.append({
                'id': f'discussion_{i+1}',
                'content': block.strip(),
                'estimated_duration': f'{len(block.split()) // 100 + 1} minutes',
                'key_participants': _extract_speakers_from_block(block)
            })
    
    return discussions


def _extract_speakers_from_block(text_block: str) -> List[str]:
    """Extract speaker names from text block."""
    # Simple pattern matching for names
    speaker_patterns = [
        r'([A-Z][a-z]+)\s+said',
        r'([A-Z][a-z]+)\s+mentioned',
        r'([A-Z][a-z]+)\s+noted'
    ]
    
    speakers = set()
    
    for pattern in speaker_patterns:
        matches = re.finditer(pattern, text_block)
        for match in matches:
            speaker = match.group(1)
            if len(speaker) > 2:
                speakers.add(speaker)
    
    return list(speakers)


def _create_executive_summary(key_topics: List[str], main_discussions: List[Dict], 
                            meeting_type: str) -> str:
    """Create executive summary of meeting."""
    
    summary = f"This {meeting_type.replace('_', ' ')} meeting covered {len(key_topics)} main topics. "
    
    if key_topics:
        top_topics = key_topics[:3]  # Top 3 topics
        summary += f"Key areas of focus included: {', '.join(top_topics)}. "
    
    summary += f"The meeting included {len(main_discussions)} substantial discussions "
    summary += "with active participation from attendees. "
    
    # Add meeting type specific summary elements
    if meeting_type == 'safety':
        summary += "Safety reviews and risk assessments were primary focus areas."
    elif meeting_type == 'investigator':
        summary += "Protocol compliance and site performance were key discussion points."
    elif meeting_type == 'steering_committee':
        summary += "Strategic decisions and governance matters were addressed."
    
    return summary


def _extract_key_points(notes: str, agenda: List[Dict]) -> List[str]:
    """Extract key points from meeting notes."""
    key_points = []
    
    # Look for explicit key point indicators
    key_point_patterns = [
        r'(?:key point|important|note)[:\s]*(.+?)(?:\.|$)',
        r'(?:highlight|emphasis|focus)[:\s]*(.+?)(?:\.|$)',
        r'(?:main|primary|principal)[:\s]*(.+?)(?:\.|$)'
    ]
    
    for pattern in key_point_patterns:
        matches = re.finditer(pattern, notes, re.IGNORECASE)
        for match in matches:
            point = match.group(1).strip()
            if len(point) > 10:
                key_points.append(point)
    
    # Extract points from agenda items
    for item in agenda:
        if 'objectives' in item:
            key_points.extend(item['objectives'])
    
    return key_points[:10]  # Limit to top 10


def _identify_meeting_outcomes(notes: str, discussions: List[Dict]) -> List[str]:
    """Identify meeting outcomes."""
    outcomes = []
    
    outcome_patterns = [
        r'(?:outcome|result|conclusion)[:\s]*(.+?)(?:\.|$)',
        r'(?:end result|final)[:\s]*(.+?)(?:\.|$)',
        r'(?:achieved|accomplished)[:\s]*(.+?)(?:\.|$)'
    ]
    
    for pattern in outcome_patterns:
        matches = re.finditer(pattern, notes, re.IGNORECASE)
        for match in matches:
            outcome = match.group(1).strip()
            if len(outcome) > 10:
                outcomes.append(outcome)
    
    return outcomes


def _analyze_participation(notes: str) -> Dict:
    """Analyze participation patterns in meeting."""
    # Simple analysis - count speaking indicators
    speaking_indicators = ['said', 'mentioned', 'noted', 'asked', 'responded', 'suggested']
    
    total_speaking_instances = 0
    for indicator in speaking_indicators:
        total_speaking_instances += notes.lower().count(indicator)
    
    return {
        'estimated_speaking_instances': total_speaking_instances,
        'participation_level': 'High' if total_speaking_instances > 20 else 'Moderate' if total_speaking_instances > 10 else 'Low',
        'discussion_balance': 'Active discussion observed' if total_speaking_instances > 15 else 'Limited discussion recorded'
    }


def _analyze_time_spent_on_topics(notes: str, agenda: List[Dict]) -> Dict:
    """Analyze estimated time spent on topics."""
    time_analysis = {}
    
    for item in agenda:
        topic = item.get('title', 'Unknown Topic')
        allocated_time = item.get('time_allocated', 'Unknown')
        
        # Estimate actual time based on content volume
        topic_content = _extract_discussion_for_agenda_item(notes, item)
        estimated_time = max(5, len(topic_content.split()) // 50)  # Rough estimate
        
        time_analysis[topic] = {
            'allocated_time': allocated_time,
            'estimated_actual_time': f'{estimated_time} minutes',
            'content_volume': len(topic_content.split())
        }
    
    return time_analysis


def _calculate_summary_statistics(summary: Dict) -> Dict:
    """Calculate statistics for meeting summary."""
    return {
        'topics_covered': len(summary.get('key_topics_discussed', [])),
        'main_discussions': len(summary.get('main_discussions', [])),
        'key_points_identified': len(summary.get('key_points', [])),
        'outcomes_recorded': len(summary.get('meeting_outcomes', [])),
        'summary_completeness': 'Comprehensive' if len(summary.get('key_topics_discussed', [])) > 3 else 'Basic'
    }


def _generate_meeting_insights(summary: Dict, meeting_type: str) -> List[str]:
    """Generate insights from meeting summary."""
    insights = []
    
    topics = summary.get('key_topics_discussed', [])
    if len(topics) > 5:
        insights.append(f"Meeting covered extensive agenda with {len(topics)} topics")
    elif len(topics) < 2:
        insights.append("Meeting had focused agenda with limited topics")
    
    discussions = summary.get('main_discussions', [])
    avg_discussion_length = sum(len(d.get('content', '').split()) for d in discussions) // len(discussions) if discussions else 0
    
    if avg_discussion_length > 200:
        insights.append("Discussions were detailed and thorough")
    elif avg_discussion_length < 50:
        insights.append("Discussions were brief and focused")
    
    participation = summary.get('attendance_summary', {})
    if participation.get('participation_level') == 'High':
        insights.append("Meeting showed high participant engagement")
    
    return insights


# Additional helper functions for various meeting types

def _add_safety_meeting_sections(sections: Dict, structured_content: Dict) -> Dict:
    """Add safety-specific sections."""
    sections['Safety Data Review'] = {
        'content': 'Review of safety data and adverse events',
        'summary': 'Safety data reviewed according to protocol requirements'
    }
    
    sections['Risk Assessment'] = {
        'content': 'Assessment of study risks and mitigation strategies',
        'summary': 'Risk assessment completed with appropriate mitigation plans'
    }
    
    return sections


def _add_steering_committee_sections(sections: Dict, structured_content: Dict) -> Dict:
    """Add steering committee-specific sections."""
    sections['Governance Review'] = {
        'content': 'Review of governance matters and oversight responsibilities',
        'summary': 'Governance items reviewed and decisions made'
    }
    
    sections['Strategic Planning'] = {
        'content': 'Strategic planning and future direction discussions',
        'summary': 'Strategic plans reviewed and updated'
    }
    
    return sections


def _add_investigator_meeting_sections(sections: Dict, structured_content: Dict) -> Dict:
    """Add investigator meeting-specific sections."""
    sections['Site Performance'] = {
        'content': 'Review of site performance metrics and enrollment status',
        'summary': 'Site performance reviewed with feedback provided'
    }
    
    sections['Protocol Training'] = {
        'content': 'Protocol training updates and education items',
        'summary': 'Training requirements reviewed and scheduled'
    }
    
    return sections


def _categorize_action_items(action_items: List[Dict]) -> Dict:
    """Categorize action items by type."""
    categories = {}
    
    for action in action_items:
        category = action.get('category', 'general')
        if category not in categories:
            categories[category] = []
        categories[category].append(action)
    
    return categories


def _prioritize_action_items(action_items: List[Dict], meeting_type: str) -> List[Dict]:
    """Sort action items by priority and urgency."""
    priority_order = {'high': 3, 'medium': 2, 'low': 1}
    
    return sorted(action_items, key=lambda x: (
        priority_order.get(x.get('priority', 'medium'), 2),
        x.get('due_date', 'ZZZ')  # Sort unknown dates last
    ), reverse=True)


def _create_action_tracking_info(action_items: List[Dict]) -> Dict:
    """Create action tracking information."""
    return {
        'total_actions': len(action_items),
        'by_priority': {
            'high': len([a for a in action_items if a.get('priority') == 'high']),
            'medium': len([a for a in action_items if a.get('priority') == 'medium']),
            'low': len([a for a in action_items if a.get('priority') == 'low'])
        },
        'by_category': dict(Counter(a.get('category', 'general') for a in action_items)),
        'assigned_actions': len([a for a in action_items if a.get('assignee', 'TBD') != 'TBD']),
        'unassigned_actions': len([a for a in action_items if a.get('assignee', 'TBD') == 'TBD']),
        'tracking_recommendations': [
            'Send action item summary to all assignees',
            'Schedule follow-up check-ins for high-priority items',
            'Update action status before next meeting'
        ]
    }


def _generate_action_item_recommendations(action_items: List[Dict]) -> List[str]:
    """Generate recommendations for action item management."""
    recommendations = []
    
    unassigned_count = len([a for a in action_items if a.get('assignee', 'TBD') == 'TBD'])
    if unassigned_count > 0:
        recommendations.append(f"Assign owners to {unassigned_count} unassigned action items")
    
    no_due_date_count = len([a for a in action_items if a.get('due_date', 'TBD') == 'TBD'])
    if no_due_date_count > 0:
        recommendations.append(f"Set due dates for {no_due_date_count} action items")
    
    high_priority_count = len([a for a in action_items if a.get('priority') == 'high'])
    if high_priority_count > 0:
        recommendations.append(f"Focus immediate attention on {high_priority_count} high-priority items")
    
    recommendations.append("Distribute action item summary within 24 hours")
    recommendations.append("Track progress and report status at next meeting")
    
    return recommendations


def _determine_agenda_item_status(item: Dict, structured_content: Dict) -> str:
    """Determine status of agenda item."""
    item_id = item.get('id', '')
    agenda_content = structured_content.get('agenda_based_content', {})
    
    if item_id in agenda_content:
        content = agenda_content[item_id]
        if content.get('discussion') and len(content['discussion']) > 50:
            return 'Discussed'
        else:
            return 'Mentioned'
    else:
        return 'Not Covered'


def _get_agenda_item_summary(item: Dict, structured_content: Dict) -> str:
    """Get summary for agenda item."""
    item_id = item.get('id', '')
    agenda_content = structured_content.get('agenda_based_content', {})
    
    if item_id in agenda_content:
        discussion = agenda_content[item_id].get('discussion', '')
        if discussion:
            # Create brief summary
            sentences = discussion.split('.')[:2]  # First 2 sentences
            return '. '.join(sentences) + '.' if sentences else 'Brief discussion held'
    
    return 'No detailed discussion recorded'


def _determine_next_meeting_info(meeting_info: Dict) -> Dict:
    """Determine next meeting information."""
    frequency = meeting_info.get('frequency', 'monthly')
    current_date = meeting_info.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Calculate next meeting date
    try:
        current = datetime.strptime(current_date, '%Y-%m-%d')
        
        if frequency == 'weekly':
            next_date = current + timedelta(weeks=1)
        elif frequency == 'monthly':
            next_date = current + timedelta(days=30)  # Approximation
        elif frequency == 'quarterly':
            next_date = current + timedelta(days=90)  # Approximation
        else:
            next_date = current + timedelta(days=30)  # Default
        
        next_date_str = next_date.strftime('%Y-%m-%d')
    except:
        next_date_str = 'TBD'
    
    return {
        'estimated_date': next_date_str,
        'frequency': frequency,
        'location': meeting_info.get('location', 'TBD'),
        'tentative_agenda_items': [
            'Review action items from this meeting',
            'Regular business items',
            'New business'
        ]
    }


def _identify_follow_up_requirements(action_items: List[Dict]) -> List[str]:
    """Identify follow-up requirements."""
    requirements = []
    
    immediate_actions = [a for a in action_items if a.get('priority') == 'high']
    if immediate_actions:
        requirements.append(f"Monitor progress on {len(immediate_actions)} high-priority actions")
    
    pending_assignments = [a for a in action_items if a.get('assignee', 'TBD') == 'TBD']
    if pending_assignments:
        requirements.append(f"Assign owners to {len(pending_assignments)} action items")
    
    requirements.append("Send meeting minutes to all attendees within 48 hours")
    requirements.append("Schedule follow-up meetings as needed")
    
    return requirements


def _extract_reporting_deadlines(action_items: List[Dict], meeting_info: Dict) -> List[Dict]:
    """Extract reporting deadlines from action items."""
    deadlines = []
    
    for action in action_items:
        due_date = action.get('due_date', 'TBD')
        if due_date != 'TBD' and 'report' in action.get('description', '').lower():
            deadlines.append({
                'action': action.get('description', ''),
                'assignee': action.get('assignee', 'TBD'),
                'due_date': due_date,
                'type': 'report'
            })
    
    return deadlines


def _extract_key_points_from_discussion(discussion: str) -> List[str]:
    """Extract key points from discussion text."""
    if not discussion or len(discussion) < 50:
        return ['No detailed discussion recorded']
    
    # Simple extraction - split into sentences and take substantive ones
    sentences = [s.strip() for s in discussion.split('.') if len(s.strip()) > 20]
    
    # Return up to 3 key sentences
    return sentences[:3] if sentences else ['Discussion held but details not captured']


def _format_minutes_pdf_ready(minutes: Dict, format_style: str) -> str:
    """Format minutes ready for PDF conversion."""
    html = _format_minutes_html(minutes, format_style)
    
    # Add PDF-specific styling
    pdf_styles = """
    <style>
    @media print {
        body { font-size: 11pt; }
        .header { page-break-inside: avoid; }
        .section { page-break-inside: avoid; }
        .action-items-table { page-break-inside: avoid; }
    }
    </style>
    """
    
    return html.replace('<head>', f'<head>{pdf_styles}')


def _format_minutes_docx_structure(minutes: Dict, format_style: str) -> Dict:
    """Format minutes as structure suitable for DOCX generation."""
    return {
        'document_title': minutes.get('header', {}).get('document_title', 'Meeting Minutes'),
        'sections': [
            {
                'title': 'Meeting Information',
                'content': _format_meeting_info_for_docx(minutes.get('header', {}))
            },
            {
                'title': 'Attendees',
                'content': _format_attendees_for_docx(minutes.get('attendees', {}))
            },
            {
                'title': 'Content Sections',
                'content': _format_content_sections_for_docx(minutes.get('content_sections', {}))
            },
            {
                'title': 'Action Items',
                'content': _format_action_items_for_docx(minutes.get('action_items', []))
            }
        ]
    }


def _format_meeting_info_for_docx(header: Dict) -> List[Dict]:
    """Format meeting info for DOCX structure."""
    return [
        {'type': 'paragraph', 'content': f"Meeting Type: {header.get('meeting_type', 'TBD')}"},
        {'type': 'paragraph', 'content': f"Date: {header.get('date', 'TBD')}"},
        {'type': 'paragraph', 'content': f"Time: {header.get('time', 'TBD')}"},
        {'type': 'paragraph', 'content': f"Location: {header.get('location', 'TBD')}"},
        {'type': 'paragraph', 'content': f"Chairperson: {header.get('chairperson', 'TBD')}"}
    ]


def _format_attendees_for_docx(attendees: Dict) -> List[Dict]:
    """Format attendees for DOCX structure."""
    content = [{'type': 'heading', 'level': 3, 'content': 'Present:'}]
    
    for attendee in attendees.get('present', []):
        content.append({
            'type': 'bullet_point',
            'content': f"{attendee.get('name', 'TBD')} - {attendee.get('role', 'TBD')}"
        })
    
    if attendees.get('absent_with_apology'):
        content.append({'type': 'heading', 'level': 3, 'content': 'Apologies:'})
        for attendee in attendees['absent_with_apology']:
            content.append({
                'type': 'bullet_point',
                'content': f"{attendee.get('name', 'TBD')} - {attendee.get('role', 'TBD')}"
            })
    
    return content


def _format_content_sections_for_docx(sections: Dict) -> List[Dict]:
    """Format content sections for DOCX structure."""
    content = []
    
    for section_name, section_data in sections.items():
        content.append({'type': 'heading', 'level': 2, 'content': section_name})
        
        if isinstance(section_data, dict):
            if 'discussion_summary' in section_data:
                content.append({'type': 'paragraph', 'content': section_data['discussion_summary']})
            
            if 'key_points' in section_data and section_data['key_points']:
                content.append({'type': 'heading', 'level': 3, 'content': 'Key Points:'})
                for point in section_data['key_points']:
                    content.append({'type': 'bullet_point', 'content': point})
    
    return content


def _format_action_items_for_docx(action_items: List[Dict]) -> List[Dict]:
    """Format action items for DOCX structure."""
    content = []
    
    if action_items:
        content.append({'type': 'table_header', 'columns': ['Action', 'Assigned To', 'Due Date', 'Priority']})
        
        for action in action_items:
            content.append({
                'type': 'table_row',
                'columns': [
                    action.get('description', 'TBD'),
                    action.get('assignee', 'TBD'),
                    action.get('due_date', 'TBD'),
                    action.get('priority', 'Medium').title()
                ]
            })
    else:
        content.append({'type': 'paragraph', 'content': 'No action items recorded'})
    
    return content


def _get_format_specific_notes(output_format: str) -> List[str]:
    """Get format-specific notes and recommendations."""
    notes = {
        'html': [
            'HTML format includes interactive styling',
            'Suitable for web distribution and viewing',
            'CSS styles embedded for consistent appearance'
        ],
        'markdown': [
            'Markdown format is platform-independent',
            'Easy to convert to other formats',
            'Version control friendly'
        ],
        'text': [
            'Plain text format for universal compatibility',
            'Suitable for email distribution',
            'No formatting dependencies'
        ],
        'pdf_ready': [
            'Optimized for PDF conversion',
            'Includes print-specific styling',
            'Page break considerations included'
        ],
        'docx_structure': [
            'Structured format for document generation',
            'Compatible with word processing software',
            'Maintains formatting hierarchy'
        ]
    }
    
    return notes.get(output_format, ['Standard formatting applied'])


def _get_template_usage_instructions(meeting_type: str) -> List[str]:
    """Get usage instructions for meeting minutes template."""
    return [
        f"Template designed for {meeting_type.replace('_', ' ')} meetings",
        "Fill in placeholder fields marked with [FIELD_NAME]",
        "Customize sections based on actual agenda items",
        "Review and approve minutes before distribution",
        "Archive completed minutes according to study requirements"
    ]


def _get_customization_options(meeting_type: str, format_style: str) -> Dict:
    """Get customization options for template."""
    return {
        'style_options': ['formal', 'detailed', 'executive_summary', 'action_focused'],
        'section_customization': 'Add or remove sections based on meeting content',
        'branding_options': 'Include study logo and institutional branding',
        'distribution_customization': 'Adjust distribution list based on attendees',
        'format_variations': ['html', 'markdown', 'text', 'pdf_ready', 'docx_structure']
    }