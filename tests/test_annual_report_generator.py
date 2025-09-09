import pytest
from tools.annual_report_generator import run


def test_annual_report_generator_complete_report():
    """Test generating a complete IND annual report."""
    input_data = {
        'ind_number': 'IND123456',
        'reporting_period_start': '2023-01-01',
        'reporting_period_end': '2023-12-31',
        'studies': [
            {
                'study_id': 'STUDY001',
                'title': 'Phase I Safety Study',
                'planned_enrollment': 30,
                'enrolled_subjects': 25,
                'completed_subjects': 20,
                'discontinued_subjects': 5,
                'status': 'Active',
                'safety_data': {
                    'subjects_exposed': 25,
                    'total_aes': 45,
                    'saes': 3,
                    'deaths': 0,
                    'discontinuations_ae': 2,
                    'susars': 1,
                    'dlts': 0,
                    'ae_by_system_organ_class': {
                        'Gastrointestinal disorders': 15,
                        'Nervous system disorders': 10,
                        'Skin disorders': 8
                    }
                },
                'demographics': {
                    'age_groups': {'18-65': 20, '65+': 5},
                    'sex_distribution': {'Male': 15, 'Female': 10},
                    'race_distribution': {'White': 18, 'Black': 4, 'Hispanic': 3}
                },
                'compliance_data': {
                    'protocol_deviations': 3,
                    'regulatory_violations': 0,
                    'overdue_submissions': [],
                    'inspection_findings': []
                }
            }
        ],
        'drug_information': {
            'name': 'Investigational Drug XYZ',
            'chemical_name': '2-methyl-3-phenyl compound',
            'cas_number': '123456-78-9',
            'molecular_formula': 'C15H20N2O',
            'therapeutic_category': 'Oncology'
        },
        'sponsor_information': {
            'name': 'DCRI Clinical Research',
            'address': '123 Research Drive, Durham, NC 27705',
            'contact_person': 'Dr. Jane Smith',
            'phone': '(919) 555-1234',
            'email': 'jane.smith@dcri.org'
        }
    }
    
    result = run(input_data)
    
    assert 'annual_report' in result
    assert 'IND123456' in result['annual_report']
    assert 'DCRI Clinical Research' in result['annual_report']
    assert result['safety_summary']['total_subjects_exposed'] == 25
    assert result['safety_summary']['serious_adverse_events'] == 3
    assert result['safety_summary']['sae_rate'] == 12.0  # 3/25 * 100
    
    assert result['enrollment_summary']['total_enrolled'] == 25
    assert result['enrollment_summary']['enrollment_rate'] == 83.33  # 25/30 * 100
    assert result['enrollment_summary']['completion_rate'] == 80.0  # 20/25 * 100
    
    assert len(result['submission_checklist']) > 0
    assert len(result['recommendations']) > 0


def test_annual_report_generator_multiple_studies():
    """Test annual report generation with multiple studies."""
    input_data = {
        'ind_number': 'IND789012',
        'reporting_period_start': '2023-01-01',
        'reporting_period_end': '2023-12-31',
        'studies': [
            {
                'study_id': 'STUDY001',
                'title': 'Phase I Study',
                'planned_enrollment': 30,
                'enrolled_subjects': 30,
                'completed_subjects': 25,
                'discontinued_subjects': 5,
                'status': 'Completed',
                'safety_data': {
                    'subjects_exposed': 30,
                    'total_aes': 60,
                    'saes': 5,
                    'deaths': 1,
                    'discontinuations_ae': 3,
                    'susars': 2
                }
            },
            {
                'study_id': 'STUDY002',
                'title': 'Phase II Efficacy Study',
                'planned_enrollment': 100,
                'enrolled_subjects': 75,
                'completed_subjects': 60,
                'discontinued_subjects': 15,
                'status': 'Active',
                'safety_data': {
                    'subjects_exposed': 75,
                    'total_aes': 120,
                    'saes': 8,
                    'deaths': 0,
                    'discontinuations_ae': 5,
                    'susars': 1
                }
            }
        ],
        'drug_information': {
            'name': 'Test Drug ABC',
            'therapeutic_category': 'Cardiology'
        },
        'sponsor_information': {
            'name': 'DCRI'
        }
    }
    
    result = run(input_data)
    
    # Aggregate safety data across studies
    assert result['safety_summary']['total_subjects_exposed'] == 105  # 30 + 75
    assert result['safety_summary']['serious_adverse_events'] == 13  # 5 + 8
    assert result['safety_summary']['deaths'] == 1
    assert result['safety_summary']['susars'] == 3  # 2 + 1
    
    # Aggregate enrollment data
    assert result['enrollment_summary']['total_planned_enrollment'] == 130  # 30 + 100
    assert result['enrollment_summary']['total_enrolled'] == 105  # 30 + 75
    assert result['enrollment_summary']['total_completed'] == 85  # 25 + 60
    
    assert len(result['enrollment_summary']['enrollment_by_study']) == 2


def test_annual_report_generator_safety_recommendations():
    """Test recommendations generation based on safety data."""
    input_data = {
        'ind_number': 'IND345678',
        'reporting_period_start': '2023-01-01',
        'reporting_period_end': '2023-12-31',
        'studies': [
            {
                'study_id': 'STUDY001',
                'title': 'High SAE Study',
                'planned_enrollment': 20,
                'enrolled_subjects': 20,
                'completed_subjects': 15,
                'discontinued_subjects': 5,
                'status': 'Active',
                'safety_data': {
                    'subjects_exposed': 20,
                    'total_aes': 100,
                    'saes': 5,  # 25% SAE rate - high
                    'deaths': 0,
                    'discontinuations_ae': 8,  # 40% discontinuation rate - high
                    'susars': 3  # Multiple SUSARs
                }
            }
        ],
        'drug_information': {'name': 'High Risk Drug'},
        'sponsor_information': {'name': 'DCRI'}
    }
    
    result = run(input_data)
    
    # Check that high SAE rate triggers recommendation
    assert result['safety_summary']['sae_rate'] == 25.0
    assert result['safety_summary']['discontinuation_rate'] == 40.0
    
    recommendations = ' '.join(result['recommendations'])
    assert 'enhanced safety monitoring' in recommendations.lower()
    assert 'unexpected serious reactions' in recommendations.lower()


def test_annual_report_generator_enrollment_recommendations():
    """Test recommendations for enrollment issues."""
    input_data = {
        'ind_number': 'IND901234',
        'reporting_period_start': '2023-01-01',
        'reporting_period_end': '2023-12-31',
        'studies': [
            {
                'study_id': 'STUDY001',
                'title': 'Slow Enrollment Study',
                'planned_enrollment': 100,
                'enrolled_subjects': 60,  # 60% enrollment rate - low
                'completed_subjects': 40,  # 66.7% completion rate - low
                'discontinued_subjects': 20,
                'status': 'Active',
                'safety_data': {
                    'subjects_exposed': 60,
                    'total_aes': 30,
                    'saes': 2,
                    'deaths': 0,
                    'discontinuations_ae': 1,
                    'susars': 0
                }
            }
        ],
        'drug_information': {'name': 'Test Drug'},
        'sponsor_information': {'name': 'DCRI'}
    }
    
    result = run(input_data)
    
    assert result['enrollment_summary']['enrollment_rate'] == 60.0
    assert result['enrollment_summary']['completion_rate'] == 66.67
    
    recommendations = ' '.join(result['recommendations'])
    assert 'enrollment strategies' in recommendations.lower()
    assert 'discontinuation' in recommendations.lower()


def test_annual_report_generator_executive_summary():
    """Test executive summary generation."""
    input_data = {
        'ind_number': 'IND567890',
        'reporting_period_start': '2023-06-01',
        'reporting_period_end': '2024-05-31',
        'studies': [
            {
                'study_id': 'STUDY001',
                'title': 'Test Study',
                'planned_enrollment': 50,
                'enrolled_subjects': 45,
                'completed_subjects': 40,
                'discontinued_subjects': 5,
                'status': 'Active',
                'safety_data': {
                    'subjects_exposed': 45,
                    'total_aes': 75,
                    'saes': 3,
                    'deaths': 0,
                    'discontinuations_ae': 2,
                    'susars': 0
                }
            }
        ],
        'drug_information': {'name': 'Study Drug'},
        'sponsor_information': {'name': 'DCRI'}
    }
    
    result = run(input_data)
    
    executive_summary = result['executive_summary']
    assert 'IND567890' in executive_summary
    assert '06/01/2023' in executive_summary
    assert '05/31/2024' in executive_summary
    assert 'Subjects Enrolled: 45' in executive_summary
    assert 'Serious Adverse Events: 3' in executive_summary
    assert 'SUSARs: 0' in executive_summary


def test_annual_report_generator_missing_ind_number():
    """Test error handling when IND number is missing."""
    input_data = {
        'reporting_period_start': '2023-01-01',
        'reporting_period_end': '2023-12-31',
        'studies': []
    }
    
    result = run(input_data)
    
    assert 'error' in result
    assert 'IND number is required' in result['error']
    assert len(result['recommendations']) > 0


def test_annual_report_generator_invalid_dates():
    """Test error handling with invalid date formats."""
    input_data = {
        'ind_number': 'IND123456',
        'reporting_period_start': 'invalid-date',
        'reporting_period_end': '2023-12-31',
        'studies': []
    }
    
    result = run(input_data)
    
    assert 'error' in result
    assert 'Invalid date format' in result['error']


def test_annual_report_generator_submission_checklist():
    """Test submission checklist generation."""
    input_data = {
        'ind_number': 'IND111222',
        'reporting_period_start': '2023-01-01',
        'reporting_period_end': '2023-12-31',
        'studies': [],
        'drug_information': {'name': 'Test Drug'},
        'sponsor_information': {'name': 'DCRI'}
    }
    
    result = run(input_data)
    
    checklist = result['submission_checklist']
    assert len(checklist) > 0
    
    # Check for required checklist items
    checklist_items = [item['item'] for item in checklist]
    assert 'Cover Letter' in checklist_items
    assert 'Annual Report Form' in checklist_items
    assert 'Safety Summary' in checklist_items
    assert 'Clinical Updates' in checklist_items