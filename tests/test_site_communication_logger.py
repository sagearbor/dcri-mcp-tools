"""
Tests for Site Communication Logger Tool
"""

import pytest
from datetime import datetime, timedelta
from tools.site_communication_logger import run

class TestSiteCommunicationLogger:
    
    def test_successful_communication_tracking(self):
        """Test successful communication tracking and analysis"""
        current_date = datetime.now()
        input_data = {
            'communication_records': [
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=30)).isoformat(),
                    'communication_type': 'email',
                    'direction': 'outbound',
                    'priority': 'normal',
                    'subject': 'Protocol clarification',
                    'status': 'responded',
                    'response_required': True,
                    'actual_response_date': (current_date - timedelta(days=28)).isoformat()
                },
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=25)).isoformat(),
                    'communication_type': 'phone',
                    'direction': 'inbound',
                    'priority': 'high',
                    'subject': 'Safety question',
                    'status': 'completed'
                },
                {
                    'site_id': 'SITE002',
                    'communication_date': (current_date - timedelta(days=20)).isoformat(),
                    'communication_type': 'email',
                    'direction': 'outbound',
                    'priority': 'urgent',
                    'subject': 'Urgent protocol deviation',
                    'status': 'sent',
                    'response_required': True,
                    'response_deadline': (current_date - timedelta(days=15)).isoformat()  # Overdue
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Metro Medical Center'
                },
                {
                    'site_id': 'SITE002',
                    'site_name': 'University Hospital'
                }
            ],
            'analysis_period': 60
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'communication_data' in result
        
        comm_data = result['communication_data']
        assert comm_data['overall_analysis']['total_communications'] == 3
        assert len(comm_data['site_communications']) == 2
        
        # Check site-specific tracking
        site1_comm = comm_data['site_communications']['SITE001']
        assert site1_comm['total_communications'] == 2
        assert site1_comm['outbound_communications'] == 1
        assert site1_comm['inbound_communications'] == 1
        
        # Should detect overdue response
        assert len(comm_data['overall_analysis']['escalation_events']) > 0
    
    def test_response_time_analysis(self):
        """Test response time analysis"""
        current_date = datetime.now()
        input_data = {
            'communication_records': [
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=30)).isoformat(),
                    'communication_type': 'email',
                    'direction': 'outbound',
                    'response_required': True,
                    'actual_response_date': (current_date - timedelta(days=29)).isoformat()  # 1 day response
                },
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=25)).isoformat(),
                    'communication_type': 'email',
                    'direction': 'outbound',
                    'response_required': True,
                    'actual_response_date': (current_date - timedelta(days=22)).isoformat()  # 3 day response
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Test Site'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        comm_data = result['communication_data']
        
        # Check response time tracking
        site_comm = comm_data['site_communications']['SITE001']
        assert len(site_comm['response_times']) == 2
        assert site_comm['average_response_time_hours'] > 0
        
        # Check overall response time analysis
        assert len(comm_data['overall_analysis']['response_times']) == 2
    
    def test_escalation_detection(self):
        """Test escalation detection for overdue responses"""
        current_date = datetime.now()
        input_data = {
            'communication_records': [
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=10)).isoformat(),
                    'communication_type': 'email',
                    'direction': 'outbound',
                    'priority': 'urgent',
                    'response_required': True,
                    'response_deadline': (current_date - timedelta(days=5)).isoformat(),  # 5 days overdue
                    'subject': 'Urgent response needed'
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Test Site'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        comm_data = result['communication_data']
        
        # Should detect escalation
        escalation_events = comm_data['overall_analysis']['escalation_events']
        assert len(escalation_events) > 0
        
        escalation = escalation_events[0]
        assert escalation['site_id'] == 'SITE001'
        assert escalation['days_overdue'] == 5
        assert escalation['escalation_level'] in ['high', 'urgent']
    
    def test_communication_frequency_scoring(self):
        """Test communication frequency scoring"""
        current_date = datetime.now()
        # Create high frequency communication data
        input_data = {
            'communication_records': [
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=i)).isoformat(),
                    'communication_type': 'email',
                    'direction': 'outbound',
                    'subject': f'Communication {i}'
                } for i in range(1, 15)  # 14 communications in last 14 days
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'High Volume Site'
                }
            ],
            'analysis_period': 14
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        comm_data = result['communication_data']
        
        # Should calculate high frequency score
        site_comm = comm_data['site_communications']['SITE001']
        assert site_comm['communication_frequency_score'] == 7.0  # 14 comms / 14 days * 7 = 7 per week
    
    def test_responsiveness_scoring(self):
        """Test responsiveness scoring calculation"""
        current_date = datetime.now()
        input_data = {
            'communication_records': [
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=30)).isoformat(),
                    'communication_type': 'email',
                    'direction': 'outbound',
                    'response_required': True,
                    'actual_response_date': (current_date - timedelta(days=29)).isoformat()  # Fast response
                },
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=20)).isoformat(),
                    'communication_type': 'email',
                    'direction': 'outbound',
                    'response_required': True  # No response - outstanding
                },
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=10)).isoformat(),
                    'communication_type': 'email',
                    'direction': 'outbound',
                    'response_required': True  # No response - outstanding
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Test Site'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        comm_data = result['communication_data']
        
        # Should calculate lower responsiveness score due to outstanding responses
        site_comm = comm_data['site_communications']['SITE001']
        assert site_comm['outstanding_responses'] == 2
        assert site_comm['responsiveness_score'] < 100  # Should be penalized
    
    def test_communication_insights(self):
        """Test generation of communication insights"""
        current_date = datetime.now()
        input_data = {
            'communication_records': [
                # High volume of urgent communications
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=i)).isoformat(),
                    'communication_type': 'email',
                    'direction': 'outbound',
                    'priority': 'urgent',
                    'subject': f'Urgent matter {i}'
                } for i in range(1, 6)  # 5 urgent communications
            ] + [
                # Low responsiveness site
                {
                    'site_id': 'SITE002',
                    'communication_date': (current_date - timedelta(days=30)).isoformat(),
                    'communication_type': 'email',
                    'direction': 'outbound',
                    'response_required': True,
                    'actual_response_date': (current_date - timedelta(days=25)).isoformat()  # Slow response (5 days)
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'High Urgent Site'
                },
                {
                    'site_id': 'SITE002',
                    'site_name': 'Slow Response Site'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        comm_data = result['communication_data']
        
        # Should generate insights
        insights = comm_data['insights']
        assert len(insights) > 0
        
        # Should identify high urgent communication pattern
        urgent_insight = next((i for i in insights if 'urgent' in i['finding'].lower()), None)
        assert urgent_insight is not None
    
    def test_communication_trends(self):
        """Test communication trend analysis"""
        current_date = datetime.now()
        input_data = {
            'communication_records': [
                # Week 1: Low volume
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=28)).isoformat(),
                    'communication_type': 'email'
                },
                # Week 2: Low volume
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=21)).isoformat(),
                    'communication_type': 'email'
                },
                # Week 3: Higher volume
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=14)).isoformat(),
                    'communication_type': 'email'
                },
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=13)).isoformat(),
                    'communication_type': 'phone'
                },
                # Week 4: Higher volume
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=7)).isoformat(),
                    'communication_type': 'email'
                },
                {
                    'site_id': 'SITE001',
                    'communication_date': (current_date - timedelta(days=6)).isoformat(),
                    'communication_type': 'email'
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Test Site'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        comm_data = result['communication_data']
        
        # Should analyze trends
        trends = comm_data['communication_trends']
        assert 'weekly_volume' in trends
        assert len(trends['weekly_volume']) > 0
    
    def test_empty_communication_data(self):
        """Test handling of empty communication data"""
        input_data = {
            'communication_records': [],
            'sites': []
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'No communication records found' in result['error']