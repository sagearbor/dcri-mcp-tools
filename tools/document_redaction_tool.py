"""
Document Redaction Tool for Clinical Studies
Redacts confidential information from documents while preserving structure
"""

import re
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime


def run(input_data: Dict) -> Dict:
    """
    Redacts confidential information from clinical documents while preserving document structure.
    
    Example:
        Input: Document text with subject IDs, names, and contact information to be redacted
        Output: Redacted document with sensitive information masked using specified replacement characters
    
    Parameters:
        text : str
            Document text content to redact
        redaction_level : str
            Redaction intensity ('minimal', 'standard', 'maximum')
        custom_patterns : list
            Custom regex patterns for redaction
        preserve_structure : bool
            Maintain document formatting during redaction
        replacement_char : str
            Character for redaction (default 'X')
        phi_categories : list
            PHI categories to redact
        allow_list : list
            Terms to never redact
        output_format : str
            Output format ('redacted_text', 'annotations', 'both')
    """
    try:
        text = input_data.get('text', '')
        redaction_level = input_data.get('redaction_level', 'standard')
        custom_patterns = input_data.get('custom_patterns', [])
        preserve_structure = input_data.get('preserve_structure', True)
        replacement_char = input_data.get('replacement_char', 'X')
        phi_categories = input_data.get('phi_categories', [])
        allow_list = input_data.get('allow_list', [])
        output_format = input_data.get('output_format', 'both')
        
        if not text:
            return {
                'success': False,
                'error': 'text is required for redaction'
            }
        
        # Initialize redaction tracking
        redactions_made = []
        original_text = text
        
        # Get redaction patterns based on level
        patterns = _get_redaction_patterns(redaction_level, phi_categories)
        
        # Add custom patterns
        if custom_patterns:
            patterns.extend([{'pattern': p, 'category': 'custom', 'description': 'Custom pattern'} 
                           for p in custom_patterns])
        
        # Apply redactions
        redacted_text, redactions_made = _apply_redactions(
            text, patterns, allow_list, replacement_char, preserve_structure
        )
        
        # Generate annotations if requested
        annotations = _generate_annotations(original_text, redactions_made) if output_format in ['annotations', 'both'] else []
        
        # Calculate statistics
        statistics = _calculate_redaction_statistics(original_text, redacted_text, redactions_made)
        
        result = {
            'success': True,
            'redaction_level': redaction_level,
            'statistics': statistics,
            'timestamp': datetime.now().isoformat()
        }
        
        if output_format in ['redacted_text', 'both']:
            result['redacted_text'] = redacted_text
        
        if output_format in ['annotations', 'both']:
            result['annotations'] = annotations
        
        result['redaction_summary'] = {
            'total_redactions': len(redactions_made),
            'categories_redacted': list(set(r['category'] for r in redactions_made)),
            'redaction_density': statistics['redaction_percentage'],
            'high_risk_items': [r for r in redactions_made if r.get('risk_level') == 'high']
        }
        
        result['compliance_notes'] = _get_compliance_notes(redaction_level, phi_categories)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error during document redaction: {str(e)}'
        }


def _get_redaction_patterns(level: str, phi_categories: List[str]) -> List[Dict]:
    """Get redaction patterns based on level and PHI categories."""
    
    base_patterns = {
        # Personal identifiers
        'names': [
            {'pattern': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', 'category': 'names', 'description': 'Person names', 'risk_level': 'high'},
            {'pattern': r'\b(?:Mr|Mrs|Ms|Dr|Prof)\.?\s+[A-Z][a-z]+', 'category': 'names', 'description': 'Titled names', 'risk_level': 'high'}
        ],
        
        # Contact information
        'contact': [
            {'pattern': r'\b\d{3}-\d{3}-\d{4}\b', 'category': 'phone', 'description': 'Phone numbers', 'risk_level': 'medium'},
            {'pattern': r'\b\d{10}\b', 'category': 'phone', 'description': 'Phone numbers (no dashes)', 'risk_level': 'medium'},
            {'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'category': 'email', 'description': 'Email addresses', 'risk_level': 'high'},
        ],
        
        # Medical identifiers
        'medical_ids': [
            {'pattern': r'\b(?:MRN|MR|Medical Record|Patient ID)[:\s#]*\s*[A-Z0-9-]+', 'category': 'mrn', 'description': 'Medical record numbers', 'risk_level': 'high'},
            {'pattern': r'\b\d{3}-\d{2}-\d{4}\b', 'category': 'ssn', 'description': 'Social Security Numbers', 'risk_level': 'high'},
            {'pattern': r'\b(?:Subject|Patient|Participant)[:\s#]*\s*[A-Z0-9-]+', 'category': 'subject_id', 'description': 'Subject identifiers', 'risk_level': 'high'}
        ],
        
        # Dates
        'dates': [
            {'pattern': r'\b\d{1,2}/\d{1,2}/\d{4}\b', 'category': 'date', 'description': 'Dates (MM/DD/YYYY)', 'risk_level': 'medium'},
            {'pattern': r'\b\d{4}-\d{2}-\d{2}\b', 'category': 'date', 'description': 'Dates (YYYY-MM-DD)', 'risk_level': 'medium'},
            {'pattern': r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', 'category': 'date', 'description': 'Written dates', 'risk_level': 'medium'}
        ],
        
        # Addresses
        'addresses': [
            {'pattern': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\.?\b', 'category': 'address', 'description': 'Street addresses', 'risk_level': 'medium'},
            {'pattern': r'\b\d{5}(?:-\d{4})?\b', 'category': 'zip', 'description': 'ZIP codes', 'risk_level': 'low'}
        ],
        
        # Financial information
        'financial': [
            {'pattern': r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', 'category': 'currency', 'description': 'Dollar amounts', 'risk_level': 'medium'},
            {'pattern': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 'category': 'credit_card', 'description': 'Credit card numbers', 'risk_level': 'high'}
        ],
        
        # Institution information
        'institutions': [
            {'pattern': r'\b[A-Z][a-z]+\s+(?:Hospital|Medical Center|Clinic|University|Institute)\b', 'category': 'institution', 'description': 'Medical institutions', 'risk_level': 'medium'},
            {'pattern': r'\b(?:Duke|Mayo|Johns Hopkins|Cleveland Clinic|Mass General|UCSF)\b', 'category': 'institution', 'description': 'Known institutions', 'risk_level': 'medium'}
        ]
    }
    
    # Select patterns based on level
    if level == 'minimal':
        categories = ['medical_ids', 'contact']
    elif level == 'standard':
        categories = ['names', 'contact', 'medical_ids', 'dates']
    else:  # maximum
        categories = list(base_patterns.keys())
    
    # Filter by PHI categories if specified
    if phi_categories:
        categories = [cat for cat in categories if cat in phi_categories]
    
    # Flatten patterns
    patterns = []
    for category in categories:
        if category in base_patterns:
            patterns.extend(base_patterns[category])
    
    return patterns


def _apply_redactions(text: str, patterns: List[Dict], allow_list: List[str], 
                     replacement_char: str, preserve_structure: bool) -> Tuple[str, List[Dict]]:
    """Apply redaction patterns to text."""
    redacted_text = text
    redactions_made = []
    
    for pattern_info in patterns:
        pattern = pattern_info['pattern']
        matches = list(re.finditer(pattern, redacted_text, re.IGNORECASE))
        
        for match in reversed(matches):  # Reverse to maintain positions
            matched_text = match.group()
            
            # Check allow list
            if _is_in_allow_list(matched_text, allow_list):
                continue
            
            start_pos = match.start()
            end_pos = match.end()
            
            # Create redaction
            if preserve_structure:
                # Preserve length and some structure
                redaction = _create_structured_redaction(matched_text, replacement_char)
            else:
                redaction = f'[{pattern_info["category"].upper()}_REDACTED]'
            
            # Apply redaction
            redacted_text = redacted_text[:start_pos] + redaction + redacted_text[end_pos:]
            
            # Track redaction
            redactions_made.append({
                'original_text': matched_text,
                'redacted_text': redaction,
                'category': pattern_info['category'],
                'description': pattern_info['description'],
                'risk_level': pattern_info.get('risk_level', 'medium'),
                'start_position': start_pos,
                'end_position': end_pos,
                'length': len(matched_text)
            })
    
    return redacted_text, redactions_made


def _create_structured_redaction(text: str, replacement_char: str) -> str:
    """Create a structured redaction that preserves text formatting."""
    redaction = ''
    for char in text:
        if char.isalnum():
            redaction += replacement_char
        elif char in '@.-':  # Preserve some structural characters
            redaction += char
        else:
            redaction += char  # Preserve spaces and punctuation
    return redaction


def _is_in_allow_list(text: str, allow_list: List[str]) -> bool:
    """Check if text is in the allow list."""
    text_lower = text.lower()
    # Check if the matched text is part of any allow_list term OR contains any allow_list term
    return any(
        allow_term.lower() in text_lower or text_lower in allow_term.lower() 
        for allow_term in allow_list
    )


def _generate_annotations(original_text: str, redactions: List[Dict]) -> List[Dict]:
    """Generate annotations for redacted content."""
    annotations = []
    
    for i, redaction in enumerate(redactions):
        annotation = {
            'id': f'redaction_{i+1}',
            'type': 'redaction',
            'category': redaction['category'],
            'description': redaction['description'],
            'risk_level': redaction['risk_level'],
            'start_position': redaction['start_position'],
            'end_position': redaction['end_position'],
            'original_length': redaction['length'],
            'redaction_reason': f'PHI/{redaction["category"]} detected'
        }
        annotations.append(annotation)
    
    return annotations


def _calculate_redaction_statistics(original_text: str, redacted_text: str, 
                                  redactions: List[Dict]) -> Dict:
    """Calculate redaction statistics."""
    total_chars = len(original_text)
    redacted_chars = sum(r['length'] for r in redactions)
    
    category_counts = {}
    risk_level_counts = {}
    
    for redaction in redactions:
        category = redaction['category']
        risk_level = redaction.get('risk_level', 'medium')
        
        category_counts[category] = category_counts.get(category, 0) + 1
        risk_level_counts[risk_level] = risk_level_counts.get(risk_level, 0) + 1
    
    return {
        'original_length': total_chars,
        'redacted_length': len(redacted_text),
        'characters_redacted': redacted_chars,
        'redaction_percentage': round((redacted_chars / total_chars * 100) if total_chars > 0 else 0, 2),
        'total_redactions': len(redactions),
        'redactions_by_category': category_counts,
        'redactions_by_risk_level': risk_level_counts,
        'words_original': len(original_text.split()),
        'words_redacted': len(redacted_text.split())
    }


def _get_compliance_notes(redaction_level: str, phi_categories: List[str]) -> List[str]:
    """Get compliance notes for redaction."""
    notes = [
        "Redaction performed to protect sensitive information",
        "Review redacted document before distribution",
        "Ensure redaction meets regulatory requirements"
    ]
    
    if redaction_level == 'minimal':
        notes.append("Minimal redaction - verify sufficient for intended use")
    elif redaction_level == 'maximum':
        notes.append("Maximum redaction - confirm readability for intended purpose")
    
    if 'medical_ids' in phi_categories:
        notes.append("Medical identifiers redacted per HIPAA requirements")
    
    if 'financial' in phi_categories:
        notes.append("Financial information redacted - verify compliance with financial privacy laws")
    
    return notes