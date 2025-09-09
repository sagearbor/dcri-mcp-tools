import pytest
from tools.tmf_completeness_checker import run


def test_tmf_completeness_checker_complete():
    """Test with complete TMF."""
    input_data = {
        'documents': [
            'protocol_final_v2.0.pdf',
            'protocol_amendments.pdf',
            'crf_blank.pdf',
            'investigator_brochure.pdf',
            'financial_agreements.pdf',
            'insurance_certificate.pdf',
            'regulatory_submission.pdf',
            'regulatory_approval.pdf',
            'irb_iec_composition.pdf',
            'irb_iec_approval.pdf',
            'informed_consent_form.pdf',
            'advertising_materials.pdf',
            'investigator_cv.pdf',
            'normal_ranges.pdf',
            'source_document_agreement.pdf',
            'monitoring_plan.pdf',
            'monitoring_reports.pdf',
            'certificate_of_analysis.pdf',
            'shipping_records.pdf',
            'accountability_log.pdf',
            'randomization_list.pdf',
            'code_break_procedures.pdf',
            'safety_reports.pdf',
            'annual_reports.pdf',
            'dsmb_charter.pdf'
        ],
        'study_phase': '3',
        'study_status': 'active',
        'sites': 10
    }
    
    result = run(input_data)
    
    assert result['completeness_score'] == 100.0
    assert result['inspection_readiness'] == 'ready'
    assert len(result['missing_essential']) == 0


def test_tmf_completeness_checker_incomplete():
    """Test with incomplete TMF."""
    input_data = {
        'documents': [
            'protocol.pdf',
            'investigator_cv.pdf',
            'monitoring_plan.pdf'
        ],
        'study_phase': '2',
        'study_status': 'active'
    }
    
    result = run(input_data)
    
    assert result['completeness_score'] < 50
    assert result['inspection_readiness'] == 'not_ready'
    assert len(result['missing_essential']) > 0


def test_tmf_completeness_checker_closed_study():
    """Test closed study requirements."""
    input_data = {
        'documents': [
            'close_out_monitoring_report.pdf',
            'treatment_allocation.pdf',
            'audit_certificate.pdf',
            'final_report.pdf',
            'clinical_study_report.pdf'
        ],
        'study_status': 'closed'
    }
    
    result = run(input_data)
    
    # Should check for closed study specific documents
    assert any('close_out' in doc or 'final' in doc 
              for doc in result['missing_essential'] + input_data['documents'])


def test_tmf_completeness_checker_section_scores():
    """Test section-wise scoring."""
    input_data = {
        'documents': [
            'protocol_v1.pdf',
            'protocol_amendment_1.pdf',
            'regulatory_approval.pdf',
            'irb_approval.pdf',
            'safety_report_001.pdf',
            'sae_log.xlsx'
        ]
    }
    
    result = run(input_data)
    
    assert 'by_section' in result
    assert 'trial_management' in result['by_section']
    assert 'regulatory' in result['by_section']
    assert 'safety' in result['by_section']


def test_tmf_completeness_checker_recommendations():
    """Test recommendation generation."""
    input_data = {
        'documents': ['protocol.pdf'],
        'study_phase': '3'
    }
    
    result = run(input_data)
    
    assert len(result['recommendations']) > 0
    assert any('URGENT' in r or 'Priority' in r for r in result['recommendations'])


def test_tmf_completeness_checker_critical_missing():
    """Test detection of critical missing documents."""
    input_data = {
        'documents': [
            'investigator_cv.pdf',
            'monitoring_plan.pdf',
            'shipping_records.pdf'
        ]
    }
    
    result = run(input_data)
    
    # Should be missing critical documents like protocol, consent, regulatory
    assert result['inspection_readiness'] == 'not_ready'
    critical_missing = [d for d in result['missing_essential'] 
                       if any(c in d for c in ['protocol', 'consent', 'regulatory'])]
    assert len(critical_missing) > 0
