from typing import Dict, Any, List
from datetime import datetime, timedelta


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format SUSARs (Suspected Unexpected Serious Adverse Reactions) for regulatory submission.
    Validates SUSAR data and generates formatted reports for regulatory authorities.
    
    Args:
        input_data: Dict containing:
            - susar_data (dict): Core SUSAR information
            - format_type (str): 'E2B_XML', 'CIOMS', 'FDA_3500A', 'EMA_EUDRAVIGILANCE'
            - regulatory_authority (str): Target regulatory authority
            - urgency (str): 'expedited' (7/15 days) or 'routine'
            - include_narrative (bool, optional): Include detailed narrative
            - blinding_status (str, optional): 'blinded', 'unblinded', 'emergency_unblinding'
            - reference_date (str, optional): Reference date for timeline calculations (YYYY-MM-DD)
    
    Returns:
        Dict containing:
            - formatted_report (str): Formatted SUSAR report
            - validation_status (str): 'valid', 'invalid', 'warnings'
            - validation_errors (list): Critical validation errors
            - validation_warnings (list): Non-critical warnings
            - submission_deadline (str): Regulatory submission deadline
            - report_metadata (dict): Report generation metadata
            - regulatory_requirements (dict): Authority-specific requirements met
    """
    susar_data = input_data.get('susar_data', {})
    format_type = input_data.get('format_type', 'CIOMS').upper()
    authority = input_data.get('regulatory_authority', '').upper()
    urgency = input_data.get('urgency', 'expedited').lower()
    include_narrative = input_data.get('include_narrative', True)
    blinding_status = input_data.get('blinding_status', 'blinded')
    
    # Parse reference date if provided, otherwise use current date
    reference_date_str = input_data.get('reference_date')
    if reference_date_str:
        try:
            reference_date = datetime.strptime(reference_date_str, '%Y-%m-%d')
        except ValueError:
            reference_date = datetime.now()
    else:
        reference_date = datetime.now()
    
    if not susar_data:
        return {
            'error': 'No SUSAR data provided',
            'formatted_report': '',
            'validation_status': 'invalid',
            'validation_errors': ['Missing SUSAR data'],
            'validation_warnings': [],
            'submission_deadline': '',
            'report_metadata': {},
            'regulatory_requirements': {}
        }
    
    # Validate required SUSAR fields
    validation_errors = []
    validation_warnings = []
    
    # Core required fields
    required_fields = [
        'patient_identifier', 'age', 'sex', 'adverse_event_description',
        'onset_date', 'event_outcome', 'drug_name', 'dose', 'indication',
        'concomitant_medications', 'medical_history', 'reporter_information'
    ]
    
    for field in required_fields:
        if not susar_data.get(field):
            validation_errors.append(f'Missing required field: {field}')
    
    # Validate specific field formats
    if susar_data.get('onset_date'):
        try:
            onset_date = datetime.strptime(susar_data['onset_date'], '%Y-%m-%d')
        except ValueError:
            validation_errors.append('Invalid onset_date format (should be YYYY-MM-DD)')
            onset_date = reference_date
    else:
        onset_date = reference_date
    
    # Check for late reporting
    days_since_onset = (reference_date - onset_date).days
    if urgency == 'expedited':
        if days_since_onset > 15:
            validation_warnings.append(f'SUSAR is {days_since_onset} days old - may exceed expedited reporting timeline')
    
    # Validate seriousness criteria
    seriousness_criteria = susar_data.get('seriousness_criteria', [])
    if not seriousness_criteria:
        validation_errors.append('Missing seriousness criteria - required for SUSAR classification')
    
    # Validate expectedness assessment
    expectedness = susar_data.get('expectedness', '').lower()
    if expectedness not in ['expected', 'unexpected']:
        validation_errors.append('Expectedness must be specified as "expected" or "unexpected"')
    elif expectedness == 'expected':
        validation_warnings.append('Event marked as expected - confirm this qualifies as SUSAR')
    
    # Calculate submission deadline
    submission_deadline = _calculate_submission_deadline(onset_date, urgency, authority)
    
    # Generate formatted report based on format type
    if validation_errors:
        validation_status = 'invalid'
        formatted_report = ''
    else:
        validation_status = 'warnings' if validation_warnings else 'valid'
        formatted_report = _generate_formatted_report(
            susar_data, format_type, authority, include_narrative, blinding_status
        )
    
    # Check regulatory authority specific requirements
    regulatory_requirements = _check_regulatory_requirements(susar_data, authority)
    
    # Generate report metadata
    report_metadata = {
        'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'format_type': format_type,
        'regulatory_authority': authority,
        'urgency_classification': urgency,
        'report_version': '1.0',
        'blinding_status': blinding_status,
        'word_count': len(formatted_report.split()) if formatted_report else 0
    }
    
    return {
        'formatted_report': formatted_report,
        'validation_status': validation_status,
        'validation_errors': validation_errors,
        'validation_warnings': validation_warnings,
        'submission_deadline': submission_deadline,
        'report_metadata': report_metadata,
        'regulatory_requirements': regulatory_requirements,
        'summary': {
            'is_ready_for_submission': validation_status == 'valid',
            'critical_errors': len(validation_errors),
            'warnings': len(validation_warnings),
            'days_until_deadline': (datetime.strptime(submission_deadline, '%Y-%m-%d') - datetime.now()).days if submission_deadline else None
        }
    }


def _calculate_submission_deadline(onset_date: datetime, urgency: str, authority: str) -> str:
    """Calculate regulatory submission deadline based on authority requirements."""
    if urgency == 'expedited':
        if authority in ['FDA', 'USFDA']:
            # FDA requires 15 calendar days for expedited reports
            deadline = onset_date + timedelta(days=15)
        elif authority in ['EMA', 'MHRA', 'EU']:
            # EU requires 15 calendar days for fatal/life-threatening, 15 days for others
            deadline = onset_date + timedelta(days=15)
        else:
            # Default to 15 days for expedited reporting
            deadline = onset_date + timedelta(days=15)
    else:
        # Routine reporting is typically annual or periodic
        deadline = onset_date + timedelta(days=365)
    
    return deadline.strftime('%Y-%m-%d')


def _generate_formatted_report(susar_data: Dict[str, Any], format_type: str, 
                              authority: str, include_narrative: bool, blinding_status: str) -> str:
    """Generate formatted SUSAR report based on specified format."""
    
    if format_type == 'CIOMS':
        return _generate_cioms_report(susar_data, include_narrative, blinding_status)
    elif format_type == 'E2B_XML':
        return _generate_e2b_xml_report(susar_data, authority)
    elif format_type == 'FDA_3500A':
        return _generate_fda_3500a_report(susar_data)
    elif format_type == 'EMA_EUDRAVIGILANCE':
        return _generate_ema_report(susar_data)
    else:
        return _generate_generic_report(susar_data, include_narrative)


def _generate_cioms_report(susar_data: Dict[str, Any], include_narrative: bool, blinding_status: str) -> str:
    """Generate CIOMS I format report."""
    report = f"""CIOMS I - INTERNATIONAL REPORTING OF PERIODIC DRUG-SAFETY UPDATE SUMMARIES
    
PATIENT INFORMATION:
Patient Identifier: {susar_data.get('patient_identifier', 'Not provided')}
Age: {susar_data.get('age', 'Unknown')} years
Sex: {susar_data.get('sex', 'Unknown')}
Weight: {susar_data.get('weight', 'Not provided')} kg

ADVERSE EVENT INFORMATION:
Event Description: {susar_data.get('adverse_event_description', 'Not provided')}
Onset Date: {susar_data.get('onset_date', 'Not provided')}
Event Outcome: {susar_data.get('event_outcome', 'Unknown')}
Seriousness Criteria: {', '.join(susar_data.get('seriousness_criteria', []))}

DRUG INFORMATION:
Drug Name: {susar_data.get('drug_name', 'Not provided')}
Dose: {susar_data.get('dose', 'Not provided')}
Route: {susar_data.get('route', 'Not provided')}
Indication: {susar_data.get('indication', 'Not provided')}

MEDICAL HISTORY:
{susar_data.get('medical_history', 'None reported')}

CONCOMITANT MEDICATIONS:
{susar_data.get('concomitant_medications', 'None reported')}

REPORTER INFORMATION:
{susar_data.get('reporter_information', 'Not provided')}

BLINDING STATUS: {blinding_status.upper()}
"""
    
    if include_narrative:
        narrative = susar_data.get('narrative', 'No detailed narrative provided.')
        report += f"\nDETAILED NARRATIVE:\n{narrative}\n"
    
    report += f"\nREPORT GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return report


def _generate_e2b_xml_report(susar_data: Dict[str, Any], authority: str) -> str:
    """Generate E2B XML format structure (simplified)."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<ichicsr xmlns="http://www.meddra.org/hl7v3">
    <messagenumber>{datetime.now().strftime('%Y%m%d%H%M%S')}</messagenumber>
    <messagesender>
        <messageSenderIdentifier>DCRI_CLINICAL_TRIAL</messageSenderIdentifier>
    </messagesender>
    <safetyreport>
        <patient>
            <patientcharacteristic>
                <patientagecode>{susar_data.get('age', '')}</patientagecode>
                <patientsex>{susar_data.get('sex', '').upper()}</patientsex>
            </patientcharacteristic>
        </patient>
        <summary>
            <reporttype>1</reporttype>
            <primarysource>1</primarysource>
            <reportdate>{susar_data.get('onset_date', datetime.now().strftime('%Y%m%d'))}</reportdate>
        </summary>
    </safetyreport>
</ichicsr>"""


def _generate_fda_3500a_report(susar_data: Dict[str, Any]) -> str:
    """Generate FDA Form 3500A format."""
    return f"""FDA FORM 3500A - ADVERSE EVENT REPORT

PATIENT INFORMATION (A):
1. Patient Identifier: {susar_data.get('patient_identifier', '')}
2. Age: {susar_data.get('age', '')} Sex: {susar_data.get('sex', '')}
3. Weight: {susar_data.get('weight', '')} lbs

ADVERSE EVENT (B):
4. Date of Event: {susar_data.get('onset_date', '')}
5. Event Description: {susar_data.get('adverse_event_description', '')}
6. Outcome: {susar_data.get('event_outcome', '')}

SUSPECT PRODUCT (C):
7. Name: {susar_data.get('drug_name', '')}
8. Dose: {susar_data.get('dose', '')}
9. Route: {susar_data.get('route', '')}

INITIAL REPORTER (D):
10. Reporter: {susar_data.get('reporter_information', '')}
11. Report Date: {datetime.now().strftime('%m/%d/%Y')}
"""


def _generate_ema_report(susar_data: Dict[str, Any]) -> str:
    """Generate EMA EudraVigilance format."""
    return f"""EMA EUDRAVIGILANCE REPORT

Subject: {susar_data.get('patient_identifier', 'Unknown')}
Age/Sex: {susar_data.get('age', 'Unknown')}/{susar_data.get('sex', 'Unknown')}
Event: {susar_data.get('adverse_event_description', '')}
Date of Onset: {susar_data.get('onset_date', '')}
Product: {susar_data.get('drug_name', '')}
Dose: {susar_data.get('dose', '')}
Outcome: {susar_data.get('event_outcome', '')}

Medical History: {susar_data.get('medical_history', 'None')}
Concomitant Medications: {susar_data.get('concomitant_medications', 'None')}

Reporter: {susar_data.get('reporter_information', '')}
Report Date: {datetime.now().strftime('%d/%m/%Y')}
"""


def _generate_generic_report(susar_data: Dict[str, Any], include_narrative: bool) -> str:
    """Generate generic SUSAR report format."""
    report = f"""SUSPECTED UNEXPECTED SERIOUS ADVERSE REACTION (SUSAR) REPORT

PATIENT: {susar_data.get('patient_identifier', 'Unknown')}
AGE/SEX: {susar_data.get('age', 'Unknown')}/{susar_data.get('sex', 'Unknown')}

ADVERSE EVENT: {susar_data.get('adverse_event_description', '')}
ONSET DATE: {susar_data.get('onset_date', '')}
OUTCOME: {susar_data.get('event_outcome', '')}

SUSPECT DRUG: {susar_data.get('drug_name', '')}
DOSE/ROUTE: {susar_data.get('dose', '')}/{susar_data.get('route', '')}

MEDICAL HISTORY: {susar_data.get('medical_history', 'None reported')}
CONCOMITANT MEDS: {susar_data.get('concomitant_medications', 'None reported')}
"""
    
    if include_narrative:
        report += f"\nNARRATIVE: {susar_data.get('narrative', 'None provided')}"
    
    return report


def _check_regulatory_requirements(susar_data: Dict[str, Any], authority: str) -> Dict[str, Any]:
    """Check authority-specific regulatory requirements."""
    requirements = {
        'authority': authority,
        'requirements_met': [],
        'requirements_missing': []
    }
    
    if authority in ['FDA', 'USFDA']:
        # FDA specific requirements
        if susar_data.get('patient_identifier'):
            requirements['requirements_met'].append('Patient identifier present')
        else:
            requirements['requirements_missing'].append('Patient identifier required by FDA')
            
        if susar_data.get('adverse_event_description'):
            requirements['requirements_met'].append('AE description present')
        else:
            requirements['requirements_missing'].append('Detailed AE description required')
    
    elif authority in ['EMA', 'EU', 'MHRA']:
        # EMA specific requirements
        if susar_data.get('onset_date'):
            requirements['requirements_met'].append('Event onset date documented')
        else:
            requirements['requirements_missing'].append('Event onset date mandatory for EMA')
    
    return requirements