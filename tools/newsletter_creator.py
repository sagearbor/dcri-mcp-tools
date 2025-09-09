"""
Newsletter Creator Tool for Clinical Studies
Creates study newsletters with updates, announcements, and participant communications
"""

import re
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
from collections import Counter


def run(input_data: Dict) -> Dict:
    """
    Create study newsletters with updates and communications.
    
    Args:
        input_data: Dictionary containing:
            - action: 'create', 'template', 'format', 'schedule', 'analyze'
            - newsletter_type: 'participant', 'investigator', 'sponsor', 'general'
            - content_items: List of news items/updates
            - template_style: 'formal', 'friendly', 'clinical', 'brief'
            - frequency: 'weekly', 'monthly', 'quarterly', 'milestone'
            - study_info: Basic study information
            - format_options: Formatting preferences
            - distribution_list: Target audience info
    
    Returns:
        Dictionary with newsletter content and metadata
    """
    try:
        action = input_data.get('action', 'create').lower()
        newsletter_type = input_data.get('newsletter_type', 'general')
        content_items = input_data.get('content_items', [])
        template_style = input_data.get('template_style', 'friendly')
        frequency = input_data.get('frequency', 'monthly')
        study_info = input_data.get('study_info', {})
        format_options = input_data.get('format_options', {})
        distribution_list = input_data.get('distribution_list', {})
        
        result = {'success': True, 'action': action}
        
        if action == 'create':
            result.update(_create_newsletter(
                newsletter_type, content_items, template_style, frequency, 
                study_info, format_options
            ))
        elif action == 'template':
            result.update(_generate_newsletter_template(
                newsletter_type, template_style, frequency
            ))
        elif action == 'format':
            result.update(_format_newsletter(content_items, format_options))
        elif action == 'schedule':
            result.update(_create_newsletter_schedule(frequency, study_info))
        elif action == 'analyze':
            result.update(_analyze_newsletter_performance(content_items))
        else:
            return {
                'success': False,
                'error': f'Unknown action: {action}',
                'valid_actions': ['create', 'template', 'format', 'schedule', 'analyze']
            }
        
        # Add metadata
        result['metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'newsletter_type': newsletter_type,
            'template_style': template_style,
            'frequency': frequency,
            'content_items_count': len(content_items)
        }
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error creating newsletter: {str(e)}'
        }


def _create_newsletter(newsletter_type: str, content_items: List[Dict], 
                      template_style: str, frequency: str, study_info: Dict,
                      format_options: Dict) -> Dict:
    """Create a complete newsletter."""
    
    # Get newsletter template
    template = _get_newsletter_template(newsletter_type, template_style, frequency)
    
    # Process content items
    processed_content = _process_content_items(content_items, newsletter_type, template_style)
    
    # Create newsletter sections
    sections = _create_newsletter_sections(processed_content, newsletter_type, template_style)
    
    # Generate header and footer
    header = _create_newsletter_header(study_info, newsletter_type, frequency)
    footer = _create_newsletter_footer(study_info, newsletter_type)
    
    # Assemble newsletter
    newsletter_content = _assemble_newsletter(
        header, sections, footer, template_style, format_options
    )
    
    # Generate different formats
    formatted_versions = {
        'html': _format_as_html(newsletter_content, template_style),
        'text': _format_as_text(newsletter_content),
        'markdown': _format_as_markdown(newsletter_content),
        'pdf_ready': _format_for_pdf(newsletter_content, template_style)
    }
    
    # Calculate newsletter statistics
    statistics = _calculate_newsletter_statistics(newsletter_content, content_items)
    
    return {
        'newsletter_content': newsletter_content,
        'formatted_versions': formatted_versions,
        'statistics': statistics,
        'distribution_info': _generate_distribution_info(newsletter_type),
        'recommendations': _generate_newsletter_recommendations(sections, statistics)
    }


def _generate_newsletter_template(newsletter_type: str, template_style: str, 
                                frequency: str) -> Dict:
    """Generate a newsletter template."""
    
    template = {
        'structure': _get_template_structure(newsletter_type),
        'style_guide': _get_style_guide(template_style),
        'content_guidelines': _get_content_guidelines(newsletter_type),
        'frequency_recommendations': _get_frequency_recommendations(frequency),
        'sample_sections': _get_sample_sections(newsletter_type, template_style)
    }
    
    return {
        'template': template,
        'template_type': newsletter_type,
        'style': template_style,
        'frequency': frequency,
        'usage_notes': _get_template_usage_notes(newsletter_type, template_style)
    }


def _format_newsletter(content_items: List[Dict], format_options: Dict) -> Dict:
    """Format newsletter content in various formats."""
    
    formatted_content = {}
    
    # Process each content item
    for item in content_items:
        item_id = item.get('id', f'item_{len(formatted_content)}')
        formatted_content[item_id] = {
            'original': item,
            'html': _format_content_item_html(item, format_options),
            'text': _format_content_item_text(item),
            'markdown': _format_content_item_markdown(item)
        }
    
    return {
        'formatted_content': formatted_content,
        'format_options': format_options,
        'formatting_notes': _get_formatting_notes(format_options)
    }


def _create_newsletter_schedule(frequency: str, study_info: Dict) -> Dict:
    """Create a newsletter publication schedule."""
    
    study_start = study_info.get('start_date')
    study_end = study_info.get('end_date')
    
    if not study_start:
        study_start = datetime.now().isoformat()
    
    # Convert string dates to datetime
    if isinstance(study_start, str):
        study_start = datetime.fromisoformat(study_start.replace('Z', '+00:00'))
    if isinstance(study_end, str) and study_end:
        study_end = datetime.fromisoformat(study_end.replace('Z', '+00:00'))
    
    # Calculate publication dates
    publication_dates = _calculate_publication_dates(frequency, study_start, study_end)
    
    # Create schedule with themes
    schedule = []
    for i, date in enumerate(publication_dates):
        issue_number = i + 1
        theme = _determine_newsletter_theme(issue_number, frequency, date, study_start)
        
        schedule.append({
            'issue_number': issue_number,
            'publication_date': date.isoformat(),
            'theme': theme,
            'suggested_content': _get_suggested_content_for_theme(theme),
            'deadline': (date - timedelta(days=7)).isoformat(),  # One week before publication
            'status': 'planned'
        })
    
    return {
        'publication_schedule': schedule,
        'frequency': frequency,
        'total_issues_planned': len(schedule),
        'schedule_summary': _create_schedule_summary(schedule, frequency)
    }


def _analyze_newsletter_performance(content_items: List[Dict]) -> Dict:
    """Analyze newsletter content and performance."""
    
    analysis = {
        'content_analysis': _analyze_content_types(content_items),
        'engagement_metrics': _estimate_engagement_metrics(content_items),
        'readability_analysis': _analyze_readability(content_items),
        'content_balance': _analyze_content_balance(content_items),
        'trend_analysis': _analyze_content_trends(content_items)
    }
    
    recommendations = _generate_performance_recommendations(analysis)
    insights = _extract_performance_insights(analysis)
    
    return {
        'analysis': analysis,
        'recommendations': recommendations,
        'insights': insights,
        'performance_score': _calculate_performance_score(analysis)
    }


def _get_newsletter_template(newsletter_type: str, template_style: str, 
                           frequency: str) -> Dict:
    """Get newsletter template configuration."""
    
    templates = {
        'participant': {
            'friendly': {
                'greeting': 'Dear Study Participants,',
                'tone': 'warm and encouraging',
                'sections': ['welcome', 'study_updates', 'participant_spotlight', 'upcoming_events', 'contact_info'],
                'closing': 'Thank you for your continued participation!'
            },
            'formal': {
                'greeting': 'Dear Participants,',
                'tone': 'professional and informative',
                'sections': ['introduction', 'study_progress', 'important_updates', 'resources', 'contact_information'],
                'closing': 'Sincerely, The Research Team'
            }
        },
        'investigator': {
            'clinical': {
                'greeting': 'Dear Principal Investigators and Study Staff,',
                'tone': 'professional and detailed',
                'sections': ['protocol_updates', 'enrollment_status', 'regulatory_updates', 'training_announcements', 'contact_information'],
                'closing': 'Best regards, Study Leadership'
            },
            'brief': {
                'greeting': 'Study Team,',
                'tone': 'concise and action-oriented',
                'sections': ['key_updates', 'action_items', 'deadlines', 'resources'],
                'closing': 'Thank you for your dedication'
            }
        }
    }
    
    # Get base template or create default
    base_template = templates.get(newsletter_type, {}).get(template_style, {
        'greeting': 'Dear Recipients,',
        'tone': 'professional',
        'sections': ['updates', 'announcements', 'contact_info'],
        'closing': 'Best regards'
    })
    
    return base_template


def _process_content_items(content_items: List[Dict], newsletter_type: str, 
                          template_style: str) -> List[Dict]:
    """Process and enhance content items."""
    
    processed_items = []
    
    for item in content_items:
        processed_item = item.copy()
        
        # Standardize content structure
        processed_item['id'] = item.get('id', f'content_{len(processed_items)}')
        processed_item['title'] = item.get('title', item.get('headline', 'Update'))
        processed_item['content'] = item.get('content', item.get('text', item.get('description', '')))
        processed_item['type'] = item.get('type', _determine_content_type(processed_item))
        processed_item['priority'] = item.get('priority', 'medium')
        processed_item['target_audience'] = item.get('target_audience', newsletter_type)
        
        # Add formatting based on style
        processed_item['formatted_title'] = _format_title_for_style(
            processed_item['title'], template_style
        )
        processed_item['formatted_content'] = _format_content_for_style(
            processed_item['content'], template_style, newsletter_type
        )
        
        # Add metadata
        processed_item['word_count'] = len(processed_item['content'].split())
        processed_item['estimated_read_time'] = max(1, processed_item['word_count'] // 200)
        processed_item['urgency'] = _assess_content_urgency(processed_item)
        
        processed_items.append(processed_item)
    
    # Sort by priority and urgency
    processed_items.sort(key=lambda x: (
        {'high': 3, 'medium': 2, 'low': 1}.get(x.get('priority', 'medium'), 2),
        {'urgent': 3, 'important': 2, 'normal': 1}.get(x.get('urgency', 'normal'), 1)
    ), reverse=True)
    
    return processed_items


def _create_newsletter_sections(content_items: List[Dict], newsletter_type: str, 
                               template_style: str) -> Dict:
    """Create organized newsletter sections."""
    
    sections = {}
    
    # Group content by type and importance
    content_groups = _group_content_by_type(content_items)
    
    # Create sections based on newsletter type
    if newsletter_type == 'participant':
        sections = _create_participant_sections(content_groups, template_style)
    elif newsletter_type == 'investigator':
        sections = _create_investigator_sections(content_groups, template_style)
    elif newsletter_type == 'sponsor':
        sections = _create_sponsor_sections(content_groups, template_style)
    else:
        sections = _create_general_sections(content_groups, template_style)
    
    # Add section metadata
    for section_name, section_content in sections.items():
        sections[section_name] = {
            'content': section_content,
            'word_count': sum(len(item.get('content', '').split()) for item in section_content if isinstance(item, dict)),
            'item_count': len(section_content) if isinstance(section_content, list) else 1,
            'priority': _calculate_section_priority(section_content)
        }
    
    return sections


def _create_newsletter_header(study_info: Dict, newsletter_type: str, 
                             frequency: str) -> Dict:
    """Create newsletter header."""
    
    study_name = study_info.get('name', study_info.get('title', 'Clinical Study'))
    study_id = study_info.get('id', study_info.get('protocol_number', 'STUDY-001'))
    issue_date = datetime.now().strftime('%B %Y')
    
    # Determine issue number based on frequency and date
    issue_number = _calculate_issue_number(frequency, study_info.get('start_date'))
    
    header = {
        'study_name': study_name,
        'study_id': study_id,
        'newsletter_title': _get_newsletter_title(newsletter_type, frequency),
        'issue_number': issue_number,
        'issue_date': issue_date,
        'logo_placeholder': '[STUDY_LOGO]',
        'tagline': _get_newsletter_tagline(newsletter_type)
    }
    
    return header


def _create_newsletter_footer(study_info: Dict, newsletter_type: str) -> Dict:
    """Create newsletter footer."""
    
    contact_info = study_info.get('contact_info', {})
    
    footer = {
        'contact_information': {
            'phone': contact_info.get('phone', '[STUDY_PHONE]'),
            'email': contact_info.get('email', '[STUDY_EMAIL]'),
            'website': contact_info.get('website', '[STUDY_WEBSITE]'),
            'address': contact_info.get('address', '[STUDY_ADDRESS]')
        },
        'unsubscribe_info': _get_unsubscribe_text(newsletter_type),
        'privacy_notice': 'Your privacy is important to us. This newsletter contains study-related information.',
        'copyright': f'© {datetime.now().year} {study_info.get("institution", "[INSTITUTION]")}',
        'social_media_links': study_info.get('social_media', {})
    }
    
    return footer


def _assemble_newsletter(header: Dict, sections: Dict, footer: Dict, 
                        template_style: str, format_options: Dict) -> Dict:
    """Assemble complete newsletter."""
    
    newsletter = {
        'header': header,
        'greeting': _get_greeting_for_style(template_style),
        'introduction': _generate_newsletter_introduction(header, template_style),
        'sections': sections,
        'conclusion': _generate_newsletter_conclusion(template_style),
        'footer': footer,
        'metadata': {
            'total_word_count': _calculate_total_word_count(sections),
            'estimated_read_time': _calculate_total_read_time(sections),
            'section_count': len(sections),
            'creation_date': datetime.now().isoformat()
        }
    }
    
    return newsletter


def _format_as_html(newsletter: Dict, template_style: str) -> str:
    """Format newsletter as HTML."""
    
    header = newsletter.get('header', {})
    sections = newsletter.get('sections', {})
    footer = newsletter.get('footer', {})
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{header.get('newsletter_title', 'Newsletter')}</title>
        <style>
            {_get_html_styles(template_style)}
        </style>
    </head>
    <body>
        <!-- Header -->
        <div class="header">
            <h1>{header.get('study_name', 'Study Newsletter')}</h1>
            <h2>{header.get('newsletter_title', 'Newsletter')}</h2>
            <p>Issue #{header.get('issue_number', 1)} - {header.get('issue_date', 'Current Issue')}</p>
        </div>
        
        <!-- Greeting -->
        <div class="greeting">
            {newsletter.get('greeting', 'Dear Recipients,')}
        </div>
        
        <!-- Introduction -->
        <div class="introduction">
            {newsletter.get('introduction', 'Welcome to this issue of our newsletter.')}
        </div>
        
        <!-- Content Sections -->
        <div class="content">
    """
    
    # Add sections
    for section_name, section_data in sections.items():
        html += f"""
        <div class="section">
            <h3>{section_name.replace('_', ' ').title()}</h3>
        """
        
        section_content = section_data.get('content', [])
        if isinstance(section_content, list):
            for item in section_content:
                if isinstance(item, dict):
                    html += f"""
                    <div class="content-item">
                        <h4>{item.get('title', 'Update')}</h4>
                        <p>{item.get('content', '')}</p>
                    </div>
                    """
                else:
                    html += f"<p>{item}</p>"
        else:
            html += f"<p>{section_content}</p>"
        
        html += "</div>"
    
    # Add conclusion and footer
    html += f"""
        </div>
        
        <!-- Conclusion -->
        <div class="conclusion">
            {newsletter.get('conclusion', 'Thank you for reading!')}
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <div class="contact-info">
                <h4>Contact Information</h4>
                <p>Phone: {footer.get('contact_information', {}).get('phone', '[PHONE]')}</p>
                <p>Email: {footer.get('contact_information', {}).get('email', '[EMAIL]')}</p>
            </div>
            <div class="legal">
                <p>{footer.get('privacy_notice', '')}</p>
                <p>{footer.get('copyright', '')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def _format_as_text(newsletter: Dict) -> str:
    """Format newsletter as plain text."""
    
    header = newsletter.get('header', {})
    sections = newsletter.get('sections', {})
    footer = newsletter.get('footer', {})
    
    text = f"""
{header.get('study_name', 'Study Newsletter').upper()}
{header.get('newsletter_title', 'Newsletter')}
Issue #{header.get('issue_number', 1)} - {header.get('issue_date', 'Current Issue')}

{newsletter.get('greeting', 'Dear Recipients,')}

{newsletter.get('introduction', 'Welcome to this issue of our newsletter.')}

"""
    
    # Add sections
    for section_name, section_data in sections.items():
        text += f"\n{section_name.replace('_', ' ').upper()}\n"
        text += "=" * len(section_name) + "\n\n"
        
        section_content = section_data.get('content', [])
        if isinstance(section_content, list):
            for item in section_content:
                if isinstance(item, dict):
                    text += f"{item.get('title', 'Update')}\n"
                    text += "-" * len(item.get('title', 'Update')) + "\n"
                    text += f"{item.get('content', '')}\n\n"
                else:
                    text += f"{item}\n\n"
        else:
            text += f"{section_content}\n\n"
    
    # Add conclusion and footer
    text += f"\n{newsletter.get('conclusion', 'Thank you for reading!')}\n\n"
    
    text += "CONTACT INFORMATION\n"
    text += "===================\n"
    contact_info = footer.get('contact_information', {})
    text += f"Phone: {contact_info.get('phone', '[PHONE]')}\n"
    text += f"Email: {contact_info.get('email', '[EMAIL]')}\n"
    text += f"\n{footer.get('privacy_notice', '')}\n"
    text += f"{footer.get('copyright', '')}\n"
    
    return text


def _format_as_markdown(newsletter: Dict) -> str:
    """Format newsletter as Markdown."""
    
    header = newsletter.get('header', {})
    sections = newsletter.get('sections', {})
    footer = newsletter.get('footer', {})
    
    markdown = f"""
# {header.get('study_name', 'Study Newsletter')}
## {header.get('newsletter_title', 'Newsletter')}

**Issue #{header.get('issue_number', 1)}** - {header.get('issue_date', 'Current Issue')}

---

{newsletter.get('greeting', 'Dear Recipients,')}

{newsletter.get('introduction', 'Welcome to this issue of our newsletter.')}

"""
    
    # Add sections
    for section_name, section_data in sections.items():
        markdown += f"\n## {section_name.replace('_', ' ').title()}\n\n"
        
        section_content = section_data.get('content', [])
        if isinstance(section_content, list):
            for item in section_content:
                if isinstance(item, dict):
                    markdown += f"### {item.get('title', 'Update')}\n\n"
                    markdown += f"{item.get('content', '')}\n\n"
                else:
                    markdown += f"{item}\n\n"
        else:
            markdown += f"{section_content}\n\n"
    
    # Add conclusion and footer
    markdown += f"\n---\n\n{newsletter.get('conclusion', 'Thank you for reading!')}\n\n"
    
    markdown += "## Contact Information\n\n"
    contact_info = footer.get('contact_information', {})
    markdown += f"- **Phone:** {contact_info.get('phone', '[PHONE]')}\n"
    markdown += f"- **Email:** {contact_info.get('email', '[EMAIL]')}\n"
    markdown += f"\n{footer.get('privacy_notice', '')}\n\n"
    markdown += f"*{footer.get('copyright', '')}*\n"
    
    return markdown


def _format_for_pdf(newsletter: Dict, template_style: str) -> str:
    """Format newsletter for PDF conversion."""
    # Return HTML optimized for PDF conversion
    html = _format_as_html(newsletter, template_style)
    
    # Add PDF-specific styles
    pdf_styles = """
    <style>
    @media print {
        .no-print { display: none; }
        body { font-size: 12pt; }
        h1 { page-break-before: always; }
    }
    </style>
    """
    
    return html.replace('<style>', pdf_styles + '<style>')


def _determine_content_type(item: Dict) -> str:
    """Determine the type of content item."""
    title = item.get('title', '').lower()
    content = item.get('content', '').lower()
    
    if any(word in title + content for word in ['enrollment', 'participant', 'recruit']):
        return 'enrollment_update'
    elif any(word in title + content for word in ['safety', 'adverse', 'side effect']):
        return 'safety_update'
    elif any(word in title + content for word in ['protocol', 'amendment', 'change']):
        return 'protocol_update'
    elif any(word in title + content for word in ['milestone', 'achievement', 'progress']):
        return 'milestone'
    elif any(word in title + content for word in ['event', 'meeting', 'conference']):
        return 'event_announcement'
    elif any(word in title + content for word in ['training', 'education', 'course']):
        return 'training_update'
    else:
        return 'general_update'


def _format_title_for_style(title: str, style: str) -> str:
    """Format title based on template style."""
    if style == 'friendly':
        return title  # Keep original friendly tone
    elif style == 'formal':
        return title.title()  # Title case for formal
    elif style == 'clinical':
        return title.upper()  # All caps for clinical
    elif style == 'brief':
        return title[:50] + '...' if len(title) > 50 else title  # Truncate for brief
    else:
        return title


def _format_content_for_style(content: str, style: str, newsletter_type: str) -> str:
    """Format content based on template style and type."""
    if style == 'friendly':
        # Add encouraging language
        if newsletter_type == 'participant':
            return content + " Thank you for your continued participation!"
    elif style == 'clinical':
        # Keep clinical, remove casual language
        content = re.sub(r'\b(great|awesome|fantastic)\b', 'significant', content, flags=re.IGNORECASE)
    elif style == 'brief':
        # Shorten content
        sentences = content.split('.')
        if len(sentences) > 2:
            content = '. '.join(sentences[:2]) + '.'
    
    return content


def _assess_content_urgency(item: Dict) -> str:
    """Assess the urgency of content."""
    content_text = (item.get('title', '') + ' ' + item.get('content', '')).lower()
    
    urgent_keywords = ['urgent', 'immediate', 'critical', 'emergency', 'asap']
    important_keywords = ['important', 'significant', 'deadline', 'reminder']
    
    if any(keyword in content_text for keyword in urgent_keywords):
        return 'urgent'
    elif any(keyword in content_text for keyword in important_keywords):
        return 'important'
    else:
        return 'normal'


def _group_content_by_type(content_items: List[Dict]) -> Dict:
    """Group content items by their type."""
    groups = {}
    
    for item in content_items:
        content_type = item.get('type', 'general_update')
        if content_type not in groups:
            groups[content_type] = []
        groups[content_type].append(item)
    
    return groups


def _create_participant_sections(content_groups: Dict, template_style: str) -> Dict:
    """Create sections for participant newsletters."""
    sections = {}
    
    # Study Updates section
    study_updates = []
    for update_type in ['enrollment_update', 'milestone', 'protocol_update']:
        if update_type in content_groups:
            study_updates.extend(content_groups[update_type])
    
    if study_updates:
        sections['Study Updates'] = study_updates
    
    # Safety Information
    if 'safety_update' in content_groups:
        sections['Safety Information'] = content_groups['safety_update']
    
    # Upcoming Events
    if 'event_announcement' in content_groups:
        sections['Upcoming Events'] = content_groups['event_announcement']
    
    # General Updates
    general_items = []
    for update_type in ['general_update', 'training_update']:
        if update_type in content_groups:
            general_items.extend(content_groups[update_type])
    
    if general_items:
        sections['General Updates'] = general_items
    
    # Add participant-specific content
    sections['Participant Resources'] = [{
        'title': 'Need Help?',
        'content': 'Remember that our study team is here to support you. Please don\'t hesitate to reach out if you have any questions or concerns.',
        'type': 'support_message'
    }]
    
    return sections


def _create_investigator_sections(content_groups: Dict, template_style: str) -> Dict:
    """Create sections for investigator newsletters."""
    sections = {}
    
    # Protocol Updates (highest priority)
    if 'protocol_update' in content_groups:
        sections['Protocol Updates'] = content_groups['protocol_update']
    
    # Enrollment Status
    if 'enrollment_update' in content_groups:
        sections['Enrollment Status'] = content_groups['enrollment_update']
    
    # Safety Updates
    if 'safety_update' in content_groups:
        sections['Safety Communications'] = content_groups['safety_update']
    
    # Training and Education
    if 'training_update' in content_groups:
        sections['Training Updates'] = content_groups['training_update']
    
    # Regulatory Communications
    regulatory_items = []
    for item in content_groups.get('general_update', []):
        if any(word in item.get('content', '').lower() for word in ['regulatory', 'compliance', 'audit']):
            regulatory_items.append(item)
    
    if regulatory_items:
        sections['Regulatory Updates'] = regulatory_items
    
    # Upcoming Events
    if 'event_announcement' in content_groups:
        sections['Upcoming Events'] = content_groups['event_announcement']
    
    return sections


def _create_sponsor_sections(content_groups: Dict, template_style: str) -> Dict:
    """Create sections for sponsor newsletters."""
    sections = {}
    
    # Executive Summary
    sections['Executive Summary'] = [{
        'title': 'Study Overview',
        'content': 'High-level summary of study progress and key metrics.',
        'type': 'executive_summary'
    }]
    
    # Enrollment Metrics
    if 'enrollment_update' in content_groups:
        sections['Enrollment Metrics'] = content_groups['enrollment_update']
    
    # Milestones and Achievements
    if 'milestone' in content_groups:
        sections['Milestones'] = content_groups['milestone']
    
    # Protocol and Regulatory Updates
    protocol_items = []
    for update_type in ['protocol_update', 'general_update']:
        if update_type in content_groups:
            protocol_items.extend(content_groups[update_type])
    
    if protocol_items:
        sections['Protocol and Regulatory'] = protocol_items
    
    # Risk Management
    if 'safety_update' in content_groups:
        sections['Risk Management'] = content_groups['safety_update']
    
    return sections


def _create_general_sections(content_groups: Dict, template_style: str) -> Dict:
    """Create general newsletter sections."""
    sections = {}
    
    # Main Updates
    main_updates = []
    for update_type in ['protocol_update', 'milestone', 'enrollment_update']:
        if update_type in content_groups:
            main_updates.extend(content_groups[update_type])
    
    if main_updates:
        sections['Study Updates'] = main_updates
    
    # Announcements
    announcements = []
    for update_type in ['event_announcement', 'training_update']:
        if update_type in content_groups:
            announcements.extend(content_groups[update_type])
    
    if announcements:
        sections['Announcements'] = announcements
    
    # Other Updates
    if 'general_update' in content_groups:
        sections['Other Updates'] = content_groups['general_update']
    
    return sections


def _calculate_publication_dates(frequency: str, start_date: datetime, 
                               end_date: Optional[datetime] = None) -> List[datetime]:
    """Calculate publication dates based on frequency."""
    dates = []
    current_date = start_date
    
    # Set end date if not provided (2 years from start)
    if not end_date:
        end_date = start_date + timedelta(days=730)
    
    # Calculate interval based on frequency
    if frequency == 'weekly':
        interval = timedelta(weeks=1)
    elif frequency == 'monthly':
        interval = timedelta(days=30)  # Approximation
    elif frequency == 'quarterly':
        interval = timedelta(days=90)  # Approximation
    elif frequency == 'milestone':
        # For milestone-based, create quarterly schedule as default
        interval = timedelta(days=90)
    else:
        interval = timedelta(days=30)  # Default to monthly
    
    # Generate dates
    while current_date <= end_date:
        dates.append(current_date)
        current_date += interval
        
        # Limit to reasonable number of issues
        if len(dates) >= 52:  # Max weekly for a year
            break
    
    return dates


def _determine_newsletter_theme(issue_number: int, frequency: str, 
                               date: datetime, start_date: datetime) -> str:
    """Determine theme for newsletter issue."""
    
    # Calculate months since start
    months_since_start = (date - start_date).days // 30
    
    themes = {
        1: 'Welcome and Study Launch',
        2: 'First Month Progress',
        3: 'Enrollment Focus',
        4: 'Mid-Study Update',
        6: 'Safety Review',
        8: 'Milestone Celebration',
        10: 'Year-End Review',
        12: 'Study Completion Preparation'
    }
    
    # Season-based themes
    month = date.month
    if month in [12, 1, 2]:
        season_theme = 'Winter Update'
    elif month in [3, 4, 5]:
        season_theme = 'Spring Progress'
    elif month in [6, 7, 8]:
        season_theme = 'Summer Update'
    else:
        season_theme = 'Fall Report'
    
    # Return specific theme if available, otherwise use season
    return themes.get(issue_number, season_theme)


def _get_suggested_content_for_theme(theme: str) -> List[str]:
    """Get suggested content for newsletter theme."""
    content_suggestions = {
        'Welcome and Study Launch': [
            'Welcome message from PI',
            'Study overview and objectives',
            'Team introductions',
            'What to expect'
        ],
        'Enrollment Focus': [
            'Enrollment progress updates',
            'Recruitment strategies',
            'Site performance highlights',
            'Participant demographics'
        ],
        'Safety Review': [
            'Safety data summary',
            'Adverse event reporting',
            'Protocol deviations',
            'Risk mitigation updates'
        ],
        'Milestone Celebration': [
            'Achievement highlights',
            'Team recognition',
            'Progress statistics',
            'Looking ahead'
        ]
    }
    
    return content_suggestions.get(theme, [
        'Study progress update',
        'Important announcements',
        'Upcoming events',
        'Contact information'
    ])


def _calculate_issue_number(frequency: str, start_date: Optional[str]) -> int:
    """Calculate issue number based on frequency and date."""
    if not start_date:
        return 1
    
    try:
        if isinstance(start_date, str):
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        else:
            start = start_date
        
        now = datetime.now()
        months_diff = (now.year - start.year) * 12 + (now.month - start.month)
        
        if frequency == 'weekly':
            return ((now - start).days // 7) + 1
        elif frequency == 'monthly':
            return months_diff + 1
        elif frequency == 'quarterly':
            return (months_diff // 3) + 1
        else:
            return months_diff + 1  # Default to monthly
    except:
        return 1


def _get_newsletter_title(newsletter_type: str, frequency: str) -> str:
    """Get newsletter title based on type and frequency."""
    titles = {
        'participant': f'{frequency.title()} Participant Update',
        'investigator': f'{frequency.title()} Investigator Newsletter',
        'sponsor': f'{frequency.title()} Sponsor Report',
        'general': f'{frequency.title()} Study Newsletter'
    }
    
    return titles.get(newsletter_type, f'{frequency.title()} Newsletter')


def _get_newsletter_tagline(newsletter_type: str) -> str:
    """Get newsletter tagline."""
    taglines = {
        'participant': 'Keeping You Informed and Connected',
        'investigator': 'Essential Updates for Study Teams',
        'sponsor': 'Strategic Insights and Progress Reports',
        'general': 'Your Source for Study Updates'
    }
    
    return taglines.get(newsletter_type, 'Staying Connected')


def _get_unsubscribe_text(newsletter_type: str) -> str:
    """Get unsubscribe text."""
    if newsletter_type == 'participant':
        return "If you no longer wish to receive these newsletters, please contact the study team. Note that you will still receive essential study communications."
    else:
        return "To unsubscribe from this newsletter, please contact the study administration team."


def _calculate_total_word_count(sections: Dict) -> int:
    """Calculate total word count for newsletter."""
    total_words = 0
    
    for section_data in sections.values():
        if isinstance(section_data, dict):
            content = section_data.get('content', [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        total_words += len(item.get('content', '').split())
                    else:
                        total_words += len(str(item).split())
            else:
                total_words += len(str(content).split())
    
    return total_words


def _calculate_total_read_time(sections: Dict) -> int:
    """Calculate estimated read time in minutes."""
    word_count = _calculate_total_word_count(sections)
    return max(1, word_count // 200)  # Assuming 200 words per minute


def _calculate_section_priority(section_content) -> str:
    """Calculate priority level for a section."""
    if isinstance(section_content, list):
        priorities = [item.get('priority', 'medium') for item in section_content if isinstance(item, dict)]
        if 'high' in priorities:
            return 'high'
        elif 'medium' in priorities:
            return 'medium'
        else:
            return 'low'
    return 'medium'


def _get_html_styles(template_style: str) -> str:
    """Get CSS styles for HTML formatting."""
    
    base_styles = """
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        margin: 0;
        padding: 20px;
        background-color: #f9f9f9;
    }
    .header {
        background-color: #007cba;
        color: white;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    .section {
        background-color: white;
        margin-bottom: 20px;
        padding: 20px;
        border-left: 4px solid #007cba;
    }
    .content-item {
        margin-bottom: 15px;
        padding: 10px;
        border-bottom: 1px solid #eee;
    }
    .footer {
        background-color: #333;
        color: white;
        padding: 20px;
        margin-top: 20px;
    }
    """
    
    style_variants = {
        'friendly': """
        .header { background-color: #28a745; }
        .section { border-left-color: #28a745; }
        h3 { color: #28a745; }
        """,
        'formal': """
        .header { background-color: #333; }
        .section { border-left-color: #333; }
        h3 { color: #333; }
        """,
        'clinical': """
        .header { background-color: #dc3545; }
        .section { border-left-color: #dc3545; }
        h3 { color: #dc3545; }
        """,
        'brief': """
        .content-item { padding: 5px; }
        .section { padding: 15px; }
        """
    }
    
    return base_styles + style_variants.get(template_style, '')


def _get_greeting_for_style(template_style: str) -> str:
    """Get greeting based on template style."""
    greetings = {
        'friendly': 'Dear Friends and Participants,',
        'formal': 'Dear Recipients,',
        'clinical': 'Dear Study Team Members,',
        'brief': 'Team,'
    }
    
    return greetings.get(template_style, 'Dear Recipients,')


def _generate_newsletter_introduction(header: Dict, template_style: str) -> str:
    """Generate newsletter introduction."""
    study_name = header.get('study_name', 'our study')
    issue_number = header.get('issue_number', 1)
    
    intros = {
        'friendly': f"Welcome to issue #{issue_number} of our {study_name} newsletter! We're excited to share the latest updates and developments with you.",
        'formal': f"This is issue #{issue_number} of the {study_name} newsletter, providing important updates and information.",
        'clinical': f"Newsletter #{issue_number} contains critical updates and communications regarding {study_name}.",
        'brief': f"Issue #{issue_number} - Key updates for {study_name}."
    }
    
    return intros.get(template_style, intros['formal'])


def _generate_newsletter_conclusion(template_style: str) -> str:
    """Generate newsletter conclusion."""
    conclusions = {
        'friendly': "Thank you for being part of our study community. Your participation makes this research possible!",
        'formal': "Thank you for your continued involvement and dedication to this research study.",
        'clinical': "Your adherence to protocol requirements and continued participation is essential for study success.",
        'brief': "Thank you for your participation."
    }
    
    return conclusions.get(template_style, conclusions['formal'])


def _generate_distribution_info(newsletter_type: str) -> Dict:
    """Generate distribution information."""
    return {
        'target_audience': newsletter_type,
        'distribution_methods': ['email', 'portal', 'print'],
        'estimated_recipients': {
            'participant': 'All enrolled participants',
            'investigator': 'PIs and study coordinators',
            'sponsor': 'Sponsor team and key stakeholders',
            'general': 'All study stakeholders'
        }.get(newsletter_type, 'Study stakeholders'),
        'delivery_recommendations': _get_delivery_recommendations(newsletter_type)
    }


def _get_delivery_recommendations(newsletter_type: str) -> List[str]:
    """Get delivery recommendations for newsletter type."""
    recommendations = {
        'participant': [
            'Send via preferred communication method',
            'Include in participant portal',
            'Follow up with participants who haven\'t opened'
        ],
        'investigator': [
            'Send to all site staff',
            'Include in investigator meetings',
            'Archive in study documentation system'
        ],
        'sponsor': [
            'Distribute to key decision makers',
            'Include metrics and KPIs',
            'Schedule review meetings as needed'
        ]
    }
    
    return recommendations.get(newsletter_type, [
        'Send to appropriate distribution list',
        'Ensure accessibility compliance',
        'Track engagement metrics'
    ])


def _generate_newsletter_recommendations(sections: Dict, statistics: Dict) -> List[str]:
    """Generate recommendations for newsletter improvement."""
    recommendations = []
    
    word_count = statistics.get('total_word_count', 0)
    if word_count > 1500:
        recommendations.append("Consider shortening content for better readability")
    elif word_count < 300:
        recommendations.append("Consider adding more detailed content")
    
    section_count = len(sections)
    if section_count > 8:
        recommendations.append("Consider consolidating sections for cleaner organization")
    
    recommendations.append("Include engaging visuals or graphics where appropriate")
    recommendations.append("Ensure all content is relevant to target audience")
    recommendations.append("Review for consistent tone and messaging")
    
    return recommendations


def _calculate_newsletter_statistics(newsletter: Dict, content_items: List[Dict]) -> Dict:
    """Calculate newsletter statistics."""
    sections = newsletter.get('sections', {})
    
    return {
        'total_word_count': _calculate_total_word_count(sections),
        'estimated_read_time': _calculate_total_read_time(sections),
        'section_count': len(sections),
        'content_item_count': len(content_items),
        'priority_breakdown': {
            'high': len([item for item in content_items if item.get('priority') == 'high']),
            'medium': len([item for item in content_items if item.get('priority') == 'medium']),
            'low': len([item for item in content_items if item.get('priority') == 'low'])
        },
        'content_type_breakdown': dict(Counter(item.get('type', 'unknown') for item in content_items))
    }


# Additional helper functions for template, format, schedule, and analyze actions

def _get_template_structure(newsletter_type: str) -> List[str]:
    """Get recommended template structure."""
    structures = {
        'participant': ['header', 'greeting', 'study_updates', 'safety_info', 'events', 'resources', 'contact'],
        'investigator': ['header', 'protocol_updates', 'enrollment', 'safety', 'training', 'regulatory', 'contact'],
        'sponsor': ['header', 'executive_summary', 'metrics', 'milestones', 'risks', 'financials', 'contact']
    }
    
    return structures.get(newsletter_type, ['header', 'updates', 'announcements', 'contact'])


def _get_style_guide(template_style: str) -> Dict:
    """Get style guide for template."""
    return {
        'tone': {
            'friendly': 'warm, encouraging, personal',
            'formal': 'professional, respectful, informative',
            'clinical': 'precise, factual, medical terminology',
            'brief': 'concise, direct, action-oriented'
        }.get(template_style, 'professional'),
        'word_count_target': {
            'friendly': '800-1200',
            'formal': '600-1000',
            'clinical': '400-800',
            'brief': '200-500'
        }.get(template_style, '600-1000'),
        'formatting_notes': [
            'Use clear headings and subheadings',
            'Include white space for readability',
            'Use bullet points for lists',
            'Highlight important information'
        ]
    }


def _get_content_guidelines(newsletter_type: str) -> List[str]:
    """Get content guidelines for newsletter type."""
    guidelines = {
        'participant': [
            'Use plain language and avoid jargon',
            'Include practical information participants can use',
            'Maintain encouraging and supportive tone',
            'Provide clear contact information'
        ],
        'investigator': [
            'Include actionable protocol information',
            'Provide regulatory updates and deadlines',
            'Share best practices and lessons learned',
            'Include training opportunities'
        ],
        'sponsor': [
            'Focus on metrics and key performance indicators',
            'Include risk assessments and mitigation strategies',
            'Provide executive-level insights',
            'Include financial and timeline updates'
        ]
    }
    
    return guidelines.get(newsletter_type, [
        'Provide relevant, timely information',
        'Maintain consistent messaging',
        'Include appropriate level of detail',
        'Ensure accuracy and completeness'
    ])


def _get_frequency_recommendations(frequency: str) -> Dict:
    """Get recommendations for newsletter frequency."""
    return {
        'content_planning': f"Plan content {frequency} with appropriate lead time",
        'content_volume': {
            'weekly': 'Keep content concise and focused on recent developments',
            'monthly': 'Include comprehensive updates and forward-looking information',
            'quarterly': 'Provide strategic overview and major milestone updates'
        }.get(frequency, 'Adjust content volume to frequency'),
        'engagement_tips': [
            'Maintain consistent publication schedule',
            'Include interactive elements when possible',
            'Track open rates and engagement metrics',
            'Solicit feedback from recipients'
        ]
    }


def _get_sample_sections(newsletter_type: str, template_style: str) -> Dict:
    """Get sample sections for template."""
    return {
        'study_updates': {
            'title': 'Study Progress Update',
            'content_example': 'We are pleased to report that enrollment continues to progress well...',
            'formatting_notes': 'Include specific metrics and timelines'
        },
        'safety_information': {
            'title': 'Safety Communication',
            'content_example': 'No new safety signals have been identified in the most recent review...',
            'formatting_notes': 'Use clear, factual language'
        },
        'upcoming_events': {
            'title': 'Upcoming Events',
            'content_example': 'Please mark your calendars for the following upcoming events...',
            'formatting_notes': 'Use bullet points and include dates/locations'
        }
    }


def _get_template_usage_notes(newsletter_type: str, template_style: str) -> List[str]:
    """Get usage notes for template."""
    return [
        f"Template optimized for {newsletter_type} audience",
        f"Style guide emphasizes {template_style} communication",
        "Customize content placeholders with study-specific information",
        "Review and approve all content before distribution",
        "Maintain consistent branding and messaging"
    ]


def _format_content_item_html(item: Dict, format_options: Dict) -> str:
    """Format individual content item as HTML."""
    return f"""
    <div class="content-item">
        <h4>{item.get('title', 'Update')}</h4>
        <p>{item.get('content', '')}</p>
    </div>
    """


def _format_content_item_text(item: Dict) -> str:
    """Format individual content item as text."""
    return f"{item.get('title', 'Update')}\n{'-' * len(item.get('title', 'Update'))}\n{item.get('content', '')}\n"


def _format_content_item_markdown(item: Dict) -> str:
    """Format individual content item as markdown."""
    return f"## {item.get('title', 'Update')}\n\n{item.get('content', '')}\n\n"


def _get_formatting_notes(format_options: Dict) -> List[str]:
    """Get formatting notes."""
    return [
        "Ensure consistent formatting across all content items",
        "Use appropriate heading levels for hierarchy",
        "Include alt text for images",
        "Test formatting in target delivery system"
    ]


def _create_schedule_summary(schedule: List[Dict], frequency: str) -> str:
    """Create summary of publication schedule."""
    return f"Created {len(schedule)} issue schedule for {frequency} publication. Next issue planned for {schedule[0]['publication_date'] if schedule else 'TBD'}."


def _analyze_content_types(content_items: List[Dict]) -> Dict:
    """Analyze types of content in newsletter."""
    type_counts = Counter(item.get('type', 'unknown') for item in content_items)
    
    return {
        'type_distribution': dict(type_counts),
        'most_common_type': type_counts.most_common(1)[0] if type_counts else ('none', 0),
        'type_diversity': len(type_counts),
        'content_balance_score': _calculate_content_balance_score(type_counts)
    }


def _estimate_engagement_metrics(content_items: List[Dict]) -> Dict:
    """Estimate engagement metrics based on content."""
    total_items = len(content_items)
    high_priority_items = len([item for item in content_items if item.get('priority') == 'high'])
    
    # Simple engagement estimation
    engagement_score = min(100, (high_priority_items / total_items * 100) if total_items > 0 else 0)
    
    return {
        'estimated_open_rate': f"{max(60, engagement_score)}%",
        'estimated_read_through_rate': f"{max(40, engagement_score - 20)}%",
        'engagement_factors': [
            'High-priority content increases engagement',
            'Shorter newsletters typically have higher completion rates',
            'Personalized content improves open rates'
        ]
    }


def _analyze_readability(content_items: List[Dict]) -> Dict:
    """Analyze readability of newsletter content."""
    total_words = sum(len(item.get('content', '').split()) for item in content_items)
    total_sentences = sum(item.get('content', '').count('.') + 
                         item.get('content', '').count('!') + 
                         item.get('content', '').count('?') for item in content_items)
    
    avg_words_per_sentence = total_words / max(1, total_sentences)
    
    # Simple readability assessment
    if avg_words_per_sentence < 15:
        readability_level = 'Easy'
    elif avg_words_per_sentence < 20:
        readability_level = 'Moderate'
    else:
        readability_level = 'Difficult'
    
    return {
        'average_words_per_sentence': round(avg_words_per_sentence, 1),
        'readability_level': readability_level,
        'total_word_count': total_words,
        'recommendations': [
            'Keep sentences under 20 words for better readability',
            'Use active voice when possible',
            'Define technical terms for target audience'
        ]
    }


def _analyze_content_balance(content_items: List[Dict]) -> Dict:
    """Analyze balance of content types."""
    priorities = Counter(item.get('priority', 'medium') for item in content_items)
    types = Counter(item.get('type', 'general') for item in content_items)
    
    return {
        'priority_balance': dict(priorities),
        'type_balance': dict(types),
        'balance_score': _calculate_content_balance_score(types),
        'recommendations': _get_balance_recommendations(priorities, types)
    }


def _analyze_content_trends(content_items: List[Dict]) -> Dict:
    """Analyze content trends (simplified)."""
    return {
        'trending_topics': ['enrollment', 'safety', 'protocol updates'],
        'content_evolution': 'Increasing focus on participant communication',
        'seasonal_patterns': 'Higher activity during enrollment periods'
    }


def _calculate_content_balance_score(type_counts: Counter) -> float:
    """Calculate content balance score."""
    if not type_counts:
        return 0.0
    
    # Perfect balance would be equal distribution
    total_items = sum(type_counts.values())
    ideal_per_type = total_items / len(type_counts)
    
    # Calculate deviation from ideal
    deviations = [abs(count - ideal_per_type) for count in type_counts.values()]
    average_deviation = sum(deviations) / len(deviations)
    
    # Convert to score (lower deviation = higher score)
    balance_score = max(0, 100 - (average_deviation / ideal_per_type * 100))
    
    return round(balance_score, 1)


def _get_balance_recommendations(priorities: Counter, types: Counter) -> List[str]:
    """Get recommendations for content balance."""
    recommendations = []
    
    if priorities.get('high', 0) > priorities.get('medium', 0) + priorities.get('low', 0):
        recommendations.append("Consider balancing high-priority items with routine updates")
    
    if len(types) < 3:
        recommendations.append("Consider diversifying content types for better engagement")
    
    most_common_type = types.most_common(1)[0][0] if types else 'none'
    if types.get(most_common_type, 0) > sum(types.values()) * 0.5:
        recommendations.append(f"Consider reducing {most_common_type} content for better variety")
    
    return recommendations or ["Content balance looks good"]


def _generate_performance_recommendations(analysis: Dict) -> List[str]:
    """Generate performance recommendations."""
    recommendations = []
    
    content_analysis = analysis.get('content_analysis', {})
    if content_analysis.get('type_diversity', 0) < 3:
        recommendations.append("Increase content type diversity to improve engagement")
    
    readability = analysis.get('readability_analysis', {})
    if readability.get('readability_level') == 'Difficult':
        recommendations.append("Simplify language and sentence structure for better readability")
    
    balance = analysis.get('content_balance', {})
    if balance.get('balance_score', 0) < 70:
        recommendations.append("Improve content balance across different types and priorities")
    
    return recommendations or ["Newsletter performance looks good"]


def _extract_performance_insights(analysis: Dict) -> List[str]:
    """Extract insights from performance analysis."""
    insights = []
    
    content_types = analysis.get('content_analysis', {}).get('type_distribution', {})
    if content_types:
        most_common = max(content_types.items(), key=lambda x: x[1])
        insights.append(f"Most common content type: {most_common[0]} ({most_common[1]} items)")
    
    readability = analysis.get('readability_analysis', {})
    insights.append(f"Content readability: {readability.get('readability_level', 'Unknown')}")
    
    balance_score = analysis.get('content_balance', {}).get('balance_score', 0)
    insights.append(f"Content balance score: {balance_score}/100")
    
    return insights


def _calculate_performance_score(analysis: Dict) -> float:
    """Calculate overall performance score."""
    scores = []
    
    # Content balance score
    balance_score = analysis.get('content_balance', {}).get('balance_score', 0)
    scores.append(balance_score)
    
    # Readability score
    readability = analysis.get('readability_analysis', {}).get('readability_level', 'Moderate')
    readability_score = {'Easy': 100, 'Moderate': 75, 'Difficult': 50}.get(readability, 75)
    scores.append(readability_score)
    
    # Content diversity score
    diversity = analysis.get('content_analysis', {}).get('type_diversity', 0)
    diversity_score = min(100, diversity * 25)  # Up to 4 types for full score
    scores.append(diversity_score)
    
    return sum(scores) / len(scores) if scores else 0