"""
Tests for Document Redaction Tool
"""

import pytest
import json
from tools.document_redaction_tool import run


class TestDocumentRedactionTool:
    
    def test_minimal_redaction_level(self):
        """Test minimal redaction level"""
        document_text = """
        Patient: John Smith, DOB: 01/15/1975, SSN: 123-45-6789
        MRN: MR123456, Phone: 555-123-4567
        Study participation: The patient consented to participate.
        """
        
        input_data = {
            'text': document_text,
            'redaction_level': 'minimal'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'redacted_text' in result
        
        # Should redact medical IDs and contact info
        redacted_text = result['redacted_text']
        assert 'MR123456' not in redacted_text or 'XXXXX' in redacted_text
        assert '555-123-4567' not in redacted_text or 'XXX' in redacted_text
        assert '123-45-6789' not in redacted_text or 'XXX' in redacted_text
        
        # Statistics should be present
        stats = result['statistics']
        assert 'redaction_percentage' in stats
        assert stats['total_redactions'] > 0
    
    def test_standard_redaction_level(self):
        """Test standard redaction level"""
        document_text = """
        Patient Name: Jane Doe
        Date of Birth: 12/25/1980
        Medical Record: MR789012
        Address: 123 Main Street, Anytown, ST 12345
        Email: jane.doe@email.com
        Phone: (555) 987-6543
        """
        
        input_data = {
            'text': document_text,
            'redaction_level': 'standard'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        redacted_text = result['redacted_text']
        
        # Should redact names, dates, medical IDs, and contact info
        assert 'Jane Doe' not in redacted_text or 'XXXX' in redacted_text
        assert '12/25/1980' not in redacted_text or 'XX/XX/XXXX' in redacted_text
        assert 'MR789012' not in redacted_text or 'XXXXXXXX' in redacted_text
        assert 'jane.doe@email.com' not in redacted_text or 'XXXX' in redacted_text
        
        # Should have higher redaction count than minimal
        assert result['statistics']['total_redactions'] > 3
    
    def test_maximum_redaction_level(self):
        """Test maximum redaction level"""
        document_text = """
        Dr. Smith from Mayo Clinic treated the patient.
        Financial information: Payment of $5,000.00 was processed.
        Credit card: 4111-1111-1111-1111
        Institution: Duke University Medical Center
        ZIP Code: 27710
        """
        
        input_data = {
            'text': document_text,
            'redaction_level': 'maximum'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        redacted_text = result['redacted_text']
        
        # Should redact everything including institutions and financial info
        assert 'Mayo Clinic' not in redacted_text or 'XXXX' in redacted_text
        assert '$5,000.00' not in redacted_text or '$X,XXX.XX' in redacted_text
        assert '4111-1111-1111-1111' not in redacted_text or 'XXXX' in redacted_text
        assert 'Duke University' not in redacted_text or 'XXXX' in redacted_text
        
        # Should have highest redaction count
        assert result['statistics']['total_redactions'] > 5
    
    def test_custom_patterns_redaction(self):
        """Test custom redaction patterns"""
        document_text = """
        Patient ID: STUDY-001-001
        Protocol Number: PROTO-2024-ABC
        Custom identifier: CUSTOM_ID_12345
        """
        
        custom_patterns = [
            r'STUDY-\d{3}-\d{3}',
            r'PROTO-\d{4}-[A-Z]{3}',
            r'CUSTOM_ID_\d{5}'
        ]
        
        input_data = {
            'text': document_text,
            'redaction_level': 'standard',
            'custom_patterns': custom_patterns
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        redacted_text = result['redacted_text']
        
        # Custom patterns should be redacted
        assert 'STUDY-001-001' not in redacted_text
        assert 'PROTO-2024-ABC' not in redacted_text
        assert 'CUSTOM_ID_12345' not in redacted_text
    
    def test_preserve_structure_option(self):
        """Test structure preservation during redaction"""
        document_text = """
        Email: test.user@domain.com
        Phone: 555-123-4567
        Date: 01/15/2024
        """
        
        input_data = {
            'text': document_text,
            'redaction_level': 'standard',
            'preserve_structure': True,
            'replacement_char': 'X'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        redacted_text = result['redacted_text']
        
        # Structure should be preserved (same length, some chars preserved)
        assert '@' in redacted_text  # Email structure preserved
        assert '-' in redacted_text  # Phone structure preserved
        assert '/' in redacted_text  # Date structure preserved
    
    def test_allow_list_functionality(self):
        """Test allow list to prevent certain terms from being redacted"""
        document_text = """
        Patient: John Smith at Duke University
        Another person: Jane Doe
        Institution: Duke University Medical Center
        """
        
        input_data = {
            'text': document_text,
            'redaction_level': 'maximum',
            'allow_list': ['Duke University']  # Protect this term
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        redacted_text = result['redacted_text']
        
        # Allow list items should not be redacted
        assert 'Duke University' in redacted_text
        # But other names should still be redacted
        assert 'John Smith' not in redacted_text or 'XXXX' in redacted_text
    
    def test_phi_categories_specific_redaction(self):
        """Test redaction of specific PHI categories"""
        document_text = """
        Patient: John Smith
        DOB: 01/15/1975
        Address: 123 Main St
        Phone: 555-123-4567
        MRN: MR123456
        Treatment cost: $2,500
        """
        
        input_data = {
            'text': document_text,
            'redaction_level': 'standard',
            'phi_categories': ['names', 'contact', 'medical_ids']  # Exclude dates and financial
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        redacted_text = result['redacted_text']
        
        # Selected categories should be redacted
        assert 'John Smith' not in redacted_text or 'XXXX' in redacted_text
        assert '555-123-4567' not in redacted_text or 'XXX' in redacted_text
        assert 'MR123456' not in redacted_text or 'XXXXXXX' in redacted_text
        
        # Non-selected categories should remain
        assert '01/15/1975' in redacted_text  # Date not in selected categories
        assert '$2,500' in redacted_text      # Financial not in selected categories
    
    def test_annotations_output_format(self):
        """Test annotations output format"""
        document_text = "Patient John Smith, MRN: MR123456"
        
        input_data = {
            'text': document_text,
            'redaction_level': 'standard',
            'output_format': 'annotations'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'annotations' in result
        assert 'redacted_text' not in result  # Only annotations requested
        
        annotations = result['annotations']
        assert len(annotations) > 0
        
        # Check annotation structure
        annotation = annotations[0]
        assert 'id' in annotation
        assert 'category' in annotation
        assert 'start_position' in annotation
        assert 'end_position' in annotation
        assert 'risk_level' in annotation
    
    def test_both_output_format(self):
        """Test both redacted text and annotations output"""
        document_text = "Dr. Smith, phone 555-1234"
        
        input_data = {
            'text': document_text,
            'redaction_level': 'standard',
            'output_format': 'both'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        assert 'redacted_text' in result
        assert 'annotations' in result
        
        # Both should be present and meaningful
        assert len(result['redacted_text']) > 0
        assert len(result['annotations']) > 0
    
    def test_comprehensive_statistics(self):
        """Test comprehensive redaction statistics"""
        document_text = """
        HIGH RISK: John Smith, SSN: 123-45-6789, DOB: 01/15/1975
        MEDIUM RISK: Phone (555) 123-4567, Address: 123 Main St
        LOW RISK: ZIP 12345
        """
        
        input_data = {
            'text': document_text,
            'redaction_level': 'standard'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        
        statistics = result['statistics']
        
        # Check comprehensive statistics
        assert 'original_length' in statistics
        assert 'redacted_length' in statistics
        assert 'characters_redacted' in statistics
        assert 'redaction_percentage' in statistics
        assert 'total_redactions' in statistics
        assert 'redactions_by_category' in statistics
        assert 'redactions_by_risk_level' in statistics
        
        # Verify data makes sense
        assert statistics['original_length'] > 0
        assert statistics['redacted_length'] > 0
        assert statistics['redaction_percentage'] >= 0
        assert statistics['redaction_percentage'] <= 100
    
    def test_redaction_summary_analysis(self):
        """Test redaction summary with risk analysis"""
        document_text = """
        URGENT: Patient John Smith requires immediate attention.
        Critical SSN: 123-45-6789
        Important MRN: MR987654
        Regular phone: 555-0000
        """
        
        input_data = {
            'text': document_text,
            'redaction_level': 'standard'
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        
        summary = result['redaction_summary']
        
        # Check summary structure
        assert 'total_redactions' in summary
        assert 'categories_redacted' in summary
        assert 'redaction_density' in summary
        assert 'high_risk_items' in summary
        
        # Should identify high risk items
        assert len(summary['high_risk_items']) > 0
        
        # Categories should be meaningful
        assert len(summary['categories_redacted']) > 0
    
    def test_compliance_notes_by_categories(self):
        """Test compliance notes for different PHI categories"""
        document_text = "Financial data: $50,000 payment, Account: 123456789"
        
        input_data = {
            'text': document_text,
            'redaction_level': 'standard',
            'phi_categories': ['financial']
        }
        
        result = run(input_data)
        
        assert result['success'] is True
        
        compliance_notes = result['compliance_notes']
        assert len(compliance_notes) > 0
        
        # Should include financial-specific compliance notes
        financial_note_found = any('financial' in note.lower() for note in compliance_notes)
        assert financial_note_found
    
    def test_error_handling_no_text(self):
        """Test error handling when no text provided"""
        input_data = {
            'redaction_level': 'standard'
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'text is required' in result['error']
    
    def test_empty_text_handling(self):
        """Test handling of empty text"""
        input_data = {
            'text': '',
            'redaction_level': 'standard'
        }
        
        result = run(input_data)
        
        assert result['success'] is False
        assert 'text is required' in result['error']