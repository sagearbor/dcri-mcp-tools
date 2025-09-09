"""
P-value Adjuster

Performs multiplicity adjustments for multiple comparisons.
"""

from typing import Dict, Any, List
import math


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adjust p-values for multiple comparisons.
    
    Args:
        input_data: Dictionary containing:
            - pvalues: list of p-values
            - method: str ('bonferroni', 'holm', 'hochberg', 'fdr_bh', 'fdr_by')
            - alpha: float (significance level, default 0.05)
            - labels: list of test labels (optional)
    
    Returns:
        Dictionary with adjusted p-values and conclusions
    """
    
    pvalues = input_data.get('pvalues', [])
    method = input_data.get('method', 'bonferroni')
    alpha = input_data.get('alpha', 0.05)
    labels = input_data.get('labels', [f'Test {i+1}' for i in range(len(pvalues))])
    
    if not pvalues:
        return {'error': 'No p-values provided'}
    
    # Perform adjustment
    if method == 'bonferroni':
        adjusted = _bonferroni_adjustment(pvalues, alpha)
    elif method == 'holm':
        adjusted = _holm_adjustment(pvalues, alpha)
    elif method == 'hochberg':
        adjusted = _hochberg_adjustment(pvalues, alpha)
    elif method == 'fdr_bh':
        adjusted = _fdr_bh_adjustment(pvalues, alpha)
    elif method == 'fdr_by':
        adjusted = _fdr_by_adjustment(pvalues, alpha)
    else:
        return {'error': f'Unknown method: {method}'}
    
    # Generate results
    results = []
    for i, (label, orig_p, adj_p, reject) in enumerate(zip(
        labels, pvalues, adjusted['adjusted_pvalues'], adjusted['reject']
    )):
        results.append({
            'test': label,
            'original_pvalue': round(orig_p, 6),
            'adjusted_pvalue': round(adj_p, 6),
            'significant': reject,
            'conclusion': 'Reject null' if reject else 'Fail to reject null'
        })
    
    # Summary statistics
    n_significant = sum(adjusted['reject'])
    
    return {
        'method': method,
        'alpha': alpha,
        'n_tests': len(pvalues),
        'n_significant': n_significant,
        'results': results,
        'summary': {
            'min_pvalue': min(pvalues),
            'max_pvalue': max(pvalues),
            'min_adjusted': min(adjusted['adjusted_pvalues']),
            'max_adjusted': min(1.0, max(adjusted['adjusted_pvalues']))
        },
        'interpretation': _generate_interpretation(method, n_significant, len(pvalues))
    }


def _bonferroni_adjustment(pvalues: List[float], alpha: float) -> Dict:
    """Bonferroni correction."""
    n = len(pvalues)
    adjusted = [min(1.0, p * n) for p in pvalues]
    reject = [p <= alpha/n for p in pvalues]
    
    return {
        'adjusted_pvalues': adjusted,
        'reject': reject,
        'adjusted_alpha': alpha/n
    }


def _holm_adjustment(pvalues: List[float], alpha: float) -> Dict:
    """Holm-Bonferroni step-down procedure."""
    n = len(pvalues)
    sorted_indices = sorted(range(n), key=lambda i: pvalues[i])
    sorted_pvalues = [pvalues[i] for i in sorted_indices]
    
    adjusted = [0] * n
    reject = [False] * n
    
    for i, idx in enumerate(sorted_indices):
        adj_p = min(1.0, sorted_pvalues[i] * (n - i))
        adjusted[idx] = adj_p
        
        if i == 0:
            reject[idx] = sorted_pvalues[i] <= alpha/(n-i)
        else:
            # Step-down: if previous was rejected, test this one
            prev_idx = sorted_indices[i-1]
            if reject[prev_idx]:
                reject[idx] = sorted_pvalues[i] <= alpha/(n-i)
    
    return {
        'adjusted_pvalues': adjusted,
        'reject': reject
    }


def _hochberg_adjustment(pvalues: List[float], alpha: float) -> Dict:
    """Hochberg step-up procedure."""
    n = len(pvalues)
    sorted_indices = sorted(range(n), key=lambda i: pvalues[i], reverse=True)
    sorted_pvalues = [pvalues[i] for i in sorted_indices]
    
    adjusted = [0] * n
    reject = [False] * n
    
    for i, idx in enumerate(sorted_indices):
        adj_p = min(1.0, sorted_pvalues[i] * (i + 1))
        adjusted[idx] = adj_p
        
        if sorted_pvalues[i] <= alpha/(i+1):
            # Step-up: reject this and all smaller p-values
            for j in range(i, n):
                reject[sorted_indices[j]] = True
            break
    
    return {
        'adjusted_pvalues': adjusted,
        'reject': reject
    }


def _fdr_bh_adjustment(pvalues: List[float], alpha: float) -> Dict:
    """Benjamini-Hochberg FDR procedure."""
    n = len(pvalues)
    sorted_indices = sorted(range(n), key=lambda i: pvalues[i])
    sorted_pvalues = [pvalues[i] for i in sorted_indices]
    
    adjusted = [0] * n
    reject = [False] * n
    
    # Find largest i such that P(i) <= (i/n) * alpha
    for i in range(n-1, -1, -1):
        if sorted_pvalues[i] <= (i+1)/n * alpha:
            # Reject H(1)...H(i)
            for j in range(i+1):
                reject[sorted_indices[j]] = True
            break
    
    # Calculate adjusted p-values
    for i, idx in enumerate(sorted_indices):
        adj_p = min(1.0, sorted_pvalues[i] * n / (i+1))
        adjusted[idx] = adj_p
    
    return {
        'adjusted_pvalues': adjusted,
        'reject': reject
    }


def _fdr_by_adjustment(pvalues: List[float], alpha: float) -> Dict:
    """Benjamini-Yekutieli FDR procedure."""
    n = len(pvalues)
    c_n = sum(1/i for i in range(1, n+1))  # Harmonic series sum
    
    sorted_indices = sorted(range(n), key=lambda i: pvalues[i])
    sorted_pvalues = [pvalues[i] for i in sorted_indices]
    
    adjusted = [0] * n
    reject = [False] * n
    
    # Find largest i such that P(i) <= (i/(n*c_n)) * alpha
    for i in range(n-1, -1, -1):
        if sorted_pvalues[i] <= (i+1)/(n*c_n) * alpha:
            for j in range(i+1):
                reject[sorted_indices[j]] = True
            break
    
    # Calculate adjusted p-values
    for i, idx in enumerate(sorted_indices):
        adj_p = min(1.0, sorted_pvalues[i] * n * c_n / (i+1))
        adjusted[idx] = adj_p
    
    return {
        'adjusted_pvalues': adjusted,
        'reject': reject
    }


def _generate_interpretation(method: str, n_significant: int, n_tests: int) -> str:
    """Generate interpretation of results."""
    
    if n_significant == 0:
        return f"No significant results after {method} adjustment for {n_tests} tests."
    
    interpretations = {
        'bonferroni': f"Using Bonferroni correction (most conservative), {n_significant}/{n_tests} tests remain significant.",
        'holm': f"Using Holm-Bonferroni (step-down), {n_significant}/{n_tests} tests remain significant.",
        'hochberg': f"Using Hochberg (step-up), {n_significant}/{n_tests} tests remain significant.",
        'fdr_bh': f"Using Benjamini-Hochberg FDR control, {n_significant}/{n_tests} tests remain significant.",
        'fdr_by': f"Using Benjamini-Yekutieli FDR control, {n_significant}/{n_tests} tests remain significant."
    }
    
    return interpretations.get(method, f"{n_significant}/{n_tests} tests significant after adjustment.")
