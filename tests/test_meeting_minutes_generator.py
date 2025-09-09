"""
Tests for Meeting Minutes Generator Tool
"""

import pytest
import json
from tools.meeting_minutes_generator import run


class TestMeetingMinutesGenerator:
    
    def test_generate_investigator_meeting_minutes(self):
        """Test generating investigator meeting minutes"""
        meeting_info = {
            'title': 'Monthly Investigator Meeting',
            'date': '2024-02-15',
            'time': '10:00 AM',
            'location': 'Conference Room A',
            'chair': 'Dr. Principal Investigator',
            'secretary': 'Jane Study Coordinator',
            'attendees': [
                {'name': 'Dr. Principal Investigator', 'role': 'Principal Investigator'},
                {'name': 'Jane Study Coordinator', 'role': 'Study Coordinator'},
                {'name': 'Dr. Site Investigator', 'role': 'Site PI'},
                {'name': 'John Data Manager', 'role': 'Data Manager'}
            ]
        }
        
        notes = """
        Welcome and Introductions
        Dr. PI welcomed everyone to the monthly investigator meeting.
        
        Enrollment Update
        We have enrolled 45 participants this month, bringing total enrollment to 150.
        Sites 1, 2, and 3 are performing well. Site 4 needs additional support.
        Action: Jane will contact Site 4 to provide additional training.
        
        Safety Review
        No new safety signals identified in monthly safety review.
        Two non-serious adverse events reported, both expected.
        Action: Dr. PI will review safety data with DSMB next week.
        
        Protocol Amendments
        Amendment #3 has been approved by IRB.
        All sites need to update their informed consent forms.
        Action: All sites to implement new consent by March 1st.
        """
        
        agenda = [
            {'title': 'Welcome and Introductions', 'presenter': 'Dr. PI'},
            {'title': 'Enrollment Update', 'presenter': 'Jane Study Coordinator'},
            {'title': 'Safety Review', 'presenter': 'Dr. PI'},
            {'title': 'Protocol Amendments', 'presenter': 'Dr. PI'}
        ]
        
        input_data = {
            'action': 'generate',
            'meeting_type': 'investigator',
            'meeting_info': meeting_info,
            'notes': notes,
            'agenda': agenda,
            'format_style': 'formal'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'meeting_minutes' in result
        
        minutes = result['meeting_minutes']
        
        # Check header information
        header = minutes['header']
        assert header['meeting_type'] == 'Investigator'
        assert header['date'] == '2024-02-15'
        assert header['chairperson'] == 'Dr. Principal Investigator'
        
        # Check attendees
        attendees = minutes['attendees']
        assert len(attendees['present']) == 4
        assert attendees['total_attendees'] == 4
        
        # Check content sections
        sections = minutes['content_sections']
        assert len(sections) > 0
        
        # Should have enrollment section
        section_names = list(sections.keys())
        assert any('Enrollment' in name for name in section_names)
        
        # Check action items extraction
        action_items = minutes['action_items']
        assert len(action_items) >= 3  # Should extract 3 action items
        
        # Verify specific action items
        action_descriptions = [action['description'] for action in action_items]
        assert any('contact Site 4' in desc for desc in action_descriptions)
        assert any('consent' in desc for desc in action_descriptions)
    
    def test_generate_safety_meeting_minutes(self):
        """Test generating safety meeting minutes"""
        meeting_info = {
            'title': 'Safety Review Committee Meeting',
            'date': '2024-02-20',
            'time': '2:00 PM',
            'meeting_type': 'safety',
            'chair': 'Dr. Safety Officer',
            'attendees': [
                {'name': 'Dr. Safety Officer', 'role': 'Safety Officer'},
                {'name': 'Dr. Medical Monitor', 'role': 'Medical Monitor'},
                {'name': 'Jane Pharmacovigilance', 'role': 'Pharmacovigilance Specialist'}
            ]
        }
        
        notes = """
        Safety Data Review
        Reviewed safety data from January 2024.
        Total of 15 adverse events reported, 2 serious.
        
        Serious Adverse Events
        SAE #1: Hospitalization due to cardiac event (Patient 001-015)
        Assessed as not related to study drug by investigator.
        SAE #2: Emergency department visit for severe headache (Patient 002-008)
        Possibly related to study drug, requires further evaluation.
        
        Risk Assessment
        Overall risk-benefit profile remains favorable.
        No new safety signals identified.
        Decision: Continue study as planned with enhanced monitoring.
        
        Action Items
        Dr. Medical Monitor will request additional cardiac monitoring for Patient 001-015.
        Jane will update safety database with new assessments.
        Next safety review scheduled for March 20, 2024.
        """
        
        input_data = {
            'action': 'generate',
            'meeting_type': 'safety',
            'meeting_info': meeting_info,
            'notes': notes,
            'format_style': 'clinical'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        minutes = result['meeting_minutes']
        
        # Check safety-specific sections
        sections = minutes['content_sections']
        section_names = list(sections.keys())
        
        # Should have safety-specific sections
        assert any('Safety' in name or 'Risk' in name for name in section_names)
        
        # Check decisions were extracted
        decisions = minutes['decisions_made']
        assert len(decisions) > 0
        
        decision_texts = [decision['decision'] for decision in decisions]
        assert any('Continue study' in text for text in decision_texts)
        
        # Check action items
        action_items = minutes['action_items']
        assert len(action_items) >= 2
        
        # Should identify high-priority safety actions
        high_priority_actions = [action for action in action_items if action.get('priority') == 'high']
        assert len(high_priority_actions) > 0
    
    def test_generate_meeting_template(self):
        """Test generating meeting minutes template"""
        input_data = {
            'action': 'template',
            'meeting_type': 'investigator',
            'format_style': 'formal'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'template' in result
        
        template = result['template']
        
        # Check template structure
        assert 'structure' in template
        assert 'required_sections' in template
        assert 'optional_sections' in template
        assert 'formatting_guidelines' in template
        
        # Check usage instructions
        assert 'usage_instructions' in result
        instructions = result['usage_instructions']
        assert len(instructions) > 0
        assert any('investigator' in instruction.lower() for instruction in instructions)
    
    def test_format_meeting_minutes_html(self):
        """Test formatting meeting minutes as HTML"""
        meeting_minutes = {
            'header': {
                'document_title': 'Test Meeting Minutes',
                'meeting_type': 'Investigator',
                'date': '2024-02-15',
                'time': '10:00 AM',
                'chairperson': 'Dr. Test Chair'
            },
            'attendees': {
                'present': [
                    {'name': 'Dr. Test Chair', 'role': 'Chair'},
                    {'name': 'Jane Attendee', 'role': 'Coordinator'}
                ],
                'total_attendees': 2
            },
            'content_sections': {
                'Test Agenda Item': {
                    'discussion_summary': 'This is a test discussion summary.',
                    'key_points': ['Point 1', 'Point 2'],
                    'outcomes': ['Outcome 1']
                }
            },
            'action_items': [
                {
                    'description': 'Test action item',
                    'assignee': 'Jane Attendee',
                    'due_date': '2024-03-01',
                    'priority': 'high'
                }
            ]
        }
        
        input_data = {
            'action': 'format',
            'meeting_info': meeting_minutes,
            'output_format': 'html'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'formatted_minutes' in result
        
        html_output = result['formatted_minutes']
        
        # Check HTML structure
        assert '<!DOCTYPE html>' in html_output
        assert '<html>' in html_output
        assert 'Test Meeting Minutes' in html_output
        assert 'Dr. Test Chair' in html_output
        assert 'Test action item' in html_output
        
        # Check CSS styling
        assert '<style>' in html_output
        assert 'priority-high' in html_output
    
    def test_summarize_meeting_content(self):
        """Test summarizing meeting content"""
        notes = """
        Project Status Review
        The clinical trial is progressing well with 85% enrollment achieved.
        We are on track to complete enrollment by the end of March.
        
        Budget Review
        Current spending is within 95% of projected budget.
        Some equipment costs were higher than expected.
        
        Site Performance
        Site 1: Excellent performance, ahead of schedule
        Site 2: Good performance, meeting targets
        Site 3: Behind schedule, needs support
        
        Next Steps
        Focus recruitment efforts on Site 3
        Prepare for database lock activities
        Schedule interim analysis meeting
        """
        
        agenda = [
            {'title': 'Project Status Review', 'presenter': 'Project Manager'},
            {'title': 'Budget Review', 'presenter': 'Finance Manager'},
            {'title': 'Site Performance', 'presenter': 'CRA Manager'}
        ]
        
        input_data = {
            'action': 'summarize',
            'notes': notes,
            'agenda': agenda,
            'meeting_type': 'investigator'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'meeting_summary' in result
        
        summary = result['meeting_summary']
        
        # Check executive summary
        executive_summary = summary['executive_summary']
        assert len(executive_summary) > 50  # Should be substantial
        assert 'investigator' in executive_summary.lower()
        
        # Check key topics
        key_topics = summary['key_topics_discussed']
        assert len(key_topics) >= 3
        topic_names = [topic.lower() for topic in key_topics]
        assert any('status' in topic for topic in topic_names)
        assert any('budget' in topic for topic in topic_names)
        
        # Check outcomes
        outcomes = summary['meeting_outcomes']
        assert len(outcomes) > 0
        
        # Check statistics
        stats = result['summary_statistics']
        assert 'topics_covered' in stats
        assert stats['topics_covered'] >= 3
    
    def test_extract_action_items_only(self):
        """Test extracting action items only"""
        notes = """
        Discussion on enrollment strategies
        We need to improve our recruitment efforts.
        
        Action Item 1: John will contact potential participants by Friday.
        Action Item 2: Sarah should update the recruitment materials.
        
        Budget discussion
        The current budget is on track.
        Task: Finance team to provide updated projections by next week.
        
        Follow-up: Dr. Smith will review the protocol with the team.
        """
        
        meeting_info = {
            'date': '2024-02-15',
            'meeting_type': 'investigator'
        }
        
        input_data = {
            'action': 'extract_actions',
            'notes': notes,
            'meeting_info': meeting_info
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'action_items' in result
        
        action_items = result['action_items']
        assert len(action_items) >= 3  # Should extract multiple action items
        
        # Check action item structure
        action = action_items[0]
        assert 'description' in action
        assert 'id' in action
        assert 'status' in action
        assert action['status'] == 'open'
        
        # Check categorization
        categorized_actions = result['categorized_actions']
        assert len(categorized_actions) > 0
        
        # Check prioritization
        prioritized_actions = result['prioritized_actions']
        assert len(prioritized_actions) == len(action_items)
        
        # Check tracking information
        tracking = result['action_tracking']
        assert 'total_actions' in tracking
        assert tracking['total_actions'] == len(action_items)
    
    def test_comprehensive_meeting_workflow(self):
        """Test comprehensive meeting minutes generation workflow"""
        # Complete meeting information
        meeting_info = {
            'title': 'Comprehensive Study Meeting',
            'date': '2024-02-25',
            'time': '1:00 PM - 3:00 PM',
            'location': 'Virtual (Zoom)',
            'chair': 'Dr. Study Director',
            'secretary': 'Meeting Secretary',
            'attendees': [
                {'name': 'Dr. Study Director', 'role': 'Study Director', 'organization': 'DCRI'},
                {'name': 'Dr. Principal Investigator', 'role': 'Principal Investigator', 'organization': 'Duke'},
                {'name': 'Jane Data Manager', 'role': 'Data Manager', 'organization': 'DCRI'},
                {'name': 'John Statistician', 'role': 'Biostatistician', 'organization': 'DCRI'}
            ],
            'study_info': {
                'name': 'Comprehensive Clinical Trial',
                'id': 'CCT-2024-001'
            }
        }
        
        # Detailed meeting notes
        notes = """
        1. Welcome and Introductions
        Dr. Study Director welcomed all attendees and reviewed the meeting agenda.
        
        2. Enrollment Progress Review
        Current enrollment: 180 participants (90% of target)
        Top performing sites: Duke (35 participants), Mayo (28 participants)
        Underperforming sites: Site 7 (8 participants), Site 12 (5 participants)
        
        Key Discussion Points:
        - Site 7 experiencing staffing issues
        - Site 12 has low screening rate due to competitor study
        - Consider adding two new sites to meet timeline
        
        Decisions Made:
        - Approved addition of Sites 15 and 16
        - Approved additional coordinator funding for Site 7
        
        Action Items:
        - Jane will prepare site activation materials for new sites (Due: March 15)
        - Dr. PI will conduct site visit to Site 7 (Due: March 1)
        
        3. Data Quality Review
        Data completion rate: 95.2% (target: 95%)
        Query rate: 2.8 queries per participant (target: <3)
        Outstanding queries: 45 (down from 62 last month)
        
        Discussion:
        John presented data quality metrics showing improvement.
        Few critical queries remain open, mostly related to concomitant medications.
        
        Action Items:
        - Sites to resolve all critical queries by March 10
        - Jane to send query resolution training reminder
        
        4. Safety Update
        Total AEs reported: 125 (expected for population)
        Serious AEs: 8 (all assessed as unrelated or unlikely related)
        No safety signals identified in quarterly review
        
        Decision: Continue study as planned, no protocol modifications needed
        
        5. Statistical Analysis Planning
        John reviewed the Statistical Analysis Plan draft.
        Primary analysis approach confirmed as intention-to-treat.
        Interim analysis planned after 150 participants complete 6-month follow-up.
        
        Action Items:
        - John to finalize SAP by March 20
        - Dr. PI to review and approve SAP
        
        6. Budget and Timeline Review
        Current budget utilization: 78% (on track)
        Study completion timeline: December 2024 (unchanged)
        Last participant last visit projected for October 2024
        
        7. Next Meeting
        Next monthly meeting scheduled for March 25, 2024 at 1:00 PM
        """
        
        # Structured agenda
        agenda = [
            {'title': 'Welcome and Introductions', 'presenter': 'Dr. Study Director', 'time_allocated': '5 minutes'},
            {'title': 'Enrollment Progress Review', 'presenter': 'Jane Data Manager', 'time_allocated': '30 minutes'},
            {'title': 'Data Quality Review', 'presenter': 'Jane Data Manager', 'time_allocated': '20 minutes'},
            {'title': 'Safety Update', 'presenter': 'Dr. Principal Investigator', 'time_allocated': '20 minutes'},
            {'title': 'Statistical Analysis Planning', 'presenter': 'John Statistician', 'time_allocated': '25 minutes'},
            {'title': 'Budget and Timeline Review', 'presenter': 'Dr. Study Director', 'time_allocated': '15 minutes'},
            {'title': 'Next Meeting Planning', 'presenter': 'Meeting Secretary', 'time_allocated': '5 minutes'}
        ]
        
        input_data = {
            'action': 'generate',
            'meeting_type': 'investigator',
            'meeting_info': meeting_info,
            'notes': notes,
            'agenda': agenda,
            'format_style': 'detailed'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        
        minutes = result['meeting_minutes']
        
        # Check comprehensive structure
        assert 'header' in minutes
        assert 'attendees' in minutes
        assert 'agenda_review' in minutes
        assert 'content_sections' in minutes
        assert 'action_items' in minutes
        assert 'decisions_made' in minutes
        assert 'next_steps' in minutes
        assert 'footer' in minutes
        
        # Check detailed content extraction
        action_items = minutes['action_items']
        assert len(action_items) >= 5  # Should extract multiple action items
        
        # Verify specific action items
        action_descriptions = [action['description'] for action in action_items]
        assert any('site activation materials' in desc.lower() for desc in action_descriptions)
        assert any('site visit' in desc.lower() for desc in action_descriptions)
        assert any('sap' in desc.lower() for desc in action_descriptions)
        
        # Check decisions extraction
        decisions = minutes['decisions_made']
        assert len(decisions) >= 2
        
        decision_texts = [decision['decision'] for decision in decisions]
        assert any('addition of sites' in text.lower() for text in decision_texts)
        assert any('continue study' in text.lower() for text in decision_texts)
        
        # Check formatted outputs
        formatted_outputs = result['formatted_outputs']
        
        # HTML output should be comprehensive
        html_output = formatted_outputs['html']
        assert len(html_output) > 5000  # Should be substantial
        assert 'Comprehensive Study Meeting' in html_output
        assert 'Dr. Study Director' in html_output
        assert 'site activation materials' in html_output
        
        # Markdown output should be well-structured
        markdown_output = formatted_outputs['markdown']
        assert '# Comprehensive Study Meeting' in markdown_output
        assert '## Enrollment Progress Review' in markdown_output
        assert '| Action |' in markdown_output  # Action items table
        
        # Check statistics
        statistics = result['statistics']
        assert statistics['total_action_items'] >= 5
        assert statistics['total_decisions'] >= 2
        assert statistics['content_sections'] >= 6
        
        # Check recommendations
        recommendations = result['recommendations']
        assert len(recommendations) > 0
    
    def test_different_meeting_types(self):
        """Test different meeting types generate appropriate structures"""
        meeting_types = ['investigator', 'safety', 'steering_committee', 'site_initiation']
        
        base_meeting_info = {
            'date': '2024-03-01',
            'time': '10:00 AM',
            'chair': 'Dr. Chair',
            'attendees': [{'name': 'Dr. Chair', 'role': 'Chairperson'}]
        }
        
        base_notes = "Meeting discussion about study progress and key decisions."
        
        for meeting_type in meeting_types:
            input_data = {
                'action': 'generate',
                'meeting_type': meeting_type,
                'meeting_info': base_meeting_info,
                'notes': base_notes,
                'format_style': 'formal'
            }
            
            result = run(input_data)
            
            assert result['success'] is True
            
            minutes = result['meeting_minutes']
            header = minutes['header']
            
            # Check meeting type is reflected
            assert meeting_type.replace('_', ' ').title() in header['meeting_type']
            
            # Different meeting types should have different section structures
            sections = minutes['content_sections']
            
            if meeting_type == 'safety':
                section_names = list(sections.keys())
                assert any('Safety' in name or 'Risk' in name for name in section_names)
            elif meeting_type == 'steering_committee':
                section_names = list(sections.keys())
                assert any('Governance' in name or 'Strategic' in name for name in section_names)
    
    def test_error_handling_invalid_action(self):
        """Test error handling for invalid action"""
        input_data = {
            'action': 'invalid_action',
            'meeting_type': 'investigator'
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'Unknown action' in result['error']
        assert 'valid_actions' in result
    
    def test_error_handling_missing_notes(self):
        """Test handling of missing or empty notes"""
        input_data = {
            'action': 'generate',
            'meeting_type': 'investigator',
            'meeting_info': {'date': '2024-03-01'},
            'notes': '',  # Empty notes
            'format_style': 'formal'
        }
        
        result = run(input_data)
        
        # Should handle gracefully
        assert result['success'] is True
        
        minutes = result['meeting_minutes']
        
        # Should still have basic structure
        assert 'header' in minutes
        assert 'attendees' in minutes
        
        # Action items might be empty
        action_items = minutes.get('action_items', [])
        assert isinstance(action_items, list)  # Should be list even if empty