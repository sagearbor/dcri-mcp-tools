from typing import Dict, Any, List
from datetime import datetime, timedelta


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Track and validate informed consent versions across subjects in clinical trials.
    
    Example:
        Input: Subject records with consent information, current consent version, and protocol amendments
        Output: Consent compliance tracking with violations, version distribution, and reconsent requirements
    
    Parameters:
        subjects : list
            List of subject records with consent information
        current_consent_version : str
            Current approved consent version
        protocol_amendments : list, optional
            List of protocol amendments with dates requiring reconsent
        site_id : str, optional
            Site identifier for filtering subjects
        check_reconsent_required : bool, optional
            Whether to check if reconsent is needed after amendments
    """
    subjects = input_data.get('subjects', [])
    current_version = input_data.get('current_consent_version', '')
    amendments = input_data.get('protocol_amendments', [])
    site_id = input_data.get('site_id', '')
    check_reconsent = input_data.get('check_reconsent_required', True)
    
    if not subjects:
        return {
            'error': 'No subject data provided',
            'total_subjects': 0,
            'subjects_current_consent': 0,
            'subjects_outdated_consent': 0,
            'reconsent_required': [],
            'consent_violations': [],
            'version_distribution': {},
            'recommendations': ['Provide subject consent data to perform tracking']
        }
    
    if not current_version:
        return {
            'error': 'Current consent version not specified',
            'total_subjects': len(subjects),
            'subjects_current_consent': 0,
            'subjects_outdated_consent': 0,
            'reconsent_required': [],
            'consent_violations': [],
            'version_distribution': {},
            'recommendations': ['Specify current consent version for comparison']
        }
    
    # Filter subjects by site if specified
    if site_id:
        subjects = [s for s in subjects if s.get('site_id') == site_id]
    
    # Initialize tracking variables
    subjects_current = 0
    subjects_outdated = 0
    reconsent_required = []
    consent_violations = []
    version_distribution = {}
    recommendations = []
    
    # Parse amendment dates for reconsent requirements
    amendment_dates = []
    if check_reconsent and amendments:
        for amendment in amendments:
            try:
                if isinstance(amendment.get('date'), str):
                    date = datetime.strptime(amendment['date'], '%Y-%m-%d')
                    amendment_dates.append({
                        'date': date,
                        'version': amendment.get('consent_version_required', current_version),
                        'requires_reconsent': amendment.get('requires_reconsent', False)
                    })
            except (ValueError, KeyError):
                continue
    
    # Process each subject
    for subject in subjects:
        subject_id = subject.get('subject_id', 'Unknown')
        consent_version = subject.get('consent_version', '')
        consent_date = subject.get('consent_date', '')
        reconsent_date = subject.get('reconsent_date', '')
        
        # Track version distribution
        if consent_version:
            version_distribution[consent_version] = version_distribution.get(consent_version, 0) + 1
        else:
            version_distribution['Missing'] = version_distribution.get('Missing', 0) + 1
            consent_violations.append({
                'subject_id': subject_id,
                'violation_type': 'missing_consent_version',
                'description': 'Subject missing consent version information',
                'severity': 'high'
            })
            continue
        
        # Check if subject has current consent version
        if consent_version == current_version:
            subjects_current += 1
        else:
            subjects_outdated += 1
            consent_violations.append({
                'subject_id': subject_id,
                'violation_type': 'outdated_consent',
                'description': f'Subject has consent version {consent_version}, current is {current_version}',
                'severity': 'medium'
            })
        
        # Check reconsent requirements based on amendments
        if check_reconsent and consent_date:
            try:
                subject_consent_date = datetime.strptime(consent_date, '%Y-%m-%d')
                
                for amendment in amendment_dates:
                    if (amendment['requires_reconsent'] and 
                        subject_consent_date < amendment['date']):
                        
                        # Check if subject has been reconsented after amendment
                        reconsented = False
                        if reconsent_date:
                            try:
                                subject_reconsent_date = datetime.strptime(reconsent_date, '%Y-%m-%d')
                                if subject_reconsent_date >= amendment['date']:
                                    reconsented = True
                            except ValueError:
                                pass
                        
                        if not reconsented:
                            reconsent_required.append({
                                'subject_id': subject_id,
                                'current_consent_version': consent_version,
                                'required_consent_version': amendment['version'],
                                'amendment_date': amendment['date'].strftime('%Y-%m-%d'),
                                'consent_date': consent_date,
                                'days_overdue': (datetime.now() - amendment['date']).days
                            })
                            
                            consent_violations.append({
                                'subject_id': subject_id,
                                'violation_type': 'reconsent_required',
                                'description': f'Subject requires reconsent due to amendment on {amendment["date"].strftime("%Y-%m-%d")}',
                                'severity': 'high'
                            })
                            break
                            
            except ValueError:
                consent_violations.append({
                    'subject_id': subject_id,
                    'violation_type': 'invalid_consent_date',
                    'description': f'Invalid consent date format: {consent_date}',
                    'severity': 'medium'
                })
    
    # Generate recommendations
    if subjects_outdated > 0:
        recommendations.append(f'{subjects_outdated} subjects have outdated consent versions - review and update as needed')
    
    if len(reconsent_required) > 0:
        recommendations.append(f'{len(reconsent_required)} subjects require reconsent due to protocol amendments')
    
    if len(consent_violations) > 0:
        high_severity = sum(1 for v in consent_violations if v['severity'] == 'high')
        if high_severity > 0:
            recommendations.append(f'{high_severity} high-severity consent violations require immediate attention')
    
    if len(version_distribution) > 2:  # Current version + maybe one old version is normal
        recommendations.append('Multiple consent versions in use - consider standardization efforts')
    
    # Calculate compliance percentage
    total_subjects = len(subjects)
    compliance_percentage = (subjects_current / total_subjects * 100) if total_subjects > 0 else 0
    
    return {
        'total_subjects': total_subjects,
        'subjects_current_consent': subjects_current,
        'subjects_outdated_consent': subjects_outdated,
        'reconsent_required': reconsent_required,
        'consent_violations': consent_violations,
        'version_distribution': version_distribution,
        'compliance_percentage': round(compliance_percentage, 2),
        'recommendations': recommendations,
        'summary': {
            'status': 'compliant' if len(consent_violations) == 0 else 'violations_found',
            'critical_issues': len([v for v in consent_violations if v['severity'] == 'high']),
            'total_violations': len(consent_violations)
        }
    }