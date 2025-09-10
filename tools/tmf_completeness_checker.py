from typing import Dict, Any, List
from datetime import datetime


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check Trial Master File (TMF) completeness against regulatory requirements and inspection readiness.
    
    Example:
        Input: TMF document list with study phase, status, and site information
        Output: Completeness assessment with missing documents, inspection readiness, and compliance score
    
    Parameters:
        documents : list
            List of documents currently in the TMF
        study_phase : str
            Clinical trial phase: '1', '2', '3', or '4'
        study_status : str
            Current study status: 'planning', 'active', 'closed'
        sites : int
            Number of investigational sites in the study
    """
    documents = input_data.get('documents', [])
    study_phase = input_data.get('study_phase', '3')
    study_status = input_data.get('study_status', 'active')
    num_sites = input_data.get('sites', 1)
    
    # Get required documents based on study characteristics
    essential_docs = _get_essential_documents(study_phase, study_status)
    recommended_docs = _get_recommended_documents()
    
    # Normalize document names
    doc_names_lower = [doc.lower() for doc in documents]
    
    # Check completeness
    missing_essential = []
    for doc in essential_docs:
        if not _document_exists(doc, doc_names_lower):
            missing_essential.append(doc)
    
    missing_recommended = []
    for doc in recommended_docs:
        if not _document_exists(doc, doc_names_lower):
            missing_recommended.append(doc)
    
    # Calculate scores by section
    section_scores = _calculate_section_scores(documents, essential_docs)
    
    # Overall completeness
    found_essential = len(essential_docs) - len(missing_essential)
    completeness_score = (found_essential / len(essential_docs) * 100) if essential_docs else 0
    
    # Determine inspection readiness
    inspection_readiness = _determine_inspection_readiness(completeness_score, missing_essential)
    
    # Generate recommendations
    recommendations = _generate_recommendations(missing_essential, missing_recommended, 
                                              section_scores, inspection_readiness)
    
    return {
        'completeness_score': round(completeness_score, 1),
        'missing_essential': missing_essential,
        'missing_recommended': missing_recommended,
        'by_section': section_scores,
        'inspection_readiness': inspection_readiness,
        'recommendations': recommendations,
        'statistics': {
            'total_documents': len(documents),
            'essential_required': len(essential_docs),
            'essential_found': found_essential,
            'recommended_required': len(recommended_docs),
            'sites': num_sites
        }
    }


def _get_essential_documents(phase: str, status: str) -> List[str]:
    """Get list of essential TMF documents based on ICH-GCP E6."""
    essential = [
        # Trial Management
        'protocol_final',
        'protocol_amendments',
        'crf_blank',
        'investigator_brochure',
        'financial_agreements',
        'insurance_certificate',
        
        # Regulatory
        'regulatory_submission',
        'regulatory_approval',
        'irb_iec_composition',
        'irb_iec_approval',
        'informed_consent_form',
        'advertising_materials',
        
        # Site
        'investigator_cv',
        'normal_ranges',
        'source_document_agreement',
        'monitoring_plan',
        'monitoring_reports',
        
        # Product
        'certificate_of_analysis',
        'shipping_records',
        'accountability_log',
        'randomization_list',
        'code_break_procedures',
        
        # Safety
        'safety_reports',
        'annual_reports',
        'dsmb_charter'
    ]
    
    if status == 'closed':
        essential.extend([
            'close_out_monitoring_report',
            'treatment_allocation',
            'audit_certificate',
            'final_report',
            'clinical_study_report'
        ])
    
    return essential


def _get_recommended_documents() -> List[str]:
    """Get list of recommended TMF documents."""
    return [
        'study_team_list',
        'delegation_log',
        'signature_log',
        'training_records',
        'meeting_minutes',
        'correspondence',
        'protocol_deviations_log',
        'sae_reconciliation',
        'query_log',
        'tmf_plan'
    ]


def _document_exists(required: str, doc_list: List[str]) -> bool:
    """Check if document exists in list."""
    search_terms = required.replace('_', ' ')
    
    for doc in doc_list:
        if search_terms in doc or required in doc:
            return True
    
    return False


def _calculate_section_scores(documents: List[str], essential_docs: List[str]) -> Dict:
    """Calculate completeness scores by TMF section."""
    sections = {
        'trial_management': ['protocol', 'crf', 'statistical'],
        'regulatory': ['regulatory', 'irb', 'iec', 'consent', 'ethics'],
        'site_management': ['investigator', 'site', 'delegation', 'training'],
        'product_accountability': ['drug', 'accountability', 'randomization', 'shipping'],
        'safety': ['safety', 'sae', 'adverse', 'dsmb'],
        'data_management': ['data', 'query', 'database', 'validation'],
        'monitoring': ['monitoring', 'visit', 'close-out']
    }
    
    section_scores = {}
    doc_lower = [d.lower() for d in documents]
    
    for section, keywords in sections.items():
        section_docs = sum(1 for doc in doc_lower if any(kw in doc for kw in keywords))
        expected = sum(1 for ed in essential_docs if any(kw in ed for kw in keywords))
        
        if expected > 0:
            score = min(100, (section_docs / expected) * 100)
        else:
            score = 100 if section_docs > 0 else 0
        
        section_scores[section] = round(score, 1)
    
    return section_scores


def _determine_inspection_readiness(score: float, missing_essential: List) -> str:
    """Determine TMF inspection readiness."""
    critical_docs = ['protocol', 'consent', 'irb', 'regulatory_approval', 'safety']
    
    critical_missing = any(
        any(critical in doc for critical in critical_docs)
        for doc in missing_essential
    )
    
    if score >= 95 and not critical_missing:
        return 'ready'
    elif score >= 80 and not critical_missing:
        return 'needs_work'
    else:
        return 'not_ready'


def _generate_recommendations(missing_essential: List, missing_recommended: List,
                             section_scores: Dict, readiness: str) -> List[str]:
    """Generate TMF improvement recommendations."""
    recommendations = []
    
    if readiness == 'not_ready':
        recommendations.append("URGENT: TMF not inspection ready - immediate action required")
    elif readiness == 'needs_work':
        recommendations.append("TMF requires attention before inspection")
    
    # Prioritize critical missing documents
    if missing_essential:
        recommendations.append(f"Priority: Obtain {len(missing_essential)} missing essential documents")
        
        critical = ['protocol', 'consent', 'regulatory']
        for doc in missing_essential[:5]:  # Top 5 missing
            if any(c in doc for c in critical):
                recommendations.append(f"CRITICAL: Missing {doc}")
    
    # Section-specific recommendations
    low_sections = [s for s, score in section_scores.items() if score < 80]
    if low_sections:
        recommendations.append(f"Focus on sections: {', '.join(low_sections)}")
    
    # General recommendations
    if len(missing_recommended) > 5:
        recommendations.append("Consider adding recommended documents for completeness")
    
    recommendations.append("Implement TMF review schedule (monthly recommended)")
    recommendations.append("Ensure all documents are current versions")
    
    return recommendations
