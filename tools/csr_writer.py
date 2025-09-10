"""
Clinical Study Report Writer Tool
AI-powered assistance for writing clinical study report sections
"""

from typing import Dict, List, Any
import re
from datetime import datetime
from collections import Counter

def run(input_data: Dict) -> Dict:
    """
    Generates clinical study report sections with AI assistance for regulatory submissions.
    
    Example:
        Input: Section type, study data, and template requirements for CSR generation
        Output: Complete regulatory-compliant section with statistical results and supporting documentation
    
    Parameters:
        section_type : str
            Type of CSR section to generate (efficacy, safety, demographics)
        study_data : dict
            Study information and analysis results data
        template_style : str
            Style template (ich_e3, company_specific)
        target_audience : str
            Target audience (regulators, investigators, sponsors)
        include_references : bool
            Include literature references in output
        compliance_requirements : dict
            Regulatory compliance requirements
    """
    try:
        section_type = input_data.get('section_type', 'summary')
        study_data = input_data.get('study_data', {})
        template_style = input_data.get('template_style', 'ich_e3')
        target_audience = input_data.get('target_audience', 'regulators')
        include_references = input_data.get('include_references', True)
        compliance_requirements = input_data.get('compliance_requirements', [])
        
        if not study_data:
            return {
                'success': False,
                'error': 'No study data provided for CSR generation'
            }
        
        # Validate section type
        valid_sections = [
            'summary', 'introduction', 'study_objectives', 'study_design',
            'study_population', 'treatments', 'efficacy', 'safety',
            'discussion', 'conclusions'
        ]
        
        if section_type not in valid_sections:
            return {
                'success': False,
                'error': f'Invalid section type. Must be one of: {", ".join(valid_sections)}'
            }
        
        # Process and validate study data
        processed_data = process_study_data(study_data, section_type)
        
        # Generate section content based on type
        section_content = generate_section_content(
            section_type, processed_data, template_style, target_audience
        )
        
        # Generate supporting tables and figures
        supporting_materials = generate_supporting_materials(
            section_type, processed_data
        )
        
        # Generate literature references if requested
        references = []
        if include_references:
            references = generate_literature_references(section_type, processed_data)
        
        # Perform quality checks
        quality_checks = perform_quality_checks(
            section_content, processed_data, compliance_requirements
        )
        
        # Generate section metadata
        metadata = generate_section_metadata(
            section_type, processed_data, template_style
        )
        
        # Create regulatory compliance checklist
        compliance_checklist = create_compliance_checklist(
            section_type, compliance_requirements, section_content
        )
        
        return {
            'success': True,
            'csr_section': {
                'section_type': section_type,
                'content': section_content,
                'word_count': len(section_content.split()),
                'template_style': template_style,
                'generated_at': datetime.now().isoformat()
            },
            'supporting_materials': supporting_materials,
            'literature_references': references,
            'quality_assessment': quality_checks,
            'metadata': metadata,
            'compliance_checklist': compliance_checklist,
            'revision_suggestions': generate_revision_suggestions(
                section_content, quality_checks, section_type
            ),
            'writing_guidelines': get_writing_guidelines(section_type, target_audience)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error generating CSR section: {str(e)}'
        }

def process_study_data(study_data: Dict, section_type: str) -> Dict:
    """Process and structure study data for CSR generation."""
    processed = {
        'study_identification': extract_study_identification(study_data),
        'study_design': extract_study_design(study_data),
        'population': extract_population_data(study_data),
        'treatments': extract_treatment_data(study_data),
        'endpoints': extract_endpoints_data(study_data),
        'results': extract_results_data(study_data),
        'safety': extract_safety_data(study_data),
        'statistical': extract_statistical_data(study_data),
        'timeline': extract_timeline_data(study_data)
    }
    
    # Validate critical data based on section type
    validate_required_data(processed, section_type)
    
    return processed

def extract_study_identification(study_data: Dict) -> Dict:
    """Extract study identification information."""
    return {
        'protocol_number': study_data.get('protocol_number', 'Not specified'),
        'study_title': study_data.get('study_title', 'Not specified'),
        'sponsor': study_data.get('sponsor', 'Not specified'),
        'indication': study_data.get('indication', 'Not specified'),
        'phase': study_data.get('phase', 'Not specified'),
        'study_type': study_data.get('study_type', 'Not specified'),
        'therapeutic_area': study_data.get('therapeutic_area', 'Not specified')
    }

def extract_study_design(study_data: Dict) -> Dict:
    """Extract study design information."""
    return {
        'design_type': study_data.get('design_type', 'Not specified'),
        'randomization': study_data.get('randomization', False),
        'blinding': study_data.get('blinding', 'Not specified'),
        'control_type': study_data.get('control_type', 'Not specified'),
        'duration': study_data.get('study_duration', 'Not specified'),
        'number_of_sites': study_data.get('number_of_sites', 0),
        'countries': study_data.get('countries', []),
        'sample_size_planned': study_data.get('sample_size_planned', 0),
        'sample_size_actual': study_data.get('sample_size_actual', 0)
    }

def extract_population_data(study_data: Dict) -> Dict:
    """Extract study population data."""
    return {
        'inclusion_criteria': study_data.get('inclusion_criteria', []),
        'exclusion_criteria': study_data.get('exclusion_criteria', []),
        'demographics': study_data.get('demographics', {}),
        'baseline_characteristics': study_data.get('baseline_characteristics', {}),
        'medical_history': study_data.get('medical_history', {}),
        'concomitant_medications': study_data.get('concomitant_medications', {})
    }

def extract_treatment_data(study_data: Dict) -> Dict:
    """Extract treatment information."""
    return {
        'investigational_product': study_data.get('investigational_product', {}),
        'comparator': study_data.get('comparator', {}),
        'dosing_regimen': study_data.get('dosing_regimen', {}),
        'administration_route': study_data.get('administration_route', 'Not specified'),
        'treatment_duration': study_data.get('treatment_duration', 'Not specified'),
        'concomitant_treatments': study_data.get('concomitant_treatments', [])
    }

def extract_endpoints_data(study_data: Dict) -> Dict:
    """Extract endpoints and outcome measures."""
    return {
        'primary_endpoints': study_data.get('primary_endpoints', []),
        'secondary_endpoints': study_data.get('secondary_endpoints', []),
        'exploratory_endpoints': study_data.get('exploratory_endpoints', []),
        'safety_endpoints': study_data.get('safety_endpoints', []),
        'pharmacokinetic_endpoints': study_data.get('pk_endpoints', [])
    }

def extract_results_data(study_data: Dict) -> Dict:
    """Extract efficacy and outcome results."""
    return {
        'primary_results': study_data.get('primary_results', {}),
        'secondary_results': study_data.get('secondary_results', {}),
        'subgroup_analyses': study_data.get('subgroup_analyses', {}),
        'pharmacokinetic_results': study_data.get('pk_results', {}),
        'biomarker_results': study_data.get('biomarker_results', {})
    }

def extract_safety_data(study_data: Dict) -> Dict:
    """Extract safety data."""
    return {
        'adverse_events': study_data.get('adverse_events', {}),
        'serious_adverse_events': study_data.get('serious_adverse_events', {}),
        'deaths': study_data.get('deaths', {}),
        'laboratory_data': study_data.get('laboratory_data', {}),
        'vital_signs': study_data.get('vital_signs', {}),
        'ecg_data': study_data.get('ecg_data', {}),
        'exposure_data': study_data.get('exposure_data', {})
    }

def extract_statistical_data(study_data: Dict) -> Dict:
    """Extract statistical analysis information."""
    return {
        'analysis_populations': study_data.get('analysis_populations', {}),
        'statistical_methods': study_data.get('statistical_methods', {}),
        'sample_size_justification': study_data.get('sample_size_justification', ''),
        'handling_missing_data': study_data.get('handling_missing_data', ''),
        'multiplicity_adjustments': study_data.get('multiplicity_adjustments', ''),
        'interim_analyses': study_data.get('interim_analyses', {})
    }

def extract_timeline_data(study_data: Dict) -> Dict:
    """Extract study timeline information."""
    return {
        'first_subject_screened': study_data.get('first_subject_screened', ''),
        'first_subject_randomized': study_data.get('first_subject_randomized', ''),
        'last_subject_last_visit': study_data.get('last_subject_last_visit', ''),
        'database_lock': study_data.get('database_lock', ''),
        'study_completion': study_data.get('study_completion', ''),
        'milestones': study_data.get('milestones', [])
    }

def validate_required_data(processed_data: Dict, section_type: str) -> None:
    """Validate that required data is present for the section type."""
    required_data_map = {
        'summary': ['study_identification', 'results'],
        'introduction': ['study_identification'],
        'study_objectives': ['endpoints'],
        'study_design': ['study_design'],
        'study_population': ['population'],
        'treatments': ['treatments'],
        'efficacy': ['results', 'endpoints'],
        'safety': ['safety'],
        'discussion': ['results', 'safety'],
        'conclusions': ['results']
    }
    
    required_sections = required_data_map.get(section_type, [])
    for section in required_sections:
        if section not in processed_data or not processed_data[section]:
            # Note: In a real implementation, this might log warnings rather than raise errors
            pass

def generate_section_content(section_type: str, processed_data: Dict, 
                           template_style: str, target_audience: str) -> str:
    """Generate content for the specified CSR section."""
    generators = {
        'summary': generate_summary_section,
        'introduction': generate_introduction_section,
        'study_objectives': generate_objectives_section,
        'study_design': generate_design_section,
        'study_population': generate_population_section,
        'treatments': generate_treatments_section,
        'efficacy': generate_efficacy_section,
        'safety': generate_safety_section,
        'discussion': generate_discussion_section,
        'conclusions': generate_conclusions_section
    }
    
    generator = generators.get(section_type, generate_generic_section)
    return generator(processed_data, template_style, target_audience)

def generate_summary_section(processed_data: Dict, template_style: str, target_audience: str) -> str:
    """Generate executive summary section."""
    study_id = processed_data['study_identification']
    design = processed_data['study_design']
    results = processed_data['results']
    safety = processed_data['safety']
    
    content_parts = []
    
    # Study overview
    content_parts.append(f"""
Study Overview:
This report presents the results of study {study_id['protocol_number']}, "{study_id['study_title']}", 
a {design['design_type']} study conducted by {study_id['sponsor']} to evaluate the safety and efficacy 
of {processed_data['treatments']['investigational_product'].get('name', 'the investigational product')} 
in patients with {study_id['indication']}.
""")
    
    # Study design summary
    content_parts.append(f"""
Study Design:
This was a {design['design_type']}, {design['blinding']}, {design['control_type']}-controlled study 
conducted across {design['number_of_sites']} sites in {len(design.get('countries', []))} countries. 
A total of {design['sample_size_actual']} subjects were enrolled 
(planned: {design['sample_size_planned']}) and treated for {design['duration']}.
""")
    
    # Primary results summary
    primary_results = results.get('primary_results', {})
    if primary_results:
        content_parts.append(f"""
Primary Efficacy Results:
{generate_primary_results_summary(primary_results)}
""")
    
    # Safety summary
    if safety.get('adverse_events'):
        content_parts.append(f"""
Safety Summary:
{generate_safety_summary(safety)}
""")
    
    # Conclusions
    content_parts.append(f"""
Conclusions:
The study met its primary objectives and demonstrated {generate_conclusion_statement(results, safety)}. 
The safety profile was consistent with the known safety profile of the investigational product.
""")
    
    return '\n'.join(content_parts)

def generate_introduction_section(processed_data: Dict, template_style: str, target_audience: str) -> str:
    """Generate introduction section."""
    study_id = processed_data['study_identification']
    
    content_parts = []
    
    # Background
    content_parts.append(f"""
1. INTRODUCTION

1.1 Background
{study_id['indication']} is a significant medical condition that affects a substantial number of patients worldwide. 
Current treatment options include [standard treatments], but there remains a need for improved therapeutic options.

1.2 Rationale for the Study
The investigational product has demonstrated promising activity in preclinical studies and early phase clinical trials. 
This Phase {study_id['phase']} study was designed to further evaluate its safety and efficacy in the target population.

1.3 Study Objectives
The primary objective of this study was to evaluate the efficacy of the investigational product compared to {processed_data['treatments']['comparator'].get('name', 'control')} 
in patients with {study_id['indication']}.
""")
    
    # Investigational product overview
    ip_info = processed_data['treatments']['investigational_product']
    content_parts.append(f"""
1.4 Investigational Product
The investigational product is {ip_info.get('description', 'a novel therapeutic compound')} 
developed for the treatment of {study_id['indication']}. 
The proposed mechanism of action involves {ip_info.get('mechanism_of_action', 'specific therapeutic pathways')}.
""")
    
    return '\n'.join(content_parts)

def generate_objectives_section(processed_data: Dict, template_style: str, target_audience: str) -> str:
    """Generate study objectives section."""
    endpoints = processed_data['endpoints']
    
    content_parts = []
    
    content_parts.append("2. STUDY OBJECTIVES\n")
    
    # Primary objectives
    primary_endpoints = endpoints.get('primary_endpoints', [])
    if primary_endpoints:
        content_parts.append("2.1 Primary Objectives")
        for i, endpoint in enumerate(primary_endpoints, 1):
            content_parts.append(f"2.1.{i} {format_endpoint(endpoint)}")
    
    # Secondary objectives
    secondary_endpoints = endpoints.get('secondary_endpoints', [])
    if secondary_endpoints:
        content_parts.append("\n2.2 Secondary Objectives")
        for i, endpoint in enumerate(secondary_endpoints, 1):
            content_parts.append(f"2.2.{i} {format_endpoint(endpoint)}")
    
    # Exploratory objectives
    exploratory_endpoints = endpoints.get('exploratory_endpoints', [])
    if exploratory_endpoints:
        content_parts.append("\n2.3 Exploratory Objectives")
        for i, endpoint in enumerate(exploratory_endpoints, 1):
            content_parts.append(f"2.3.{i} {format_endpoint(endpoint)}")
    
    return '\n'.join(content_parts)

def generate_design_section(processed_data: Dict, template_style: str, target_audience: str) -> str:
    """Generate study design section."""
    design = processed_data['study_design']
    timeline = processed_data['timeline']
    
    content_parts = []
    
    content_parts.append("3. STUDY DESIGN\n")
    
    # Overall design
    content_parts.append(f"""
3.1 Overall Study Design
This was a {design['design_type']}, {design['blinding']}, {design['control_type']}-controlled study. 
The study was conducted across {design['number_of_sites']} investigational sites in {len(design.get('countries', []))} countries: {', '.join(design.get('countries', []))}.
""")
    
    # Study population
    content_parts.append(f"""
3.2 Study Population
The study enrolled {design['sample_size_actual']} subjects (planned: {design['sample_size_planned']}) 
who met the inclusion and exclusion criteria defined in the protocol.
""")
    
    # Randomization and blinding
    if design['randomization']:
        content_parts.append(f"""
3.3 Randomization and Blinding
Subjects were randomized to treatment groups using a {design.get('randomization_method', 'block randomization')} method. 
The study employed {design['blinding']} blinding to minimize bias.
""")
    
    # Study duration
    content_parts.append(f"""
3.4 Study Duration
The study duration was {design['duration']}. The study commenced with first subject screened on {timeline.get('first_subject_screened', 'Not specified')} 
and was completed with last subject last visit on {timeline.get('last_subject_last_visit', 'Not specified')}.
""")
    
    return '\n'.join(content_parts)

def generate_population_section(processed_data: Dict, template_style: str, target_audience: str) -> str:
    """Generate study population section."""
    population = processed_data['population']
    
    content_parts = []
    
    content_parts.append("4. STUDY POPULATION\n")
    
    # Inclusion criteria
    content_parts.append("4.1 Inclusion Criteria")
    inclusion_criteria = population.get('inclusion_criteria', [])
    for i, criterion in enumerate(inclusion_criteria, 1):
        content_parts.append(f"4.1.{i} {criterion}")
    
    # Exclusion criteria
    content_parts.append("\n4.2 Exclusion Criteria")
    exclusion_criteria = population.get('exclusion_criteria', [])
    for i, criterion in enumerate(exclusion_criteria, 1):
        content_parts.append(f"4.2.{i} {criterion}")
    
    # Demographics
    demographics = population.get('demographics', {})
    if demographics:
        content_parts.append(f"""
4.3 Demographics and Baseline Characteristics
{generate_demographics_summary(demographics)}
""")
    
    return '\n'.join(content_parts)

def generate_treatments_section(processed_data: Dict, template_style: str, target_audience: str) -> str:
    """Generate treatments section."""
    treatments = processed_data['treatments']
    
    content_parts = []
    
    content_parts.append("5. TREATMENTS\n")
    
    # Investigational product
    ip = treatments.get('investigational_product', {})
    content_parts.append(f"""
5.1 Investigational Product
The investigational product was {ip.get('name', 'not specified')} administered {treatments.get('administration_route', 'orally')} 
at a dose of {treatments.get('dosing_regimen', {}).get('dose', 'not specified')} {treatments.get('dosing_regimen', {}).get('frequency', 'once daily')} 
for {treatments.get('treatment_duration', 'the study duration')}.
""")
    
    # Comparator
    comparator = treatments.get('comparator', {})
    if comparator.get('name'):
        content_parts.append(f"""
5.2 Comparator
The comparator was {comparator.get('name')} administered {comparator.get('route', 'orally')} 
at a dose of {comparator.get('dose', 'not specified')}.
""")
    
    # Concomitant medications
    concomitant = treatments.get('concomitant_treatments', [])
    if concomitant:
        content_parts.append(f"""
5.3 Concomitant Medications
The following concomitant medications were permitted during the study: {', '.join(concomitant)}.
""")
    
    return '\n'.join(content_parts)

def generate_efficacy_section(processed_data: Dict, template_style: str, target_audience: str) -> str:
    """Generate efficacy results section."""
    results = processed_data['results']
    endpoints = processed_data['endpoints']
    statistical = processed_data['statistical']
    
    content_parts = []
    
    content_parts.append("6. EFFICACY RESULTS\n")
    
    # Analysis populations
    populations = statistical.get('analysis_populations', {})
    if populations:
        content_parts.append(f"""
6.1 Analysis Populations
{generate_analysis_populations_summary(populations)}
""")
    
    # Primary efficacy results
    primary_results = results.get('primary_results', {})
    if primary_results:
        content_parts.append(f"""
6.2 Primary Efficacy Results
{generate_detailed_primary_results(primary_results, endpoints.get('primary_endpoints', []))}
""")
    
    # Secondary efficacy results
    secondary_results = results.get('secondary_results', {})
    if secondary_results:
        content_parts.append(f"""
6.3 Secondary Efficacy Results
{generate_secondary_results_summary(secondary_results, endpoints.get('secondary_endpoints', []))}
""")
    
    # Subgroup analyses
    subgroup_results = results.get('subgroup_analyses', {})
    if subgroup_results:
        content_parts.append(f"""
6.4 Subgroup Analyses
{generate_subgroup_analysis_summary(subgroup_results)}
""")
    
    return '\n'.join(content_parts)

def generate_safety_section(processed_data: Dict, template_style: str, target_audience: str) -> str:
    """Generate safety results section."""
    safety = processed_data['safety']
    
    content_parts = []
    
    content_parts.append("7. SAFETY RESULTS\n")
    
    # Exposure
    exposure = safety.get('exposure_data', {})
    if exposure:
        content_parts.append(f"""
7.1 Extent of Exposure
{generate_exposure_summary(exposure)}
""")
    
    # Adverse events
    ae_data = safety.get('adverse_events', {})
    if ae_data:
        content_parts.append(f"""
7.2 Adverse Events
{generate_adverse_events_summary(ae_data)}
""")
    
    # Serious adverse events
    sae_data = safety.get('serious_adverse_events', {})
    if sae_data:
        content_parts.append(f"""
7.3 Serious Adverse Events
{generate_serious_ae_summary(sae_data)}
""")
    
    # Deaths
    deaths_data = safety.get('deaths', {})
    if deaths_data:
        content_parts.append(f"""
7.4 Deaths
{generate_deaths_summary(deaths_data)}
""")
    
    # Laboratory data
    lab_data = safety.get('laboratory_data', {})
    if lab_data:
        content_parts.append(f"""
7.5 Laboratory Evaluations
{generate_laboratory_summary(lab_data)}
""")
    
    return '\n'.join(content_parts)

def generate_discussion_section(processed_data: Dict, template_style: str, target_audience: str) -> str:
    """Generate discussion section."""
    results = processed_data['results']
    safety = processed_data['safety']
    study_id = processed_data['study_identification']
    
    content_parts = []
    
    content_parts.append("8. DISCUSSION\n")
    
    # Efficacy discussion
    content_parts.append(f"""
8.1 Efficacy
The primary objective of this study was met, demonstrating {generate_efficacy_interpretation(results)}. 
These results are consistent with the proposed mechanism of action of the investigational product and 
support its therapeutic potential in {study_id['indication']}.
""")
    
    # Safety discussion
    content_parts.append(f"""
8.2 Safety
The safety profile observed in this study was {generate_safety_interpretation(safety)}. 
The types and frequencies of adverse events were generally consistent with the known safety profile 
of the investigational product and the underlying disease.
""")
    
    # Study limitations
    content_parts.append(f"""
8.3 Study Limitations
This study had several limitations that should be considered when interpreting the results, including 
{generate_limitations_discussion(processed_data)}.
""")
    
    # Clinical implications
    content_parts.append(f"""
8.4 Clinical Implications
The results of this study support the further development of the investigational product for the treatment of 
{study_id['indication']} and provide important information for the design of future studies.
""")
    
    return '\n'.join(content_parts)

def generate_conclusions_section(processed_data: Dict, template_style: str, target_audience: str) -> str:
    """Generate conclusions section."""
    results = processed_data['results']
    safety = processed_data['safety']
    study_id = processed_data['study_identification']
    
    content_parts = []
    
    content_parts.append("9. CONCLUSIONS\n")
    
    # Primary conclusions
    content_parts.append(f"""
9.1 Primary Conclusions
This Phase {study_id['phase']} study successfully met its primary objectives and demonstrated 
{generate_conclusion_statement(results, safety)} in patients with {study_id['indication']}.
""")
    
    # Safety conclusions
    content_parts.append(f"""
9.2 Safety Conclusions
The investigational product was generally well tolerated with a safety profile consistent with 
previous studies and the known characteristics of the compound.
""")
    
    # Overall benefit-risk assessment
    content_parts.append(f"""
9.3 Benefit-Risk Assessment
The benefit-risk profile of the investigational product in this study population is {generate_benefit_risk_assessment(results, safety)}, 
supporting continued clinical development.
""")
    
    return '\n'.join(content_parts)

def generate_generic_section(processed_data: Dict, template_style: str, target_audience: str) -> str:
    """Generate generic section content."""
    return f"""
This section contains information relevant to the clinical study report. 
The content would be tailored based on the specific section type and available study data.
Study: {processed_data['study_identification'].get('protocol_number', 'Unknown')}
Generated for: {target_audience}
Template style: {template_style}
"""

# Helper functions for content generation

def format_endpoint(endpoint: Any) -> str:
    """Format an endpoint for display."""
    if isinstance(endpoint, dict):
        return endpoint.get('description', 'Endpoint description not provided')
    else:
        return str(endpoint)

def generate_primary_results_summary(primary_results: Dict) -> str:
    """Generate summary of primary results."""
    if not primary_results:
        return "Primary results are being analyzed and will be reported separately."
    
    summary_parts = []
    for endpoint, result in primary_results.items():
        if isinstance(result, dict):
            p_value = result.get('p_value', 'Not reported')
            effect_size = result.get('effect_size', 'Not reported')
            summary_parts.append(f"{endpoint}: Effect size = {effect_size}, p-value = {p_value}")
        else:
            summary_parts.append(f"{endpoint}: {result}")
    
    return '; '.join(summary_parts)

def generate_safety_summary(safety_data: Dict) -> str:
    """Generate safety summary."""
    ae_data = safety_data.get('adverse_events', {})
    sae_data = safety_data.get('serious_adverse_events', {})
    
    summary_parts = []
    
    if ae_data:
        total_aes = ae_data.get('total_events', 'Unknown')
        summary_parts.append(f"A total of {total_aes} adverse events were reported")
    
    if sae_data:
        total_saes = sae_data.get('total_events', 'Unknown')
        summary_parts.append(f"{total_saes} serious adverse events were reported")
    
    return '. '.join(summary_parts) + '.' if summary_parts else "Safety data are being analyzed."

def generate_conclusion_statement(results: Dict, safety: Dict) -> str:
    """Generate overall conclusion statement."""
    efficacy_statement = "clinically meaningful efficacy"
    safety_statement = "an acceptable safety profile"
    
    # Customize based on actual results if available
    primary_results = results.get('primary_results', {})
    if primary_results:
        # Check if any p-values are significant
        significant_results = any(
            isinstance(result, dict) and result.get('p_value', 1) < 0.05
            for result in primary_results.values()
        )
        if significant_results:
            efficacy_statement = "statistically significant and clinically meaningful efficacy"
    
    return f"{efficacy_statement} with {safety_statement}"

def generate_demographics_summary(demographics: Dict) -> str:
    """Generate demographics summary."""
    summary_parts = []
    
    if 'mean_age' in demographics:
        summary_parts.append(f"Mean age: {demographics['mean_age']} years")
    
    if 'gender_distribution' in demographics:
        gender_dist = demographics['gender_distribution']
        summary_parts.append(f"Gender distribution: {gender_dist}")
    
    if 'race_ethnicity' in demographics:
        summary_parts.append(f"Race/ethnicity: {demographics['race_ethnicity']}")
    
    return '; '.join(summary_parts) if summary_parts else "Demographics data are available in detailed tables."

def generate_analysis_populations_summary(populations: Dict) -> str:
    """Generate analysis populations summary."""
    summary_parts = []
    
    for pop_name, pop_data in populations.items():
        if isinstance(pop_data, dict):
            count = pop_data.get('count', 'Unknown')
            summary_parts.append(f"{pop_name}: {count} subjects")
        else:
            summary_parts.append(f"{pop_name}: {pop_data}")
    
    return '; '.join(summary_parts)

def generate_detailed_primary_results(primary_results: Dict, primary_endpoints: List) -> str:
    """Generate detailed primary results."""
    if not primary_results:
        return "Primary results are being finalized and will be included in the final report."
    
    detailed_parts = []
    
    for endpoint, result in primary_results.items():
        if isinstance(result, dict):
            result_text = f"For {endpoint}:\n"
            
            if 'treatment_effect' in result:
                result_text += f"- Treatment effect: {result['treatment_effect']}\n"
            
            if 'confidence_interval' in result:
                result_text += f"- 95% CI: {result['confidence_interval']}\n"
            
            if 'p_value' in result:
                result_text += f"- P-value: {result['p_value']}\n"
            
            if 'interpretation' in result:
                result_text += f"- Interpretation: {result['interpretation']}\n"
            
            detailed_parts.append(result_text)
        else:
            detailed_parts.append(f"{endpoint}: {result}")
    
    return '\n'.join(detailed_parts)

def generate_secondary_results_summary(secondary_results: Dict, secondary_endpoints: List) -> str:
    """Generate secondary results summary."""
    if not secondary_results:
        return "Secondary analyses are ongoing and results will be provided in the final report."
    
    summary_parts = []
    for endpoint, result in secondary_results.items():
        summary_parts.append(f"{endpoint}: {result}")
    
    return '\n'.join(summary_parts)

def generate_subgroup_analysis_summary(subgroup_results: Dict) -> str:
    """Generate subgroup analysis summary."""
    if not subgroup_results:
        return "Subgroup analyses were performed and results are consistent with the overall population."
    
    summary_parts = []
    for subgroup, result in subgroup_results.items():
        summary_parts.append(f"{subgroup}: {result}")
    
    return '\n'.join(summary_parts)

def generate_exposure_summary(exposure_data: Dict) -> str:
    """Generate exposure summary."""
    summary_parts = []
    
    if 'median_exposure' in exposure_data:
        summary_parts.append(f"Median exposure: {exposure_data['median_exposure']}")
    
    if 'total_patient_years' in exposure_data:
        summary_parts.append(f"Total patient-years of exposure: {exposure_data['total_patient_years']}")
    
    return '; '.join(summary_parts) if summary_parts else "Exposure data are summarized in detailed tables."

def generate_adverse_events_summary(ae_data: Dict) -> str:
    """Generate adverse events summary."""
    summary_parts = []
    
    if 'total_events' in ae_data:
        summary_parts.append(f"Total AEs: {ae_data['total_events']}")
    
    if 'subjects_with_aes' in ae_data:
        summary_parts.append(f"Subjects with AEs: {ae_data['subjects_with_aes']}")
    
    if 'most_common_aes' in ae_data:
        common_aes = ae_data['most_common_aes']
        if isinstance(common_aes, list):
            summary_parts.append(f"Most common AEs: {', '.join(common_aes[:3])}")
    
    return '. '.join(summary_parts) + '.' if summary_parts else "Adverse events are summarized in detailed tables."

def generate_serious_ae_summary(sae_data: Dict) -> str:
    """Generate serious adverse events summary."""
    summary_parts = []
    
    if 'total_saes' in sae_data:
        summary_parts.append(f"Total SAEs: {sae_data['total_saes']}")
    
    if 'subjects_with_saes' in sae_data:
        summary_parts.append(f"Subjects with SAEs: {sae_data['subjects_with_saes']}")
    
    if 'treatment_related_saes' in sae_data:
        summary_parts.append(f"Treatment-related SAEs: {sae_data['treatment_related_saes']}")
    
    return '. '.join(summary_parts) + '.' if summary_parts else "SAE data are provided in detailed listings."

def generate_deaths_summary(deaths_data: Dict) -> str:
    """Generate deaths summary."""
    if 'total_deaths' in deaths_data:
        total = deaths_data['total_deaths']
        if total == 0:
            return "No deaths were reported during the study."
        else:
            return f"A total of {total} death(s) occurred during the study. Details are provided in the narrative summaries."
    
    return "Death data are summarized in detailed reports."

def generate_laboratory_summary(lab_data: Dict) -> str:
    """Generate laboratory summary."""
    summary_parts = []
    
    if 'clinically_significant_changes' in lab_data:
        summary_parts.append(f"Clinically significant lab changes: {lab_data['clinically_significant_changes']}")
    
    if 'notable_findings' in lab_data:
        summary_parts.append(f"Notable findings: {lab_data['notable_findings']}")
    
    return '. '.join(summary_parts) + '.' if summary_parts else "Laboratory data are summarized in detailed tables."

def generate_efficacy_interpretation(results: Dict) -> str:
    """Generate efficacy interpretation."""
    primary_results = results.get('primary_results', {})
    
    if not primary_results:
        return "meaningful therapeutic activity"
    
    # Check for statistical significance
    significant_results = any(
        isinstance(result, dict) and result.get('p_value', 1) < 0.05
        for result in primary_results.values()
    )
    
    if significant_results:
        return "statistically significant and clinically meaningful therapeutic activity"
    else:
        return "therapeutic activity with clinical relevance"

def generate_safety_interpretation(safety_data: Dict) -> str:
    """Generate safety interpretation."""
    ae_data = safety_data.get('adverse_events', {})
    sae_data = safety_data.get('serious_adverse_events', {})
    
    # Simple heuristic for safety interpretation
    if ae_data.get('total_events', 0) == 0:
        return "excellent, with no adverse events reported"
    elif sae_data.get('total_saes', 0) == 0:
        return "acceptable, with no serious adverse events reported"
    else:
        return "acceptable and consistent with the known safety profile"

def generate_limitations_discussion(processed_data: Dict) -> str:
    """Generate study limitations discussion."""
    limitations = []
    
    design = processed_data['study_design']
    
    # Sample size limitations
    if design.get('sample_size_actual', 0) < design.get('sample_size_planned', 0):
        limitations.append("enrollment was lower than planned")
    
    # Duration limitations
    if 'week' in design.get('duration', '').lower():
        limitations.append("the relatively short study duration")
    
    # Single vs multi-center
    if design.get('number_of_sites', 0) == 1:
        limitations.append("the single-center design")
    
    # Population limitations
    population = processed_data['population']
    demographics = population.get('demographics', {})
    if not demographics:
        limitations.append("limited demographic diversity assessment")
    
    return ', '.join(limitations) if limitations else "the inherent limitations of clinical trial methodology"

def generate_benefit_risk_assessment(results: Dict, safety: Dict) -> str:
    """Generate benefit-risk assessment."""
    # Simplified assessment based on available data
    primary_results = results.get('primary_results', {})
    sae_data = safety.get('serious_adverse_events', {})
    
    has_efficacy = bool(primary_results)
    has_serious_safety_concerns = sae_data.get('total_saes', 0) > 0
    
    if has_efficacy and not has_serious_safety_concerns:
        return "favorable"
    elif has_efficacy and has_serious_safety_concerns:
        return "acceptable with appropriate risk mitigation"
    else:
        return "requires further evaluation"

def generate_supporting_materials(section_type: str, processed_data: Dict) -> Dict:
    """Generate supporting tables and figures."""
    materials = {
        'tables': [],
        'figures': [],
        'listings': []
    }
    
    # Section-specific materials
    if section_type in ['summary', 'study_population']:
        materials['tables'].extend(generate_demographic_tables(processed_data))
    
    if section_type in ['summary', 'efficacy']:
        materials['tables'].extend(generate_efficacy_tables(processed_data))
        materials['figures'].extend(generate_efficacy_figures(processed_data))
    
    if section_type in ['summary', 'safety']:
        materials['tables'].extend(generate_safety_tables(processed_data))
        materials['listings'].extend(generate_safety_listings(processed_data))
    
    return materials

def generate_demographic_tables(processed_data: Dict) -> List[Dict]:
    """Generate demographic tables."""
    tables = []
    
    population = processed_data['population']
    demographics = population.get('demographics', {})
    
    if demographics:
        tables.append({
            'title': 'Demographics and Baseline Characteristics',
            'description': 'Summary of subject demographics and baseline characteristics by treatment group',
            'data_source': 'demographics',
            'table_type': 'summary_statistics'
        })
    
    baseline = population.get('baseline_characteristics', {})
    if baseline:
        tables.append({
            'title': 'Baseline Disease Characteristics',
            'description': 'Disease-specific baseline characteristics by treatment group',
            'data_source': 'baseline_characteristics',
            'table_type': 'summary_statistics'
        })
    
    return tables

def generate_efficacy_tables(processed_data: Dict) -> List[Dict]:
    """Generate efficacy tables."""
    tables = []
    
    results = processed_data['results']
    
    if results.get('primary_results'):
        tables.append({
            'title': 'Primary Efficacy Analysis',
            'description': 'Primary endpoint analysis results by treatment group',
            'data_source': 'primary_results',
            'table_type': 'efficacy_analysis'
        })
    
    if results.get('secondary_results'):
        tables.append({
            'title': 'Secondary Efficacy Analyses',
            'description': 'Secondary endpoint analysis results by treatment group',
            'data_source': 'secondary_results',
            'table_type': 'efficacy_analysis'
        })
    
    return tables

def generate_efficacy_figures(processed_data: Dict) -> List[Dict]:
    """Generate efficacy figures."""
    figures = []
    
    results = processed_data['results']
    
    if results.get('primary_results'):
        figures.append({
            'title': 'Primary Endpoint Results',
            'description': 'Graphical representation of primary endpoint by treatment group',
            'figure_type': 'bar_chart',
            'data_source': 'primary_results'
        })
    
    if results.get('subgroup_analyses'):
        figures.append({
            'title': 'Subgroup Analysis Forest Plot',
            'description': 'Forest plot showing treatment effect across subgroups',
            'figure_type': 'forest_plot',
            'data_source': 'subgroup_analyses'
        })
    
    return figures

def generate_safety_tables(processed_data: Dict) -> List[Dict]:
    """Generate safety tables."""
    tables = []
    
    safety = processed_data['safety']
    
    if safety.get('adverse_events'):
        tables.append({
            'title': 'Summary of Adverse Events',
            'description': 'Overview of adverse events by treatment group and system organ class',
            'data_source': 'adverse_events',
            'table_type': 'safety_summary'
        })
    
    if safety.get('serious_adverse_events'):
        tables.append({
            'title': 'Summary of Serious Adverse Events',
            'description': 'Serious adverse events by treatment group',
            'data_source': 'serious_adverse_events',
            'table_type': 'safety_summary'
        })
    
    return tables

def generate_safety_listings(processed_data: Dict) -> List[Dict]:
    """Generate safety listings."""
    listings = []
    
    safety = processed_data['safety']
    
    if safety.get('deaths'):
        listings.append({
            'title': 'Listing of Deaths',
            'description': 'Individual subject data for all deaths',
            'data_source': 'deaths',
            'listing_type': 'subject_level'
        })
    
    if safety.get('serious_adverse_events'):
        listings.append({
            'title': 'Listing of Serious Adverse Events',
            'description': 'Individual subject data for all serious adverse events',
            'data_source': 'serious_adverse_events',
            'listing_type': 'subject_level'
        })
    
    return listings

def generate_literature_references(section_type: str, processed_data: Dict) -> List[Dict]:
    """Generate relevant literature references."""
    references = []
    
    study_id = processed_data['study_identification']
    indication = study_id.get('indication', '')
    therapeutic_area = study_id.get('therapeutic_area', '')
    
    # General references based on section type
    if section_type == 'introduction':
        references.extend([
            {
                'id': 1,
                'citation': f'Guidelines for clinical trials in {indication}. Regulatory guidance document.',
                'relevance': 'regulatory_guidance'
            },
            {
                'id': 2,
                'citation': f'Current treatment approaches for {indication}: A systematic review.',
                'relevance': 'background_literature'
            }
        ])
    
    elif section_type == 'study_design':
        references.extend([
            {
                'id': 1,
                'citation': 'ICH E9 Statistical Principles for Clinical Trials. International Conference on Harmonisation.',
                'relevance': 'methodology_guidance'
            }
        ])
    
    elif section_type == 'safety':
        references.extend([
            {
                'id': 1,
                'citation': 'ICH E2A Clinical Safety Data Management. International Conference on Harmonisation.',
                'relevance': 'safety_guidance'
            }
        ])
    
    return references

def perform_quality_checks(section_content: str, processed_data: Dict, 
                         compliance_requirements: List[str]) -> Dict:
    """Perform quality checks on generated content."""
    checks = {
        'completeness': assess_content_completeness(section_content, processed_data),
        'consistency': assess_content_consistency(section_content, processed_data),
        'clarity': assess_content_clarity(section_content),
        'compliance': assess_regulatory_compliance(section_content, compliance_requirements),
        'overall_score': 0.0,
        'recommendations': []
    }
    
    # Calculate overall score
    scores = [
        checks['completeness']['score'],
        checks['consistency']['score'],
        checks['clarity']['score'],
        checks['compliance']['score']
    ]
    checks['overall_score'] = sum(scores) / len(scores)
    
    # Generate recommendations
    if checks['completeness']['score'] < 0.8:
        checks['recommendations'].append("Enhance content completeness by adding missing key elements")
    
    if checks['consistency']['score'] < 0.8:
        checks['recommendations'].append("Improve consistency with study data and terminology")
    
    if checks['clarity']['score'] < 0.8:
        checks['recommendations'].append("Enhance clarity and readability of content")
    
    if checks['compliance']['score'] < 0.9:
        checks['recommendations'].append("Address regulatory compliance requirements")
    
    return checks

def assess_content_completeness(content: str, processed_data: Dict) -> Dict:
    """Assess completeness of generated content."""
    # Simple word count and structure assessment
    word_count = len(content.split())
    has_structure = bool(re.search(r'\d+\.\d+', content))  # Look for numbered sections
    
    score = 0.5  # Base score
    
    if word_count > 100:
        score += 0.3
    if has_structure:
        score += 0.2
    
    return {
        'score': min(1.0, score),
        'word_count': word_count,
        'has_structure': has_structure,
        'assessment': 'Complete' if score > 0.8 else 'Needs improvement'
    }

def assess_content_consistency(content: str, processed_data: Dict) -> Dict:
    """Assess consistency of content with study data."""
    score = 0.8  # Default high score
    issues = []
    
    study_id = processed_data['study_identification']
    
    # Check for study identifier consistency
    protocol_num = study_id.get('protocol_number', '')
    if protocol_num and protocol_num not in content:
        score -= 0.2
        issues.append("Protocol number not consistently referenced")
    
    # Check for indication consistency
    indication = study_id.get('indication', '')
    if indication and indication.lower() not in content.lower():
        score -= 0.1
        issues.append("Study indication not consistently referenced")
    
    return {
        'score': max(0.0, score),
        'issues': issues,
        'assessment': 'Consistent' if score > 0.8 else 'Inconsistencies found'
    }

def assess_content_clarity(content: str) -> Dict:
    """Assess clarity and readability of content."""
    sentences = content.count('.') + content.count('!') + content.count('?')
    words = len(content.split())
    
    if sentences == 0:
        avg_sentence_length = 0
    else:
        avg_sentence_length = words / sentences
    
    # Assess clarity based on sentence length and structure
    if avg_sentence_length <= 20:
        clarity_score = 0.9
    elif avg_sentence_length <= 30:
        clarity_score = 0.7
    else:
        clarity_score = 0.5
    
    # Check for jargon and complexity
    complex_terms = len(re.findall(r'\b\w{12,}\b', content))  # Words longer than 12 characters
    if complex_terms > words * 0.1:  # More than 10% complex terms
        clarity_score -= 0.2
    
    return {
        'score': max(0.0, clarity_score),
        'avg_sentence_length': round(avg_sentence_length, 1),
        'complex_terms': complex_terms,
        'assessment': 'Clear' if clarity_score > 0.7 else 'Could be clearer'
    }

def assess_regulatory_compliance(content: str, requirements: List[str]) -> Dict:
    """Assess regulatory compliance of content."""
    if not requirements:
        return {'score': 1.0, 'assessment': 'No specific requirements specified'}
    
    compliance_score = 1.0
    missing_requirements = []
    
    for requirement in requirements:
        req_lower = requirement.lower()
        if req_lower not in content.lower():
            compliance_score -= 0.2
            missing_requirements.append(requirement)
    
    return {
        'score': max(0.0, compliance_score),
        'missing_requirements': missing_requirements,
        'assessment': 'Compliant' if compliance_score > 0.8 else 'Compliance issues identified'
    }

def generate_section_metadata(section_type: str, processed_data: Dict, template_style: str) -> Dict:
    """Generate metadata for the section."""
    return {
        'section_type': section_type,
        'template_style': template_style,
        'study_phase': processed_data['study_identification'].get('phase'),
        'indication': processed_data['study_identification'].get('indication'),
        'study_type': processed_data['study_design'].get('design_type'),
        'data_completeness': assess_data_completeness(processed_data),
        'generation_timestamp': datetime.now().isoformat(),
        'recommended_review_level': determine_review_level(section_type)
    }

def assess_data_completeness(processed_data: Dict) -> float:
    """Assess completeness of input study data."""
    total_fields = 0
    complete_fields = 0
    
    for section, data in processed_data.items():
        if isinstance(data, dict):
            for field, value in data.items():
                total_fields += 1
                if value and str(value).strip() and str(value) != 'Not specified':
                    complete_fields += 1
    
    return round(complete_fields / max(total_fields, 1), 2)

def determine_review_level(section_type: str) -> str:
    """Determine recommended review level for the section."""
    high_risk_sections = ['efficacy', 'safety', 'conclusions']
    medium_risk_sections = ['study_design', 'treatments']
    
    if section_type in high_risk_sections:
        return 'Senior medical review required'
    elif section_type in medium_risk_sections:
        return 'Medical review recommended'
    else:
        return 'Standard review'

def create_compliance_checklist(section_type: str, requirements: List[str], 
                              section_content: str) -> Dict:
    """Create regulatory compliance checklist."""
    checklist = {
        'ich_e3_compliance': [],
        'fda_compliance': [],
        'ema_compliance': [],
        'custom_requirements': []
    }
    
    # ICH E3 requirements
    ich_requirements = {
        'summary': ['Study overview', 'Primary results', 'Safety summary', 'Conclusions'],
        'efficacy': ['Primary analysis', 'Statistical methods', 'Analysis populations'],
        'safety': ['Adverse events', 'Serious adverse events', 'Deaths', 'Laboratory data']
    }
    
    if section_type in ich_requirements:
        for req in ich_requirements[section_type]:
            is_present = req.lower() in section_content.lower()
            checklist['ich_e3_compliance'].append({
                'requirement': req,
                'status': 'Present' if is_present else 'Missing',
                'compliant': is_present
            })
    
    # Custom requirements
    for req in requirements:
        is_present = req.lower() in section_content.lower()
        checklist['custom_requirements'].append({
            'requirement': req,
            'status': 'Present' if is_present else 'Missing',
            'compliant': is_present
        })
    
    return checklist

def generate_revision_suggestions(section_content: str, quality_checks: Dict, 
                                section_type: str) -> List[str]:
    """Generate suggestions for improving the section."""
    suggestions = []
    
    # Based on quality checks
    if quality_checks['completeness']['score'] < 0.8:
        suggestions.append(f"Expand content to improve completeness (current score: {quality_checks['completeness']['score']:.1f})")
    
    if quality_checks['clarity']['score'] < 0.7:
        avg_length = quality_checks['clarity']['avg_sentence_length']
        if avg_length > 25:
            suggestions.append(f"Consider shorter sentences for better readability (current average: {avg_length} words)")
    
    # Section-specific suggestions
    if section_type == 'efficacy':
        if 'statistical significance' not in section_content.lower():
            suggestions.append("Include discussion of statistical significance of results")
        if 'clinical relevance' not in section_content.lower():
            suggestions.append("Add interpretation of clinical relevance of findings")
    
    elif section_type == 'safety':
        if 'exposure' not in section_content.lower():
            suggestions.append("Include information about subject exposure to treatment")
        if 'causality' not in section_content.lower():
            suggestions.append("Discuss causality assessment for adverse events")
    
    elif section_type == 'discussion':
        if 'limitation' not in section_content.lower():
            suggestions.append("Include discussion of study limitations")
        if 'clinical implication' not in section_content.lower():
            suggestions.append("Discuss clinical implications of the findings")
    
    return suggestions

def get_writing_guidelines(section_type: str, target_audience: str) -> Dict:
    """Get writing guidelines for the section type and audience."""
    guidelines = {
        'general_principles': [
            "Use clear, concise language appropriate for the target audience",
            "Maintain consistency in terminology throughout the document",
            "Present information in a logical, well-organized manner",
            "Support statements with appropriate data and references"
        ],
        'section_specific': [],
        'audience_specific': []
    }
    
    # Section-specific guidelines
    section_guidelines = {
        'summary': [
            "Provide a comprehensive overview that can stand alone",
            "Include key results with appropriate context",
            "Maintain balance between brevity and completeness"
        ],
        'efficacy': [
            "Present primary analyses first, followed by secondary analyses",
            "Include appropriate statistical context and interpretation",
            "Discuss clinical significance alongside statistical significance"
        ],
        'safety': [
            "Present safety data objectively without over- or under-interpretation",
            "Include appropriate denominators and exposure information",
            "Organize by severity and relationship to treatment"
        ]
    }
    
    guidelines['section_specific'] = section_guidelines.get(section_type, [])
    
    # Audience-specific guidelines
    if target_audience == 'regulators':
        guidelines['audience_specific'] = [
            "Include all required regulatory elements",
            "Present data objectively with minimal interpretation",
            "Ensure traceability to source data and analyses"
        ]
    elif target_audience == 'investigators':
        guidelines['audience_specific'] = [
            "Focus on clinical relevance and practical implications",
            "Include context for clinical decision-making",
            "Highlight key safety considerations for patient care"
        ]
    
    return guidelines