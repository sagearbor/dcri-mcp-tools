"""
Tests for Enrollment Predictor Tool
"""

import pytest
from datetime import datetime, timedelta
from tools.enrollment_predictor import run

class TestEnrollmentPredictor:
    
    def test_successful_prediction_with_historical_data(self):
        """Test successful enrollment prediction with historical data"""
        current_date = datetime.now()
        input_data = {
            'historical_data': [
                {
                    'date': (current_date - timedelta(days=90)).isoformat(),
                    'cumulative_enrolled': 10
                },
                {
                    'date': (current_date - timedelta(days=60)).isoformat(),
                    'cumulative_enrolled': 25
                },
                {
                    'date': (current_date - timedelta(days=30)).isoformat(),
                    'cumulative_enrolled': 45
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'enrolled_subjects': 20,
                    'monthly_enrollment_rate': 8.0,
                    'target_enrollment': 30,
                    'status': 'active'
                },
                {
                    'site_id': 'SITE002',
                    'enrolled_subjects': 25,
                    'monthly_enrollment_rate': 6.0,
                    'target_enrollment': 40,
                    'status': 'active'
                }
            ],
            'target_enrollment': 100,
            'forecast_months': 12
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'prediction_data' in result
        
        prediction = result['prediction_data']
        assert prediction['current_enrolled'] == 45
        assert prediction['target_enrollment'] == 100
        assert prediction['active_sites'] == 2
        assert len(prediction['monthly_predictions']) == 12
        
        # Check scenario analysis
        scenarios = prediction['completion_timeline']['scenarios']
        assert 'optimistic' in scenarios
        assert 'realistic' in scenarios
        assert 'pessimistic' in scenarios
    
    def test_prediction_with_site_data_only(self):
        """Test prediction using only site data without historical data"""
        input_data = {
            'historical_data': [],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'enrolled_subjects': 15,
                    'monthly_enrollment_rate': 5.0,
                    'target_enrollment': 25,
                    'status': 'active'
                }
            ],
            'target_enrollment': 50,
            'forecast_months': 6
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        prediction = result['prediction_data']
        assert prediction['baseline_enrollment_rate'] == 5.0
        assert len(prediction['monthly_predictions']) == 6
    
    def test_no_data_provided(self):
        """Test handling when no data is provided"""
        input_data = {
            'historical_data': [],
            'sites': [],
            'target_enrollment': 100
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'No historical data or site information provided' in result['error']
    
    def test_seasonal_factors_application(self):
        """Test application of seasonal factors to predictions"""
        input_data = {
            'sites': [
                {
                    'site_id': 'SITE001',
                    'enrolled_subjects': 10,
                    'monthly_enrollment_rate': 5.0,
                    'target_enrollment': 30,
                    'status': 'active'
                }
            ],
            'target_enrollment': 60,
            'forecast_months': 3,
            'seasonal_factors': {
                'Jan': 0.5,  # Low enrollment in January
                'Feb': 1.5,  # High enrollment in February
                'Mar': 1.0   # Normal enrollment in March
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        predictions = result['prediction_data']['monthly_predictions']
        
        # Check that seasonal factors are applied
        for pred in predictions:
            assert 'seasonal_factor' in pred
            assert pred['seasonal_factor'] > 0
    
    def test_capacity_constraints(self):
        """Test prediction with site capacity constraints"""
        input_data = {
            'sites': [
                {
                    'site_id': 'SITE001',
                    'enrolled_subjects': 28,  # Close to capacity
                    'monthly_enrollment_rate': 10.0,
                    'target_enrollment': 30,
                    'status': 'active'
                }
            ],
            'target_enrollment': 100,
            'forecast_months': 6
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        predictions = result['prediction_data']['monthly_predictions']
        
        # Should show capacity constraints affecting predictions
        for pred in predictions:
            assert 'capacity_factor' in pred
            assert pred['capacity_factor'] <= 1.0
    
    def test_risk_assessment(self):
        """Test risk assessment functionality"""
        input_data = {
            'historical_data': [
                {
                    'date': (datetime.now() - timedelta(days=30)).isoformat(),
                    'cumulative_enrolled': 10
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'enrolled_subjects': 10,
                    'monthly_enrollment_rate': 2.0,
                    'target_enrollment': 20,
                    'status': 'active'
                }
            ],
            'target_enrollment': 100,
            'forecast_months': 12
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        risk_assessment = result['prediction_data']['risk_assessment']
        assert 'confidence_level' in risk_assessment
        assert 'risk_factors' in risk_assessment
        assert risk_assessment['confidence_level'] in ['High', 'Medium', 'Low']
    
    def test_recommendations_generation(self):
        """Test generation of recommendations based on predictions"""
        input_data = {
            'sites': [
                {
                    'site_id': 'SITE001',
                    'enrolled_subjects': 5,
                    'monthly_enrollment_rate': 1.0,  # Very low rate
                    'target_enrollment': 20,
                    'status': 'active'
                }
            ],
            'target_enrollment': 100,
            'forecast_months': 6  # Short timeframe with low rate
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        recommendations = result['prediction_data']['recommendations']
        assert len(recommendations['general']) > 0
        
        # Should recommend actions due to low enrollment rate
        assert any('recruitment' in rec.lower() for rec in recommendations['general'])