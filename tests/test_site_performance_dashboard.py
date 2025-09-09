"""
Tests for Site Performance Dashboard Tool
"""

import pytest
from tools.site_performance_dashboard import run

class TestSitePerformanceDashboard:
    
    def test_successful_dashboard_generation(self):
        """Test successful dashboard generation with valid site data"""
        input_data = {
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Metro Medical Center',
                    'enrolled_subjects': 25,
                    'target_enrollment': 30,
                    'monthly_enrollment_rate': 4.2,
                    'protocol_deviations': 3,
                    'total_visits': 120,
                    'data_queries': 8,
                    'dropouts': 2,
                    'last_updated': '2024-01-15T00:00:00'
                },
                {
                    'site_id': 'SITE002',
                    'site_name': 'University Hospital',
                    'enrolled_subjects': 15,
                    'target_enrollment': 25,
                    'monthly_enrollment_rate': 3.1,
                    'protocol_deviations': 8,
                    'total_visits': 75,
                    'data_queries': 12,
                    'dropouts': 4,
                    'last_updated': '2024-01-15T00:00:00'
                }
            ],
            'time_period': 30,
            'metrics_threshold': {
                'enrollment_rate': 4.0,
                'protocol_deviation_rate': 0.05,
                'query_rate': 0.15,
                'dropout_rate': 0.12
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'dashboard_data' in result
        
        dashboard = result['dashboard_data']
        assert dashboard['overall_statistics']['total_enrollment'] == 40
        assert dashboard['overall_statistics']['sites_count'] == 2
        assert len(dashboard['site_metrics']) == 2
        
        # Check site performance scoring
        site1 = next(s for s in dashboard['site_metrics'] if s['site_id'] == 'SITE001')
        assert site1['performance_category'] == 'High Performer'
        
        site2 = next(s for s in dashboard['site_metrics'] if s['site_id'] == 'SITE002')
        assert site2['performance_category'] in ['Average', 'Underperformer']
    
    def test_empty_sites_data(self):
        """Test handling of empty sites data"""
        input_data = {
            'sites': [],
            'time_period': 30
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'No site data provided' in result['error']
    
    def test_single_site_analysis(self):
        """Test analysis with single site"""
        input_data = {
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'Solo Site',
                    'enrolled_subjects': 10,
                    'target_enrollment': 20,
                    'monthly_enrollment_rate': 2.0,
                    'protocol_deviations': 1,
                    'total_visits': 50,
                    'data_queries': 3,
                    'dropouts': 1
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        dashboard = result['dashboard_data']
        assert dashboard['overall_statistics']['sites_count'] == 1
        assert len(dashboard['site_metrics']) == 1
    
    def test_performance_thresholds(self):
        """Test performance assessment against thresholds"""
        input_data = {
            'sites': [
                {
                    'site_id': 'SITE001',
                    'enrolled_subjects': 10,
                    'target_enrollment': 20,
                    'monthly_enrollment_rate': 1.0,  # Below threshold
                    'protocol_deviations': 10,
                    'total_visits': 50,  # High deviation rate
                    'data_queries': 8,   # High query rate
                    'dropouts': 3        # High dropout rate
                }
            ],
            'metrics_threshold': {
                'enrollment_rate': 2.0,
                'protocol_deviation_rate': 0.1,
                'query_rate': 0.1,
                'dropout_rate': 0.1
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        site_metrics = result['dashboard_data']['site_metrics'][0]
        assert len(site_metrics['alerts']) > 0
        assert site_metrics['performance_category'] == 'Underperformer'
    
    def test_recommendations_generation(self):
        """Test generation of recommendations based on performance"""
        input_data = {
            'sites': [
                {
                    'site_id': f'SITE00{i}',
                    'enrolled_subjects': 5,
                    'target_enrollment': 20,
                    'monthly_enrollment_rate': 1.0,
                    'protocol_deviations': 5,
                    'total_visits': 25,
                    'data_queries': 4,
                    'dropouts': 2
                } for i in range(1, 6)  # 5 underperforming sites
            ],
            'metrics_threshold': {
                'enrollment_rate': 3.0,
                'protocol_deviation_rate': 0.1,
                'query_rate': 0.15,
                'dropout_rate': 0.15
            }
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        recommendations = result['dashboard_data']['recommendations']
        assert len(recommendations) > 0
        assert any('underperforming sites' in rec.lower() for rec in recommendations)
    
    def test_missing_optional_fields(self):
        """Test handling of missing optional fields"""
        input_data = {
            'sites': [
                {
                    'site_id': 'SITE001',
                    'enrolled_subjects': 15,
                    'target_enrollment': 25
                    # Missing optional fields like monthly_rate, deviations, etc.
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        dashboard = result['dashboard_data']
        assert len(dashboard['site_metrics']) == 1
        
        site_metric = dashboard['site_metrics'][0]
        assert site_metric['enrollment']['enrolled'] == 15
        assert site_metric['enrollment']['target'] == 25