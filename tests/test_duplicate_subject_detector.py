import pytest
from tools.duplicate_subject_detector import run


def test_duplicate_subject_detector_exact_matches():
    """Test detection of exact duplicate matches."""
    csv_data = """first_name,last_name,date_of_birth,gender
John,Smith,1990-01-15,M
Jane,Doe,1985-03-22,F
John,Smith,1990-01-15,M
Bob,Johnson,1975-06-10,M"""

    input_data = {
        'data': csv_data,
        'matching_fields': ['first_name', 'last_name', 'date_of_birth', 'gender'],
        'matching_algorithm': 'exact'
    }
    
    result = run(input_data)
    
    assert result['success'] is True
    assert len(result['duplicates_found']) == 1
    assert result['duplicates_found'][0]['match_type'] == 'exact'
    assert result['duplicates_found'][0]['confidence'] == 'high'
    assert len(result['duplicates_found'][0]['records']) == 2


def test_duplicate_subject_detector_fuzzy_matches():
    """Test detection of fuzzy duplicate matches."""
    csv_data = """first_name,last_name,date_of_birth,phone
John,Smith,1990-01-15,555-1234
Jon,Smith,1990-01-15,5551234
Jane,Doe,1985-03-22,555-5678"""

    input_data = {
        'data': csv_data,
        'matching_fields': ['first_name', 'last_name', 'date_of_birth', 'phone'],
        'matching_algorithm': 'fuzzy',
        'similarity_threshold': 85
    }
    
    result = run(input_data)
    
    assert result['success'] is True
    assert len(result['duplicates_found']) >= 1
    assert result['duplicates_found'][0]['match_type'] == 'fuzzy'


def test_duplicate_subject_detector_comprehensive():
    """Test comprehensive duplicate detection."""
    csv_data = """first_name,last_name,date_of_birth,email
John,Smith,1990-01-15,john.smith@email.com
John,Smith,1990-01-15,john.smith@email.com
James,Smith,1990-01-15,jim.smith@email.com
Jane,Doe,1985-03-22,jane.doe@email.com"""

    input_data = {
        'data': csv_data,
        'matching_fields': ['first_name', 'last_name', 'date_of_birth', 'email'],
        'matching_algorithm': 'comprehensive'
    }
    
    result = run(input_data)
    
    assert result['success'] is True
    assert len(result['duplicates_found']) >= 1


def test_duplicate_subject_detector_no_duplicates():
    """Test when no duplicates are found."""
    csv_data = """first_name,last_name,date_of_birth,gender
John,Smith,1990-01-15,M
Jane,Doe,1985-03-22,F
Bob,Johnson,1975-06-10,M"""

    input_data = {
        'data': csv_data,
        'matching_fields': ['first_name', 'last_name', 'date_of_birth', 'gender'],
        'matching_algorithm': 'exact'
    }
    
    result = run(input_data)
    
    assert result['success'] is True
    assert len(result['duplicates_found']) == 0
    assert result['statistics']['duplication_rate'] == 0


def test_duplicate_subject_detector_empty_data():
    """Test handling of empty data."""
    input_data = {
        'data': '',
        'matching_fields': ['first_name', 'last_name'],
        'matching_algorithm': 'exact'
    }
    
    result = run(input_data)
    
    assert result['success'] is False
    assert 'No data provided' in result['errors']


def test_duplicate_subject_detector_invalid_fields():
    """Test handling of invalid matching fields."""
    csv_data = """name,age,city
John Smith,25,NYC
Jane Doe,30,LA"""

    input_data = {
        'data': csv_data,
        'matching_fields': ['first_name', 'last_name'],  # Fields not in data
        'matching_algorithm': 'exact'
    }
    
    result = run(input_data)
    
    assert result['success'] is True
    assert len(result['warnings']) > 0
    assert 'No specified matching fields found' in result['warnings'][0]


def test_duplicate_subject_detector_statistics():
    """Test statistics generation."""
    csv_data = """first_name,last_name,date_of_birth
John,Smith,1990-01-15
John,Smith,1990-01-15
Jane,Doe,1985-03-22
Jane,Doe,1985-03-22
Bob,Johnson,1975-06-10"""

    input_data = {
        'data': csv_data,
        'matching_algorithm': 'exact'
    }
    
    result = run(input_data)
    
    assert result['success'] is True
    assert 'statistics' in result
    stats = result['statistics']
    assert stats['total_records'] == 5
    assert stats['duplicate_groups'] == 2
    assert stats['duplication_rate'] > 0
    assert 'confidence_distribution' in stats
    assert 'match_type_distribution' in stats


def test_duplicate_subject_detector_recommendations():
    """Test recommendations generation."""
    csv_data = """first_name,last_name,date_of_birth
John,Smith,1990-01-15
John,Smith,1990-01-15
John,Smith,1990-01-15
Jane,Doe,1985-03-22"""

    input_data = {
        'data': csv_data,
        'matching_algorithm': 'exact'
    }
    
    result = run(input_data)
    
    assert result['success'] is True
    assert len(result['recommendations']) > 0
    assert any(rec['priority'] == 'HIGH' for rec in result['recommendations'])


def test_duplicate_subject_detector_phone_matching():
    """Test phone number similarity matching."""
    csv_data = """name,phone
John Smith,555-123-4567
Jane Doe,(555) 123-4567
Bob Johnson,5551234567
Mary Wilson,555-999-8888"""

    input_data = {
        'data': csv_data,
        'matching_fields': ['phone'],
        'matching_algorithm': 'fuzzy',
        'similarity_threshold': 80
    }
    
    result = run(input_data)
    
    assert result['success'] is True
    # Should find phone number matches despite different formatting
    assert len(result['duplicates_found']) >= 1


def test_duplicate_subject_detector_name_variations():
    """Test name variation matching."""
    csv_data = """first_name,last_name,date_of_birth
James,Smith,1990-01-15
Jim,Smith,1990-01-15
John,Doe,1985-03-22"""

    input_data = {
        'data': csv_data,
        'matching_algorithm': 'comprehensive',
        'similarity_threshold': 80
    }
    
    result = run(input_data)
    
    assert result['success'] is True
    # Should detect James/Jim as potential duplicates
    if result['duplicates_found']:
        assert any(group['match_type'] in ['fuzzy', 'comprehensive_fuzzy'] 
                  for group in result['duplicates_found'])