"""
Glossary Manager Tool for Clinical Studies
Maintains and checks study glossaries and terminology consistency
"""

import re
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime


def run(input_data: Dict) -> Dict:
    """
    Manage and check study glossaries and terminology.
    
    Args:
        input_data: Dictionary containing:
            - action: 'create', 'add_terms', 'validate_document', 'search', 'export', 'merge'
            - glossary: Current glossary dict or list of terms
            - terms: New terms to add (list of dicts or single dict)
            - document_text: Text to validate against glossary
            - search_query: Term to search for
            - validation_options: Dict with validation settings
            - merge_glossaries: List of glossaries to merge
            - export_format: 'json', 'csv', 'html', 'markdown'
    
    Returns:
        Dictionary with glossary management results
    """
    try:
        action = input_data.get('action', '').lower()
        glossary = input_data.get('glossary', {})
        terms = input_data.get('terms', [])
        document_text = input_data.get('document_text', '')
        search_query = input_data.get('search_query', '')
        validation_options = input_data.get('validation_options', {})
        merge_glossaries = input_data.get('merge_glossaries', [])
        export_format = input_data.get('export_format', 'json')
        
        if not action:
            return {
                'success': False,
                'error': 'action is required',
                'valid_actions': ['create', 'add_terms', 'validate_document', 'search', 'export', 'merge']
            }
        
        result = {'success': True, 'action': action}
        
        if action == 'create':
            result.update(_create_glossary(terms))
        elif action == 'add_terms':
            result.update(_add_terms_to_glossary(glossary, terms))
        elif action == 'validate_document':
            result.update(_validate_document_terminology(document_text, glossary, validation_options))
        elif action == 'search':
            result.update(_search_glossary(glossary, search_query))
        elif action == 'export':
            result.update(_export_glossary(glossary, export_format))
        elif action == 'merge':
            result.update(_merge_glossaries(merge_glossaries))
        else:
            return {
                'success': False,
                'error': f'Unknown action: {action}',
                'valid_actions': ['create', 'add_terms', 'validate_document', 'search', 'export', 'merge']
            }
        
        # Add metadata
        result['metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'glossary_size': len(glossary) if isinstance(glossary, dict) else 0,
            'action_performed': action
        }
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error in glossary management: {str(e)}'
        }


def _create_glossary(terms: List[Dict]) -> Dict:
    """Create a new glossary from terms."""
    glossary = {}
    added_terms = []
    errors = []
    
    # Handle single term input
    if isinstance(terms, dict):
        terms = [terms]
    
    for i, term_data in enumerate(terms):
        try:
            if isinstance(term_data, str):
                # Simple string term
                term_id = _generate_term_id(term_data)
                standardized_term = _create_standard_term_entry(term_data)
            else:
                # Dictionary term
                term = term_data.get('term', '')
                if not term:
                    errors.append(f'Term {i+1}: "term" field is required')
                    continue
                
                term_id = term_data.get('id') or _generate_term_id(term)
                standardized_term = _create_standard_term_entry(term, term_data)
            
            glossary[term_id] = standardized_term
            added_terms.append(term_id)
            
        except Exception as e:
            errors.append(f'Term {i+1}: {str(e)}')
    
    return {
        'glossary': glossary,
        'created_terms': added_terms,
        'term_count': len(glossary),
        'errors': errors,
        'summary': f'Created glossary with {len(glossary)} terms'
    }


def _add_terms_to_glossary(existing_glossary: Dict, new_terms: List[Dict]) -> Dict:
    """Add new terms to existing glossary."""
    updated_glossary = existing_glossary.copy()
    added_terms = []
    updated_terms = []
    errors = []
    
    # Handle single term input
    if isinstance(new_terms, dict):
        new_terms = [new_terms]
    
    for i, term_data in enumerate(new_terms):
        try:
            if isinstance(term_data, str):
                term = term_data
                term_id = _generate_term_id(term)
                standardized_term = _create_standard_term_entry(term)
            else:
                term = term_data.get('term', '')
                if not term:
                    errors.append(f'Term {i+1}: "term" field is required')
                    continue
                
                term_id = term_data.get('id') or _generate_term_id(term)
                standardized_term = _create_standard_term_entry(term, term_data)
            
            if term_id in updated_glossary:
                # Update existing term
                updated_glossary[term_id].update(standardized_term)
                updated_terms.append(term_id)
            else:
                # Add new term
                updated_glossary[term_id] = standardized_term
                added_terms.append(term_id)
            
        except Exception as e:
            errors.append(f'Term {i+1}: {str(e)}')
    
    return {
        'updated_glossary': updated_glossary,
        'added_terms': added_terms,
        'updated_terms': updated_terms,
        'new_term_count': len(added_terms),
        'updated_term_count': len(updated_terms),
        'total_terms': len(updated_glossary),
        'errors': errors
    }


def _validate_document_terminology(document_text: str, glossary: Dict, 
                                 options: Dict) -> Dict:
    """Validate document terminology against glossary."""
    if not document_text:
        return {'error': 'document_text is required for validation'}
    
    if not glossary:
        return {'error': 'glossary is required for validation'}
    
    # Validation options
    case_sensitive = options.get('case_sensitive', False)
    check_definitions = options.get('check_definitions', True)
    check_consistency = options.get('check_consistency', True)
    highlight_undefined = options.get('highlight_undefined', True)
    min_term_length = options.get('min_term_length', 3)
    
    validation_results = {
        'defined_terms_found': [],
        'undefined_terms_found': [],
        'inconsistent_usage': [],
        'definition_mismatches': [],
        'suggestions': []
    }
    
    # Extract potential terms from document
    document_terms = _extract_terms_from_text(document_text, min_term_length)
    
    # Check each term against glossary
    for term_info in document_terms:
        term = term_info['term']
        positions = term_info['positions']
        
        # Find matching glossary entries
        matching_entries = _find_matching_glossary_entries(term, glossary, case_sensitive)
        
        if matching_entries:
            # Term is defined
            for entry_id, entry in matching_entries:
                validation_results['defined_terms_found'].append({
                    'term': term,
                    'glossary_id': entry_id,
                    'positions': positions,
                    'definition': entry.get('definition', ''),
                    'preferred_form': entry.get('term', term)
                })
                
                # Check for consistency issues
                if check_consistency:
                    consistency_issues = _check_term_consistency(
                        term, entry, document_text, positions
                    )
                    validation_results['inconsistent_usage'].extend(consistency_issues)
        else:
            # Term not defined
            if highlight_undefined and _is_likely_technical_term(term):
                validation_results['undefined_terms_found'].append({
                    'term': term,
                    'positions': positions,
                    'context': [_get_term_context(document_text, pos) for pos in positions[:3]]
                })
    
    # Generate suggestions for undefined terms
    validation_results['suggestions'] = _generate_terminology_suggestions(
        validation_results['undefined_terms_found'], glossary
    )
    
    # Calculate validation score
    total_technical_terms = len([t for t in document_terms if _is_likely_technical_term(t['term'])])
    defined_technical_terms = len(set(t['term'].lower() for t in validation_results['defined_terms_found']))
    
    validation_score = (defined_technical_terms / total_technical_terms * 100) if total_technical_terms > 0 else 100
    
    return {
        'validation_results': validation_results,
        'statistics': {
            'total_terms_found': len(document_terms),
            'defined_terms': len(validation_results['defined_terms_found']),
            'undefined_terms': len(validation_results['undefined_terms_found']),
            'consistency_issues': len(validation_results['inconsistent_usage']),
            'validation_score': round(validation_score, 2),
            'terminology_coverage': f"{defined_technical_terms}/{total_technical_terms} technical terms defined"
        },
        'recommendations': _generate_validation_recommendations(validation_results, validation_score)
    }


def _search_glossary(glossary: Dict, query: str) -> Dict:
    """Search glossary for terms matching query."""
    if not query:
        return {
            'search_results': list(glossary.values()),
            'result_count': len(glossary),
            'query': 'all terms'
        }
    
    query_lower = query.lower()
    search_results = []
    
    for term_id, term_entry in glossary.items():
        relevance_score = _calculate_term_relevance(term_entry, query_lower)
        
        if relevance_score > 0:
            result = term_entry.copy()
            result['glossary_id'] = term_id
            result['relevance_score'] = relevance_score
            search_results.append(result)
    
    # Sort by relevance
    search_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return {
        'search_results': search_results,
        'result_count': len(search_results),
        'query': query,
        'search_summary': _generate_search_summary(search_results, query)
    }


def _export_glossary(glossary: Dict, format_type: str) -> Dict:
    """Export glossary in specified format."""
    export_functions = {
        'json': _export_glossary_json,
        'csv': _export_glossary_csv,
        'html': _export_glossary_html,
        'markdown': _export_glossary_markdown,
        'xlsx': _export_glossary_excel
    }
    
    if format_type not in export_functions:
        return {
            'error': f'Unsupported export format: {format_type}',
            'supported_formats': list(export_functions.keys())
        }
    
    try:
        exported_data = export_functions[format_type](glossary)
        return {
            'exported_data': exported_data,
            'format': format_type,
            'term_count': len(glossary),
            'export_notes': _get_export_notes(format_type)
        }
    except Exception as e:
        return {
            'error': f'Export failed: {str(e)}',
            'format': format_type
        }


def _merge_glossaries(glossaries: List[Dict]) -> Dict:
    """Merge multiple glossaries."""
    if not glossaries:
        return {'error': 'No glossaries provided for merging'}
    
    merged_glossary = {}
    merge_conflicts = []
    merge_statistics = {
        'total_input_glossaries': len(glossaries),
        'total_input_terms': 0,
        'unique_terms_merged': 0,
        'conflicts_resolved': 0
    }
    
    for i, glossary in enumerate(glossaries):
        if not isinstance(glossary, dict):
            continue
        
        merge_statistics['total_input_terms'] += len(glossary)
        
        for term_id, term_entry in glossary.items():
            if term_id in merged_glossary:
                # Handle conflict
                conflict = _resolve_term_conflict(
                    term_id, merged_glossary[term_id], term_entry, i
                )
                merge_conflicts.append(conflict)
                merged_glossary[term_id] = conflict['resolved_term']
                merge_statistics['conflicts_resolved'] += 1
            else:
                merged_glossary[term_id] = term_entry
                merge_statistics['unique_terms_merged'] += 1
    
    return {
        'merged_glossary': merged_glossary,
        'merge_conflicts': merge_conflicts,
        'merge_statistics': merge_statistics,
        'recommendations': _generate_merge_recommendations(merge_conflicts)
    }


def _create_standard_term_entry(term: str, term_data: Dict = None) -> Dict:
    """Create a standardized term entry."""
    if term_data is None:
        term_data = {}
    
    return {
        'term': term,
        'definition': term_data.get('definition', ''),
        'category': term_data.get('category', 'general'),
        'synonyms': term_data.get('synonyms', []),
        'abbreviations': term_data.get('abbreviations', []),
        'related_terms': term_data.get('related_terms', []),
        'usage_notes': term_data.get('usage_notes', ''),
        'examples': term_data.get('examples', []),
        'source': term_data.get('source', ''),
        'date_added': term_data.get('date_added', datetime.now().isoformat()),
        'last_updated': datetime.now().isoformat(),
        'status': term_data.get('status', 'active'),
        'domain': term_data.get('domain', 'clinical'),
        'confidence_level': term_data.get('confidence_level', 'high')
    }


def _generate_term_id(term: str) -> str:
    """Generate a unique ID for a term."""
    # Clean term and create ID
    clean_term = re.sub(r'[^\w\s]', '', term.lower())
    clean_term = re.sub(r'\s+', '_', clean_term.strip())
    return f"term_{clean_term}"


def _extract_terms_from_text(text: str, min_length: int = 3) -> List[Dict]:
    """Extract potential terms from text."""
    # Define patterns for different types of terms
    patterns = [
        # Multi-word technical terms (capitalized)
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b',
        # Acronyms
        r'\b[A-Z]{2,6}\b',
        # Single technical words (longer than min_length)
        rf'\b[a-zA-Z]{{{min_length},}}\b',
        # Hyphenated terms
        r'\b[a-zA-Z]+-[a-zA-Z]+(?:-[a-zA-Z]+)*\b'
    ]
    
    terms_found = {}
    
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            term = match.group().strip()
            start_pos = match.start()
            
            if len(term) >= min_length and not _is_common_word(term):
                term_key = term.lower()
                if term_key not in terms_found:
                    terms_found[term_key] = {
                        'term': term,
                        'positions': []
                    }
                terms_found[term_key]['positions'].append(start_pos)
    
    return list(terms_found.values())


def _is_common_word(word: str) -> bool:
    """Check if word is a common English word."""
    common_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 
        'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
        'those', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all',
        'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
        'only', 'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will',
        'just', 'should', 'now', 'may', 'also', 'been', 'have', 'had', 'has',
        'were', 'said', 'each', 'which', 'their', 'time', 'will', 'about',
        'would', 'there', 'could', 'other'
    }
    return word.lower() in common_words


def _is_likely_technical_term(term: str) -> bool:
    """Determine if a term is likely technical/medical."""
    # Patterns that suggest technical terms
    technical_indicators = [
        len(term) > 8,  # Long words often technical
        bool(re.search(r'[A-Z]{2,}', term)),  # Contains acronyms
        bool(re.search(r'(?:ology|osis|itis|emia|uria|pathy|therapy|gram)$', term, re.IGNORECASE)),  # Medical suffixes
        bool(re.search(r'^(?:anti|pre|post|sub|super|trans|inter|intra)', term, re.IGNORECASE)),  # Medical prefixes
        term.count('-') > 0,  # Hyphenated terms often technical
        bool(re.search(r'(?:trial|study|protocol|endpoint|adverse|efficacy|safety)', term, re.IGNORECASE))  # Clinical trial terms
    ]
    
    return sum(technical_indicators) >= 2


def _find_matching_glossary_entries(term: str, glossary: Dict, 
                                  case_sensitive: bool = False) -> List[Tuple[str, Dict]]:
    """Find glossary entries that match the term."""
    matches = []
    search_term = term if case_sensitive else term.lower()
    
    for entry_id, entry in glossary.items():
        entry_term = entry.get('term', '')
        if not case_sensitive:
            entry_term = entry_term.lower()
        
        # Exact match
        if search_term == entry_term:
            matches.append((entry_id, entry))
            continue
        
        # Check synonyms
        synonyms = entry.get('synonyms', [])
        for synonym in synonyms:
            synonym_check = synonym if case_sensitive else synonym.lower()
            if search_term == synonym_check:
                matches.append((entry_id, entry))
                break
        
        # Check abbreviations
        abbreviations = entry.get('abbreviations', [])
        for abbrev in abbreviations:
            abbrev_check = abbrev if case_sensitive else abbrev.lower()
            if search_term == abbrev_check:
                matches.append((entry_id, entry))
                break
    
    return matches


def _check_term_consistency(term: str, entry: Dict, document_text: str, 
                          positions: List[int]) -> List[Dict]:
    """Check for consistency issues in term usage."""
    issues = []
    
    preferred_form = entry.get('term', '')
    if term != preferred_form:
        issues.append({
            'type': 'preferred_form_not_used',
            'term_used': term,
            'preferred_form': preferred_form,
            'positions': positions,
            'severity': 'medium',
            'suggestion': f'Consider using preferred form "{preferred_form}" instead of "{term}"'
        })
    
    # Check for mixed case usage
    all_usages = []
    for pos in positions:
        context = _get_term_context(document_text, pos, 0)
        all_usages.append(context)
    
    unique_forms = set(all_usages)
    if len(unique_forms) > 1:
        issues.append({
            'type': 'inconsistent_capitalization',
            'term': term,
            'variations_found': list(unique_forms),
            'positions': positions,
            'severity': 'low',
            'suggestion': 'Standardize capitalization throughout document'
        })
    
    return issues


def _get_term_context(text: str, position: int, context_words: int = 5) -> str:
    """Get context around a term at given position."""
    if context_words == 0:
        # Find just the term at this position
        start = position
        end = position
        while end < len(text) and text[end].isalnum():
            end += 1
        return text[start:end]
    
    # Get surrounding context
    words_before = []
    words_after = []
    
    # Get words before
    pos = position - 1
    word_count = 0
    current_word = ""
    
    while pos >= 0 and word_count < context_words:
        if text[pos].isalnum():
            current_word = text[pos] + current_word
        else:
            if current_word:
                words_before.insert(0, current_word)
                current_word = ""
                word_count += 1
        pos -= 1
    
    if current_word:
        words_before.insert(0, current_word)
    
    # Get the term itself
    pos = position
    term = ""
    while pos < len(text) and text[pos].isalnum():
        term += text[pos]
        pos += 1
    
    # Get words after
    word_count = 0
    current_word = ""
    
    while pos < len(text) and word_count < context_words:
        if text[pos].isalnum():
            current_word += text[pos]
        else:
            if current_word:
                words_after.append(current_word)
                current_word = ""
                word_count += 1
        pos += 1
    
    if current_word:
        words_after.append(current_word)
    
    return " ".join(words_before + [f"**{term}**"] + words_after)


def _generate_terminology_suggestions(undefined_terms: List[Dict], 
                                    glossary: Dict) -> List[Dict]:
    """Generate suggestions for undefined terms."""
    suggestions = []
    
    for term_info in undefined_terms[:10]:  # Limit suggestions
        term = term_info['term']
        
        # Find similar terms in glossary
        similar_terms = _find_similar_terms(term, glossary)
        
        suggestion = {
            'undefined_term': term,
            'suggestions': []
        }
        
        if similar_terms:
            suggestion['suggestions'] = similar_terms[:3]  # Top 3 suggestions
        else:
            suggestion['suggestions'] = [
                {
                    'action': 'add_to_glossary',
                    'suggestion': f'Consider adding "{term}" to glossary with definition'
                }
            ]
        
        suggestions.append(suggestion)
    
    return suggestions


def _find_similar_terms(term: str, glossary: Dict) -> List[Dict]:
    """Find similar terms in glossary."""
    from difflib import SequenceMatcher
    
    similarities = []
    term_lower = term.lower()
    
    for entry_id, entry in glossary.items():
        entry_term = entry.get('term', '').lower()
        similarity = SequenceMatcher(None, term_lower, entry_term).ratio()
        
        if similarity > 0.6:  # 60% similarity threshold
            similarities.append({
                'glossary_term': entry.get('term', ''),
                'similarity_score': similarity,
                'definition': entry.get('definition', ''),
                'action': 'consider_existing_term'
            })
        
        # Also check synonyms
        for synonym in entry.get('synonyms', []):
            synonym_similarity = SequenceMatcher(None, term_lower, synonym.lower()).ratio()
            if synonym_similarity > 0.7:
                similarities.append({
                    'glossary_term': entry.get('term', ''),
                    'matched_synonym': synonym,
                    'similarity_score': synonym_similarity,
                    'definition': entry.get('definition', ''),
                    'action': 'synonym_match'
                })
    
    return sorted(similarities, key=lambda x: x['similarity_score'], reverse=True)


def _calculate_term_relevance(term_entry: Dict, query: str) -> float:
    """Calculate relevance score for search."""
    score = 0.0
    
    # Term name match
    term = term_entry.get('term', '').lower()
    if query in term:
        score += 10.0 + (5.0 if term.startswith(query) else 0)
    
    # Definition match
    definition = term_entry.get('definition', '').lower()
    if query in definition:
        score += 5.0
    
    # Synonyms match
    synonyms = ' '.join(term_entry.get('synonyms', [])).lower()
    if query in synonyms:
        score += 7.0
    
    # Category match
    category = term_entry.get('category', '').lower()
    if query in category:
        score += 3.0
    
    # Examples match
    examples = ' '.join(term_entry.get('examples', [])).lower()
    if query in examples:
        score += 2.0
    
    return score


def _resolve_term_conflict(term_id: str, existing_term: Dict, 
                         new_term: Dict, source_index: int) -> Dict:
    """Resolve conflict when merging terms."""
    # Simple resolution strategy - prefer more complete entries
    existing_completeness = _calculate_term_completeness(existing_term)
    new_completeness = _calculate_term_completeness(new_term)
    
    if new_completeness > existing_completeness:
        resolved_term = new_term.copy()
        resolution_reason = "New term more complete"
    else:
        resolved_term = existing_term.copy()
        resolution_reason = "Existing term more complete"
    
    # Merge non-conflicting fields
    merged_term = _merge_term_fields(existing_term, new_term)
    
    return {
        'term_id': term_id,
        'conflict_type': 'duplicate_term',
        'existing_term': existing_term,
        'new_term': new_term,
        'resolved_term': merged_term,
        'resolution_reason': resolution_reason,
        'source_index': source_index
    }


def _calculate_term_completeness(term: Dict) -> float:
    """Calculate completeness score for a term."""
    score = 0.0
    
    # Required fields
    if term.get('term'):
        score += 2.0
    if term.get('definition'):
        score += 3.0
    
    # Optional but valuable fields
    if term.get('synonyms'):
        score += 1.0
    if term.get('examples'):
        score += 1.0
    if term.get('category'):
        score += 0.5
    if term.get('usage_notes'):
        score += 0.5
    if term.get('related_terms'):
        score += 1.0
    
    return score


def _merge_term_fields(term1: Dict, term2: Dict) -> Dict:
    """Merge fields from two term entries."""
    merged = term1.copy()
    
    # Merge list fields
    for field in ['synonyms', 'abbreviations', 'related_terms', 'examples']:
        items1 = set(term1.get(field, []))
        items2 = set(term2.get(field, []))
        merged[field] = list(items1.union(items2))
    
    # Use non-empty definitions (prefer longer ones)
    def1 = term1.get('definition', '')
    def2 = term2.get('definition', '')
    if len(def2) > len(def1):
        merged['definition'] = def2
    
    # Merge usage notes
    notes1 = term1.get('usage_notes', '')
    notes2 = term2.get('usage_notes', '')
    if notes1 and notes2 and notes1 != notes2:
        merged['usage_notes'] = f"{notes1}; {notes2}"
    elif notes2 and not notes1:
        merged['usage_notes'] = notes2
    
    return merged


def _export_glossary_json(glossary: Dict) -> str:
    """Export glossary as JSON."""
    return json.dumps(glossary, indent=2, default=str)


def _export_glossary_csv(glossary: Dict) -> str:
    """Export glossary as CSV."""
    import csv
    import io
    
    output = io.StringIO()
    if glossary:
        # Get all possible field names
        all_fields = set()
        for entry in glossary.values():
            all_fields.update(entry.keys())
        
        fieldnames = ['term_id'] + sorted(all_fields)
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for term_id, entry in glossary.items():
            row = {'term_id': term_id}
            row.update(entry)
            # Convert lists to strings
            for key, value in row.items():
                if isinstance(value, list):
                    row[key] = '; '.join(map(str, value))
            writer.writerow(row)
    
    return output.getvalue()


def _export_glossary_html(glossary: Dict) -> str:
    """Export glossary as HTML."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Study Glossary</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .term { margin-bottom: 20px; padding: 10px; border-left: 3px solid #007cba; }
            .term-name { font-weight: bold; font-size: 1.2em; color: #007cba; }
            .definition { margin: 5px 0; }
            .synonyms { font-style: italic; color: #666; }
            .category { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <h1>Study Glossary</h1>
    """
    
    # Sort terms alphabetically
    sorted_terms = sorted(glossary.items(), key=lambda x: x[1].get('term', '').lower())
    
    for term_id, entry in sorted_terms:
        html += f"""
        <div class="term">
            <div class="term-name">{entry.get('term', '')}</div>
            <div class="definition">{entry.get('definition', '')}</div>
        """
        
        if entry.get('synonyms'):
            html += f"<div class='synonyms'>Synonyms: {', '.join(entry['synonyms'])}</div>"
        
        if entry.get('category'):
            html += f"<div><span class='category'>{entry['category']}</span></div>"
        
        if entry.get('examples'):
            html += "<div><strong>Examples:</strong><ul>"
            for example in entry['examples']:
                html += f"<li>{example}</li>"
            html += "</ul></div>"
        
        html += "</div>"
    
    html += """
    </body>
    </html>
    """
    
    return html


def _export_glossary_markdown(glossary: Dict) -> str:
    """Export glossary as Markdown."""
    markdown = "# Study Glossary\n\n"
    
    # Sort terms alphabetically
    sorted_terms = sorted(glossary.items(), key=lambda x: x[1].get('term', '').lower())
    
    for term_id, entry in sorted_terms:
        markdown += f"## {entry.get('term', '')}\n\n"
        markdown += f"{entry.get('definition', '')}\n\n"
        
        if entry.get('synonyms'):
            markdown += f"**Synonyms:** {', '.join(entry['synonyms'])}\n\n"
        
        if entry.get('category'):
            markdown += f"**Category:** {entry['category']}\n\n"
        
        if entry.get('examples'):
            markdown += "**Examples:**\n\n"
            for example in entry['examples']:
                markdown += f"- {example}\n"
            markdown += "\n"
        
        if entry.get('usage_notes'):
            markdown += f"**Usage Notes:** {entry['usage_notes']}\n\n"
        
        markdown += "---\n\n"
    
    return markdown


def _export_glossary_excel(glossary: Dict) -> str:
    """Export glossary as Excel (returns CSV for simplicity)."""
    return _export_glossary_csv(glossary)


def _generate_validation_recommendations(validation_results: Dict, score: float) -> List[str]:
    """Generate validation recommendations."""
    recommendations = []
    
    undefined_count = len(validation_results['undefined_terms_found'])
    consistency_count = len(validation_results['inconsistent_usage'])
    
    if score < 70:
        recommendations.append("Consider expanding glossary to cover more technical terms")
    
    if undefined_count > 10:
        recommendations.append(f"High number of undefined terms ({undefined_count}) - review and add important terms to glossary")
    
    if consistency_count > 5:
        recommendations.append(f"Multiple consistency issues found ({consistency_count}) - standardize term usage")
    
    if not recommendations:
        recommendations.append("Terminology validation passed - maintain current glossary standards")
    
    return recommendations


def _generate_search_summary(results: List[Dict], query: str) -> str:
    """Generate search summary."""
    if not results:
        return f"No terms found matching '{query}'"
    
    categories = set(r.get('category', 'unknown') for r in results)
    return f"Found {len(results)} terms matching '{query}' across {len(categories)} categories"


def _generate_merge_recommendations(conflicts: List[Dict]) -> List[str]:
    """Generate recommendations for merge conflicts."""
    recommendations = []
    
    if not conflicts:
        recommendations.append("Glossaries merged successfully without conflicts")
    else:
        recommendations.append(f"Resolved {len(conflicts)} merge conflicts")
        recommendations.append("Review merged terms for accuracy and completeness")
        recommendations.append("Consider establishing glossary management standards to prevent future conflicts")
    
    return recommendations


def _get_export_notes(format_type: str) -> List[str]:
    """Get export format notes."""
    notes = {
        'json': ["Machine-readable format suitable for data exchange"],
        'csv': ["Can be opened in Excel or other spreadsheet software"],
        'html': ["Web-friendly format with visual styling"],
        'markdown': ["Text format suitable for documentation systems"],
        'xlsx': ["Excel format for easy editing and sharing"]
    }
    return notes.get(format_type, [])