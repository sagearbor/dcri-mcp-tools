"""
Tests for Site Visit Report Generator Tool
"""

import pytest
from datetime import datetime, timedelta
from tools.site_visit_report_generator import run

class TestSiteVisitReportGenerator:
    
    def test_successful_report_generation(self):
        """Test successful site visit report generation"""
        input_data = {
            'visit_details': {
                'site_id': 'SITE001',
                'site_name': 'Metro Medical Center',
                'visit_date': datetime.now().isoformat(),
                'visit_type': 'Routine Monitoring',
                'monitor_name': 'John Monitor',
                'study_id': 'STUDY123',
                'duration_hours': 6,
                'visit_outcome': 'Completed successfully'
            },
            'findings': [
                {
                    'finding_id': 'F001',
                    'category': 'Data Quality',
                    'description': 'Missing visit date in subject 001',
                    'severity': 'minor',
                    'subject_id': '001',
                    'corrective_action': 'Update CRF with correct date',
                    'responsible_person': 'Site coordinator'
                },
                {
                    'finding_id': 'F002',
                    'category': 'Protocol Compliance',
                    'description': 'Visit window deviation for subject 002',
                    'severity': 'major',
                    'subject_id': '002',
                    'corrective_action': 'Document deviation and provide explanation',
                    'responsible_person': 'Principal Investigator'
                }
            ],
            'site_metrics': {
                'enrollment': {
                    'current_enrolled': 25,
                    'target': 30,
                    'monthly_rate': 4.2
                },
                'quality': {
                    'protocol_deviation_rate': 0.08,
                    'query_rate': 0.15,
                    'sdv_completion_rate': 0.92
                }
            },
            'previous_visit_findings': [
                {
                    'finding_id': 'PF001',
                    'description': 'Previous data issue',
                    'finding_date': '2024-01-15',
                    'status': 'closed',
                    'resolution_notes': 'Corrected in system',
                    'verification_date': '2024-01-20'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'report_data' in result
        
        report = result['report_data']
        assert report['report_header']['site_id'] == 'SITE001'
        assert report['report_header']['visit_type'] == 'Routine Monitoring'
        
        # Check findings analysis
        assert len(report['findings_summary']['findings_by_category']) == 2
        assert 'Data Quality' in report['findings_summary']['findings_by_category']
        assert 'Protocol Compliance' in report['findings_summary']['findings_by_category']
        
        # Check executive summary
        assert report['executive_summary']['total_findings'] == 2
        assert 'risk_level' in report['executive_summary']
    
    def test_critical_findings_assessment(self):
        """Test assessment with critical findings"""
        input_data = {
            'visit_details': {
                'site_id': 'SITE001',
                'site_name': 'Test Site',
                'visit_date': datetime.now().isoformat(),
                'monitor_name': 'Test Monitor',
                'study_id': 'TEST123'
            },
            'findings': [
                {
                    'finding_id': 'F001',
                    'category': 'Safety',
                    'description': 'Unreported SAE',
                    'severity': 'critical',
                    'corrective_action': 'Report SAE immediately',
                    'responsible_person': 'Principal Investigator'
                },
                {
                    'finding_id': 'F002',
                    'category': 'Regulatory',
                    'description': 'Missing informed consent signature',
                    'severity': 'critical',
                    'corrective_action': 'Obtain proper consent',
                    'responsible_person': 'Site coordinator'
                }
            ],
            'site_metrics': {
                'enrollment': {
                    'current_enrolled': 10,
                    'target': 20,
                    'monthly_rate': 2.0
                }
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        report = result['report_data']
        
        # Should assess as high risk due to critical findings
        assert report['executive_summary']['risk_level'] == 'High'
        assert 'critical' in report['executive_summary']['overall_assessment'].lower()
        
        # Should have immediate action items
        action_items = report['action_items']
        immediate_actions = [item for item in action_items if item['priority'] == 'Immediate']
        assert len(immediate_actions) == 2
        
        # Should recommend enhanced monitoring
        recommendations = report['recommendations']
        assert any('enhanced monitoring' in rec.lower() for rec in recommendations)
    
    def test_performance_based_recommendations(self):
        """Test recommendations based on site performance"""
        input_data = {
            'visit_details': {
                'site_id': 'SITE001',
                'site_name': 'Low Performing Site',
                'visit_date': datetime.now().isoformat(),
                'monitor_name': 'Test Monitor',
                'study_id': 'TEST123'
            },
            'findings': [],
            'site_metrics': {
                'enrollment': {
                    'current_enrolled': 5,
                    'target': 30,
                    'monthly_rate': 1.5  # Low enrollment rate
                },
                'quality': {
                    'protocol_deviation_rate': 0.18,  # High deviation rate
                    'query_rate': 0.25  # High query rate
                }
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        report = result['report_data']
        
        # Should have performance concerns
        performance_concerns = report['site_performance']['performance_concerns']
        assert len(performance_concerns) > 0
        
        # Should generate performance-based action items
        action_items = report['action_items']
        assert any('enrollment' in item['action'].lower() for item in action_items)
    
    def test_previous_findings_follow_up(self):
        """Test follow-up on previous visit findings"""
        input_data = {
            'visit_details': {
                'site_id': 'SITE001',
                'site_name': 'Test Site',
                'visit_date': datetime.now().isoformat(),
                'monitor_name': 'Test Monitor',
                'study_id': 'TEST123'
            },
            'findings': [],
            'previous_visit_findings': [
                {
                    'finding_id': 'PF001',
                    'description': 'Open finding 1',
                    'finding_date': '2024-01-15',
                    'status': 'open'
                },
                {
                    'finding_id': 'PF002',
                    'description': 'Open finding 2',
                    'finding_date': '2024-01-10',
                    'status': 'pending'
                },
                {
                    'finding_id': 'PF003',
                    'description': 'Closed finding',
                    'finding_date': '2024-01-01',
                    'status': 'closed',
                    'resolution_notes': 'Resolved'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        report = result['report_data']
        
        # Should track previous findings status
        follow_up = report['previous_findings_follow_up']
        assert follow_up['total_previous_findings'] == 3
        assert follow_up['open_previous_findings'] == 2
        assert follow_up['closure_rate'] == 33.3  # 1/3 closed
    
    def test_next_visit_planning(self):
        """Test next visit planning based on current findings"""
        input_data = {
            'visit_details': {
                'site_id': 'SITE001',
                'site_name': 'Test Site',
                'visit_date': datetime.now().isoformat(),
                'monitor_name': 'Test Monitor',
                'study_id': 'TEST123'
            },
            'findings': [
                {
                    'finding_id': 'F001',
                    'category': 'Safety',
                    'description': 'Critical safety issue',
                    'severity': 'critical'
                },
                {
                    'finding_id': 'F002',
                    'category': 'Data Quality',
                    'description': 'Major data issue',
                    'severity': 'major'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        report = result['report_data']
        
        # Should recommend follow-up visit due to critical findings
        next_visit = report['next_visit_planning']
        assert next_visit['visit_type'] == 'Follow-up'
        assert next_visit['visit_interval_days'] == 30  # Should be sooner due to critical findings
        
        # Should include focus areas
        focus_areas = next_visit['focus_areas']
        assert 'Safety' in focus_areas
    
    def test_findings_categorization(self):
        """Test proper categorization of findings by category and severity"""
        input_data = {
            'visit_details': {
                'site_id': 'SITE001',
                'site_name': 'Test Site',
                'visit_date': datetime.now().isoformat(),
                'monitor_name': 'Test Monitor',
                'study_id': 'TEST123'
            },
            'findings': [
                {
                    'finding_id': 'F001',
                    'category': 'Data Quality',
                    'severity': 'critical'
                },
                {
                    'finding_id': 'F002',
                    'category': 'Data Quality',
                    'severity': 'minor'
                },
                {
                    'finding_id': 'F003',
                    'category': 'Protocol Compliance',
                    'severity': 'major'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        report = result['report_data']
        
        # Check findings categorization
        findings_by_category = report['findings_summary']['findings_by_category']
        assert len(findings_by_category['Data Quality']['findings']) == 2
        assert len(findings_by_category['Protocol Compliance']['findings']) == 1
        
        # Check severity breakdown
        data_quality_severity = findings_by_category['Data Quality']['severity_breakdown']
        assert data_quality_severity['critical'] == 1
        assert data_quality_severity['minor'] == 1
    
    def test_minimal_visit_data(self):
        """Test report generation with minimal data"""
        input_data = {
            'visit_details': {
                'site_id': 'SITE001',
                'visit_date': datetime.now().isoformat()
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        report = result['report_data']
        
        # Should still generate basic report structure
        assert 'report_header' in report
        assert 'executive_summary' in report
        assert report['report_header']['site_id'] == 'SITE001'
    
    def test_empty_visit_details(self):
        """Test handling of empty visit details"""
        input_data = {}
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'Visit details are required' in result['error']