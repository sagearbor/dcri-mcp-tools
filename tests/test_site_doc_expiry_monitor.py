"""
Tests for Site Document Expiry Monitor Tool
"""

import pytest
from datetime import datetime, timedelta
from tools.site_doc_expiry_monitor import run

class TestSiteDocExpiryMonitor:
    
    def test_successful_document_monitoring(self):
        """Test successful document expiry monitoring"""
        current_date = datetime.now()
        input_data = {
            'site_documents': [
                {
                    'document_id': 'DOC001',
                    'site_id': 'SITE001',
                    'document_type_id': 'IRB_APPROVAL',
                    'document_name': 'IRB Approval Letter',
                    'expiry_date': (current_date + timedelta(days=45)).isoformat(),
                    'submission_date': (current_date - timedelta(days=320)).isoformat(),
                    'status': 'active',
                    'responsible_person': 'Dr. Smith'
                },
                {
                    'document_id': 'DOC002',
                    'site_id': 'SITE001',
                    'document_type_id': 'CV',
                    'document_name': 'Principal Investigator CV',
                    'expiry_date': (current_date + timedelta(days=200)).isoformat(),
                    'submission_date': (current_date - timedelta(days=565)).isoformat(),
                    'status': 'active',
                    'responsible_person': 'Dr. Smith'
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Metro Medical Center'
                }
            ],
            'alert_thresholds': {
                'critical': 7,
                'urgent': 30,
                'warning': 60,
                'notice': 90
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'monitoring_data' in result
        
        monitoring = result['monitoring_data']
        assert monitoring['summary_statistics']['total_documents'] == 2
        assert len(monitoring['document_status']) == 2
        
        # Check alert generation for document expiring in 45 days (warning level)
        assert len(monitoring['expiry_alerts']) > 0
        irb_alert = next(a for a in monitoring['expiry_alerts'] if a['document_type'] == 'IRB Approval')
        assert irb_alert['alert_level'] == 'warning'
    
    def test_expired_document_detection(self):
        """Test detection of expired documents"""
        current_date = datetime.now()
        input_data = {
            'site_documents': [
                {
                    'document_id': 'DOC001',
                    'site_id': 'SITE001',
                    'document_type_id': 'IRB_APPROVAL',
                    'document_name': 'Expired IRB Approval',
                    'expiry_date': (current_date - timedelta(days=10)).isoformat(),  # Expired 10 days ago
                    'status': 'active'
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Metro Medical Center'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        monitoring = result['monitoring_data']
        
        # Should detect expired document
        assert monitoring['summary_statistics']['expired_documents'] == 1
        assert len(monitoring['expiry_alerts']) > 0
        
        alert = monitoring['expiry_alerts'][0]
        assert alert['alert_level'] == 'expired'
        assert alert['priority'] == 'critical'
        assert alert['days_overdue_or_until_due'] == 10
    
    def test_critical_alert_for_critical_documents(self):
        """Test critical alerts for critical document types"""
        current_date = datetime.now()
        input_data = {
            'site_documents': [
                {
                    'document_id': 'DOC001',
                    'site_id': 'SITE001',
                    'document_type_id': 'FREEZER',  # Critical equipment
                    'document_name': 'Freezer Calibration Certificate',
                    'expiry_date': (current_date + timedelta(days=5)).isoformat(),  # Critical threshold
                    'status': 'active'
                }
            ],
            'document_types': {
                'FREEZER': {
                    'name': 'Freezer Calibration',
                    'renewal_period_days': 365,
                    'critical': True
                }
            },
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Metro Medical Center'
                }
            ],
            'alert_thresholds': {
                'critical': 7,
                'urgent': 30,
                'warning': 60,
                'notice': 90
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        monitoring = result['monitoring_data']
        
        # Should generate critical priority alert
        assert len(monitoring['expiry_alerts']) > 0
        alert = monitoring['expiry_alerts'][0]
        assert alert['priority'] == 'critical'  # Critical document type
        assert alert['alert_level'] == 'critical'
    
    def test_site_compliance_calculation(self):
        """Test site compliance percentage calculation"""
        current_date = datetime.now()
        input_data = {
            'site_documents': [
                {
                    'document_id': 'DOC001',
                    'site_id': 'SITE001',
                    'document_type_id': 'IRB_APPROVAL',
                    'expiry_date': (current_date + timedelta(days=200)).isoformat(),  # Valid
                    'status': 'active'
                },
                {
                    'document_id': 'DOC002',
                    'site_id': 'SITE001',
                    'document_type_id': 'CV',
                    'expiry_date': (current_date - timedelta(days=10)).isoformat(),  # Expired
                    'status': 'active'
                },
                {
                    'document_id': 'DOC003',
                    'site_id': 'SITE001',
                    'document_type_id': 'LICENSE',
                    'expiry_date': (current_date + timedelta(days=20)).isoformat(),  # Expiring soon
                    'status': 'active'
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Metro Medical Center'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        monitoring = result['monitoring_data']
        
        # Check site compliance calculation
        site_compliance = monitoring['site_compliance']['SITE001']
        assert site_compliance['total_documents'] == 3
        assert site_compliance['valid_documents'] == 1
        assert site_compliance['expired_documents'] == 1
        assert site_compliance['expiring_documents'] == 1
        assert site_compliance['compliance_percentage'] == 33.3  # 1/3 valid
    
    def test_upcoming_renewals_schedule(self):
        """Test upcoming renewals scheduling"""
        current_date = datetime.now()
        input_data = {
            'site_documents': [
                {
                    'document_id': 'DOC001',
                    'site_id': 'SITE001',
                    'document_type_id': 'IRB_APPROVAL',
                    'expiry_date': (current_date + timedelta(days=30)).isoformat(),
                    'status': 'active'
                },
                {
                    'document_id': 'DOC002',
                    'site_id': 'SITE001',
                    'document_type_id': 'CV',
                    'expiry_date': (current_date + timedelta(days=90)).isoformat(),
                    'status': 'active'
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Metro Medical Center'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        monitoring = result['monitoring_data']
        
        # Should have upcoming renewals by month
        assert len(monitoring['upcoming_renewals_by_month']) > 0
    
    def test_inactive_document_exclusion(self):
        """Test exclusion of inactive documents"""
        current_date = datetime.now()
        input_data = {
            'site_documents': [
                {
                    'document_id': 'DOC001',
                    'site_id': 'SITE001',
                    'document_type_id': 'IRB_APPROVAL',
                    'expiry_date': (current_date + timedelta(days=30)).isoformat(),
                    'status': 'active'
                },
                {
                    'document_id': 'DOC002',
                    'site_id': 'SITE001',
                    'document_type_id': 'CV',
                    'expiry_date': (current_date - timedelta(days=10)).isoformat(),
                    'status': 'inactive'  # Should be excluded
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Metro Medical Center'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        monitoring = result['monitoring_data']
        
        # Should only process active documents
        assert monitoring['summary_statistics']['total_documents'] == 1
        assert len(monitoring['document_status']) == 1
    
    def test_recommendations_generation(self):
        """Test generation of recommendations"""
        current_date = datetime.now()
        input_data = {
            'site_documents': [
                {
                    'document_id': f'DOC00{i}',
                    'site_id': 'SITE001',
                    'document_type_id': 'IRB_APPROVAL',
                    'document_name': f'IRB Approval {i}',
                    'expiry_date': (current_date - timedelta(days=i*10)).isoformat(),  # Multiple expired
                    'status': 'active'
                } for i in range(1, 4)  # 3 expired documents
            ],
            'document_types': {
                'IRB_APPROVAL': {
                    'name': 'IRB Approval',
                    'critical': True
                }
            },
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Metro Medical Center'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        monitoring = result['monitoring_data']
        
        # Should generate recommendations for expired documents
        recommendations = monitoring['recommendations']
        assert len(recommendations) > 0
        assert any('expired' in rec.lower() for rec in recommendations)
    
    def test_empty_documents_data(self):
        """Test handling of empty documents data"""
        input_data = {
            'site_documents': [],
            'sites': []
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'No site documents provided' in result['error']