"""
Glossary Explainer Tool
AI-powered term explanation system for clinical trial glossaries
"""

from typing import Dict, List, Any
import re
from datetime import datetime

def run(input_data: Dict) -> Dict:
    """
    Explain clinical trial terms using SharePoint glossary data
    
    Args:
        input_data: Dictionary containing:
            - term: The term to explain
            - context: Optional context where the term was encountered
            - glossary_data: Dict of terms and definitions from SharePoint
            - include_related: Include related terms in response
            - complexity_level: Target explanation complexity (basic, intermediate, advanced)
    
    Returns:
        Dictionary with term explanation, related terms, and usage examples
    """
    try:
        term = input_data.get('term', '').strip()
        context = input_data.get('context', '').strip()
        glossary_data = input_data.get('glossary_data', {})
        include_related = input_data.get('include_related', True)
        complexity_level = input_data.get('complexity_level', 'intermediate')
        
        if not term:
            return {
                'success': False,
                'error': 'No term provided for explanation'
            }
        
        # Normalize term for searching
        term_normalized = normalize_term(term)
        
        # Search for exact match first
        explanation = find_exact_match(term_normalized, glossary_data)
        match_type = 'exact'
        
        # If no exact match, try fuzzy matching
        if not explanation:
            explanation, match_confidence = find_fuzzy_match(term_normalized, glossary_data)
            if explanation and match_confidence >= 0.6:
                match_type = 'fuzzy'
            else:
                explanation = None
                match_type = 'none'
        
        # If still no match, generate explanation based on term pattern
        if not explanation:
            explanation = generate_pattern_based_explanation(term_normalized)
            match_type = 'generated'
        
        # Enhance explanation based on context
        if context and explanation:
            explanation = enhance_with_context(explanation, context, complexity_level)
        
        # Find related terms
        related_terms = []
        if include_related and glossary_data:
            related_terms = find_related_terms(term_normalized, glossary_data, explanation)
        
        # Generate usage examples
        usage_examples = generate_usage_examples(term_normalized, explanation, context)
        
        # Create response based on match type
        if match_type == 'none':
            return {
                'success': True,
                'term': term,
                'explanation': f"I don't have a specific definition for '{term}' in the glossary.",
                'match_type': match_type,
                'confidence_score': 0.0,
                'suggested_terms': suggest_similar_terms(term_normalized, glossary_data),
                'general_guidance': get_general_guidance(term_normalized),
                'search_tips': [
                    "Try searching for abbreviations or full forms of the term",
                    "Check if the term might be part of a longer phrase",
                    "Consider looking for related clinical trial concepts"
                ]
            }
        
        # Calculate confidence score, preserving fuzzy match confidence
        if match_type == 'fuzzy' and 'match_confidence' in locals():
            confidence_score = match_confidence
        else:
            confidence_score = calculate_confidence_score(match_type, explanation, term_normalized)
        
        return {
            'success': True,
            'term': term,
            'explanation': explanation,
            'match_type': match_type,
            'confidence_score': confidence_score,
            'complexity_level': complexity_level,
            'related_terms': related_terms[:5],  # Top 5 related terms
            'usage_examples': usage_examples,
            'context_analysis': analyze_context(context) if context else None,
            'additional_resources': get_additional_resources(term_normalized),
            'explanation_metadata': {
                'generated_at': datetime.now().isoformat(),
                'glossary_entries_searched': len(glossary_data),
                'term_category': categorize_term(term_normalized),
                'regulatory_relevance': assess_regulatory_relevance(term_normalized)
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error explaining term: {str(e)}'
        }

def normalize_term(term: str) -> str:
    """Normalize term for better matching."""
    # Convert to lowercase and remove extra spaces
    normalized = re.sub(r'\s+', ' ', term.lower().strip())
    
    # Remove common punctuation
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    
    # Handle abbreviations - remove periods
    normalized = normalized.replace('.', '')
    
    return normalized

def find_exact_match(term: str, glossary_data: Dict) -> str:
    """Find exact match in glossary data."""
    # Try direct lookup
    if term in glossary_data:
        return glossary_data[term]
    
    # Try variations (with/without spaces, hyphens)
    variations = [
        term.replace(' ', ''),
        term.replace(' ', '-'),
        term.replace('-', ' '),
        term.replace('-', ''),
        term.upper(),
        term.title()
    ]
    
    for variation in variations:
        if variation in glossary_data:
            return glossary_data[variation]
        # Also check if variation matches any key
        for key, definition in glossary_data.items():
            if key.lower() == variation.lower():
                return definition
    
    return None

def find_fuzzy_match(term: str, glossary_data: Dict) -> tuple:
    """Find fuzzy matches using similarity scoring."""
    best_match = None
    best_score = 0.0
    
    # Check for abbreviations first (common in clinical trials)
    if len(term) <= 4:
        for key, definition in glossary_data.items():
            # Create abbreviation from key words
            words = key.lower().split()
            abbrev = ''.join(word[0] for word in words if word)
            if abbrev == term.lower():
                return definition, 0.9  # High confidence for abbreviation match
            
            # Check for common clinical abbreviations
            if term.lower() == 'ae' and 'adverse event' in key.lower():
                return definition, 0.85
            if term.lower() == 'sae' and 'serious adverse event' in key.lower():
                return definition, 0.85
    
    for key, definition in glossary_data.items():
        score = calculate_similarity(term, key.lower())
        if score > best_score and score > 0.7:  # Higher minimum threshold
            best_score = score
            best_match = definition
    
    # Also check for partial matches
    for key, definition in glossary_data.items():
        if term in key.lower() or key.lower() in term:
            partial_score = min(len(term), len(key)) / max(len(term), len(key))
            if partial_score > best_score and partial_score > 0.6:  # Higher threshold
                best_score = partial_score
                best_match = definition
    
    return best_match, best_score

def calculate_similarity(term1: str, term2: str) -> float:
    """Calculate similarity between two terms using Levenshtein-like approach."""
    if term1 == term2:
        return 1.0
    
    # Simple similarity based on common characters and length
    common_chars = len(set(term1) & set(term2))
    total_chars = len(set(term1) | set(term2))
    
    if total_chars == 0:
        return 0.0
    
    char_similarity = common_chars / total_chars
    
    # Length similarity
    length_similarity = min(len(term1), len(term2)) / max(len(term1), len(term2))
    
    # Combined score
    return (char_similarity * 0.7 + length_similarity * 0.3)

def generate_pattern_based_explanation(term: str) -> str:
    """Generate explanation based on term patterns."""
    term_lower = term.lower()
    
    # Common clinical trial abbreviations and patterns
    patterns = {
        r'\bae\b|\badverse event\b': "An Adverse Event (AE) is any untoward medical occurrence in a patient or clinical investigation subject administered a pharmaceutical product.",
        r'\bsae\b|\bserious adverse event\b': "A Serious Adverse Event (SAE) is an adverse event that results in death, is life-threatening, requires hospitalization, or results in significant disability.",
        r'\bicf\b|\binformed consent\b': "Informed Consent Form (ICF) is a document that explains the details of a study and confirms that a participant agrees to take part in the research.",
        r'\bcrfb\b|\bcase report form\b': "Case Report Form (CRF) is a printed, optical, or electronic document designed to record all protocol-required information.",
        r'\bpi\b|\bprincipal investigator\b': "Principal Investigator (PI) is the person responsible for the conduct of the clinical trial at a study site.",
        r'\birb\b|\binstitutional review board\b': "Institutional Review Board (IRB) is an independent ethics committee that reviews and approves clinical research protocols.",
        r'\bfda\b|\bfood and drug administration\b': "Food and Drug Administration (FDA) is the U.S. regulatory agency responsible for protecting public health by regulating drugs and medical devices.",
        r'\bgcp\b|\bgood clinical practice\b': "Good Clinical Practice (GCP) is an international quality standard for clinical trials that ensures the rights, safety and well-being of trial subjects are protected.",
        r'\bpk\b|\bpharmacokinetic\b': "Pharmacokinetics (PK) is the study of how the body processes a drug, including absorption, distribution, metabolism, and excretion.",
        r'\bpd\b|\bpharmacodynamic\b': "Pharmacodynamics (PD) is the study of the effects of drugs on the body and the mechanisms by which drugs exert their effects.",
        r'\btmf\b|\btrial master file\b': "Trial Master File (TMF) is a collection of essential documents that individually and collectively permit evaluation of the conduct of a study and the quality of the data produced."
    }
    
    for pattern, explanation in patterns.items():
        if re.search(pattern, term_lower):
            return explanation
    
    # Generic explanations based on term structure
    if term_lower.endswith('ectomy'):
        return f"'{term}' appears to be a medical term referring to a surgical removal procedure."
    elif term_lower.endswith('itis'):
        return f"'{term}' appears to be a medical term referring to an inflammation condition."
    elif term_lower.endswith('osis') or term_lower.endswith('oses'):
        return f"'{term}' appears to be a medical term referring to a condition or disease state."
    elif 'phase' in term_lower and any(char.isdigit() for char in term):
        return f"'{term}' likely refers to a clinical trial phase, which indicates the stage of drug development and testing."
    elif 'endpoint' in term_lower:
        return f"'{term}' refers to a predefined outcome measure used to assess the effectiveness or safety of a treatment in a clinical trial."
    
    return f"'{term}' is a clinical trial term that may require additional context for proper explanation."

def enhance_with_context(explanation: str, context: str, complexity_level: str) -> str:
    """Enhance explanation based on context and complexity level."""
    enhanced = explanation
    
    # Add context-specific information
    if context:
        context_lower = context.lower()
        if 'safety' in context_lower or 'adverse' in context_lower:
            enhanced += " In the context of safety reporting, this term is particularly important for ensuring participant safety and regulatory compliance."
        elif 'efficacy' in context_lower or 'endpoint' in context_lower:
            enhanced += " From an efficacy perspective, this term relates to measuring treatment outcomes and study success."
        elif 'protocol' in context_lower:
            enhanced += " In protocol design, this term helps define study procedures and requirements."
        elif 'regulatory' in context_lower or 'submission' in context_lower:
            enhanced += " For regulatory purposes, this term is relevant to compliance requirements and submission documentation."
    
    # Adjust complexity level
    if complexity_level == 'basic':
        enhanced = simplify_explanation(enhanced)
    elif complexity_level == 'advanced':
        enhanced = add_technical_details(enhanced)
    
    return enhanced

def simplify_explanation(explanation: str) -> str:
    """Simplify explanation for basic level."""
    # Replace technical terms with simpler alternatives
    replacements = {
        'pharmaceutical product': 'study drug',
        'administered': 'given',
        'untoward medical occurrence': 'unwanted health problem',
        'clinical investigation subject': 'study participant',
        'hospitalization': 'hospital stay'
    }
    
    simplified = explanation
    for technical, simple in replacements.items():
        simplified = simplified.replace(technical, simple)
    
    return simplified

def add_technical_details(explanation: str) -> str:
    """Add technical details for advanced level."""
    # This would typically add regulatory references, ICH guidelines, etc.
    if 'adverse event' in explanation.lower():
        explanation += " (Reference: ICH E2A Clinical Safety Data Management)"
    elif 'informed consent' in explanation.lower():
        explanation += " (Reference: ICH E6 Good Clinical Practice Guidelines)"
    elif 'good clinical practice' in explanation.lower():
        explanation += " (Reference: ICH E6(R2) Integrated Addendum)"
    
    return explanation

def find_related_terms(term: str, glossary_data: Dict, explanation: str) -> List[Dict]:
    """Find related terms based on the current term and explanation."""
    related = []
    
    # Extract keywords from the explanation
    explanation_words = set(explanation.lower().split())
    term_words = set(term.lower().split())
    
    for key, definition in glossary_data.items():
        if key.lower() == term.lower():
            continue  # Skip the same term
        
        # Check for related terms based on shared keywords
        key_words = set(key.lower().split())
        definition_words = set(definition.lower().split())
        
        # Calculate relatedness score
        shared_with_term = len(term_words & key_words)
        shared_with_explanation = len(explanation_words & definition_words)
        shared_with_def = len(explanation_words & key_words)
        
        relatedness_score = shared_with_term * 2 + shared_with_explanation + shared_with_def
        
        if relatedness_score > 0:
            related.append({
                'term': key,
                'definition': definition[:200] + '...' if len(definition) > 200 else definition,
                'relatedness_score': relatedness_score
            })
    
    # Sort by relatedness score
    related.sort(key=lambda x: x['relatedness_score'], reverse=True)
    
    return related

def generate_usage_examples(term: str, explanation: str, context: str) -> List[str]:
    """Generate usage examples for the term."""
    examples = []
    term_lower = term.lower()
    
    # Generate context-appropriate examples
    if 'adverse event' in term_lower or 'ae' == term_lower:
        examples = [
            "The subject experienced a mild headache, which was reported as an AE.",
            "All AEs must be documented in the CRF within 24 hours of occurrence.",
            "The investigator assessed the AE as possibly related to study drug."
        ]
    elif 'serious adverse event' in term_lower or 'sae' == term_lower:
        examples = [
            "The hospitalization for pneumonia was classified as an SAE.",
            "All SAEs require immediate notification to the sponsor.",
            "The SAE was determined to be unrelated to the investigational product."
        ]
    elif 'informed consent' in term_lower or 'icf' in term_lower:
        examples = [
            "The subject signed the ICF before any study procedures were performed.",
            "The informed consent process must be conducted by qualified personnel.",
            "Any changes to the ICF require IRB approval before implementation."
        ]
    elif 'principal investigator' in term_lower or 'pi' == term_lower:
        examples = [
            "The PI is responsible for ensuring protocol compliance at the site.",
            "The PI must review and approve all study-related procedures.",
            "Only the PI or qualified designee can make medical decisions for subjects."
        ]
    else:
        # Generate generic examples based on context
        if context:
            examples.append(f"In the context of {context.lower()}, {term} plays an important role.")
        examples.append(f"Understanding {term} is essential for clinical trial personnel.")
        examples.append(f"The definition of {term} may vary depending on the specific study protocol.")
    
    return examples[:3]  # Return top 3 examples

def analyze_context(context: str) -> Dict:
    """Analyze the context where the term was encountered."""
    context_lower = context.lower()
    
    analysis = {
        'document_type': 'unknown',
        'section_type': 'unknown',
        'regulatory_area': [],
        'stakeholder_relevance': []
    }
    
    # Identify document type
    if any(word in context_lower for word in ['protocol', 'study design']):
        analysis['document_type'] = 'protocol'
    elif any(word in context_lower for word in ['csr', 'clinical study report']):
        analysis['document_type'] = 'clinical_study_report'
    elif any(word in context_lower for word in ['sae', 'adverse event']):
        analysis['document_type'] = 'safety_report'
    elif any(word in context_lower for word in ['consent', 'icf']):
        analysis['document_type'] = 'informed_consent'
    
    # Identify section type
    if any(word in context_lower for word in ['inclusion', 'exclusion', 'eligibility']):
        analysis['section_type'] = 'eligibility_criteria'
    elif any(word in context_lower for word in ['endpoint', 'objective']):
        analysis['section_type'] = 'study_objectives'
    elif any(word in context_lower for word in ['safety', 'monitoring']):
        analysis['section_type'] = 'safety_monitoring'
    elif any(word in context_lower for word in ['statistical', 'analysis']):
        analysis['section_type'] = 'statistical_analysis'
    
    # Regulatory areas
    if any(word in context_lower for word in ['fda', 'submission']):
        analysis['regulatory_area'].append('FDA')
    if any(word in context_lower for word in ['ema', 'european']):
        analysis['regulatory_area'].append('EMA')
    if any(word in context_lower for word in ['ich', 'guideline']):
        analysis['regulatory_area'].append('ICH')
    
    # Stakeholder relevance
    if any(word in context_lower for word in ['investigator', 'site']):
        analysis['stakeholder_relevance'].append('investigators')
    if any(word in context_lower for word in ['sponsor', 'cro']):
        analysis['stakeholder_relevance'].append('sponsors')
    if any(word in context_lower for word in ['subject', 'patient']):
        analysis['stakeholder_relevance'].append('patients')
    if any(word in context_lower for word in ['regulatory', 'authority']):
        analysis['stakeholder_relevance'].append('regulators')
    
    return analysis

def calculate_confidence_score(match_type: str, explanation: str, term: str) -> float:
    """Calculate confidence score for the explanation."""
    base_scores = {
        'exact': 0.95,
        'fuzzy': 0.75,
        'generated': 0.60,
        'none': 0.0
    }
    
    base_score = base_scores.get(match_type, 0.5)
    
    # For exact matches, keep high confidence
    if match_type == 'exact':
        return base_score
    
    # Adjust based on explanation quality for other match types
    if explanation and match_type != 'exact':
        # Longer, more detailed explanations get higher scores
        length_factor = min(1.0, len(explanation) / 200)
        
        # Presence of specific clinical trial terms increases confidence
        clinical_terms = ['clinical trial', 'study', 'protocol', 'patient', 'subject', 'fda', 'regulatory']
        term_factor = sum(1 for term in clinical_terms if term in explanation.lower()) / len(clinical_terms)
        
        # Final score adjustment
        base_score = base_score * (0.7 + length_factor * 0.15 + term_factor * 0.15)
    
    return round(min(0.95, base_score), 2)

def suggest_similar_terms(term: str, glossary_data: Dict) -> List[str]:
    """Suggest similar terms when no match is found."""
    suggestions = []
    term_lower = term.lower()
    
    # Find terms with similar characters or patterns
    for key in glossary_data.keys():
        key_lower = key.lower()
        
        # Check for partial matches
        if any(word in key_lower for word in term_lower.split() if len(word) > 2):
            suggestions.append(key)
        elif any(word in term_lower for word in key_lower.split() if len(word) > 2):
            suggestions.append(key)
    
    # Remove duplicates and limit results
    suggestions = list(set(suggestions))[:5]
    
    return suggestions

def get_general_guidance(term: str) -> str:
    """Provide general guidance for understanding the term."""
    guidance_templates = [
        f"'{term}' appears to be a clinical trial term. Consider checking:",
        "- The study protocol glossary section",
        "- FDA guidance documents",
        "- ICH guidelines",
        "- Clinical research training materials"
    ]
    
    return " ".join(guidance_templates)

def categorize_term(term: str) -> str:
    """Categorize the term by type."""
    term_lower = term.lower()
    
    if any(abbrev in term_lower for abbrev in ['ae', 'sae', 'susar', 'adr']):
        return 'safety'
    elif any(word in term_lower for word in ['endpoint', 'efficacy', 'outcome']):
        return 'efficacy'
    elif any(word in term_lower for word in ['consent', 'icf', 'irb', 'ethics']):
        return 'ethics_regulatory'
    elif any(word in term_lower for word in ['randomization', 'blinding', 'placebo']):
        return 'study_design'
    elif any(word in term_lower for word in ['crf', 'data', 'query']):
        return 'data_management'
    elif any(word in term_lower for word in ['monitor', 'audit', 'gcp']):
        return 'quality_assurance'
    elif any(word in term_lower for word in ['pk', 'pd', 'pharmacokinetic']):
        return 'pharmacology'
    else:
        return 'general'

def assess_regulatory_relevance(term: str) -> str:
    """Assess regulatory relevance of the term."""
    term_lower = term.lower()
    
    high_relevance = ['sae', 'susar', 'icf', 'gcp', 'deviation', 'amendment']
    medium_relevance = ['ae', 'crf', 'endpoint', 'protocol', 'tmf']
    
    if any(word in term_lower for word in high_relevance):
        return 'high'
    elif any(word in term_lower for word in medium_relevance):
        return 'medium'
    else:
        return 'low'

def get_additional_resources(term: str) -> List[Dict]:
    """Get additional resources for learning about the term."""
    resources = [
        {
            'type': 'ICH Guidelines',
            'description': 'International Council for Harmonisation guidelines',
            'relevance': 'high'
        },
        {
            'type': 'FDA Guidance',
            'description': 'FDA guidance documents for clinical trials',
            'relevance': 'high'
        },
        {
            'type': 'GCP Training',
            'description': 'Good Clinical Practice training materials',
            'relevance': 'medium'
        },
        {
            'type': 'Clinical Research Glossary',
            'description': 'Comprehensive clinical research terminology',
            'relevance': 'medium'
        }
    ]
    
    return resources