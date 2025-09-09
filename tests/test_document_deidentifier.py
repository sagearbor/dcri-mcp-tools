import pytest
from tools.document_deidentifier import run


def test_document_deidentifier_basic():
    """Test basic PII removal from document."""
    input_data = {
        'text': """
        Patient Name: John Doe
        DOB: 01/15/1980
        MRN: 123456789
        Email: john.doe@example.com
        Phone: 555-123-4567
        SSN: 123-45-6789
        Address: 123 Main Street, Boston, MA 02134
        """,
        'mode': 'full'
    }
    
    result = run(input_data)
    
    assert 'deidentified_text' in result
    assert 'items_removed' in result
    assert 'statistics' in result
    
    # Check that PII was removed
    assert 'John Doe' not in result['deidentified_text']
    assert '01/15/1980' not in result['deidentified_text']
    assert 'john.doe@example.com' not in result['deidentified_text']
    assert '555-123-4567' not in result['deidentified_text']
    assert '123-45-6789' not in result['deidentified_text']
    
    # Check that replacement markers are present
    assert '[' in result['deidentified_text']
    assert 'REMOVED]' in result['deidentified_text']


def test_document_deidentifier_hash_mode():
    """Test PII replacement with hash mode."""
    input_data = {
        'text': 'Patient email: test@example.com',
        'mode': 'hash'
    }
    
    result = run(input_data)
    
    assert 'test@example.com' not in result['deidentified_text']
    assert '[EMAIL_' in result['deidentified_text']
    assert result['mode_used'] == 'hash'


def test_document_deidentifier_empty_text():
    """Test with empty text."""
    input_data = {
        'text': '',
        'mode': 'full'
    }
    
    result = run(input_data)
    
    assert result['deidentified_text'] == ''
    assert result['items_removed'] == []
    assert result['statistics'] == {}


def test_document_deidentifier_custom_patterns():
    """Test with custom patterns."""
    input_data = {
        'text': 'Study ID: STUDY-2024-001, Investigator: Dr. Smith',
        'mode': 'full',
        'custom_patterns': [r'STUDY-\d{4}-\d{3}']
    }
    
    result = run(input_data)
    
    assert 'STUDY-2024-001' not in result['deidentified_text']
    assert '[CUSTOM_0_REMOVED]' in result['deidentified_text']


def test_document_deidentifier_multiple_pii_types():
    """Test removal of multiple PII types."""
    input_data = {
        'text': """
        Subject ID: ABC12345
        Email: patient@clinic.org
        Phone: (555) 987-6543
        IP Address: 192.168.1.1
        Credit Card: 1234-5678-9012-3456
        """,
        'mode': 'full'
    }
    
    result = run(input_data)
    
    assert 'patient@clinic.org' not in result['deidentified_text']
    assert '(555) 987-6543' not in result['deidentified_text']
    assert '192.168.1.1' not in result['deidentified_text']
    assert '1234-5678-9012-3456' not in result['deidentified_text']
    assert 'ABC12345' not in result['deidentified_text']
    
    assert len(result['items_removed']) >= 4
    assert result['total_items_removed'] >= 4


def test_document_deidentifier_statistics():
    """Test that statistics are correctly counted."""
    input_data = {
        'text': """
        Email1: test1@example.com
        Email2: test2@example.com
        Phone1: 555-111-2222
        Phone2: 555-333-4444
        """,
        'mode': 'full'
    }
    
    result = run(input_data)
    
    assert result['statistics'].get('email', 0) == 2
    assert result['statistics'].get('phone', 0) == 2
    assert result['total_items_removed'] == 4