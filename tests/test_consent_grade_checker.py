import pytest
from tools.consent_grade_checker import run


def test_consent_grade_checker_simple_text():
    """Test grade checking with simple text."""
    input_data = {
        'text': "This is a test. The cat sat on the mat. Dogs like to run and play.",
        'target_grade': 8
    }
    
    result = run(input_data)
    
    assert 'flesch_kincaid_grade' in result
    assert 'flesch_reading_ease' in result
    assert 'gunning_fog' in result
    assert 'average_grade' in result
    assert 'meets_target' in result
    assert result['flesch_kincaid_grade'] < 8  # Simple text should have low grade


def test_consent_grade_checker_complex_text():
    """Test grade checking with complex medical text."""
    input_data = {
        'text': """
        The investigational pharmacokinetic parameters will be evaluated through 
        comprehensive bioanalytical methodologies. Participants experiencing 
        contraindications or hypersensitivity reactions will be immediately 
        discontinued from the investigational intervention protocol.
        """,
        'target_grade': 8
    }
    
    result = run(input_data)
    
    assert result['flesch_kincaid_grade'] > 12  # Complex text should have high grade
    assert result['meets_target'] is False
    assert len(result['recommendations']) > 0
    assert 'medical terminology' in str(result['recommendations']).lower()


def test_consent_grade_checker_empty_text():
    """Test with empty text."""
    input_data = {
        'text': '',
        'target_grade': 8
    }
    
    result = run(input_data)
    
    assert result['error'] == 'No text provided'
    assert result['meets_target'] is False


def test_consent_grade_checker_statistics():
    """Test that statistics are calculated correctly."""
    input_data = {
        'text': "This is a simple sentence. It has ten words total here.",
        'target_grade': 8
    }
    
    result = run(input_data)
    
    assert 'statistics' in result
    stats = result['statistics']
    assert stats['sentences'] == 2
    assert stats['words'] == 10
    assert 'average_words_per_sentence' in stats
    assert 'average_syllables_per_word' in stats


def test_consent_grade_checker_recommendations():
    """Test recommendation generation."""
    input_data = {
        'text': """
        The pharmaceutical compound demonstrated statistically significant 
        pharmacodynamic properties in the randomized placebo-controlled 
        interventional investigation, necessitating comprehensive evaluation 
        of immunogenicity parameters and contraindication profiles throughout 
        the clinical development program.
        """,
        'target_grade': 8,
        'include_recommendations': True
    }
    
    result = run(input_data)
    
    assert len(result['recommendations']) > 0
    assert any('sentence length' in r.lower() or 'complex words' in r.lower() 
              for r in result['recommendations'])


def test_consent_grade_checker_meets_target():
    """Test target grade level checking."""
    # Simple text that should meet 8th grade target
    input_data = {
        'text': """
        We want to learn if this new drug helps people feel better.
        You will take one pill each day for four weeks.
        We will check how you feel every week.
        The drug might cause mild side effects like headache.
        You can stop taking the drug at any time.
        """,
        'target_grade': 8
    }
    
    result = run(input_data)
    
    assert result['average_grade'] < 10  # Should be reasonably simple
    assert 'flesch_reading_ease_interpretation' in result


def test_consent_grade_checker_no_recommendations():
    """Test with recommendations disabled."""
    input_data = {
        'text': "This is complex terminology with pharmaceutical interventions.",
        'target_grade': 8,
        'include_recommendations': False
    }
    
    result = run(input_data)
    
    assert result['recommendations'] == []


def test_consent_grade_checker_all_readability_scores():
    """Test that all readability scores are calculated."""
    input_data = {
        'text': """
        This clinical trial will test a new medication.
        Participants will receive either the drug or a placebo.
        Side effects may include nausea and fatigue.
        """,
        'target_grade': 8
    }
    
    result = run(input_data)
    
    # Check all scores are present and numeric
    assert isinstance(result['flesch_kincaid_grade'], (int, float))
    assert isinstance(result['flesch_reading_ease'], (int, float))
    assert isinstance(result['gunning_fog'], (int, float))
    assert isinstance(result['average_grade'], (int, float))
    
    # Check scores are in reasonable ranges
    assert 0 <= result['flesch_kincaid_grade'] <= 20
    assert 0 <= result['flesch_reading_ease'] <= 100
    assert 0 <= result['gunning_fog'] <= 20