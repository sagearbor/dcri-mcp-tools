"""
Tests for Email Template Generator Tool
"""

import pytest
import json
from datetime import datetime
from tools.email_template_generator import run


class TestEmailTemplateGenerator:
    
    def test_recruitment_email_basic(self):
        """Test basic recruitment email generation"""
        input_data = {
            'template_type': 'recruitment',
            'study_name': 'Test Study',
            'study_id': 'TEST-001',
            'pi_name': 'Dr. Test PI',
            'contact_info': {
                'phone': '555-123-4567',
                'email': 'test@example.com',
                'address': '123 Test Street'
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'template' in result
        template = result['template']
        
        assert template['type'] == 'recruitment'
        assert 'Invitation to Participate' in template['subject']
        assert 'Test Study' in template['body']
        assert 'Dr. Test PI' in template['body']
        assert '555-123-4567' in template['body']
        assert template['priority'] == 'normal'
        assert 'recruitment' in template['tags']
    
    def test_reminder_email_urgent(self):
        """Test urgent reminder email generation"""
        input_data = {
            'template_type': 'reminder',
            'study_name': 'Urgent Study',
            'urgency': 'high',
            'custom_fields': {
                'APPOINTMENT_DATE': '2024-01-15',
                'APPOINTMENT_TIME': '10:00 AM',
                'APPOINTMENT_DURATION': '2 hours'
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        template = result['template']
        
        assert template['type'] == 'reminder'
        assert 'URGENT' in template['subject']
        assert '2024-01-15' in template['body']
        assert '10:00 AM' in template['body']
        assert template['priority'] == 'high'
        assert template['suggested_send_time'] == '24_hours_before'
    
    def test_update_email_with_custom_fields(self):
        """Test update email with custom field replacements"""
        input_data = {
            'template_type': 'update',
            'study_name': 'Protocol Update Study',
            'custom_fields': {
                'UPDATE_TYPE': 'Protocol Amendment',
                'UPDATE_SUMMARY': 'New inclusion criteria added',
                'PARTICIPANT_IMPACT': 'No impact on current participants',
                'NEXT_STEPS': 'Continue with current procedures'
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        template = result['template']
        
        assert 'Protocol Amendment' in template['body']
        assert 'New inclusion criteria added' in template['body']
        assert 'No impact on current participants' in template['body']
        assert template['priority'] == 'high'
    
    def test_welcome_email_complete(self):
        """Test comprehensive welcome email"""
        input_data = {
            'template_type': 'welcome',
            'study_name': 'Welcome Study',
            'study_id': 'WEL-123',
            'pi_name': 'Dr. Welcome',
            'contact_info': {
                'phone': '555-999-8888',
                'email': 'welcome@study.com'
            },
            'custom_fields': {
                'PARTICIPANT_ID': 'P001',
                'STUDY_TIMELINE': '12 month study with monthly visits',
                'COORDINATOR_NAME': 'Jane Coordinator',
                'EMERGENCY_PHONE': '555-911-HELP'
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        template = result['template']
        
        assert 'Welcome to the Welcome Study' in template['body']
        assert 'P001' in template['body']
        assert 'Jane Coordinator' in template['body']
        assert 'Emergency' in template['body']
        assert template['suggested_send_time'] == 'upon_enrollment'
    
    def test_followup_email_medium_urgency(self):
        """Test follow-up email with medium urgency"""
        input_data = {
            'template_type': 'followup',
            'study_name': 'Follow-up Study',
            'urgency': 'medium',
            'custom_fields': {
                'FOLLOWUP_TYPE': 'Missing Form',
                'FOLLOWUP_REASON': 'incomplete baseline assessment',
                'DEADLINE_DATE': '2024-02-01',
                'FOLLOWUP_REQUIREMENTS': 'Complete demographic form'
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        template = result['template']
        
        assert 'Missing Form' in template['body']
        assert 'incomplete baseline assessment' in template['body']
        assert '2024-02-01' in template['body']
        assert template['priority'] == 'medium'
        assert 'followup' in template['tags']
    
    def test_invalid_template_type(self):
        """Test handling of invalid template type"""
        input_data = {
            'template_type': 'invalid_type',
            'study_name': 'Test Study'
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'Unsupported template type' in result['error']
        assert 'valid_types' in result
        expected_types = ['recruitment', 'reminder', 'update', 'welcome', 'followup']
        for template_type in expected_types:
            assert template_type in result['valid_types']
    
    def test_missing_template_type(self):
        """Test handling of missing template type"""
        input_data = {
            'study_name': 'Test Study'
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'template_type is required' in result['error']
    
    def test_metadata_generation(self):
        """Test metadata generation and compliance notes"""
        input_data = {
            'template_type': 'recruitment',
            'study_name': 'Metadata Test Study',
            'language': 'es',  # Spanish
            'custom_fields': {
                'STUDY_DESCRIPTION': 'This is a test study for metadata',
                'PARTICIPANT_NAME': 'Test Participant'
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'metadata' in result
        assert 'compliance_notes' in result
        
        metadata = result['metadata']
        assert metadata['study_name'] == 'Metadata Test Study'
        assert metadata['template_version'] == '1.0'
        assert 'generated_at' in metadata
        assert 'character_count' in metadata
        assert 'estimated_read_time' in metadata
        
        # Check language setting
        assert result['template']['language'] == 'es'
        
        # Check compliance notes
        compliance_notes = result['compliance_notes']
        assert len(compliance_notes) > 0
        assert any('IRB' in note for note in compliance_notes)
        assert any('voluntary' in note.lower() for note in compliance_notes)
    
    def test_comprehensive_template_data(self):
        """Test comprehensive template with all optional fields"""
        input_data = {
            'template_type': 'reminder',
            'study_name': 'Comprehensive Study',
            'study_id': 'COMP-456',
            'pi_name': 'Dr. Comprehensive',
            'contact_info': {
                'phone': '555-COMP-STU',
                'email': 'comprehensive@study.org',
                'address': '456 Comprehensive Ave, Research City, RC 12345'
            },
            'custom_fields': {
                'PARTICIPANT_NAME': 'John Comprehensive',
                'APPOINTMENT_DATE': '2024-03-15',
                'APPOINTMENT_TIME': '2:30 PM',
                'APPOINTMENT_DURATION': '3 hours',
                'ITEMS_TO_BRING': 'Insurance card, medications, photo ID',
                'PREPARATION_INSTRUCTIONS': 'Fast for 12 hours before visit',
                'CANCELLATION_POLICY': 'Please call 24 hours in advance'
            },
            'urgency': 'low',
            'language': 'en'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        template = result['template']
        
        # Verify all custom fields are replaced
        assert 'John Comprehensive' in template['body']
        assert '2024-03-15' in template['body']
        assert '2:30 PM' in template['body']
        assert 'Insurance card, medications' in template['body']
        assert 'Fast for 12 hours' in template['body']
        assert '24 hours in advance' in template['body']
        
        # Verify template properties
        assert template['type'] == 'reminder'
        assert template['priority'] == 'normal'  # Low urgency maps to normal priority
        
        # Verify variables used tracking
        assert 'variables_used' in result
        expected_vars = ['PARTICIPANT_NAME', 'APPOINTMENT_DATE', 'APPOINTMENT_TIME']
        for var in expected_vars:
            assert var in result['variables_used']