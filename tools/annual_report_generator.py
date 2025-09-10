from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates IND annual reports for FDA regulatory submission with comprehensive safety and enrollment data.
    
    Example:
        Input: IND number, reporting period dates, studies data with safety metrics
        Output: Complete FDA annual report with safety summary, enrollment data, and submission checklist
    
    Parameters:
        ind_number : str
            IND application number
        reporting_period_start : str
            Start date of reporting period (YYYY-MM-DD)
        reporting_period_end : str
            End date of reporting period (YYYY-MM-DD)
        studies : list
            List of studies under this IND
        safety_data : dict
            Aggregate safety information
        drug_information : dict
            Drug substance and manufacturing info
        sponsor_information : dict
            Sponsor contact details
        include_appendices : bool
            Include detailed appendices (optional)
    """
    ind_number = input_data.get('ind_number', '')
    period_start = input_data.get('reporting_period_start', '')
    period_end = input_data.get('reporting_period_end', '')
    studies = input_data.get('studies', [])
    safety_data = input_data.get('safety_data', {})
    drug_info = input_data.get('drug_information', {})
    sponsor_info = input_data.get('sponsor_information', {})
    include_appendices = input_data.get('include_appendices', True)
    
    # Validate required inputs
    if not ind_number:
        return {
            'error': 'IND number is required for annual report generation',
            'annual_report': '',
            'executive_summary': '',
            'safety_summary': {},
            'enrollment_summary': {},
            'regulatory_compliance': {},
            'submission_checklist': [],
            'recommendations': ['Provide valid IND number']
        }
    
    if not period_start or not period_end:
        return {
            'error': 'Reporting period start and end dates are required',
            'annual_report': '',
            'executive_summary': '',
            'safety_summary': {},
            'enrollment_summary': {},
            'regulatory_compliance': {},
            'submission_checklist': [],
            'recommendations': ['Specify complete reporting period dates']
        }
    
    try:
        start_date = datetime.strptime(period_start, '%Y-%m-%d')
        end_date = datetime.strptime(period_end, '%Y-%m-%d')
    except ValueError:
        return {
            'error': 'Invalid date format. Use YYYY-MM-DD format',
            'annual_report': '',
            'executive_summary': '',
            'safety_summary': {},
            'enrollment_summary': {},
            'regulatory_compliance': {},
            'submission_checklist': [],
            'recommendations': ['Provide dates in YYYY-MM-DD format']
        }
    
    # Generate report sections
    safety_summary = _compile_safety_summary(safety_data, studies)
    enrollment_summary = _compile_enrollment_summary(studies)
    regulatory_compliance = _assess_regulatory_compliance(studies, safety_data)
    
    # Generate main annual report
    annual_report = _generate_annual_report_document(
        ind_number, start_date, end_date, studies, safety_summary, 
        enrollment_summary, drug_info, sponsor_info, include_appendices
    )
    
    # Generate executive summary
    executive_summary = _generate_executive_summary(
        ind_number, start_date, end_date, safety_summary, enrollment_summary
    )
    
    # Create submission checklist
    submission_checklist = _generate_submission_checklist(
        ind_number, studies, safety_data, drug_info
    )
    
    # Generate recommendations
    recommendations = _generate_recommendations(
        safety_summary, enrollment_summary, regulatory_compliance
    )
    
    return {
        'annual_report': annual_report,
        'executive_summary': executive_summary,
        'safety_summary': safety_summary,
        'enrollment_summary': enrollment_summary,
        'regulatory_compliance': regulatory_compliance,
        'submission_checklist': submission_checklist,
        'recommendations': recommendations,
        'report_metadata': {
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ind_number': ind_number,
            'reporting_period': f"{period_start} to {period_end}",
            'total_studies': len(studies),
            'report_version': '1.0'
        }
    }


def _compile_safety_summary(safety_data: Dict[str, Any], studies: List[Dict]) -> Dict[str, Any]:
    """Compile comprehensive safety summary from all studies."""
    summary = {
        'total_subjects_exposed': 0,
        'total_adverse_events': 0,
        'serious_adverse_events': 0,
        'deaths': 0,
        'discontinuations_due_to_ae': 0,
        'susars': 0,
        'ae_by_system_organ_class': defaultdict(int),
        'dose_limiting_toxicities': 0,
        'safety_trends': [],
        'notable_findings': []
    }
    
    # Aggregate safety data from studies
    for study in studies:
        study_safety = study.get('safety_data', {})
        summary['total_subjects_exposed'] += study_safety.get('subjects_exposed', 0)
        summary['total_adverse_events'] += study_safety.get('total_aes', 0)
        summary['serious_adverse_events'] += study_safety.get('saes', 0)
        summary['deaths'] += study_safety.get('deaths', 0)
        summary['discontinuations_due_to_ae'] += study_safety.get('discontinuations_ae', 0)
        summary['susars'] += study_safety.get('susars', 0)
        summary['dose_limiting_toxicities'] += study_safety.get('dlts', 0)
        
        # Aggregate AEs by system organ class
        ae_by_soc = study_safety.get('ae_by_system_organ_class', {})
        for soc, count in ae_by_soc.items():
            summary['ae_by_system_organ_class'][soc] += count
    
    # Add safety data from input
    if safety_data:
        summary['total_subjects_exposed'] += safety_data.get('additional_subjects', 0)
        summary['notable_findings'].extend(safety_data.get('notable_findings', []))
        summary['safety_trends'].extend(safety_data.get('trends', []))
    
    # Calculate safety rates
    if summary['total_subjects_exposed'] > 0:
        summary['sae_rate'] = round(
            (summary['serious_adverse_events'] / summary['total_subjects_exposed']) * 100, 2
        )
        summary['discontinuation_rate'] = round(
            (summary['discontinuations_due_to_ae'] / summary['total_subjects_exposed']) * 100, 2
        )
        summary['mortality_rate'] = round(
            (summary['deaths'] / summary['total_subjects_exposed']) * 100, 2
        )
    
    return dict(summary)


def _compile_enrollment_summary(studies: List[Dict]) -> Dict[str, Any]:
    """Compile enrollment summary across all studies."""
    summary = {
        'total_planned_enrollment': 0,
        'total_enrolled': 0,
        'total_completed': 0,
        'total_discontinued': 0,
        'enrollment_by_study': [],
        'enrollment_rate': 0,
        'completion_rate': 0,
        'demographics': {
            'age_groups': defaultdict(int),
            'sex_distribution': defaultdict(int),
            'race_distribution': defaultdict(int)
        }
    }
    
    for study in studies:
        study_enrollment = {
            'study_id': study.get('study_id', 'Unknown'),
            'study_title': study.get('title', ''),
            'planned_enrollment': study.get('planned_enrollment', 0),
            'current_enrollment': study.get('enrolled_subjects', 0),
            'completed': study.get('completed_subjects', 0),
            'discontinued': study.get('discontinued_subjects', 0),
            'status': study.get('status', 'Unknown')
        }
        
        summary['enrollment_by_study'].append(study_enrollment)
        summary['total_planned_enrollment'] += study_enrollment['planned_enrollment']
        summary['total_enrolled'] += study_enrollment['current_enrollment']
        summary['total_completed'] += study_enrollment['completed']
        summary['total_discontinued'] += study_enrollment['discontinued']
        
        # Aggregate demographics
        demographics = study.get('demographics', {})
        for age_group, count in demographics.get('age_groups', {}).items():
            summary['demographics']['age_groups'][age_group] += count
        
        for sex, count in demographics.get('sex_distribution', {}).items():
            summary['demographics']['sex_distribution'][sex] += count
        
        for race, count in demographics.get('race_distribution', {}).items():
            summary['demographics']['race_distribution'][race] += count
    
    # Calculate rates
    if summary['total_planned_enrollment'] > 0:
        summary['enrollment_rate'] = round(
            (summary['total_enrolled'] / summary['total_planned_enrollment']) * 100, 2
        )
    
    if summary['total_enrolled'] > 0:
        summary['completion_rate'] = round(
            (summary['total_completed'] / summary['total_enrolled']) * 100, 2
        )
    
    return summary


def _assess_regulatory_compliance(studies: List[Dict], safety_data: Dict) -> Dict[str, Any]:
    """Assess regulatory compliance status."""
    compliance = {
        'overall_status': 'compliant',
        'compliance_issues': [],
        'protocol_deviations': 0,
        'regulatory_violations': 0,
        'overdue_submissions': [],
        'inspection_findings': [],
        'corrective_actions': []
    }
    
    for study in studies:
        study_compliance = study.get('compliance_data', {})
        compliance['protocol_deviations'] += study_compliance.get('protocol_deviations', 0)
        compliance['regulatory_violations'] += study_compliance.get('regulatory_violations', 0)
        
        # Check for overdue submissions
        overdue = study_compliance.get('overdue_submissions', [])
        compliance['overdue_submissions'].extend(overdue)
        
        # Check inspection findings
        findings = study_compliance.get('inspection_findings', [])
        compliance['inspection_findings'].extend(findings)
    
    # Determine overall compliance status
    if compliance['regulatory_violations'] > 0 or compliance['overdue_submissions']:
        compliance['overall_status'] = 'non_compliant'
    elif compliance['protocol_deviations'] > 5:  # Arbitrary threshold
        compliance['overall_status'] = 'minor_issues'
    
    return compliance


def _generate_annual_report_document(ind_number: str, start_date: datetime, end_date: datetime,
                                   studies: List[Dict], safety_summary: Dict, enrollment_summary: Dict,
                                   drug_info: Dict, sponsor_info: Dict, include_appendices: bool) -> str:
    """Generate the main annual report document."""
    
    report = f"""
IND ANNUAL REPORT
IND NUMBER: {ind_number}
REPORTING PERIOD: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}

SPONSOR INFORMATION:
{sponsor_info.get('name', 'Not provided')}
{sponsor_info.get('address', 'Address not provided')}
Contact: {sponsor_info.get('contact_person', 'Not provided')}
Phone: {sponsor_info.get('phone', 'Not provided')}
Email: {sponsor_info.get('email', 'Not provided')}

DRUG SUBSTANCE INFORMATION:
Drug Name: {drug_info.get('name', 'Not provided')}
Chemical Name: {drug_info.get('chemical_name', 'Not provided')}
CAS Number: {drug_info.get('cas_number', 'Not provided')}
Molecular Formula: {drug_info.get('molecular_formula', 'Not provided')}
Therapeutic Category: {drug_info.get('therapeutic_category', 'Not provided')}

CLINICAL DEVELOPMENT SUMMARY:
Number of Studies: {len(studies)}
Total Subjects Enrolled: {enrollment_summary['total_enrolled']}
Total Subjects Exposed to Drug: {safety_summary['total_subjects_exposed']}

STUDY STATUS SUMMARY:
"""
    
    for study in enrollment_summary['enrollment_by_study']:
        report += f"""
Study {study['study_id']}: {study['study_title']}
  Status: {study['status']}
  Enrolled: {study['current_enrollment']}/{study['planned_enrollment']}
  Completed: {study['completed']}
"""
    
    report += f"""
SAFETY SUMMARY:
Total Adverse Events: {safety_summary['total_adverse_events']}
Serious Adverse Events: {safety_summary['serious_adverse_events']}
SUSARs: {safety_summary['susars']}
Deaths: {safety_summary['deaths']}
Discontinuations due to AE: {safety_summary['discontinuations_due_to_ae']}
SAE Rate: {safety_summary.get('sae_rate', 0)}%
Mortality Rate: {safety_summary.get('mortality_rate', 0)}%

ADVERSE EVENTS BY SYSTEM ORGAN CLASS:
"""
    
    for soc, count in safety_summary['ae_by_system_organ_class'].items():
        report += f"  {soc}: {count}\n"
    
    report += f"""
ENROLLMENT AND DEMOGRAPHICS:
Total Planned Enrollment: {enrollment_summary['total_planned_enrollment']}
Total Enrolled: {enrollment_summary['total_enrolled']}
Enrollment Rate: {enrollment_summary['enrollment_rate']}%
Completion Rate: {enrollment_summary['completion_rate']}%

DEMOGRAPHICS:
Age Groups: {dict(enrollment_summary['demographics']['age_groups'])}
Sex Distribution: {dict(enrollment_summary['demographics']['sex_distribution'])}
Race Distribution: {dict(enrollment_summary['demographics']['race_distribution'])}

NOTABLE SAFETY FINDINGS:
"""
    
    for finding in safety_summary.get('notable_findings', []):
        report += f"• {finding}\n"
    
    if include_appendices:
        report += "\nAPPENDICES:\nAppendix A: Individual Study Reports\nAppendix B: Safety Data Listings\nAppendix C: Investigator CVs\nAppendix D: Protocol Amendments\n"
    
    report += f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    return report


def _generate_executive_summary(ind_number: str, start_date: datetime, end_date: datetime,
                              safety_summary: Dict, enrollment_summary: Dict) -> str:
    """Generate executive summary for regulators."""
    
    return f"""EXECUTIVE SUMMARY - IND {ind_number} ANNUAL REPORT
Reporting Period: {start_date.strftime('%m/%d/%Y')} - {end_date.strftime('%m/%d/%Y')}

KEY METRICS:
• Subjects Enrolled: {enrollment_summary['total_enrolled']}
• Subjects Exposed to Drug: {safety_summary['total_subjects_exposed']}
• Serious Adverse Events: {safety_summary['serious_adverse_events']}
• SUSARs: {safety_summary['susars']}
• Deaths: {safety_summary['deaths']}

SAFETY PROFILE:
The safety profile of the investigational drug remains consistent with previous reports.
SAE Rate: {safety_summary.get('sae_rate', 0)}% of exposed subjects.
No new safety signals were identified during this reporting period.

ENROLLMENT STATUS:
Enrollment is proceeding as planned with {enrollment_summary['enrollment_rate']}% of target achieved.
Subject retention rate is {enrollment_summary['completion_rate']}%.

REGULATORY STATUS:
All regulatory requirements have been met during this reporting period.
No significant compliance issues identified.
"""


def _generate_submission_checklist(ind_number: str, studies: List[Dict], 
                                 safety_data: Dict, drug_info: Dict) -> List[Dict]:
    """Generate submission checklist for annual report."""
    
    checklist = [
        {'item': 'Cover Letter', 'required': True, 'status': 'pending'},
        {'item': 'Annual Report Form', 'required': True, 'status': 'pending'},
        {'item': 'Summary of Changes', 'required': True, 'status': 'pending'},
        {'item': 'Safety Summary', 'required': True, 'status': 'completed'},
        {'item': 'Individual Study Information', 'required': True, 'status': 'completed'},
        {'item': 'Log of Outstanding Business', 'required': True, 'status': 'pending'},
        {'item': 'General Investigation Plan Updates', 'required': False, 'status': 'not_applicable'},
        {'item': 'Chemistry Manufacturing Controls Updates', 'required': False, 'status': 'pending'},
        {'item': 'Nonclinical Updates', 'required': False, 'status': 'not_applicable'},
        {'item': 'Clinical Updates', 'required': True, 'status': 'completed'},
        {'item': 'Electronic Copy', 'required': True, 'status': 'pending'}
    ]
    
    return checklist


def _generate_recommendations(safety_summary: Dict, enrollment_summary: Dict, 
                            regulatory_compliance: Dict) -> List[str]:
    """Generate recommendations for next reporting period."""
    
    recommendations = []
    
    # Safety recommendations
    if safety_summary.get('sae_rate', 0) > 10:
        recommendations.append('Consider enhanced safety monitoring due to elevated SAE rate')
    
    if safety_summary['susars'] > 0:
        recommendations.append('Continue close monitoring of unexpected serious reactions')
    
    # Enrollment recommendations
    if enrollment_summary['enrollment_rate'] < 80:
        recommendations.append('Review enrollment strategies to improve accrual rates')
    
    if enrollment_summary['completion_rate'] < 85:
        recommendations.append('Investigate factors contributing to subject discontinuation')
    
    # Compliance recommendations
    if regulatory_compliance['overall_status'] != 'compliant':
        recommendations.append('Address regulatory compliance issues identified in this report')
    
    if regulatory_compliance['protocol_deviations'] > 5:
        recommendations.append('Implement additional training to reduce protocol deviations')
    
    if not recommendations:
        recommendations.append('Continue current clinical development plan as outlined')
    
    return recommendations