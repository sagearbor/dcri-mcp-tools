"""
Reference Manager Tool for Clinical Studies
Manages study references, citations, and bibliographies
"""

import re
from typing import Dict, List, Optional
import json
from datetime import datetime


def run(input_data: Dict) -> Dict:
    """
    Manage study references and citations.
    
    Args:
        input_data: Dictionary containing:
            - action: 'add', 'format', 'validate', 'search', 'export', 'import'
            - references: List of reference objects or single reference
            - citation_style: 'apa', 'vancouver', 'chicago', 'mla', 'nejm'
            - search_query: Text to search for citations
            - format_options: Dict with formatting preferences
            - validation_rules: Custom validation rules
            - export_format: 'bibtex', 'endnote', 'json', 'csv'
    
    Returns:
        Dictionary with reference management results
    """
    try:
        action = input_data.get('action', '').lower()
        references = input_data.get('references', [])
        citation_style = input_data.get('citation_style', 'apa')
        search_query = input_data.get('search_query', '')
        format_options = input_data.get('format_options', {})
        validation_rules = input_data.get('validation_rules', {})
        export_format = input_data.get('export_format', 'json')
        
        if not action:
            return {
                'success': False,
                'error': 'action is required',
                'valid_actions': ['add', 'format', 'validate', 'search', 'export', 'import']
            }
        
        # Handle single reference vs list
        if isinstance(references, dict):
            references = [references]
        
        result = {'success': True, 'action': action}
        
        if action == 'add':
            result.update(_add_references(references))
        elif action == 'format':
            result.update(_format_references(references, citation_style, format_options))
        elif action == 'validate':
            result.update(_validate_references(references, validation_rules))
        elif action == 'search':
            result.update(_search_references(references, search_query))
        elif action == 'export':
            result.update(_export_references(references, export_format))
        elif action == 'import':
            result.update(_import_references(input_data.get('import_data', '')))
        else:
            return {
                'success': False,
                'error': f'Unknown action: {action}',
                'valid_actions': ['add', 'format', 'validate', 'search', 'export', 'import']
            }
        
        # Add metadata
        result['metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'total_references': len(references),
            'citation_style': citation_style if action in ['format', 'export'] else None
        }
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error in reference management: {str(e)}'
        }


def _add_references(references: List[Dict]) -> Dict:
    """Add new references to the collection."""
    added_refs = []
    errors = []
    
    for i, ref in enumerate(references):
        try:
            # Validate required fields
            ref_id = ref.get('id') or f'ref_{len(added_refs) + 1}'
            title = ref.get('title', '')
            
            if not title:
                errors.append(f'Reference {i+1}: title is required')
                continue
            
            # Standardize reference format
            standardized_ref = _standardize_reference(ref, ref_id)
            added_refs.append(standardized_ref)
            
        except Exception as e:
            errors.append(f'Reference {i+1}: {str(e)}')
    
    return {
        'added_references': added_refs,
        'added_count': len(added_refs),
        'errors': errors,
        'summary': f'Successfully added {len(added_refs)} references with {len(errors)} errors'
    }


def _format_references(references: List[Dict], style: str, options: Dict) -> Dict:
    """Format references in specified citation style."""
    formatted_refs = []
    bibliography = []
    errors = []
    
    for i, ref in enumerate(references):
        try:
            # Format in-text citation
            in_text = _format_in_text_citation(ref, style, options)
            
            # Format bibliography entry
            bib_entry = _format_bibliography_entry(ref, style, options)
            
            formatted_refs.append({
                'id': ref.get('id', f'ref_{i+1}'),
                'in_text_citation': in_text,
                'bibliography_entry': bib_entry,
                'original_reference': ref
            })
            
            bibliography.append(bib_entry)
            
        except Exception as e:
            errors.append(f'Reference {i+1}: {str(e)}')
    
    # Sort bibliography if requested
    if options.get('sort_bibliography', True):
        bibliography.sort()
    
    return {
        'formatted_references': formatted_refs,
        'bibliography': bibliography,
        'citation_style': style,
        'errors': errors,
        'formatting_notes': _get_formatting_notes(style)
    }


def _validate_references(references: List[Dict], custom_rules: Dict) -> Dict:
    """Validate references for completeness and consistency."""
    validation_results = []
    overall_score = 0
    total_checks = 0
    
    for i, ref in enumerate(references):
        ref_validation = {
            'reference_id': ref.get('id', f'ref_{i+1}'),
            'issues': [],
            'warnings': [],
            'score': 0,
            'max_score': 0
        }
        
        # Required field validation
        required_fields = _get_required_fields(ref.get('type', 'article'))
        for field in required_fields:
            ref_validation['max_score'] += 1
            total_checks += 1
            if field in ref and ref[field]:
                ref_validation['score'] += 1
            else:
                ref_validation['issues'].append(f'Missing required field: {field}')
        
        # Format validation
        format_checks = _validate_reference_formats(ref)
        ref_validation['issues'].extend(format_checks['errors'])
        ref_validation['warnings'].extend(format_checks['warnings'])
        ref_validation['score'] += format_checks['score']
        ref_validation['max_score'] += format_checks['max_score']
        total_checks += format_checks['max_score']
        
        # Custom rule validation
        if custom_rules:
            custom_checks = _apply_custom_validation_rules(ref, custom_rules)
            ref_validation['issues'].extend(custom_checks['errors'])
            ref_validation['warnings'].extend(custom_checks['warnings'])
        
        # Calculate percentage score
        ref_validation['percentage_score'] = (
            (ref_validation['score'] / ref_validation['max_score'] * 100) 
            if ref_validation['max_score'] > 0 else 0
        )
        
        validation_results.append(ref_validation)
        overall_score += ref_validation['score']
    
    # Calculate overall statistics
    total_issues = sum(len(r['issues']) for r in validation_results)
    total_warnings = sum(len(r['warnings']) for r in validation_results)
    
    return {
        'validation_results': validation_results,
        'summary': {
            'total_references': len(references),
            'overall_score_percentage': (overall_score / total_checks * 100) if total_checks > 0 else 0,
            'total_issues': total_issues,
            'total_warnings': total_warnings,
            'quality_rating': _get_quality_rating(overall_score / total_checks * 100 if total_checks > 0 else 0)
        },
        'recommendations': _generate_validation_recommendations(validation_results)
    }


def _search_references(references: List[Dict], query: str) -> Dict:
    """Search through references."""
    if not query:
        return {
            'search_results': references,
            'total_results': len(references),
            'query': 'all'
        }
    
    query_lower = query.lower()
    search_results = []
    
    for ref in references:
        # Search in multiple fields
        searchable_text = ' '.join([
            ref.get('title', ''),
            ' '.join(ref.get('authors', [])),
            ref.get('journal', ''),
            ref.get('abstract', ''),
            ' '.join(ref.get('keywords', []))
        ]).lower()
        
        if query_lower in searchable_text:
            # Calculate relevance score
            relevance_score = _calculate_relevance_score(ref, query_lower)
            search_result = ref.copy()
            search_result['relevance_score'] = relevance_score
            search_results.append(search_result)
    
    # Sort by relevance
    search_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return {
        'search_results': search_results,
        'total_results': len(search_results),
        'query': query,
        'search_summary': _generate_search_summary(search_results, query)
    }


def _export_references(references: List[Dict], format_type: str) -> Dict:
    """Export references in specified format."""
    export_functions = {
        'bibtex': _export_bibtex,
        'endnote': _export_endnote,
        'json': _export_json,
        'csv': _export_csv,
        'ris': _export_ris
    }
    
    if format_type not in export_functions:
        return {
            'error': f'Unsupported export format: {format_type}',
            'supported_formats': list(export_functions.keys())
        }
    
    try:
        exported_data = export_functions[format_type](references)
        return {
            'exported_data': exported_data,
            'format': format_type,
            'reference_count': len(references),
            'export_notes': _get_export_notes(format_type)
        }
    except Exception as e:
        return {
            'error': f'Export failed: {str(e)}',
            'format': format_type
        }


def _import_references(import_data: str) -> Dict:
    """Import references from various formats."""
    if not import_data:
        return {'error': 'import_data is required'}
    
    # Try to detect format and parse
    detected_format = _detect_import_format(import_data)
    
    parse_functions = {
        'bibtex': _parse_bibtex,
        'json': _parse_json,
        'csv': _parse_csv,
        'ris': _parse_ris
    }
    
    if detected_format in parse_functions:
        try:
            imported_refs = parse_functions[detected_format](import_data)
            return {
                'imported_references': imported_refs,
                'import_count': len(imported_refs),
                'detected_format': detected_format
            }
        except Exception as e:
            return {
                'error': f'Import failed: {str(e)}',
                'detected_format': detected_format
            }
    else:
        return {
            'error': f'Could not detect or parse format',
            'detected_format': detected_format
        }


def _standardize_reference(ref: Dict, ref_id: str) -> Dict:
    """Standardize reference format."""
    standardized = {
        'id': ref_id,
        'type': ref.get('type', 'article'),
        'title': ref.get('title', ''),
        'authors': _standardize_authors(ref.get('authors', [])),
        'year': ref.get('year', ''),
        'journal': ref.get('journal', ''),
        'volume': ref.get('volume', ''),
        'issue': ref.get('issue', ''),
        'pages': ref.get('pages', ''),
        'doi': ref.get('doi', ''),
        'pmid': ref.get('pmid', ''),
        'url': ref.get('url', ''),
        'abstract': ref.get('abstract', ''),
        'keywords': ref.get('keywords', []),
        'notes': ref.get('notes', ''),
        'date_added': datetime.now().isoformat()
    }
    
    # Add any additional fields
    for key, value in ref.items():
        if key not in standardized:
            standardized[key] = value
    
    return standardized


def _standardize_authors(authors) -> List[str]:
    """Standardize author names."""
    if isinstance(authors, str):
        authors = [author.strip() for author in authors.split(',')]
    
    standardized = []
    for author in authors:
        if isinstance(author, str):
            # Clean up author name
            author = re.sub(r'\s+', ' ', author.strip())
            standardized.append(author)
        else:
            standardized.append(str(author))
    
    return standardized


def _format_in_text_citation(ref: Dict, style: str, options: Dict) -> str:
    """Format in-text citation."""
    authors = ref.get('authors', [])
    year = ref.get('year', '')
    
    if style == 'apa':
        if len(authors) == 1:
            return f"({authors[0].split()[-1]}, {year})"
        elif len(authors) == 2:
            return f"({authors[0].split()[-1]} & {authors[1].split()[-1]}, {year})"
        else:
            return f"({authors[0].split()[-1]} et al., {year})"
    
    elif style == 'vancouver':
        ref_id = ref.get('id', '1')
        return f"({ref_id})"
    
    elif style == 'chicago':
        if authors:
            author_name = authors[0].split()[-1]
            return f"({author_name} {year})"
        return f"(Anonymous {year})"
    
    else:  # Default to simple format
        if authors:
            return f"({authors[0].split()[-1]}, {year})"
        return f"(Anonymous, {year})"


def _format_bibliography_entry(ref: Dict, style: str, options: Dict) -> str:
    """Format bibliography entry."""
    authors = ref.get('authors', [])
    title = ref.get('title', '')
    journal = ref.get('journal', '')
    year = ref.get('year', '')
    volume = ref.get('volume', '')
    pages = ref.get('pages', '')
    
    if style == 'apa':
        author_str = _format_authors_apa(authors)
        return f"{author_str} ({year}). {title}. {journal}, {volume}, {pages}."
    
    elif style == 'vancouver':
        author_str = _format_authors_vancouver(authors)
        return f"{author_str} {title}. {journal}. {year};{volume}:{pages}."
    
    elif style == 'nejm':
        author_str = _format_authors_nejm(authors)
        return f"{author_str} {title}. {journal} {year};{volume}:{pages}."
    
    else:  # Default format
        author_str = ', '.join(authors) if authors else 'Anonymous'
        return f"{author_str}. {title}. {journal} {year};{volume}:{pages}."


def _format_authors_apa(authors: List[str]) -> str:
    """Format authors in APA style."""
    if not authors:
        return "Anonymous"
    
    formatted_authors = []
    for author in authors:
        parts = author.split()
        if len(parts) >= 2:
            last_name = parts[-1]
            initials = '. '.join([name[0] for name in parts[:-1]]) + '.'
            formatted_authors.append(f"{last_name}, {initials}")
        else:
            formatted_authors.append(author)
    
    if len(formatted_authors) <= 7:
        return ', '.join(formatted_authors)
    else:
        return ', '.join(formatted_authors[:6]) + ', ... ' + formatted_authors[-1]


def _format_authors_vancouver(authors: List[str]) -> str:
    """Format authors in Vancouver style."""
    if not authors:
        return "Anonymous."
    
    formatted_authors = []
    for author in authors:
        parts = author.split()
        if len(parts) >= 2:
            last_name = parts[-1]
            initials = ''.join([name[0] for name in parts[:-1]])
            formatted_authors.append(f"{last_name} {initials}")
        else:
            formatted_authors.append(author)
    
    return ', '.join(formatted_authors) + '.'


def _format_authors_nejm(authors: List[str]) -> str:
    """Format authors in NEJM style."""
    return _format_authors_vancouver(authors)  # NEJM uses similar format


def _get_required_fields(ref_type: str) -> List[str]:
    """Get required fields for reference type."""
    field_requirements = {
        'article': ['title', 'authors', 'journal', 'year'],
        'book': ['title', 'authors', 'year', 'publisher'],
        'chapter': ['title', 'authors', 'book_title', 'year', 'pages'],
        'conference': ['title', 'authors', 'conference_name', 'year'],
        'thesis': ['title', 'authors', 'year', 'institution'],
        'website': ['title', 'url', 'access_date']
    }
    return field_requirements.get(ref_type, ['title', 'authors', 'year'])


def _validate_reference_formats(ref: Dict) -> Dict:
    """Validate reference field formats."""
    issues = []
    warnings = []
    score = 0
    max_score = 0
    
    # DOI format validation
    if 'doi' in ref and ref['doi']:
        max_score += 1
        if re.match(r'^10\.\d{4,}/.*', ref['doi']):
            score += 1
        else:
            issues.append('Invalid DOI format')
    
    # PMID format validation
    if 'pmid' in ref and ref['pmid']:
        max_score += 1
        if ref['pmid'].isdigit():
            score += 1
        else:
            issues.append('PMID should be numeric')
    
    # Year format validation
    if 'year' in ref and ref['year']:
        max_score += 1
        if re.match(r'^\d{4}$', str(ref['year'])):
            score += 1
        else:
            warnings.append('Year should be 4 digits')
    
    # URL format validation
    if 'url' in ref and ref['url']:
        max_score += 1
        if re.match(r'^https?://', ref['url']):
            score += 1
        else:
            warnings.append('URL should start with http:// or https://')
    
    return {
        'errors': issues,
        'warnings': warnings,
        'score': score,
        'max_score': max_score
    }


def _apply_custom_validation_rules(ref: Dict, rules: Dict) -> Dict:
    """Apply custom validation rules."""
    errors = []
    warnings = []
    
    for rule_name, rule_config in rules.items():
        field = rule_config.get('field')
        pattern = rule_config.get('pattern')
        required = rule_config.get('required', False)
        severity = rule_config.get('severity', 'warning')
        
        if field in ref:
            if pattern and not re.match(pattern, str(ref[field])):
                message = f"Field '{field}' doesn't match required pattern"
                if severity == 'error':
                    errors.append(message)
                else:
                    warnings.append(message)
        elif required:
            errors.append(f"Required field '{field}' is missing")
    
    return {'errors': errors, 'warnings': warnings}


def _calculate_relevance_score(ref: Dict, query: str) -> float:
    """Calculate relevance score for search results."""
    score = 0.0
    
    # Title relevance (highest weight)
    title = ref.get('title', '').lower()
    if query in title:
        score += 10.0
        score += title.count(query) * 2.0
    
    # Author relevance
    authors = ' '.join(ref.get('authors', [])).lower()
    if query in authors:
        score += 5.0
    
    # Journal relevance
    journal = ref.get('journal', '').lower()
    if query in journal:
        score += 3.0
    
    # Abstract relevance
    abstract = ref.get('abstract', '').lower()
    if query in abstract:
        score += 2.0
        score += abstract.count(query) * 0.5
    
    # Keywords relevance
    keywords = ' '.join(ref.get('keywords', [])).lower()
    if query in keywords:
        score += 7.0
    
    return score


def _export_bibtex(references: List[Dict]) -> str:
    """Export references as BibTeX."""
    bibtex_entries = []
    
    for ref in references:
        ref_type = ref.get('type', 'article')
        ref_id = ref.get('id', 'unknown')
        
        entry = f"@{ref_type}{{{ref_id},\n"
        
        if ref.get('title'):
            entry += f"  title={{{ref['title']}}},\n"
        if ref.get('authors'):
            entry += f"  author={{{' and '.join(ref['authors'])}}},\n"
        if ref.get('journal'):
            entry += f"  journal={{{ref['journal']}}},\n"
        if ref.get('year'):
            entry += f"  year={{{ref['year']}}},\n"
        if ref.get('volume'):
            entry += f"  volume={{{ref['volume']}}},\n"
        if ref.get('pages'):
            entry += f"  pages={{{ref['pages']}}},\n"
        if ref.get('doi'):
            entry += f"  doi={{{ref['doi']}}},\n"
        
        entry += "}\n\n"
        bibtex_entries.append(entry)
    
    return ''.join(bibtex_entries)


def _export_endnote(references: List[Dict]) -> str:
    """Export references in EndNote format."""
    # Simplified EndNote export
    entries = []
    for ref in references:
        entry = f"%0 {ref.get('type', 'Journal Article')}\n"
        entry += f"%T {ref.get('title', '')}\n"
        for author in ref.get('authors', []):
            entry += f"%A {author}\n"
        entry += f"%J {ref.get('journal', '')}\n"
        entry += f"%D {ref.get('year', '')}\n"
        entry += f"%V {ref.get('volume', '')}\n"
        entry += f"%P {ref.get('pages', '')}\n"
        if ref.get('doi'):
            entry += f"%R {ref['doi']}\n"
        entry += "\n"
        entries.append(entry)
    
    return ''.join(entries)


def _export_json(references: List[Dict]) -> str:
    """Export references as JSON."""
    return json.dumps(references, indent=2)


def _export_csv(references: List[Dict]) -> str:
    """Export references as CSV."""
    import csv
    import io
    
    output = io.StringIO()
    if references:
        fieldnames = list(references[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(references)
    
    return output.getvalue()


def _export_ris(references: List[Dict]) -> str:
    """Export references in RIS format."""
    ris_entries = []
    
    for ref in references:
        entry = f"TY  - {ref.get('type', 'JOUR').upper()}\n"
        entry += f"TI  - {ref.get('title', '')}\n"
        
        for author in ref.get('authors', []):
            entry += f"AU  - {author}\n"
        
        entry += f"JO  - {ref.get('journal', '')}\n"
        entry += f"PY  - {ref.get('year', '')}\n"
        entry += f"VL  - {ref.get('volume', '')}\n"
        entry += f"SP  - {ref.get('pages', '')}\n"
        
        if ref.get('doi'):
            entry += f"DO  - {ref['doi']}\n"
        
        entry += "ER  - \n\n"
        ris_entries.append(entry)
    
    return ''.join(ris_entries)


def _detect_import_format(data: str) -> str:
    """Detect import data format."""
    data_stripped = data.strip()
    
    if data_stripped.startswith('{') or data_stripped.startswith('['):
        return 'json'
    elif '@' in data_stripped and '{' in data_stripped:
        return 'bibtex'
    elif 'TY  -' in data_stripped:
        return 'ris'
    elif ',' in data_stripped and '\n' in data_stripped:
        return 'csv'
    else:
        return 'unknown'


def _parse_json(data: str) -> List[Dict]:
    """Parse JSON import data."""
    imported = json.loads(data)
    if isinstance(imported, dict):
        return [imported]
    return imported


def _parse_bibtex(data: str) -> List[Dict]:
    """Parse BibTeX import data (simplified)."""
    # This is a simplified parser - a full parser would be more complex
    entries = []
    entry_pattern = r'@(\w+)\{([^,]+),([^}]+)\}'
    
    for match in re.finditer(entry_pattern, data, re.DOTALL):
        entry_type = match.group(1).lower()
        entry_id = match.group(2).strip()
        entry_content = match.group(3)
        
        ref = {'id': entry_id, 'type': entry_type}
        
        # Parse fields
        field_pattern = r'(\w+)\s*=\s*\{([^}]+)\}'
        for field_match in re.finditer(field_pattern, entry_content):
            field_name = field_match.group(1).lower()
            field_value = field_match.group(2).strip()
            
            if field_name == 'author':
                ref['authors'] = [a.strip() for a in field_value.split(' and ')]
            else:
                ref[field_name] = field_value
        
        entries.append(ref)
    
    return entries


def _parse_csv(data: str) -> List[Dict]:
    """Parse CSV import data."""
    import csv
    import io
    
    entries = []
    reader = csv.DictReader(io.StringIO(data))
    for row in reader:
        entries.append(dict(row))
    
    return entries


def _parse_ris(data: str) -> List[Dict]:
    """Parse RIS import data."""
    entries = []
    current_entry = {}
    
    for line in data.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('TY  -'):
            if current_entry:
                entries.append(current_entry)
            current_entry = {'type': line.split('-', 1)[1].strip().lower()}
        elif line.startswith('ER  -'):
            if current_entry:
                entries.append(current_entry)
                current_entry = {}
        elif '  -' in line:
            field, value = line.split('  -', 1)
            value = value.strip()
            
            field_map = {
                'TI': 'title',
                'AU': 'authors',
                'JO': 'journal',
                'PY': 'year',
                'VL': 'volume',
                'SP': 'pages',
                'DO': 'doi'
            }
            
            field_name = field_map.get(field, field.lower())
            
            if field_name == 'authors':
                if field_name not in current_entry:
                    current_entry[field_name] = []
                current_entry[field_name].append(value)
            else:
                current_entry[field_name] = value
    
    return entries


def _get_quality_rating(score: float) -> str:
    """Get quality rating from score."""
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


def _generate_validation_recommendations(validation_results: List[Dict]) -> List[str]:
    """Generate validation recommendations."""
    recommendations = []
    
    common_issues = {}
    for result in validation_results:
        for issue in result['issues']:
            common_issues[issue] = common_issues.get(issue, 0) + 1
    
    if common_issues:
        most_common = max(common_issues.items(), key=lambda x: x[1])
        recommendations.append(f"Most common issue: {most_common[0]} (appears {most_common[1]} times)")
    
    total_issues = sum(len(r['issues']) for r in validation_results)
    if total_issues > 0:
        recommendations.append("Review and complete missing required fields")
        recommendations.append("Standardize formatting for DOIs, PMIDs, and other identifiers")
    else:
        recommendations.append("Reference validation passed - maintain current quality standards")
    
    return recommendations


def _generate_search_summary(results: List[Dict], query: str) -> str:
    """Generate search summary."""
    if not results:
        return f"No references found matching '{query}'"
    
    return f"Found {len(results)} references matching '{query}'"


def _get_formatting_notes(style: str) -> List[str]:
    """Get formatting notes for citation style."""
    notes = {
        'apa': [
            "APA style uses author-date format",
            "Use '&' between authors in citations",
            "Include DOI when available"
        ],
        'vancouver': [
            "Vancouver style uses numbered citations",
            "References numbered in order of appearance",
            "Use abbreviated journal names"
        ],
        'nejm': [
            "NEJM style similar to Vancouver",
            "Author names: Last FM",
            "No periods after initials"
        ]
    }
    return notes.get(style, ["Standard formatting applied"])


def _get_export_notes(format_type: str) -> List[str]:
    """Get export format notes."""
    notes = {
        'bibtex': ["Compatible with LaTeX and most reference managers"],
        'endnote': ["Compatible with EndNote software"],
        'json': ["Machine-readable format suitable for data exchange"],
        'csv': ["Can be opened in Excel or other spreadsheet software"],
        'ris': ["Compatible with Reference Manager and other tools"]
    }
    return notes.get(format_type, [])