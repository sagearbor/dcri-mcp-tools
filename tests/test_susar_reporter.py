import pytest
from tools.susar_reporter import run


def test_susar_reporter_valid_cioms():
    """Test SUSAR reporting with valid data in CIOMS format."""
    input_data = {
        'susar_data': {
            'patient_identifier': 'P001',
            'age': '45',
            'sex': 'Female',
            'weight': '65',
            'adverse_event_description': 'Severe allergic reaction with anaphylaxis',
            'onset_date': '2024-01-15',
            'event_outcome': 'Recovered',
            'drug_name': 'Investigational Drug XYZ',
            'dose': '10mg daily',
            'route': 'Oral',
            'indication': 'Hypertension',
            'concomitant_medications': 'Acetaminophen 500mg PRN',
            'medical_history': 'No known allergies',
            'reporter_information': 'Dr. Smith, Principal Investigator',
            'seriousness_criteria': ['Life-threatening'],
            'expectedness': 'unexpected',
            'narrative': 'Patient developed severe allergic reaction 2 hours after first dose.'
        },
        'format_type': 'CIOMS',
        'regulatory_authority': 'FDA',
        'urgency': 'expedited',
        'include_narrative': True,
        'blinding_status': 'unblinded',
        'reference_date': '2024-01-20'
    }
    
    result = run(input_data)
    
    assert result['validation_status'] == 'valid'
    assert len(result['validation_errors']) == 0
    assert result['formatted_report'] != ''
    assert 'CIOMS I' in result['formatted_report']
    assert 'P001' in result['formatted_report']
    assert 'Severe allergic reaction' in result['formatted_report']
    assert result['summary']['is_ready_for_submission'] is True
    assert result['summary']['days_until_deadline'] is not None


def test_susar_reporter_missing_required_fields():
    """Test SUSAR reporting with missing required fields."""
    input_data = {
        'susar_data': {
            'patient_identifier': 'P001',
            'age': '45',
            # Missing several required fields
            'adverse_event_description': 'Severe allergic reaction'
        },
        'format_type': 'CIOMS',
        'regulatory_authority': 'FDA',
        'urgency': 'expedited'
    }
    
    result = run(input_data)
    
    assert result['validation_status'] == 'invalid'
    assert len(result['validation_errors']) > 0
    assert result['formatted_report'] == ''
    assert result['summary']['is_ready_for_submission'] is False
    
    # Check for specific missing fields
    error_messages = ' '.join(result['validation_errors'])
    assert 'sex' in error_messages.lower()
    assert 'drug_name' in error_messages.lower()


def test_susar_reporter_fda_format():
    """Test SUSAR reporting in FDA 3500A format."""
    input_data = {
        'susar_data': {
            'patient_identifier': 'P002',
            'age': '65',
            'sex': 'Male',
            'adverse_event_description': 'Cardiac arrhythmia',
            'onset_date': '2024-02-01',
            'event_outcome': 'Ongoing',
            'drug_name': 'Study Drug ABC',
            'dose': '20mg BID',
            'route': 'Oral',
            'indication': 'Heart failure',
            'concomitant_medications': 'None',
            'medical_history': 'Previous myocardial infarction',
            'reporter_information': 'Dr. Johnson, Cardiologist',
            'seriousness_criteria': ['Hospitalization'],
            'expectedness': 'unexpected'
        },
        'format_type': 'FDA_3500A',
        'regulatory_authority': 'FDA',
        'urgency': 'expedited',
        'reference_date': '2024-02-10'
    }
    
    result = run(input_data)
    
    assert result['validation_status'] == 'valid'
    assert 'FDA FORM 3500A' in result['formatted_report']
    assert 'P002' in result['formatted_report']
    assert 'Cardiac arrhythmia' in result['formatted_report']
    assert result['regulatory_requirements']['authority'] == 'FDA'


def test_susar_reporter_e2b_xml_format():
    """Test SUSAR reporting in E2B XML format."""
    input_data = {
        'susar_data': {
            'patient_identifier': 'P003',
            'age': '30',
            'sex': 'Female',
            'adverse_event_description': 'Hepatotoxicity',
            'onset_date': '2024-01-20',
            'event_outcome': 'Recovered',
            'drug_name': 'Investigational Compound',
            'dose': '5mg daily',
            'route': 'Oral',
            'indication': 'Depression',
            'concomitant_medications': 'Birth control pills',
            'medical_history': 'None significant',
            'reporter_information': 'Dr. Wilson, Psychiatrist',
            'seriousness_criteria': ['Important medical event'],
            'expectedness': 'unexpected'
        },
        'format_type': 'E2B_XML',
        'regulatory_authority': 'EMA',
        'urgency': 'expedited',
        'reference_date': '2024-01-25'
    }
    
    result = run(input_data)
    
    assert result['validation_status'] == 'valid'
    assert '<?xml version="1.0"' in result['formatted_report']
    assert 'ichicsr' in result['formatted_report']
    assert result['regulatory_requirements']['authority'] == 'EMA'


def test_susar_reporter_late_reporting_warning():
    """Test SUSAR reporting with late reporting warning."""
    input_data = {
        'susar_data': {
            'patient_identifier': 'P004',
            'age': '55',
            'sex': 'Male',
            'adverse_event_description': 'Severe skin reaction',
            'onset_date': '2023-12-01',  # More than 15 days ago
            'event_outcome': 'Recovered',
            'drug_name': 'Test Drug',
            'dose': '15mg daily',
            'route': 'Oral',
            'indication': 'Arthritis',
            'concomitant_medications': 'Ibuprofen',
            'medical_history': 'Skin allergies',
            'reporter_information': 'Dr. Brown, Dermatologist',
            'seriousness_criteria': ['Hospitalization'],
            'expectedness': 'unexpected'
        },
        'format_type': 'CIOMS',
        'regulatory_authority': 'FDA',
        'urgency': 'expedited'
    }
    
    result = run(input_data)
    
    assert result['validation_status'] == 'warnings'
    assert len(result['validation_warnings']) > 0
    
    # Check for late reporting warning
    warning_messages = ' '.join(result['validation_warnings'])
    assert 'days old' in warning_messages.lower()


def test_susar_reporter_expected_event_warning():
    """Test SUSAR reporting with expected event warning."""
    input_data = {
        'susar_data': {
            'patient_identifier': 'P005',
            'age': '40',
            'sex': 'Female',
            'adverse_event_description': 'Nausea',
            'onset_date': '2024-01-25',
            'event_outcome': 'Recovered',
            'drug_name': 'Known Drug',
            'dose': '10mg daily',
            'route': 'Oral',
            'indication': 'Cancer',
            'concomitant_medications': 'None',
            'medical_history': 'Breast cancer',
            'reporter_information': 'Dr. Davis, Oncologist',
            'seriousness_criteria': ['Life-threatening'],
            'expectedness': 'expected'  # This should trigger a warning
        },
        'format_type': 'CIOMS',
        'regulatory_authority': 'FDA',
        'urgency': 'expedited'
    }
    
    result = run(input_data)
    
    assert result['validation_status'] == 'warnings'
    assert len(result['validation_warnings']) > 0
    
    # Check for expected event warning
    warning_messages = ' '.join(result['validation_warnings'])
    assert 'expected' in warning_messages.lower()


def test_susar_reporter_no_data():
    """Test error handling when no SUSAR data is provided."""
    input_data = {
        'format_type': 'CIOMS',
        'regulatory_authority': 'FDA'
    }
    
    result = run(input_data)
    
    assert 'error' in result
    assert result['validation_status'] == 'invalid'
    assert len(result['validation_errors']) > 0
    assert result['formatted_report'] == ''


def test_susar_reporter_ema_format():
    """Test SUSAR reporting in EMA EudraVigilance format."""
    input_data = {
        'susar_data': {
            'patient_identifier': 'P006',
            'age': '28',
            'sex': 'Male',
            'adverse_event_description': 'Neurological symptoms',
            'onset_date': '2024-02-10',
            'event_outcome': 'Ongoing',
            'drug_name': 'Experimental Drug',
            'dose': '25mg twice daily',
            'route': 'Oral',
            'indication': 'Multiple sclerosis',
            'concomitant_medications': 'Interferon beta',
            'medical_history': 'Multiple sclerosis diagnosed 2019',
            'reporter_information': 'Dr. Martinez, Neurologist',
            'seriousness_criteria': ['Disability'],
            'expectedness': 'unexpected'
        },
        'format_type': 'EMA_EUDRAVIGILANCE',
        'regulatory_authority': 'EMA',
        'urgency': 'expedited',
        'reference_date': '2024-02-15'
    }
    
    result = run(input_data)
    
    assert result['validation_status'] == 'valid'
    assert 'EMA EUDRAVIGILANCE REPORT' in result['formatted_report']
    assert 'P006' in result['formatted_report']
    assert 'Neurological symptoms' in result['formatted_report']