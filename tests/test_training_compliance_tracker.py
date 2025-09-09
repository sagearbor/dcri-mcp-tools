"""
Tests for Training Compliance Tracker Tool
"""

import pytest
from datetime import datetime, timedelta
from tools.training_compliance_tracker import run

class TestTrainingComplianceTracker:
    
    def test_successful_compliance_tracking(self):
        """Test successful training compliance tracking"""
        current_date = datetime.now()
        input_data = {
            'site_staff': [
                {
                    'staff_id': 'STAFF001',
                    'name': 'Dr. John Smith',
                    'role': 'Principal Investigator',
                    'status': 'active'
                },
                {
                    'staff_id': 'STAFF002',
                    'name': 'Jane Doe',
                    'role': 'Study Coordinator',
                    'status': 'active'
                }
            ],
            'required_trainings': [
                {
                    'training_id': 'GCP001',
                    'training_name': 'Good Clinical Practice',
                    'validity_period_days': 1095,
                    'mandatory_roles': ['Principal Investigator', 'Study Coordinator'],
                    'category': 'Regulatory'
                },
                {
                    'training_id': 'PROT001',
                    'training_name': 'Protocol Training',
                    'validity_period_days': 365,
                    'mandatory_roles': ['Study Coordinator'],
                    'category': 'Protocol'
                }
            ],
            'training_records': [
                {
                    'staff_id': 'STAFF001',
                    'training_id': 'GCP001',
                    'completion_date': (current_date - timedelta(days=100)).isoformat(),
                    'score': '95%',
                    'certificate_id': 'CERT001'
                },
                {
                    'staff_id': 'STAFF002',
                    'training_id': 'GCP001',
                    'completion_date': (current_date - timedelta(days=200)).isoformat(),
                    'score': '88%',
                    'certificate_id': 'CERT002'
                },
                {
                    'staff_id': 'STAFF002',
                    'training_id': 'PROT001',
                    'completion_date': (current_date - timedelta(days=50)).isoformat(),
                    'score': '92%',
                    'certificate_id': 'CERT003'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'compliance_data' in result
        
        compliance = result['compliance_data']
        assert compliance['overall_statistics']['total_staff'] == 2
        assert len(compliance['staff_compliance']) == 2
        
        # Check individual staff compliance
        staff1 = next(s for s in compliance['staff_compliance'] if s['staff_id'] == 'STAFF001')
        assert staff1['overall_status'] == 'Fully Compliant'
        
        staff2 = next(s for s in compliance['staff_compliance'] if s['staff_id'] == 'STAFF002')
        assert staff2['overall_status'] == 'Fully Compliant'
    
    def test_expiring_training_alerts(self):
        """Test detection of expiring training"""
        current_date = datetime.now()
        input_data = {
            'site_staff': [
                {
                    'staff_id': 'STAFF001',
                    'name': 'Dr. Smith',
                    'role': 'Principal Investigator',
                    'status': 'active'
                }
            ],
            'required_trainings': [
                {
                    'training_id': 'GCP001',
                    'training_name': 'Good Clinical Practice',
                    'validity_period_days': 365,
                    'mandatory_roles': ['Principal Investigator']
                }
            ],
            'training_records': [
                {
                    'staff_id': 'STAFF001',
                    'training_id': 'GCP001',
                    'completion_date': (current_date - timedelta(days=360)).isoformat(),  # Expires in 5 days
                    'certificate_id': 'CERT001'
                }
            ],
            'reminder_thresholds': {
                'urgent': 7,
                'warning': 30,
                'notice': 60
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        compliance = result['compliance_data']
        
        # Should have upcoming expirations
        assert len(compliance['upcoming_expirations']) > 0
        expiration = compliance['upcoming_expirations'][0]
        assert expiration['priority'] == 'urgent'
        assert expiration['staff_id'] == 'STAFF001'
    
    def test_expired_training_detection(self):
        """Test detection of expired training"""
        current_date = datetime.now()
        input_data = {
            'site_staff': [
                {
                    'staff_id': 'STAFF001',
                    'name': 'Dr. Smith',
                    'role': 'Principal Investigator',
                    'status': 'active'
                }
            ],
            'required_trainings': [
                {
                    'training_id': 'GCP001',
                    'training_name': 'Good Clinical Practice',
                    'validity_period_days': 365,
                    'mandatory_roles': ['Principal Investigator']
                }
            ],
            'training_records': [
                {
                    'staff_id': 'STAFF001',
                    'training_id': 'GCP001',
                    'completion_date': (current_date - timedelta(days=400)).isoformat(),  # Expired 35 days ago
                    'certificate_id': 'CERT001'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        compliance = result['compliance_data']
        
        # Should have compliance alerts for expired training
        assert len(compliance['compliance_alerts']) > 0
        alert = next(a for a in compliance['compliance_alerts'] if a['type'] == 'Expired Training')
        assert alert['staff_id'] == 'STAFF001'
    
    def test_missing_training_detection(self):
        """Test detection of missing training"""
        input_data = {
            'site_staff': [
                {
                    'staff_id': 'STAFF001',
                    'name': 'Dr. Smith',
                    'role': 'Principal Investigator',
                    'status': 'active'
                }
            ],
            'required_trainings': [
                {
                    'training_id': 'GCP001',
                    'training_name': 'Good Clinical Practice',
                    'validity_period_days': 365,
                    'mandatory_roles': ['Principal Investigator']
                }
            ],
            'training_records': []  # No training records
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        compliance = result['compliance_data']
        
        # Should have compliance alerts for missing training
        assert len(compliance['compliance_alerts']) > 0
        alert = next(a for a in compliance['compliance_alerts'] if a['type'] == 'Missing Training')
        assert alert['staff_id'] == 'STAFF001'
        
        # Staff should be non-compliant
        staff = compliance['staff_compliance'][0]
        assert staff['overall_status'] == 'Non-Compliant'
    
    def test_role_based_training_requirements(self):
        """Test role-based training requirements"""
        current_date = datetime.now()
        input_data = {
            'site_staff': [
                {
                    'staff_id': 'STAFF001',
                    'name': 'Dr. Smith',
                    'role': 'Principal Investigator',
                    'status': 'active'
                },
                {
                    'staff_id': 'STAFF002',
                    'name': 'Jane Doe',
                    'role': 'Study Coordinator',
                    'status': 'active'
                }
            ],
            'required_trainings': [
                {
                    'training_id': 'PI_TRAIN',
                    'training_name': 'PI Responsibilities',
                    'validity_period_days': 365,
                    'mandatory_roles': ['Principal Investigator']  # Only for PIs
                },
                {
                    'training_id': 'COORD_TRAIN',
                    'training_name': 'Coordinator Training',
                    'validity_period_days': 365,
                    'mandatory_roles': ['Study Coordinator']  # Only for coordinators
                }
            ],
            'training_records': [
                {
                    'staff_id': 'STAFF001',
                    'training_id': 'PI_TRAIN',
                    'completion_date': (current_date - timedelta(days=30)).isoformat()
                },
                {
                    'staff_id': 'STAFF002',
                    'training_id': 'COORD_TRAIN',
                    'completion_date': (current_date - timedelta(days=30)).isoformat()
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        compliance = result['compliance_data']
        
        # Both staff should be compliant with their role-specific training
        staff1 = next(s for s in compliance['staff_compliance'] if s['staff_id'] == 'STAFF001')
        staff2 = next(s for s in compliance['staff_compliance'] if s['staff_id'] == 'STAFF002')
        
        assert staff1['overall_status'] == 'Fully Compliant'
        assert staff2['overall_status'] == 'Fully Compliant'
        
        # Each should have only 1 required training
        assert staff1['required_trainings_count'] == 1
        assert staff2['required_trainings_count'] == 1
    
    def test_inactive_staff_exclusion(self):
        """Test exclusion of inactive staff from compliance tracking"""
        input_data = {
            'site_staff': [
                {
                    'staff_id': 'STAFF001',
                    'name': 'Dr. Smith',
                    'role': 'Principal Investigator',
                    'status': 'active'
                },
                {
                    'staff_id': 'STAFF002',
                    'name': 'Former Staff',
                    'role': 'Study Coordinator',
                    'status': 'inactive'  # Should be excluded
                }
            ],
            'required_trainings': [
                {
                    'training_id': 'GCP001',
                    'training_name': 'Good Clinical Practice',
                    'validity_period_days': 365,
                    'mandatory_roles': []  # Required for all roles
                }
            ],
            'training_records': []
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        compliance = result['compliance_data']
        
        # Should only track active staff
        assert len(compliance['staff_compliance']) == 1
        assert compliance['staff_compliance'][0]['staff_id'] == 'STAFF001'
    
    def test_empty_staff_data(self):
        """Test handling of empty staff data"""
        input_data = {
            'site_staff': [],
            'required_trainings': [],
            'training_records': []
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'No site staff data provided' in result['error']