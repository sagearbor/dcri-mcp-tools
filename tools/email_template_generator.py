"""
Email Template Generator Tool for Clinical Studies
Generates study email templates for recruitment, reminders, and updates
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional


def run(input_data: Dict) -> Dict:
    """
    Generate study email templates based on type and parameters.
    
    Args:
        input_data: Dictionary containing:
            - template_type: 'recruitment', 'reminder', 'update', 'welcome', 'followup'
            - study_name: Name of the study
            - study_id: Study identifier
            - pi_name: Principal investigator name
            - contact_info: Contact information dict
            - custom_fields: Dict of custom field replacements
            - language: Language code (default: 'en')
            - urgency: 'low', 'medium', 'high' (affects tone)
    
    Returns:
        Dictionary with generated template and metadata
    """
    try:
        template_type = input_data.get('template_type', '').lower()
        study_name = input_data.get('study_name', 'Clinical Study')
        study_id = input_data.get('study_id', 'STUDY-001')
        pi_name = input_data.get('pi_name', 'Dr. Principal Investigator')
        contact_info = input_data.get('contact_info', {})
        custom_fields = input_data.get('custom_fields', {})
        language = input_data.get('language', 'en')
        urgency = input_data.get('urgency', 'medium')
        
        if not template_type:
            return {
                'success': False,
                'error': 'template_type is required',
                'valid_types': ['recruitment', 'reminder', 'update', 'welcome', 'followup']
            }
        
        # Generate template based on type
        template_data = _generate_template(
            template_type, study_name, study_id, pi_name, 
            contact_info, custom_fields, language, urgency
        )
        
        if not template_data:
            return {
                'success': False,
                'error': f'Unsupported template type: {template_type}',
                'valid_types': ['recruitment', 'reminder', 'update', 'welcome', 'followup']
            }
        
        # Apply custom field replacements
        subject = _apply_replacements(template_data['subject'], custom_fields)
        body = _apply_replacements(template_data['body'], custom_fields)
        
        return {
            'success': True,
            'template': {
                'type': template_type,
                'subject': subject,
                'body': body,
                'suggested_send_time': template_data.get('send_time'),
                'priority': template_data.get('priority', 'normal'),
                'tags': template_data.get('tags', []),
                'language': language
            },
            'metadata': {
                'study_name': study_name,
                'study_id': study_id,
                'generated_at': datetime.now().isoformat(),
                'template_version': '1.0',
                'character_count': len(body),
                'estimated_read_time': max(1, len(body.split()) // 200)  # minutes
            },
            'variables_used': list(custom_fields.keys()),
            'compliance_notes': _get_compliance_notes(template_type)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error generating email template: {str(e)}'
        }


def _generate_template(template_type: str, study_name: str, study_id: str, 
                      pi_name: str, contact_info: Dict, custom_fields: Dict,
                      language: str, urgency: str) -> Optional[Dict]:
    """Generate template content based on type."""
    
    phone = contact_info.get('phone', '[CONTACT_PHONE]')
    email = contact_info.get('email', '[CONTACT_EMAIL]')
    address = contact_info.get('address', '[STUDY_ADDRESS]')
    
    templates = {
        'recruitment': {
            'subject': f'Invitation to Participate in {study_name} Research Study',
            'body': f"""Dear [PARTICIPANT_NAME],

You are being invited to participate in a research study titled "{study_name}" (Study ID: {study_id}). This study is being conducted by {pi_name} and the research team.

WHAT IS THIS STUDY ABOUT?
[STUDY_DESCRIPTION]

WHO CAN PARTICIPATE?
[ELIGIBILITY_CRITERIA]

WHAT WOULD PARTICIPATION INVOLVE?
[PARTICIPATION_DETAILS]

TIME COMMITMENT:
[TIME_COMMITMENT]

COMPENSATION:
[COMPENSATION_DETAILS]

YOUR RIGHTS:
• Participation is completely voluntary
• You may withdraw at any time without penalty
• Your privacy and confidentiality will be protected
• All study procedures follow strict ethical guidelines

NEXT STEPS:
If you are interested in learning more about this study, please contact us:

Phone: {phone}
Email: {email}
Study Location: {address}

We would be happy to answer any questions you may have about the study.

Thank you for considering participation in this important research.

Sincerely,
{pi_name}
Principal Investigator
{study_name}

[INSTITUTIONAL_FOOTER]""",
            'send_time': 'business_hours',
            'priority': 'normal',
            'tags': ['recruitment', 'invitation', 'voluntary']
        },
        
        'reminder': {
            'subject': f'{study_name} - Appointment Reminder' + (' - URGENT' if urgency == 'high' else ''),
            'body': f"""Dear [PARTICIPANT_NAME],

This is a {"friendly" if urgency == "low" else "important" if urgency == "medium" else "URGENT"} reminder about your upcoming appointment for the {study_name} study.

APPOINTMENT DETAILS:
• Date: [APPOINTMENT_DATE]
• Time: [APPOINTMENT_TIME]
• Location: {address}
• Duration: [APPOINTMENT_DURATION]

WHAT TO BRING:
[ITEMS_TO_BRING]

PREPARATION INSTRUCTIONS:
[PREPARATION_INSTRUCTIONS]

{"IMPORTANT NOTE: Please confirm your attendance as soon as possible." if urgency == "high" else "Please let us know if you need to reschedule."}

Contact us if you have any questions:
Phone: {phone}
Email: {email}

Thank you for your continued participation in this important research.

Best regards,
{study_name} Research Team
Study ID: {study_id}

[CANCELLATION_POLICY]""",
            'send_time': '24_hours_before',
            'priority': 'high' if urgency == 'high' else 'normal',
            'tags': ['reminder', 'appointment', 'scheduling']
        },
        
        'update': {
            'subject': f'{study_name} - Study Update [UPDATE_TYPE]',
            'body': f"""Dear [PARTICIPANT_NAME],

We wanted to provide you with an important update regarding the {study_name} study (Study ID: {study_id}).

UPDATE TYPE: [UPDATE_TYPE]

UPDATE SUMMARY:
[UPDATE_SUMMARY]

WHAT THIS MEANS FOR YOU:
[PARTICIPANT_IMPACT]

NEXT STEPS:
[NEXT_STEPS]

We appreciate your continued participation and patience as we work to ensure the highest quality research standards.

If you have any questions or concerns about this update, please don't hesitate to contact us:

Phone: {phone}
Email: {email}

Thank you for your valuable contribution to this research.

Sincerely,
{pi_name} and the Research Team
{study_name}

[ADDITIONAL_RESOURCES]""",
            'send_time': 'immediate',
            'priority': 'high',
            'tags': ['update', 'information', 'study_news']
        },
        
        'welcome': {
            'subject': f'Welcome to the {study_name} Research Study!',
            'body': f"""Dear [PARTICIPANT_NAME],

Welcome to the {study_name} research study! We are delighted that you have decided to participate in this important research.

STUDY OVERVIEW:
Study Name: {study_name}
Study ID: {study_id}
Principal Investigator: {pi_name}

YOUR PARTICIPANT ID: [PARTICIPANT_ID]

WHAT TO EXPECT:
[STUDY_TIMELINE]

IMPORTANT DOCUMENTS:
• Informed Consent Form (copy attached)
• Study Schedule
• Contact Information Sheet
• Emergency Procedures

YOUR STUDY TEAM:
Principal Investigator: {pi_name}
Study Coordinator: [COORDINATOR_NAME]
Contact Information: {phone} | {email}

RESOURCES:
• Study website: [STUDY_WEBSITE]
• 24/7 Emergency Line: [EMERGENCY_PHONE]
• Participant Portal: [PORTAL_LINK]

We're here to support you throughout your participation. Please don't hesitate to reach out with any questions.

Welcome aboard!

{pi_name} and the {study_name} Research Team

[PARTICIPANT_RIGHTS_SUMMARY]""",
            'send_time': 'upon_enrollment',
            'priority': 'normal',
            'tags': ['welcome', 'onboarding', 'information']
        },
        
        'followup': {
            'subject': f'{study_name} - Follow-up Required [FOLLOWUP_TYPE]',
            'body': f"""Dear [PARTICIPANT_NAME],

Thank you for your recent participation in {study_name}. We need to follow up on [FOLLOWUP_REASON].

FOLLOW-UP DETAILS:
Type: [FOLLOWUP_TYPE]
Urgency: {urgency.title()}
Required By: [DEADLINE_DATE]

WHAT WE NEED FROM YOU:
[FOLLOWUP_REQUIREMENTS]

HOW TO COMPLETE:
[COMPLETION_INSTRUCTIONS]

This follow-up is important for:
[IMPORTANCE_EXPLANATION]

Please complete this follow-up by [DEADLINE_DATE]. If you have any questions or difficulties, please contact us immediately:

Phone: {phone}
Email: {email}
Study Coordinator: [COORDINATOR_NAME]

Your participation continues to be invaluable to this research.

Thank you,
{study_name} Research Team
Study ID: {study_id}

[SUPPORT_RESOURCES]""",
            'send_time': 'as_needed',
            'priority': 'medium',
            'tags': ['followup', 'action_required', 'compliance']
        }
    }
    
    return templates.get(template_type)


def _apply_replacements(text: str, custom_fields: Dict) -> str:
    """Apply custom field replacements to template text."""
    for field, value in custom_fields.items():
        # Handle both [FIELD] and [field] formats
        text = text.replace(f'[{field.upper()}]', str(value))
        text = text.replace(f'[{field}]', str(value))
    return text


def _get_compliance_notes(template_type: str) -> List[str]:
    """Get compliance notes for the template type."""
    base_notes = [
        "Ensure all participant communications comply with IRB approval",
        "Include required regulatory language",
        "Maintain participant confidentiality"
    ]
    
    specific_notes = {
        'recruitment': [
            "Include voluntary participation language",
            "Provide clear contact information",
            "Avoid coercive language"
        ],
        'reminder': [
            "Respect communication preferences",
            "Include cancellation policies",
            "Provide alternative scheduling options"
        ],
        'update': [
            "Document all study changes",
            "Ensure timely participant notification",
            "Include impact assessment"
        ],
        'welcome': [
            "Attach required documents",
            "Provide complete contact information",
            "Include participant rights summary"
        ],
        'followup': [
            "Clearly state requirements",
            "Provide reasonable deadlines",
            "Include support resources"
        ]
    }
    
    return base_notes + specific_notes.get(template_type, [])