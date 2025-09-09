"""
Tests for Equipment Calibration Tracker Tool
"""

import pytest
from datetime import datetime, timedelta
from tools.equipment_calibration_tracker import run

class TestEquipmentCalibrationTracker:
    
    def test_successful_calibration_tracking(self):
        """Test successful equipment calibration tracking"""
        current_date = datetime.now()
        input_data = {
            'equipment_inventory': [
                {
                    'site_id': 'SITE001',
                    'equipment_id': 'EQ001',
                    'equipment_type_id': 'scale',
                    'serial_number': 'SN12345',
                    'location': 'Lab Room A',
                    'status': 'active'
                },
                {
                    'site_id': 'SITE001',
                    'equipment_id': 'EQ002',
                    'equipment_type_id': 'freezer',
                    'serial_number': 'SN67890',
                    'location': 'Storage Room',
                    'status': 'active'
                }
            ],
            'calibration_records': [
                {
                    'equipment_id': 'EQ001',
                    'calibration_date': (current_date - timedelta(days=200)).isoformat(),  # Valid calibration
                    'certificate_id': 'CAL001'
                },
                {
                    'equipment_id': 'EQ002',
                    'calibration_date': (current_date - timedelta(days=400)).isoformat(),  # Expired calibration
                    'certificate_id': 'CAL002'
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
        assert 'calibration_data' in result
        
        calib_data = result['calibration_data']
        assert calib_data['overall_analysis']['total_equipment'] == 2
        assert calib_data['overall_analysis']['expired_equipment'] == 1
        assert calib_data['overall_analysis']['compliant_equipment'] == 1
        
        # Check site equipment status
        site_status = calib_data['site_equipment_status']['SITE001']
        assert site_status['total_equipment'] == 2
        assert site_status['expired_equipment'] == 1
        assert site_status['compliant_equipment'] == 1
    
    def test_expiring_equipment_alerts(self):
        """Test detection of equipment with expiring calibrations"""
        current_date = datetime.now()
        input_data = {
            'equipment_inventory': [
                {
                    'site_id': 'SITE001',
                    'equipment_id': 'EQ001',
                    'equipment_type_id': 'scale',
                    'serial_number': 'SN12345',
                    'status': 'active'
                }
            ],
            'calibration_records': [
                {
                    'equipment_id': 'EQ001',
                    'calibration_date': (current_date - timedelta(days=360)).isoformat()  # Expires in 5 days
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
        calib_data = result['calibration_data']
        
        # Should detect expiring equipment
        assert len(calib_data['calibration_alerts']) > 0
        alert = calib_data['calibration_alerts'][0]
        assert alert['alert_level'] == 'critical'
        assert alert['equipment_id'] == 'EQ001'
        assert 4 <= alert['days_overdue_or_until_due'] <= 6  # Allow for date calculation differences
    
    def test_expired_critical_equipment(self):
        """Test handling of expired critical equipment"""
        current_date = datetime.now()
        input_data = {
            'equipment_inventory': [
                {
                    'site_id': 'SITE001',
                    'equipment_id': 'EQ001',
                    'equipment_type_id': 'freezer',  # Critical equipment
                    'serial_number': 'SN12345',
                    'status': 'active'
                }
            ],
            'calibration_records': [
                {
                    'equipment_id': 'EQ001',
                    'calibration_date': (current_date - timedelta(days=400)).isoformat()  # Expired 35 days ago
                }
            ],
            'equipment_types': {
                'freezer': {
                    'name': 'Ultra Low Freezer',
                    'calibration_frequency_days': 365,
                    'criticality': 'critical',
                    'regulatory_requirement': True
                }
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        calib_data = result['calibration_data']
        
        # Should generate critical priority alert for expired critical equipment
        assert len(calib_data['calibration_alerts']) > 0
        alert = calib_data['calibration_alerts'][0]
        assert alert['priority'] == 'critical'
        assert alert['alert_level'] == 'expired'
        assert 'REMOVE FROM SERVICE' in alert['action_required']
    
    def test_equipment_type_analysis(self):
        """Test analysis by equipment type"""
        current_date = datetime.now()
        input_data = {
            'equipment_inventory': [
                {
                    'site_id': 'SITE001',
                    'equipment_id': 'EQ001',
                    'equipment_type_id': 'scale',
                    'status': 'active'
                },
                {
                    'site_id': 'SITE001',
                    'equipment_id': 'EQ002',
                    'equipment_type_id': 'scale',
                    'status': 'active'
                },
                {
                    'site_id': 'SITE001',
                    'equipment_id': 'EQ003',
                    'equipment_type_id': 'centrifuge',
                    'status': 'active'
                }
            ],
            'calibration_records': [
                {
                    'equipment_id': 'EQ001',
                    'calibration_date': (current_date - timedelta(days=100)).isoformat()  # Compliant
                },
                {
                    'equipment_id': 'EQ002',
                    'calibration_date': (current_date - timedelta(days=400)).isoformat()  # Expired
                },
                {
                    'equipment_id': 'EQ003',
                    'calibration_date': (current_date - timedelta(days=100)).isoformat()  # Compliant
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        calib_data = result['calibration_data']
        
        # Check equipment type breakdown
        by_type = calib_data['overall_analysis']['by_type']
        assert 'Scale/Balance' in by_type
        assert 'Centrifuge' in by_type
        
        scale_data = by_type['Scale/Balance']
        assert scale_data['total'] == 2
        assert scale_data['compliant'] == 1
        assert scale_data['expired'] == 1
    
    def test_site_compliance_percentage(self):
        """Test site compliance percentage calculation"""
        current_date = datetime.now()
        input_data = {
            'equipment_inventory': [
                {
                    'site_id': 'SITE001',
                    'equipment_id': f'EQ00{i}',
                    'equipment_type_id': 'scale',
                    'status': 'active'
                } for i in range(1, 6)  # 5 pieces of equipment
            ],
            'calibration_records': [
                # 3 compliant, 2 expired
                {
                    'equipment_id': 'EQ001',
                    'calibration_date': (current_date - timedelta(days=100)).isoformat()
                },
                {
                    'equipment_id': 'EQ002',
                    'calibration_date': (current_date - timedelta(days=100)).isoformat()
                },
                {
                    'equipment_id': 'EQ003',
                    'calibration_date': (current_date - timedelta(days=100)).isoformat()
                },
                {
                    'equipment_id': 'EQ004',
                    'calibration_date': (current_date - timedelta(days=400)).isoformat()
                },
                {
                    'equipment_id': 'EQ005',
                    'calibration_date': (current_date - timedelta(days=400)).isoformat()
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
        calib_data = result['calibration_data']
        
        # Check site compliance calculation
        site_status = calib_data['site_equipment_status']['SITE001']
        assert site_status['compliance_percentage'] == 60.0  # 3/5 = 60%
    
    def test_upcoming_calibrations_schedule(self):
        """Test upcoming calibrations scheduling"""
        current_date = datetime.now()
        input_data = {
            'equipment_inventory': [
                {
                    'site_id': 'SITE001',
                    'equipment_id': 'EQ001',
                    'equipment_type_id': 'scale',
                    'status': 'active'
                }
            ],
            'calibration_records': [
                {
                    'equipment_id': 'EQ001',
                    'calibration_date': (current_date - timedelta(days=270)).isoformat()  # Due in ~3 months
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        calib_data = result['calibration_data']
        
        # Should have upcoming calibrations
        upcoming = calib_data['upcoming_calibrations_by_month']
        assert len(upcoming) > 0
    
    def test_inactive_equipment_exclusion(self):
        """Test exclusion of inactive equipment"""
        current_date = datetime.now()
        input_data = {
            'equipment_inventory': [
                {
                    'site_id': 'SITE001',
                    'equipment_id': 'EQ001',
                    'equipment_type_id': 'scale',
                    'status': 'active'
                },
                {
                    'site_id': 'SITE001',
                    'equipment_id': 'EQ002',
                    'equipment_type_id': 'scale',
                    'status': 'inactive'  # Should be excluded
                }
            ],
            'calibration_records': [
                {
                    'equipment_id': 'EQ001',
                    'calibration_date': (current_date - timedelta(days=100)).isoformat()
                },
                {
                    'equipment_id': 'EQ002',
                    'calibration_date': (current_date - timedelta(days=100)).isoformat()
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        calib_data = result['calibration_data']
        
        # Should only track active equipment
        assert calib_data['overall_analysis']['total_equipment'] == 1
        site_status = calib_data['site_equipment_status']['SITE001']
        assert site_status['total_equipment'] == 1
    
    def test_no_calibration_records(self):
        """Test handling of equipment with no calibration records"""
        input_data = {
            'equipment_inventory': [
                {
                    'site_id': 'SITE001',
                    'equipment_id': 'EQ001',
                    'equipment_type_id': 'scale',
                    'status': 'active'
                }
            ],
            'calibration_records': []  # No calibration records
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        calib_data = result['calibration_data']
        
        # Should still process equipment but mark as no calibration
        site_status = calib_data['site_equipment_status']['SITE001']
        equipment_detail = site_status['equipment_details'][0]
        assert equipment_detail['calibration_status'] == 'No Calibration Record'
    
    def test_recommendations_generation(self):
        """Test generation of recommendations"""
        current_date = datetime.now()
        input_data = {
            'equipment_inventory': [
                {
                    'site_id': 'SITE001',
                    'equipment_id': 'EQ001',
                    'equipment_type_id': 'freezer',
                    'status': 'active'
                }
            ],
            'calibration_records': [
                {
                    'equipment_id': 'EQ001',
                    'calibration_date': (current_date - timedelta(days=400)).isoformat()  # Expired
                }
            ],
            'equipment_types': {
                'freezer': {
                    'name': 'Critical Freezer',
                    'criticality': 'critical',
                    'regulatory_requirement': True
                }
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        calib_data = result['calibration_data']
        
        # Should generate recommendations for expired equipment
        recommendations = calib_data['recommendations']
        assert len(recommendations) > 0
        assert any('expired' in rec.lower() for rec in recommendations)
    
    def test_empty_equipment_inventory(self):
        """Test handling of empty equipment inventory"""
        input_data = {
            'equipment_inventory': [],
            'calibration_records': []
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'No equipment inventory provided' in result['error']