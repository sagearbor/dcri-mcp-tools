"""Tests for P-value Adjuster Tool"""
import pytest
from tools.pvalue_adjuster import run

def test_bonferroni_adjustment():
    """Test Bonferroni p-value adjustment."""
    result = run({
        'pvalues': [0.01, 0.04, 0.03, 0.25],
        'method': 'bonferroni',
        'alpha': 0.05
    })
    assert result['method'] == 'bonferroni'
    assert result['n_tests'] == 4
    assert 'n_significant' in result
    assert all(adj >= orig for adj, orig in 
              zip([r['adjusted_pvalue'] for r in result['results']], 
                  [r['original_pvalue'] for r in result['results']]))

def test_fdr_adjustment():
    """Test FDR adjustment."""
    result = run({
        'pvalues': [0.001, 0.008, 0.039, 0.041, 0.042],
        'method': 'fdr_bh',
        'alpha': 0.05
    })
    assert result['method'] == 'fdr_bh'
    assert 'results' in result

def test_empty_pvalues():
    """Test with empty p-values."""
    result = run({
        'pvalues': [],
        'method': 'bonferroni'
    })
    assert 'error' in result
