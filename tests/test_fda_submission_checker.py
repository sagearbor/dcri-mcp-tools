import pytest
from tools.fda_submission_checker import run


def test_fda_submission_checker_ind_complete():
    """Test checking a complete IND submission."""
    input_data = {
        'submission_type': 'IND',
        'documents': [
            'Form_FDA_1571.pdf',
            'Table_of_Contents.pdf',
            'Introductory_Statement.pdf',
            'General_Investigational_Plan.pdf',
            'Investigators_Brochure.pdf',
            'Protocol_v1.0.pdf',
            'Chemistry_Manufacturing_Controls.pdf',
            'Pharmacology_Toxicology_Summary.pdf',
            'Previous_Human_Experience.pdf',
            'Clinical_Protocol.pdf',
            'Investigator_Information.pdf'
        ],
        'phase': '1'
    }
    
    result = run(input_data)
    
    assert result['is_complete'] is True
    assert result['compliance_score'] == 100.0
    assert len(result['missing_required']) == 0


def test_fda_submission_checker_ind_incomplete():
    """Test checking an incomplete IND submission."""
    input_data = {
        'submission_type': 'IND',
        'documents': [
            'Form_FDA_1571.pdf',
            'Protocol_v1.0.pdf',
            'Investigators_Brochure.pdf'
        ],
        'phase': '1'
    }
    
    result = run(input_data)
    
    assert result['is_complete'] is False
    assert result['compliance_score'] < 100
    assert len(result['missing_required']) > 0
    assert 'table_of_contents' in result['missing_required']


def test_fda_submission_checker_nda():
    """Test checking NDA submission."""
    input_data = {
        'submission_type': 'NDA',
        'documents': [
            'Form_FDA_356h.pdf',
            'Index.pdf',
            'Summary.pdf',
            'Chemistry_Section.pdf',
            'Nonclinical_Pharmacology_Toxicology.pdf',
            'Human_Pharmacokinetics_Bioavailability.pdf',
            'Microbiology.pdf',
            'Clinical_Data.pdf',
            'Safety_Update.pdf',
            'Statistical_Section.pdf',
            'Case_Report_Forms.pdf',
            'Patent_Information.pdf'
        ]
    }
    
    result = run(input_data)
    
    assert result['is_complete'] is True
    assert result['submission_type'] == 'NDA'


def test_fda_submission_checker_510k():
    """Test checking 510(k) submission."""
    input_data = {
        'submission_type': '510k',
        'documents': [
            'Cover_Letter.pdf',
            'Table_of_Contents.pdf',
            'Form_FDA_3514.pdf',
            'Truthful_Accuracy_Statement.pdf',
            'Device_Description.pdf',
            'Substantial_Equivalence_Comparison.pdf',
            'Performance_Data.pdf'
        ]
    }
    
    result = run(input_data)
    
    assert result['is_complete'] is True
    assert result['submission_type'] == '510K'


def test_fda_submission_checker_fast_track():
    """Test fast track submission requirements."""
    input_data = {
        'submission_type': 'IND',
        'documents': [
            'Form_FDA_1571.pdf',
            'Fast_Track_Designation_Request.pdf'
        ],
        'fast_track': True
    }
    
    result = run(input_data)
    
    # Should require fast track designation request
    assert 'fast_track_designation_request' not in result['missing_required']


def test_fda_submission_checker_ectd_format():
    """Test eCTD format validation."""
    input_data = {
        'submission_type': 'NDA',
        'documents': [
            'm1/cover.pdf',
            'm2/summary.pdf',
            'm3/chemistry.pdf',
            'm4/nonclinical.pdf',
            'm5/clinical.pdf',
            'backbone.xml'
        ],
        'validate_format': True
    }
    
    result = run(input_data)
    
    # Should not have eCTD format issues
    ectd_issues = [i for i in result['issues'] if 'eCTD' in i or 'module' in i]
    assert len(ectd_issues) == 0


def test_fda_submission_checker_invalid_submission_type():
    """Test with invalid submission type."""
    input_data = {
        'submission_type': 'INVALID',
        'documents': ['test.pdf']
    }
    
    result = run(input_data)
    
    assert result['error'] == 'Unknown submission type: INVALID'
    assert result['is_complete'] is False


def test_fda_submission_checker_common_issues():
    """Test detection of common issues."""
    input_data = {
        'submission_type': 'IND',
        'documents': [
            'Form_FDA_1571_unsigned.pdf',
            'Protocol_DRAFT.pdf',
            'IB_2019.pdf'
        ]
    }
    
    result = run(input_data)
    
    assert len(result['issues']) > 0
    assert any('unsigned' in issue.lower() for issue in result['issues'])
    assert any('draft' in issue.lower() for issue in result['issues'])


def test_fda_submission_checker_recommendations():
    """Test recommendation generation."""
    input_data = {
        'submission_type': 'IND',
        'documents': [
            'Protocol.pdf'
        ]
    }
    
    result = run(input_data)
    
    assert len(result['recommendations']) > 0
    assert any('missing required' in rec.lower() for rec in result['recommendations'])


def test_fda_submission_checker_phase_specific():
    """Test phase-specific requirements for IND."""
    input_data = {
        'submission_type': 'IND',
        'documents': [
            'Form_FDA_1571.pdf',
            'Table_of_Contents.pdf',
            'Introductory_Statement.pdf',
            'General_Investigational_Plan.pdf',
            'Investigators_Brochure.pdf',
            'Protocol_v1.0.pdf',
            'Chemistry_Manufacturing_Controls.pdf',
            'Pharmacology_Toxicology_Summary.pdf',
            'Previous_Human_Experience.pdf',
            'Clinical_Protocol.pdf',
            'Investigator_Information.pdf',
            'Phase_1_Summary.pdf'
        ],
        'phase': '2'
    }
    
    result = run(input_data)
    
    # Phase 2 should require Phase 1 summary
    assert 'phase_1_summary' not in result['missing_required']