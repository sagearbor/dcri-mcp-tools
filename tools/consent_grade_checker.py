import re
from typing import Dict, Any, List
import math


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates reading grade level of informed consent documents using multiple readability formulas.
    
    Example:
        Input: Consent document text with target reading grade level
        Output: Grade level analysis with multiple readability scores and suggestions for improvement
    
    Parameters:
        text : str
            Consent document text content
        target_grade : int
            Target reading grade level (optional, default 8)
        include_recommendations : bool
            Include improvement suggestions (optional)
    """
    text = input_data.get('text', '')
    target_grade = input_data.get('target_grade', 8)
    include_recommendations = input_data.get('include_recommendations', True)
    
    if not text:
        return {
            'error': 'No text provided',
            'flesch_kincaid_grade': None,
            'flesch_reading_ease': None,
            'gunning_fog': None,
            'average_grade': None,
            'meets_target': False
        }
    
    # Calculate text statistics
    sentences = _count_sentences(text)
    words = _count_words(text)
    syllables = _count_syllables(text)
    complex_words = _count_complex_words(text)
    
    # Prevent division by zero
    if sentences == 0 or words == 0:
        return {
            'error': 'Text too short to analyze',
            'flesch_kincaid_grade': None,
            'flesch_reading_ease': None,
            'gunning_fog': None,
            'average_grade': None,
            'meets_target': False
        }
    
    # Calculate readability scores
    # Flesch-Kincaid Grade Level
    fk_grade = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    fk_grade = max(0, fk_grade)  # Ensure non-negative
    
    # Flesch Reading Ease
    fre_score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    
    # Gunning Fog Index
    fog_index = 0.4 * ((words / sentences) + 100 * (complex_words / words))
    
    # Calculate average grade level
    average_grade = (fk_grade + fog_index) / 2
    
    # Check if meets target
    meets_target = average_grade <= target_grade
    
    # Generate recommendations
    recommendations = []
    if include_recommendations:
        recommendations = _generate_recommendations(
            sentences, words, syllables, complex_words,
            average_grade, target_grade, text
        )
    
    # Interpret Flesch Reading Ease
    fre_interpretation = _interpret_fre(fre_score)
    
    return {
        'flesch_kincaid_grade': round(fk_grade, 1),
        'flesch_reading_ease': round(fre_score, 1),
        'flesch_reading_ease_interpretation': fre_interpretation,
        'gunning_fog': round(fog_index, 1),
        'average_grade': round(average_grade, 1),
        'target_grade': target_grade,
        'meets_target': meets_target,
        'recommendations': recommendations,
        'statistics': {
            'sentences': sentences,
            'words': words,
            'syllables': syllables,
            'complex_words': complex_words,
            'average_words_per_sentence': round(words / sentences, 1),
            'average_syllables_per_word': round(syllables / words, 2)
        }
    }


def _count_sentences(text: str) -> int:
    """Count sentences in text."""
    # Split on sentence endings
    sentences = re.split(r'[.!?]+', text)
    # Filter out empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    return len(sentences)


def _count_words(text: str) -> int:
    """Count words in text."""
    # Remove punctuation and split
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    return len(words)


def _count_syllables(text: str) -> int:
    """Count total syllables in text."""
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    total_syllables = 0
    
    for word in words:
        total_syllables += _count_syllables_in_word(word)
    
    return total_syllables


def _count_syllables_in_word(word: str) -> int:
    """Count syllables in a single word."""
    word = word.lower()
    vowels = 'aeiouy'
    syllables = 0
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllables += 1
        previous_was_vowel = is_vowel
    
    # Adjust for silent e
    if word.endswith('e'):
        syllables -= 1
    
    # Ensure at least one syllable
    if syllables == 0:
        syllables = 1
    
    return syllables


def _count_complex_words(text: str) -> int:
    """Count words with 3 or more syllables (complex words)."""
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    complex_count = 0
    
    for word in words:
        if _count_syllables_in_word(word) >= 3:
            # Don't count proper nouns or compound words
            if not word[0].isupper() and '-' not in word:
                complex_count += 1
    
    return complex_count


def _generate_recommendations(sentences: int, words: int, syllables: int,
                             complex_words: int, average_grade: float,
                             target_grade: int, text: str) -> List[str]:
    """Generate specific recommendations to improve readability."""
    recommendations = []
    
    avg_words_per_sentence = words / sentences
    avg_syllables_per_word = syllables / words
    
    if average_grade > target_grade:
        recommendations.append(f"Current grade level ({average_grade:.1f}) exceeds target ({target_grade})")
        
        if avg_words_per_sentence > 20:
            recommendations.append(
                f"Reduce sentence length (current average: {avg_words_per_sentence:.1f} words, "
                f"recommended: 15-20 words)"
            )
        
        if avg_syllables_per_word > 1.5:
            recommendations.append(
                "Use simpler words with fewer syllables"
            )
        
        if complex_words > words * 0.1:
            recommendations.append(
                f"Reduce complex words (3+ syllables). Currently {complex_words} complex words "
                f"({(complex_words/words*100):.1f}% of text)"
            )
        
        # Check for medical jargon
        medical_terms = re.findall(
            r'\b(?:randomiz|placebo|protocol|intervention|adverse|clinical|'
            r'investigational|pharmacokinetic|contraindication|'
            r'immunogenicity|pharmacodynamic)\w*\b',
            text.lower()
        )
        if medical_terms:
            recommendations.append(
                f"Consider simplifying medical terminology (found {len(set(medical_terms))} technical terms)"
            )
        
        # Check for passive voice indicators
        passive_indicators = re.findall(
            r'\b(?:was|were|been|being|is|are|be)\s+\w+ed\b',
            text.lower()
        )
        if passive_indicators:
            recommendations.append(
                "Use active voice instead of passive voice for clearer communication"
            )
    else:
        recommendations.append(f"✓ Document meets target grade level ({target_grade})")
    
    # Add specific tips
    if not recommendations or average_grade > target_grade:
        recommendations.extend([
            "Consider using bulleted lists for complex information",
            "Add section headings to break up long text blocks",
            "Include definitions for necessary medical terms",
            "Use examples to explain complex concepts"
        ])
    
    return recommendations


def _interpret_fre(score: float) -> str:
    """Interpret Flesch Reading Ease score."""
    if score >= 90:
        return "Very Easy (5th grade)"
    elif score >= 80:
        return "Easy (6th grade)"
    elif score >= 70:
        return "Fairly Easy (7th grade)"
    elif score >= 60:
        return "Standard (8th-9th grade)"
    elif score >= 50:
        return "Fairly Difficult (10th-12th grade)"
    elif score >= 30:
        return "Difficult (College)"
    else:
        return "Very Difficult (College graduate)"