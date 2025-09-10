from typing import Dict, Any, List
from datetime import datetime


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates FDA submission packages for completeness and regulatory compliance across multiple submission types.
    
    Example:
        Input: Submission type, document list, and phase information for FDA validation
        Output: Compliance assessment with missing documents list and submission recommendations
    
    Parameters:
        submission_type : str
            FDA submission type ('IND', 'NDA', 'BLA', 'ANDA', '510k', 'IDE')
        documents : list
            List of document names or paths in the submission package
        phase : str
            Clinical phase for IND submissions (optional)
        fast_track : bool
            Whether this is a fast track designation (optional)
        validate_format : bool
            Check eCTD format compliance (optional)
    """
    submission_type = input_data.get('submission_type', '').upper()
    documents = input_data.get('documents', [])
    phase = input_data.get('phase', '')
    fast_track = input_data.get('fast_track', False)
    validate_format = input_data.get('validate_format', False)
    
    # Normalize document names for comparison
    doc_names_lower = [doc.lower() for doc in documents]
    
    # Define requirements by submission type
    requirements = _get_submission_requirements(submission_type, phase, fast_track)
    
    if not requirements:
        return {
            'error': f'Unknown submission type: {submission_type}',
            'is_complete': False,
            'missing_required': [],
            'missing_recommended': [],
            'compliance_score': 0.0,
            'issues': ['Invalid submission type specified']
        }
    
    # Check for required documents
    missing_required = []
    for req_doc in requirements['required']:
        if not _document_exists(req_doc, doc_names_lower):
            missing_required.append(req_doc)
    
    # Check for recommended documents
    missing_recommended = []
    for rec_doc in requirements.get('recommended', []):
        if not _document_exists(rec_doc, doc_names_lower):
            missing_recommended.append(rec_doc)
    
    # Check for compliance issues
    issues = []
    
    # Check eCTD format if requested
    if validate_format:
        format_issues = _check_ectd_format(documents)
        issues.extend(format_issues)
    
    # Check for common issues
    common_issues = _check_common_issues(documents, submission_type)
    issues.extend(common_issues)
    
    # Calculate compliance score
    total_required = len(requirements['required'])
    found_required = total_required - len(missing_required)
    compliance_score = (found_required / total_required * 100) if total_required > 0 else 0
    
    # Generate recommendations
    recommendations = _generate_recommendations(
        submission_type, missing_required, missing_recommended, issues, compliance_score
    )
    
    return {
        'submission_type': submission_type,
        'is_complete': len(missing_required) == 0,
        'missing_required': missing_required,
        'missing_recommended': missing_recommended,
        'compliance_score': round(compliance_score, 1),
        'issues': issues,
        'recommendations': recommendations,
        'statistics': {
            'total_documents': len(documents),
            'required_documents': len(requirements['required']),
            'required_found': found_required,
            'recommended_documents': len(requirements.get('recommended', [])),
            'recommended_found': len(requirements.get('recommended', [])) - len(missing_recommended)
        }
    }


def _get_submission_requirements(submission_type: str, phase: str, fast_track: bool) -> Dict:
    """Get document requirements for submission type."""
    requirements = {
        'IND': {
            'required': [
                'form_fda_1571',
                'table_of_contents',
                'introductory_statement',
                'general_investigational_plan',
                'investigators_brochure',
                'protocol',
                'chemistry_manufacturing_controls',
                'pharmacology_toxicology',
                'previous_human_experience',
                'clinical_protocol',
                'investigator_information'
            ],
            'recommended': [
                'cover_letter',
                'environmental_assessment',
                'pharmacokinetic_data',
                'references'
            ]
        },
        'NDA': {
            'required': [
                'form_fda_356h',
                'index',
                'summary',
                'chemistry_section',
                'nonclinical_pharmacology_toxicology',
                'human_pharmacokinetics_bioavailability',
                'microbiology',
                'clinical_data',
                'safety_update',
                'statistical_section',
                'case_report_forms',
                'patent_information'
            ],
            'recommended': [
                'annotated_labeling',
                'risk_evaluation_mitigation_strategy',
                'financial_disclosure',
                'field_copy_certification'
            ]
        },
        'BLA': {
            'required': [
                'form_fda_356h',
                'summary',
                'chemistry_manufacturing_controls',
                'nonclinical_studies',
                'clinical_studies',
                'labeling',
                'establishment_description',
                'environmental_assessment'
            ],
            'recommended': [
                'pediatric_assessment',
                'patent_certification',
                'user_fee_cover_sheet'
            ]
        },
        'ANDA': {
            'required': [
                'form_fda_356h',
                'basis_for_submission',
                'drug_substance',
                'drug_product',
                'methods_validation',
                'bioequivalence_data',
                'labeling',
                'financial_certification'
            ],
            'recommended': [
                'environmental_assessment',
                'request_for_waiver'
            ]
        },
        '510K': {
            'required': [
                'cover_letter',
                'table_of_contents',
                'form_fda_3514',
                'truthful_accuracy_statement',
                'device_description',
                'substantial_equivalence_comparison',
                'performance_data'
            ],
            'recommended': [
                'clinical_data',
                'software_validation'
            ]
        },
        'IDE': {
            'required': [
                'cover_letter',
                'table_of_contents',
                'report_prior_investigations',
                'investigational_plan',
                'device_description',
                'monitoring_procedures',
                'labeling',
                'informed_consent_forms'
            ],
            'recommended': [
                'environmental_assessment',
                'manufacturing_information'
            ]
        }
    }
    
    base_req = requirements.get(submission_type, {})
    
    # Add phase-specific requirements for IND
    if submission_type == 'IND' and phase:
        if phase.lower() in ['2', 'ii', 'phase 2', 'phase ii']:
            base_req['required'].append('phase_1_summary')
        elif phase.lower() in ['3', 'iii', 'phase 3', 'phase iii']:
            base_req['required'].extend(['phase_1_summary', 'phase_2_summary'])
    
    # Add fast track specific requirements
    if fast_track:
        base_req['required'].append('fast_track_designation_request')
    
    return base_req


def _document_exists(required_doc: str, doc_list: List[str]) -> bool:
    """Check if a required document exists in the document list."""
    # Convert requirement to searchable terms
    search_terms = required_doc.replace('_', ' ').lower()
    
    # Check for exact or partial matches
    for doc in doc_list:
        if search_terms in doc or required_doc in doc:
            return True
        # Check for common variations
        if required_doc == 'form_fda_1571' and ('1571' in doc or 'fda 1571' in doc):
            return True
        if required_doc == 'form_fda_356h' and ('356h' in doc or 'fda 356h' in doc):
            return True
        if required_doc == 'investigators_brochure' and ('ib' in doc or 'investigator brochure' in doc):
            return True
    
    return False


def _check_ectd_format(documents: List[str]) -> List[str]:
    """Check for eCTD format compliance issues."""
    issues = []
    
    # Check for required eCTD structure
    required_modules = ['m1', 'm2', 'm3', 'm4', 'm5']
    found_modules = set()
    
    for doc in documents:
        doc_lower = doc.lower()
        for module in required_modules:
            if module in doc_lower:
                found_modules.add(module)
    
    missing_modules = set(required_modules) - found_modules
    if missing_modules:
        issues.append(f"Missing eCTD modules: {', '.join(sorted(missing_modules))}")
    
    # Check for XML backbone
    has_xml = any('xml' in doc.lower() for doc in documents)
    if not has_xml:
        issues.append("Missing eCTD XML backbone files")
    
    # Check for valid file naming
    invalid_chars = ['#', '&', '@', '$', '%', '^', '*']
    for doc in documents:
        if any(char in doc for char in invalid_chars):
            issues.append(f"Invalid characters in filename: {doc}")
    
    return issues


def _check_common_issues(documents: List[str], submission_type: str) -> List[str]:
    """Check for common submission issues."""
    issues = []
    
    # Check for unsigned forms
    unsigned_indicators = ['unsigned', 'draft', 'template']
    for doc in documents:
        doc_lower = doc.lower()
        if any(indicator in doc_lower for indicator in unsigned_indicators):
            issues.append(f"Potentially unsigned or draft document: {doc}")
    
    # Check for outdated forms
    if submission_type in ['IND', 'NDA', 'BLA']:
        form_dates = ['2018', '2019', '2020', '2021']
        for doc in documents:
            for date in form_dates:
                if date in doc:
                    issues.append(f"Potentially outdated form (contains {date}): {doc}")
    
    # Check for missing page numbers in key documents
    if not any('toc' in doc.lower() or 'table_of_contents' in doc.lower() for doc in documents):
        issues.append("No clear table of contents found")
    
    # Check for duplicate documents
    seen = set()
    for doc in documents:
        doc_clean = doc.lower().replace(' ', '').replace('_', '').replace('-', '')
        if doc_clean in seen:
            issues.append(f"Potential duplicate document: {doc}")
        seen.add(doc_clean)
    
    return issues


def _generate_recommendations(submission_type: str, missing_required: List[str],
                            missing_recommended: List[str], issues: List[str],
                            compliance_score: float) -> List[str]:
    """Generate recommendations for improving the submission."""
    recommendations = []
    
    if compliance_score < 100:
        recommendations.append(f"Current compliance score: {compliance_score}% - requires attention")
    
    if missing_required:
        recommendations.append(f"Priority: Add {len(missing_required)} missing required documents")
        # Prioritize most critical missing documents
        critical = ['protocol', 'informed_consent', 'investigators_brochure', 'safety']
        critical_missing = [doc for doc in missing_required if any(c in doc for c in critical)]
        if critical_missing:
            recommendations.append(f"Critical documents missing: {', '.join(critical_missing[:3])}")
    
    if missing_recommended and compliance_score >= 90:
        recommendations.append("Consider adding recommended documents to strengthen submission")
    
    if 'unsigned' in str(issues).lower():
        recommendations.append("Ensure all forms are properly signed before submission")
    
    if 'outdated' in str(issues).lower():
        recommendations.append("Update forms to current FDA versions")
    
    if submission_type == 'IND':
        recommendations.append("Ensure 30-day safety review period before starting trial")
    elif submission_type == 'NDA':
        recommendations.append("Consider requesting pre-NDA meeting with FDA")
    elif submission_type == 'BLA':
        recommendations.append("Verify all manufacturing site information is current")
    
    if not issues and not missing_required:
        recommendations.append("✓ Submission package appears complete and compliant")
    
    return recommendations