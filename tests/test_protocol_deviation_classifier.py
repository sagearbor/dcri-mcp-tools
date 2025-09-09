import pytest
from tools.protocol_deviation_classifier import run


def test_protocol_deviation_classifier_critical():
    """Test critical deviation classification."""
    input_data = {
        'deviation_text': 'Subject experienced SAE but was not reported within 24 hours',
        'deviation_date': '2024-01-15',
        'subject_id': 'SUBJ-001',
        'safety_impact': True
    }
    
    result = run(input_data)
    
    assert result['classification'] == 'critical'
    assert result['reportable'] is True
    assert result['category'] == 'safety'
    assert 'Notify sponsor within 24 hours' in result['corrective_actions']


def test_protocol_deviation_classifier_major():
    """Test major deviation classification."""
    input_data = {
        'deviation_text': 'Subject missed visit 3 and was outside the protocol window',
        'deviation_date': '2024-01-20',
        'subject_id': 'SUBJ-002'
    }
    
    result = run(input_data)
    
    assert result['classification'] == 'major'
    assert result['category'] == 'visit_schedule'


def test_protocol_deviation_classifier_minor():
    """Test minor deviation classification."""
    input_data = {
        'deviation_text': 'Temperature log entry missing for one day',
        'deviation_date': '2024-01-25',
        'safety_impact': False
    }
    
    result = run(input_data)
    
    assert result['classification'] == 'minor'
    assert result['reportable'] is False


def test_protocol_deviation_classifier_categories():
    """Test different deviation categories."""
    test_cases = [
        ('Subject did not meet inclusion criteria', 'enrollment'),
        ('Informed consent not properly dated', 'consent'),
        ('Randomization code broken', 'randomization'),
        ('Incorrect dose administered', 'dosing'),
        ('Blood sample not collected', 'procedure'),
        ('CRF data entry error', 'data')
    ]
    
    for text, expected_category in test_cases:
        result = run({'deviation_text': text})
        assert result['category'] == expected_category


def test_protocol_deviation_classifier_systematic():
    """Test systematic issue detection."""
    input_data = {
        'deviation_text': 'Multiple subjects at site showing repeated protocol violations'
    }
    
    result = run(input_data)
    
    assert result['systematic_issue'] is True


def test_protocol_deviation_classifier_impact_assessment():
    """Test impact assessment."""
    input_data = {
        'deviation_text': 'Wrong randomization assignment given to subject',
        'safety_impact': False
    }
    
    result = run(input_data)
    
    assert 'impact_assessment' in result
    assert result['impact_assessment']['statistical_analysis'] == 'high'
    assert result['impact_assessment']['regulatory_compliance'] == 'high'


def test_protocol_deviation_classifier_documentation():
    """Test documentation requirements."""
    input_data = {
        'deviation_text': 'Subject unblinded accidentally',
        'safety_impact': True
    }
    
    result = run(input_data)
    
    assert 'documentation_requirements' in result
    assert 'Sponsor notification' in result['documentation_requirements']
    assert 'CAPA documentation' in result['documentation_requirements']


def test_protocol_deviation_classifier_notifications():
    """Test notification requirements."""
    input_data = {
        'deviation_text': 'Subject given wrong study drug',
        'safety_impact': True
    }
    
    result = run(input_data)
    
    notifications = result['notification_required']
    assert notifications['sponsor'] is True
    assert notifications['timeline'] == '24 hours'
    assert notifications['regulatory'] is True
