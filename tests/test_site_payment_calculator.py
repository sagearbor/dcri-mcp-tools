"""
Tests for Site Payment Calculator Tool
"""

import pytest
from datetime import datetime, timedelta
from tools.site_payment_calculator import run

class TestSitePaymentCalculator:
    
    def test_successful_payment_calculation(self):
        """Test successful payment calculation with all components"""
        input_data = {
            'site_id': 'SITE001',
            'payment_schedule': {
                'base_rates': {
                    'per_subject_enrollment': 500,
                    'per_visit': 150,
                    'procedures': {
                        'blood_draw': 50,
                        'ecg': 100
                    }
                },
                'milestones': [
                    {
                        'id': 'first_patient_enrolled',
                        'description': 'First Patient Enrolled',
                        'amount': 2000
                    },
                    {
                        'id': 'target_enrollment_met',
                        'description': 'Target Enrollment Met',
                        'amount': 5000
                    }
                ]
            },
            'site_activities': {
                'enrolled_subjects': 15,
                'completed_visits': 45,
                'procedures': {
                    'blood_draw': 30,
                    'ecg': 15
                },
                'completed_milestones': ['first_patient_enrolled'],
                'timeline_adherence_percent': 95
            },
            'quality_metrics': {
                'overall_score': 92,
                'protocol_deviations': 2,
                'outstanding_queries': 5
            },
            'bonus_criteria': {
                'enrollment_target': 12,
                'enrollment_bonus_percent': 10,
                'quality_threshold': 90,
                'quality_bonus_amount': 1000,
                'timeline_threshold': 90,
                'timeline_bonus_amount': 500
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'payment_data' in result
        
        payment_data = result['payment_data']
        breakdown = payment_data['payment_breakdown']
        
        # Check base payments
        assert len(breakdown['base_payments']) > 0
        enrollment_payment = next(p for p in breakdown['base_payments'] if p['type'] == 'Subject Enrollment')
        assert enrollment_payment['amount'] == 7500  # 15 subjects * 500
        
        # Check milestone payments
        assert len(breakdown['milestone_payments']) == 1
        
        # Check performance bonuses (should qualify for all)
        assert len(breakdown['performance_bonuses']) == 3
        
        # Check total calculation
        assert breakdown['total_amount'] > 0
    
    def test_missing_site_id(self):
        """Test handling of missing site ID"""
        input_data = {
            'payment_schedule': {},
            'site_activities': {}
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'Site ID is required' in result['error']
    
    def test_payment_with_penalties(self):
        """Test payment calculation with quality penalties"""
        input_data = {
            'site_id': 'SITE001',
            'payment_schedule': {
                'base_rates': {
                    'per_subject_enrollment': 500
                },
                'deviation_penalty_per_incident': 100,
                'query_penalty_per_outstanding': 25,
                'late_submission_penalty': 50
            },
            'site_activities': {
                'enrolled_subjects': 10,
                'late_submissions': 3
            },
            'quality_metrics': {
                'protocol_deviations': 5,
                'outstanding_queries': 8
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        breakdown = result['payment_data']['payment_breakdown']
        
        # Should have deductions
        assert len(breakdown['deductions']) > 0
        
        # Check specific penalties
        deviation_penalty = next((d for d in breakdown['deductions'] if 'Protocol Deviation' in d['type']), None)
        assert deviation_penalty is not None
        assert deviation_penalty['amount'] == -500  # 5 * 100
        
        query_penalty = next((d for d in breakdown['deductions'] if 'Query' in d['type']), None)
        assert query_penalty is not None
        assert query_penalty['amount'] == -200  # 8 * 25
    
    def test_minimum_payment_adjustment(self):
        """Test minimum payment adjustment"""
        input_data = {
            'site_id': 'SITE001',
            'payment_schedule': {
                'base_rates': {
                    'per_subject_enrollment': 100
                },
                'minimum_payment': 1000,
                'deviation_penalty_per_incident': 200
            },
            'site_activities': {
                'enrolled_subjects': 2  # Only 200 base payment
            },
            'quality_metrics': {
                'protocol_deviations': 3  # 600 penalty, would result in negative
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        breakdown = result['payment_data']['payment_breakdown']
        
        # Should have minimum payment adjustment
        assert breakdown['total_amount'] == 1000
        assert len(breakdown['quality_adjustments']) > 0
    
    def test_performance_bonus_criteria(self):
        """Test performance bonus qualification"""
        input_data = {
            'site_id': 'SITE001',
            'payment_schedule': {
                'base_rates': {
                    'per_subject_enrollment': 500
                }
            },
            'site_activities': {
                'enrolled_subjects': 8,  # Below enrollment target
                'timeline_adherence_percent': 85  # Below timeline threshold
            },
            'quality_metrics': {
                'overall_score': 88  # Below quality threshold
            },
            'bonus_criteria': {
                'enrollment_target': 10,
                'enrollment_bonus_percent': 15,
                'quality_threshold': 90,
                'quality_bonus_amount': 1000,
                'timeline_threshold': 90,
                'timeline_bonus_amount': 500
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        breakdown = result['payment_data']['payment_breakdown']
        
        # Should not qualify for any bonuses
        assert len(breakdown['performance_bonuses']) == 0
    
    def test_next_milestones_tracking(self):
        """Test tracking of upcoming milestones"""
        input_data = {
            'site_id': 'SITE001',
            'payment_schedule': {
                'milestones': [
                    {
                        'id': 'first_patient',
                        'description': 'First Patient',
                        'amount': 1000,
                        'due_date': '2024-06-01'
                    },
                    {
                        'id': 'last_patient',
                        'description': 'Last Patient',
                        'amount': 2000,
                        'due_date': '2024-12-01'
                    }
                ]
            },
            'site_activities': {
                'completed_milestones': ['first_patient']  # Only completed first
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        payment_data = result['payment_data']
        
        # Should show next milestones
        assert len(payment_data['next_milestones']) > 0
        assert payment_data['next_milestones'][0]['id'] == 'last_patient'
    
    def test_empty_payment_data(self):
        """Test handling of empty payment data"""
        input_data = {
            'site_id': 'SITE001',
            'payment_schedule': {},
            'site_activities': {},
            'quality_metrics': {}
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        breakdown = result['payment_data']['payment_breakdown']
        assert breakdown['total_amount'] == 0