"""
Tests for Screen Failure Analyzer Tool
"""

import pytest
from datetime import datetime, timedelta
from tools.screen_failure_analyzer import run

class TestScreenFailureAnalyzer:
    
    def test_successful_screening_analysis(self):
        """Test successful screening failure analysis"""
        current_date = datetime.now()
        input_data = {
            'screening_data': [
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=30)).isoformat(),
                    'outcome': 'enrolled',
                    'age': 45,
                    'gender': 'Female',
                    'race': 'Caucasian'
                },
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=25)).isoformat(),
                    'outcome': 'failed',
                    'failure_reason': 'Age outside range',
                    'age': 80,
                    'gender': 'Male',
                    'race': 'African American'
                },
                {
                    'site_id': 'SITE002',
                    'screening_date': (current_date - timedelta(days=20)).isoformat(),
                    'outcome': 'failed',
                    'failure_reason': 'Excluded medication use',
                    'age': 55,
                    'gender': 'Female',
                    'race': 'Hispanic'
                }
            ],
            'inclusion_criteria': [
                {
                    'keyword': 'age',
                    'description': 'Age 18-75 years'
                }
            ],
            'exclusion_criteria': [
                {
                    'keyword': 'medication',
                    'description': 'Prohibited medication use'
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
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'analysis_data' in result
        
        analysis = result['analysis_data']
        assert analysis['overall_statistics']['total_screened'] == 3
        assert analysis['overall_statistics']['enrolled'] == 1
        assert analysis['overall_statistics']['screen_failures'] == 2
        assert analysis['overall_statistics']['screen_failure_rate'] == 66.7
        
        # Check failure reason analysis
        assert 'Age outside range' in analysis['failure_reasons']
        assert 'Excluded medication use' in analysis['failure_reasons']
    
    def test_failure_reason_categorization(self):
        """Test categorization of failure reasons"""
        current_date = datetime.now()
        input_data = {
            'screening_data': [
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=30)).isoformat(),
                    'outcome': 'failed',
                    'failure_reason': 'Age too young'
                },
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=25)).isoformat(),
                    'outcome': 'failed',
                    'failure_reason': 'Prohibited medication'
                }
            ],
            'inclusion_criteria': [
                {
                    'keyword': 'age',
                    'description': 'Age 18-65 years'
                }
            ],
            'exclusion_criteria': [
                {
                    'keyword': 'medication',
                    'description': 'Certain medications'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        analysis = result['analysis_data']
        
        # Check that failure reasons are categorized correctly
        age_failure = analysis['failure_reasons']['Age too young']
        assert age_failure['criteria_type'] == 'inclusion'
        
        med_failure = analysis['failure_reasons']['Prohibited medication']
        assert med_failure['criteria_type'] == 'exclusion'
    
    def test_site_performance_comparison(self):
        """Test site performance comparison"""
        current_date = datetime.now()
        input_data = {
            'screening_data': [
                # Site 1: High failure rate
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=i)).isoformat(),
                    'outcome': 'failed',
                    'failure_reason': 'Various reasons'
                } for i in range(1, 8)  # 7 failures
            ] + [
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=10)).isoformat(),
                    'outcome': 'enrolled'
                }
            ] + [
                # Site 2: Low failure rate
                {
                    'site_id': 'SITE002',
                    'screening_date': (current_date - timedelta(days=i)).isoformat(),
                    'outcome': 'enrolled'
                } for i in range(1, 8)  # 7 enrollments
            ] + [
                {
                    'site_id': 'SITE002',
                    'screening_date': (current_date - timedelta(days=10)).isoformat(),
                    'outcome': 'failed',
                    'failure_reason': 'Single failure'
                }
            ],
            'sites': [
                {
                    'site_id': 'SITE001',
                    'site_name': 'High Failure Site'
                },
                {
                    'site_id': 'SITE002',
                    'site_name': 'Low Failure Site'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        analysis = result['analysis_data']
        
        # Check site performance
        site1_perf = analysis['site_performance']['SITE001']
        site2_perf = analysis['site_performance']['SITE002']
        
        assert site1_perf['screen_failure_rate'] > site2_perf['screen_failure_rate']
        
        # Should have insights about site variation
        insights = analysis['insights']
        assert len(insights) > 0
    
    def test_demographic_analysis(self):
        """Test demographic analysis of screen failures"""
        current_date = datetime.now()
        input_data = {
            'screening_data': [
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=30)).isoformat(),
                    'outcome': 'failed',
                    'failure_reason': 'Age criteria',
                    'age': 75,
                    'gender': 'Male'
                },
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=25)).isoformat(),
                    'outcome': 'enrolled',
                    'age': 50,
                    'gender': 'Female'
                },
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=20)).isoformat(),
                    'outcome': 'failed',
                    'failure_reason': 'Other criteria',
                    'age': 30,
                    'gender': 'Male'
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        analysis = result['analysis_data']
        
        # Check demographic analysis
        demo_analysis = analysis['demographic_analysis']
        assert '65+' in demo_analysis['age_groups']  # Age 75 should be in 65+ group
        assert 'Male' in demo_analysis['gender']
        
        # Check failure rates by demographics
        male_data = demo_analysis['gender']['Male']
        assert male_data['failure_rate'] > 0  # Males had failures
    
    def test_temporal_trends(self):
        """Test temporal trend analysis"""
        current_date = datetime.now()
        # Create data spanning multiple months
        input_data = {
            'screening_data': [
                # Month 1: Higher failure rate
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=60)).isoformat(),
                    'outcome': 'failed',
                    'failure_reason': 'Various'
                },
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=55)).isoformat(),
                    'outcome': 'failed',
                    'failure_reason': 'Various'
                },
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=50)).isoformat(),
                    'outcome': 'enrolled'
                },
                # Month 2: Lower failure rate
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=30)).isoformat(),
                    'outcome': 'enrolled'
                },
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=25)).isoformat(),
                    'outcome': 'enrolled'
                },
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=20)).isoformat(),
                    'outcome': 'failed',
                    'failure_reason': 'Single failure'
                }
            ],
            'analysis_period': 90
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        analysis = result['analysis_data']
        
        # Check temporal analysis
        temporal = analysis['temporal_analysis']
        assert len(temporal) >= 2  # Should have multiple months
        
        # Check for temporal insights
        insights = analysis['insights']
        # May or may not have temporal insights depending on data patterns
        assert isinstance(insights, list)
    
    def test_multiple_failure_reasons(self):
        """Test handling of multiple failure reasons per screening"""
        current_date = datetime.now()
        input_data = {
            'screening_data': [
                {
                    'site_id': 'SITE001',
                    'screening_date': (current_date - timedelta(days=30)).isoformat(),
                    'outcome': 'failed',
                    'failure_reason': 'Age criteria, Medication use, Lab values'  # Multiple reasons
                }
            ]
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        analysis = result['analysis_data']
        
        # Should parse multiple failure reasons
        failure_reasons = analysis['failure_reasons']
        assert 'Age criteria' in failure_reasons
        assert 'Medication use' in failure_reasons
        assert 'Lab values' in failure_reasons
    
    def test_empty_screening_data(self):
        """Test handling of empty screening data"""
        input_data = {
            'screening_data': [],
            'inclusion_criteria': [],
            'exclusion_criteria': []
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'No screening data provided' in result['error']
    
    def test_no_data_in_period(self):
        """Test handling when no data exists in analysis period"""
        old_date = datetime.now() - timedelta(days=200)
        input_data = {
            'screening_data': [
                {
                    'site_id': 'SITE001',
                    'screening_date': old_date.isoformat(),  # Outside analysis period
                    'outcome': 'enrolled'
                }
            ],
            'analysis_period': 90  # Only last 90 days
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'No screening data found for the specified analysis period' in result['error']