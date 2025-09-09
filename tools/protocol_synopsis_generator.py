"""
Protocol Synopsis Generator

Creates structured protocol synopsis from key information.
"""

from typing import Dict, Any
from datetime import datetime


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate protocol synopsis.
    
    Args:
        input_data: Dictionary with protocol details
    
    Returns:
        Dictionary with formatted synopsis
    """
    
    # Extract key information
    title = input_data.get('study_title', 'Clinical Study')
    protocol_number = input_data.get('protocol_number', 'PROTO-001')
    phase = input_data.get('phase', 'Not specified')
    indication = input_data.get('indication', 'Not specified')
    
    # Generate synopsis sections
    synopsis = {
        'header': _generate_header(input_data),
        'background': _generate_background(input_data),
        'objectives': _generate_objectives(input_data),
        'design': _generate_design_summary(input_data),
        'population': _generate_population_summary(input_data),
        'treatments': _generate_treatment_summary(input_data),
        'endpoints': _generate_endpoints_summary(input_data),
        'statistics': _generate_statistics_summary(input_data),
        'timeline': _generate_timeline_summary(input_data)
    }
    
    # Create formatted text version
    formatted_synopsis = _format_synopsis_text(synopsis)
    
    # Create structured version for database/systems
    structured_synopsis = _create_structured_synopsis(synopsis)
    
    return {
        'synopsis_sections': synopsis,
        'formatted_text': formatted_synopsis,
        'structured_data': structured_synopsis,
        'metadata': {
            'generated_date': datetime.now().isoformat(),
            'protocol_number': protocol_number,
            'version': input_data.get('version', '1.0')
        }
    }


def _generate_header(data: Dict) -> Dict:
    """Generate synopsis header."""
    return {
        'protocol_number': data.get('protocol_number', 'TBD'),
        'study_title': data.get('study_title', 'TBD'),
        'short_title': data.get('short_title', ''),
        'phase': data.get('phase', 'TBD'),
        'sponsor': data.get('sponsor', 'TBD'),
        'indication': data.get('indication', 'TBD')
    }


def _generate_background(data: Dict) -> str:
    """Generate background section."""
    background = data.get('background', '')
    if not background:
        disease = data.get('indication', 'the condition')
        drug = data.get('investigational_product', 'the investigational product')
        background = f"This study evaluates {drug} for the treatment of {disease}."
    return background


def _generate_objectives(data: Dict) -> Dict:
    """Generate objectives section."""
    return {
        'primary': data.get('primary_objective', 
                           'To evaluate the efficacy of the investigational product'),
        'secondary': data.get('secondary_objectives', [
            'To evaluate the safety and tolerability',
            'To assess pharmacokinetics'
        ]),
        'exploratory': data.get('exploratory_objectives', [])
    }


def _generate_design_summary(data: Dict) -> Dict:
    """Generate study design summary."""
    return {
        'type': data.get('study_type', 'Interventional'),
        'design': data.get('design', 'Randomized, double-blind, placebo-controlled'),
        'arms': data.get('treatment_arms', ['Control', 'Treatment']),
        'randomization': data.get('randomization_ratio', '1:1'),
        'blinding': data.get('blinding', 'Double-blind'),
        'duration': data.get('study_duration', 'TBD'),
        'centers': data.get('n_centers', 'Multicenter')
    }


def _generate_population_summary(data: Dict) -> Dict:
    """Generate population summary."""
    return {
        'sample_size': data.get('sample_size', 'TBD'),
        'key_inclusion': data.get('key_inclusion_criteria', [
            'Age ≥18 years',
            'Confirmed diagnosis'
        ]),
        'key_exclusion': data.get('key_exclusion_criteria', [
            'Pregnancy or lactation',
            'Significant comorbidities'
        ])
    }


def _generate_treatment_summary(data: Dict) -> Dict:
    """Generate treatment summary."""
    return {
        'investigational_product': data.get('investigational_product', 'TBD'),
        'dosing': data.get('dosing_regimen', 'TBD'),
        'route': data.get('route_of_administration', 'TBD'),
        'duration': data.get('treatment_duration', 'TBD'),
        'comparator': data.get('comparator', 'Placebo')
    }


def _generate_endpoints_summary(data: Dict) -> Dict:
    """Generate endpoints summary."""
    return {
        'primary': data.get('primary_endpoint', 'TBD'),
        'primary_timepoint': data.get('primary_timepoint', 'TBD'),
        'secondary': data.get('secondary_endpoints', []),
        'safety': data.get('safety_endpoints', [
            'Adverse events',
            'Laboratory parameters',
            'Vital signs'
        ])
    }


def _generate_statistics_summary(data: Dict) -> Dict:
    """Generate statistical summary."""
    return {
        'sample_size_rationale': data.get('sample_size_rationale', 
                                         'Based on 80% power to detect clinically meaningful difference'),
        'primary_analysis': data.get('primary_analysis', 'TBD'),
        'analysis_populations': data.get('analysis_populations', [
            'Intent-to-treat',
            'Per-protocol',
            'Safety'
        ])
    }


def _generate_timeline_summary(data: Dict) -> Dict:
    """Generate timeline summary."""
    return {
        'first_patient_in': data.get('first_patient_in', 'TBD'),
        'last_patient_in': data.get('last_patient_in', 'TBD'),
        'last_patient_out': data.get('last_patient_out', 'TBD'),
        'database_lock': data.get('database_lock', 'TBD'),
        'final_report': data.get('final_report', 'TBD')
    }


def _format_synopsis_text(synopsis: Dict) -> str:
    """Format synopsis as readable text."""
    text = []
    
    # Header
    header = synopsis['header']
    text.append("=" * 80)
    text.append("PROTOCOL SYNOPSIS")
    text.append("=" * 80)
    text.append(f"Protocol Number: {header['protocol_number']}")
    text.append(f"Study Title: {header['study_title']}")
    text.append(f"Phase: {header['phase']}")
    text.append(f"Indication: {header['indication']}")
    text.append("")
    
    # Background
    text.append("BACKGROUND")
    text.append("-" * 40)
    text.append(synopsis['background'])
    text.append("")
    
    # Objectives
    text.append("OBJECTIVES")
    text.append("-" * 40)
    text.append(f"Primary: {synopsis['objectives']['primary']}")
    if synopsis['objectives']['secondary']:
        text.append("Secondary:")
        for obj in synopsis['objectives']['secondary']:
            text.append(f"  • {obj}")
    text.append("")
    
    # Design
    text.append("STUDY DESIGN")
    text.append("-" * 40)
    design = synopsis['design']
    text.append(f"Type: {design['type']}")
    text.append(f"Design: {design['design']}")
    text.append(f"Treatment Arms: {', '.join(design['arms'])}")
    text.append(f"Randomization: {design['randomization']}")
    text.append("")
    
    # Population
    text.append("STUDY POPULATION")
    text.append("-" * 40)
    pop = synopsis['population']
    text.append(f"Sample Size: {pop['sample_size']}")
    text.append("Key Inclusion Criteria:")
    for criterion in pop['key_inclusion']:
        text.append(f"  • {criterion}")
    text.append("")
    
    # Endpoints
    text.append("ENDPOINTS")
    text.append("-" * 40)
    endpoints = synopsis['endpoints']
    text.append(f"Primary: {endpoints['primary']}")
    text.append(f"Timepoint: {endpoints['primary_timepoint']}")
    text.append("")
    
    return "\n".join(text)


def _create_structured_synopsis(synopsis: Dict) -> Dict:
    """Create structured synopsis for systems integration."""
    return {
        'protocol_metadata': synopsis['header'],
        'study_design': {
            **synopsis['design'],
            'objectives': synopsis['objectives'],
            'endpoints': synopsis['endpoints']
        },
        'study_population': synopsis['population'],
        'treatments': synopsis['treatments'],
        'statistical_considerations': synopsis['statistics'],
        'timeline': synopsis['timeline'],
        'regulatory_classification': {
            'phase': synopsis['header']['phase'],
            'indication': synopsis['header']['indication']
        }
    }
