import re
from typing import Dict, List, Any
import hashlib


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove PII (Personally Identifiable Information) from clinical documents.
    
    Args:
        input_data: Dict containing:
            - text (str): Document text to de-identify
            - mode (str): 'full' for complete removal, 'hash' for replacement with hash
            - custom_patterns (list, optional): Additional regex patterns to match
    
    Returns:
        Dict containing:
            - deidentified_text (str): Text with PII removed
            - items_removed (list): List of types of PII found and removed
            - statistics (dict): Count of each type of PII removed
    """
    text = input_data.get('text', '')
    mode = input_data.get('mode', 'full')
    custom_patterns = input_data.get('custom_patterns', [])
    
    if not text:
        return {
            'deidentified_text': '',
            'items_removed': [],
            'statistics': {}
        }
    
    items_removed = []
    statistics = {}
    
    # Define PII patterns
    patterns = {
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        'mrn': r'\b(?:MRN|Medical Record Number)[:\s]*[\w\d-]+\b',
        'dob': r'\b(?:DOB|Date of Birth)[:\s]*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        'name_indicators': r'\b(?:Patient Name|Subject Name|Participant)[:\s]*[A-Za-z\s]+(?:\n|,|;)',
        'address': r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Plaza|Pl)\b',
        'zip_code': r'\b\d{5}(?:-\d{4})?\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'date_full': r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        'protocol_subject_id': r'\b(?:Subject|Patient|Participant)\s*(?:ID|#)[:\s]*[\w\d-]+\b'
    }
    
    # Add custom patterns
    for idx, pattern in enumerate(custom_patterns):
        patterns[f'custom_{idx}'] = pattern
    
    # Process text
    deidentified_text = text
    
    for pii_type, pattern in patterns.items():
        matches = re.findall(pattern, deidentified_text, re.IGNORECASE)
        
        if matches:
            items_removed.append(pii_type)
            statistics[pii_type] = len(matches)
            
            if mode == 'hash':
                # Replace with hash
                for match in set(matches):
                    hash_value = hashlib.sha256(match.encode()).hexdigest()[:8]
                    replacement = f'[{pii_type.upper()}_{hash_value}]'
                    deidentified_text = re.sub(
                        re.escape(match),
                        replacement,
                        deidentified_text,
                        flags=re.IGNORECASE
                    )
            else:
                # Complete removal
                deidentified_text = re.sub(
                    pattern,
                    f'[{pii_type.upper()}_REMOVED]',
                    deidentified_text,
                    flags=re.IGNORECASE
                )
    
    # Additional safety: Remove any remaining potential identifiers
    # Remove sequences that look like IDs (mix of letters and numbers)
    id_pattern = r'\b[A-Z]{2,4}\d{4,8}\b'
    id_matches = re.findall(id_pattern, deidentified_text)
    if id_matches:
        statistics['potential_ids'] = len(id_matches)
        items_removed.append('potential_ids')
        deidentified_text = re.sub(id_pattern, '[ID_REMOVED]', deidentified_text)
    
    return {
        'deidentified_text': deidentified_text,
        'items_removed': list(set(items_removed)),
        'statistics': statistics,
        'mode_used': mode,
        'total_items_removed': sum(statistics.values())
    }