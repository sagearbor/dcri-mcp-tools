"""
Translation Validator Tool for Clinical Studies
Validates translation consistency across documents and languages
"""

import re
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
import json


def run(input_data: Dict) -> Dict:
    """
    Validate translation consistency across documents and languages.
    
    Args:
        input_data: Dictionary containing:
            - source_text: Original text (string or dict with sections)
            - translations: Dict of {language_code: translated_text}
            - validation_type: 'terminology', 'structure', 'completeness', 'all'
            - terminology_glossary: Dict of {term: {lang: translation}}
            - check_formatting: Whether to validate formatting consistency
            - medical_terms_only: Focus only on medical/clinical terms
            - severity_threshold: 'low', 'medium', 'high' for reporting
    
    Returns:
        Dictionary with validation results and issues found
    """
    try:
        source_text = input_data.get('source_text', '')
        translations = input_data.get('translations', {})
        validation_type = input_data.get('validation_type', 'all')
        terminology_glossary = input_data.get('terminology_glossary', {})
        check_formatting = input_data.get('check_formatting', True)
        medical_terms_only = input_data.get('medical_terms_only', False)
        severity_threshold = input_data.get('severity_threshold', 'medium')
        
        if not source_text:
            return {
                'success': False,
                'error': 'source_text is required'
            }
        
        if not translations:
            return {
                'success': False,
                'error': 'translations dictionary is required'
            }
        
        # Initialize validation results
        validation_results = {
            'overall_score': 0.0,
            'issues_found': [],
            'language_scores': {},
            'recommendations': [],
            'statistics': {}
        }
        
        # Perform different types of validation
        if validation_type in ['terminology', 'all']:
            terminology_issues = _validate_terminology(
                source_text, translations, terminology_glossary, medical_terms_only
            )
            validation_results['issues_found'].extend(terminology_issues)
        
        if validation_type in ['structure', 'all']:
            structure_issues = _validate_structure(source_text, translations)
            validation_results['issues_found'].extend(structure_issues)
        
        if validation_type in ['completeness', 'all']:
            completeness_issues = _validate_completeness(source_text, translations)
            validation_results['issues_found'].extend(completeness_issues)
        
        if check_formatting:
            formatting_issues = _validate_formatting(source_text, translations)
            validation_results['issues_found'].extend(formatting_issues)
        
        # Calculate scores and filter by severity
        validation_results['language_scores'] = _calculate_language_scores(
            translations, validation_results['issues_found']
        )
        
        validation_results['overall_score'] = _calculate_overall_score(
            validation_results['language_scores']
        )
        
        # Filter issues by severity threshold
        validation_results['issues_found'] = _filter_by_severity(
            validation_results['issues_found'], severity_threshold
        )
        
        # Generate recommendations
        validation_results['recommendations'] = _generate_recommendations(
            validation_results['issues_found']
        )
        
        # Calculate statistics
        validation_results['statistics'] = _calculate_statistics(
            source_text, translations, validation_results['issues_found']
        )
        
        return {
            'success': True,
            'validation_results': validation_results,
            'summary': {
                'total_languages': len(translations),
                'total_issues': len(validation_results['issues_found']),
                'overall_quality': _get_quality_rating(validation_results['overall_score']),
                'highest_scoring_language': max(validation_results['language_scores'].items(), 
                                               key=lambda x: x[1], default=('none', 0))[0],
                'validation_type': validation_type,
                'timestamp': _get_timestamp()
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error validating translations: {str(e)}'
        }


def _validate_terminology(source_text: str, translations: Dict, 
                         glossary: Dict, medical_only: bool) -> List[Dict]:
    """Validate terminology consistency."""
    issues = []
    
    # Extract key terms from source
    source_terms = _extract_key_terms(source_text, medical_only)
    
    for lang_code, translated_text in translations.items():
        translated_terms = _extract_key_terms(translated_text, medical_only)
        
        # Check for missing terms
        missing_terms = set(source_terms) - set(translated_terms)
        for term in missing_terms:
            issues.append({
                'type': 'missing_term',
                'severity': 'high',
                'language': lang_code,
                'source_term': term,
                'description': f'Term "{term}" not found in {lang_code} translation',
                'suggestion': glossary.get(term, {}).get(lang_code, 'Check glossary')
            })
        
        # Check glossary consistency
        for term in source_terms:
            if term in glossary and lang_code in glossary[term]:
                expected_translation = glossary[term][lang_code]
                if expected_translation.lower() not in translated_text.lower():
                    issues.append({
                        'type': 'glossary_inconsistency',
                        'severity': 'medium',
                        'language': lang_code,
                        'source_term': term,
                        'expected_translation': expected_translation,
                        'description': f'Term "{term}" not translated as expected "{expected_translation}"',
                        'suggestion': f'Use standardized translation: {expected_translation}'
                    })
    
    return issues


def _validate_structure(source_text: str, translations: Dict) -> List[Dict]:
    """Validate structural consistency."""
    issues = []
    
    # Analyze source structure
    source_structure = _analyze_text_structure(source_text)
    
    for lang_code, translated_text in translations.items():
        trans_structure = _analyze_text_structure(translated_text)
        
        # Check paragraph count
        if source_structure['paragraphs'] != trans_structure['paragraphs']:
            issues.append({
                'type': 'paragraph_mismatch',
                'severity': 'medium',
                'language': lang_code,
                'expected': source_structure['paragraphs'],
                'actual': trans_structure['paragraphs'],
                'description': f'Paragraph count mismatch in {lang_code}',
                'suggestion': 'Ensure same paragraph structure as source'
            })
        
        # Check bullet points
        if source_structure['bullet_points'] != trans_structure['bullet_points']:
            issues.append({
                'type': 'bullet_point_mismatch',
                'severity': 'medium',
                'language': lang_code,
                'expected': source_structure['bullet_points'],
                'actual': trans_structure['bullet_points'],
                'description': f'Bullet point count mismatch in {lang_code}',
                'suggestion': 'Maintain same number of bullet points'
            })
        
        # Check numbered lists
        if source_structure['numbered_lists'] != trans_structure['numbered_lists']:
            issues.append({
                'type': 'numbered_list_mismatch',
                'severity': 'medium',
                'language': lang_code,
                'expected': source_structure['numbered_lists'],
                'actual': trans_structure['numbered_lists'],
                'description': f'Numbered list count mismatch in {lang_code}',
                'suggestion': 'Maintain same numbered list structure'
            })
    
    return issues


def _validate_completeness(source_text: str, translations: Dict) -> List[Dict]:
    """Validate translation completeness."""
    issues = []
    
    source_length = len(source_text.strip())
    source_words = len(source_text.split())
    
    for lang_code, translated_text in translations.items():
        trans_length = len(translated_text.strip())
        trans_words = len(translated_text.split())
        
        # Check for suspiciously short translations
        length_ratio = trans_length / source_length if source_length > 0 else 0
        word_ratio = trans_words / source_words if source_words > 0 else 0
        
        if length_ratio < 0.5:  # Translation is less than half the source length
            issues.append({
                'type': 'incomplete_translation',
                'severity': 'high',
                'language': lang_code,
                'length_ratio': round(length_ratio, 2),
                'description': f'Translation appears incomplete (only {length_ratio:.1%} of source length)',
                'suggestion': 'Review translation for missing content'
            })
        
        if word_ratio < 0.3:  # Very few words compared to source
            issues.append({
                'type': 'insufficient_content',
                'severity': 'high',
                'language': lang_code,
                'word_ratio': round(word_ratio, 2),
                'description': f'Translation has very few words ({word_ratio:.1%} of source)',
                'suggestion': 'Ensure all content is translated'
            })
        
        # Check for untranslated placeholder text
        placeholders = re.findall(r'\[.*?\]', translated_text)
        if placeholders:
            issues.append({
                'type': 'untranslated_placeholders',
                'severity': 'medium',
                'language': lang_code,
                'placeholders': placeholders,
                'description': f'Untranslated placeholders found: {", ".join(placeholders)}',
                'suggestion': 'Translate or localize placeholder content'
            })
    
    return issues


def _validate_formatting(source_text: str, translations: Dict) -> List[Dict]:
    """Validate formatting consistency."""
    issues = []
    
    # Extract formatting elements from source
    source_formatting = _extract_formatting_elements(source_text)
    
    for lang_code, translated_text in translations.items():
        trans_formatting = _extract_formatting_elements(translated_text)
        
        # Check markdown/HTML tags
        if source_formatting['html_tags'] != trans_formatting['html_tags']:
            issues.append({
                'type': 'html_tag_mismatch',
                'severity': 'high',
                'language': lang_code,
                'description': 'HTML/markup tags don\'t match source formatting',
                'suggestion': 'Ensure all formatting tags are preserved'
            })
        
        # Check special characters
        source_chars = set(source_formatting['special_chars'])
        trans_chars = set(trans_formatting['special_chars'])
        missing_chars = source_chars - trans_chars
        
        if missing_chars:
            issues.append({
                'type': 'missing_special_chars',
                'severity': 'medium',
                'language': lang_code,
                'missing_chars': list(missing_chars),
                'description': f'Missing special characters: {", ".join(missing_chars)}',
                'suggestion': 'Include all special formatting characters'
            })
    
    return issues


def _extract_key_terms(text: str, medical_only: bool) -> List[str]:
    """Extract key terms from text."""
    # Medical/clinical term patterns
    medical_patterns = [
        r'\b(?:study|trial|research|clinical|patient|subject|participant)\w*\b',
        r'\b(?:adverse|event|serious|safety|efficacy|endpoint)\w*\b',
        r'\b(?:randomiz|blind|placebo|control|treatment|intervention)\w*\b',
        r'\b(?:consent|IRB|ethics|protocol|amendment)\w*\b',
        r'\b(?:dose|dosage|medication|drug|therapy|therapeutic)\w*\b'
    ]
    
    if medical_only:
        patterns = medical_patterns
    else:
        # Include general important terms
        patterns = medical_patterns + [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Proper nouns
            r'\b\w{6,}\b'  # Long words (likely important)
        ]
    
    terms = []
    for pattern in patterns:
        terms.extend(re.findall(pattern, text, re.IGNORECASE))
    
    return list(set([term.lower() for term in terms]))


def _analyze_text_structure(text: str) -> Dict:
    """Analyze text structure."""
    return {
        'paragraphs': len([p for p in text.split('\n\n') if p.strip()]),
        'bullet_points': len(re.findall(r'^\s*[•·*-]\s', text, re.MULTILINE)),
        'numbered_lists': len(re.findall(r'^\s*\d+\.\s', text, re.MULTILINE)),
        'headers': len(re.findall(r'^#{1,6}\s', text, re.MULTILINE)),
        'sentences': len(re.findall(r'[.!?]+', text))
    }


def _extract_formatting_elements(text: str) -> Dict:
    """Extract formatting elements."""
    return {
        'html_tags': re.findall(r'<[^>]+>', text),
        'markdown_bold': re.findall(r'\*\*[^*]+\*\*', text),
        'markdown_italic': re.findall(r'\*[^*]+\*', text),
        'special_chars': re.findall(r'[^\w\s]', text),
        'urls': re.findall(r'https?://[^\s]+', text)
    }


def _calculate_language_scores(translations: Dict, issues: List[Dict]) -> Dict:
    """Calculate quality scores for each language."""
    scores = {}
    
    for lang_code in translations.keys():
        lang_issues = [issue for issue in issues if issue.get('language') == lang_code]
        
        # Start with perfect score
        score = 100.0
        
        # Deduct points based on issues
        for issue in lang_issues:
            severity = issue.get('severity', 'medium')
            if severity == 'high':
                score -= 15
            elif severity == 'medium':
                score -= 8
            else:  # low
                score -= 3
        
        scores[lang_code] = max(0, score)
    
    return scores


def _calculate_overall_score(language_scores: Dict) -> float:
    """Calculate overall quality score."""
    if not language_scores:
        return 0.0
    return sum(language_scores.values()) / len(language_scores)


def _filter_by_severity(issues: List[Dict], threshold: str) -> List[Dict]:
    """Filter issues by severity threshold."""
    severity_levels = {'low': 1, 'medium': 2, 'high': 3}
    threshold_level = severity_levels.get(threshold, 2)
    
    return [issue for issue in issues 
            if severity_levels.get(issue.get('severity', 'medium'), 2) >= threshold_level]


def _generate_recommendations(issues: List[Dict]) -> List[str]:
    """Generate recommendations based on issues found."""
    recommendations = []
    
    issue_types = set(issue.get('type') for issue in issues)
    
    if 'missing_term' in issue_types:
        recommendations.append("Review terminology glossary and ensure all key terms are translated")
    
    if 'incomplete_translation' in issue_types:
        recommendations.append("Check for missing content in translations")
    
    if 'paragraph_mismatch' in issue_types:
        recommendations.append("Maintain consistent document structure across all languages")
    
    if 'html_tag_mismatch' in issue_types:
        recommendations.append("Preserve all formatting tags during translation")
    
    if not recommendations:
        recommendations.append("Translation quality is good - continue current practices")
    
    return recommendations


def _calculate_statistics(source_text: str, translations: Dict, issues: List[Dict]) -> Dict:
    """Calculate validation statistics."""
    return {
        'source_word_count': len(source_text.split()),
        'translation_word_counts': {lang: len(text.split()) for lang, text in translations.items()},
        'total_issues_by_severity': {
            'high': len([i for i in issues if i.get('severity') == 'high']),
            'medium': len([i for i in issues if i.get('severity') == 'medium']),
            'low': len([i for i in issues if i.get('severity') == 'low'])
        },
        'issues_by_type': {}
    }


def _get_quality_rating(score: float) -> str:
    """Convert numeric score to quality rating."""
    if score >= 90:
        return 'Excellent'
    elif score >= 80:
        return 'Good'
    elif score >= 70:
        return 'Fair'
    elif score >= 60:
        return 'Poor'
    else:
        return 'Critical'


def _get_timestamp() -> str:
    """Get current timestamp."""
    from datetime import datetime
    return datetime.now().isoformat()