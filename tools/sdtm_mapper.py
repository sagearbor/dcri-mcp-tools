"""
SDTM Mapper Tool
Maps raw clinical trial data to SDTM (Study Data Tabulation Model) domains
Supports standard CDISC SDTM domains and custom mappings
"""

import csv
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from io import StringIO


def run(input_data: dict) -> dict:
    """
    Maps raw data to SDTM domains based on mapping specifications
    
    Args:
        input_data: Dictionary containing:
            - raw_data: Raw data as CSV string
            - mapping_config: SDTM mapping configuration
            - target_domain: Target SDTM domain (DM, AE, CM, etc.)
            - validation_mode: 'lenient' or 'strict' (default: 'lenient')
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating if mapping succeeded
            - sdtm_data: Mapped SDTM data as list of dictionaries
            - errors: List of mapping errors
            - warnings: List of mapping warnings
            - statistics: Mapping statistics
            - domain_compliance: SDTM compliance metrics
    """
    try:
        raw_data = input_data.get('raw_data', '')
        mapping_config = input_data.get('mapping_config', {})
        target_domain = input_data.get('target_domain', '').upper()
        validation_mode = input_data.get('validation_mode', 'lenient')
        
        if not raw_data:
            return {
                'success': False,
                'sdtm_data': [],
                'errors': ['No raw data provided'],
                'warnings': [],
                'statistics': {},
                'domain_compliance': {}
            }
        
        if not mapping_config:
            return {
                'success': False,
                'sdtm_data': [],
                'errors': ['No mapping configuration provided'],
                'warnings': [],
                'statistics': {},
                'domain_compliance': {}
            }
        
        if not target_domain:
            return {
                'success': False,
                'sdtm_data': [],
                'errors': ['No target SDTM domain specified'],
                'warnings': [],
                'statistics': {},
                'domain_compliance': {}
            }
        
        errors = []
        warnings = []
        statistics = {
            'total_records': 0,
            'mapped_records': 0,
            'failed_records': 0,
            'missing_required_fields': 0,
            'derived_fields': 0,
            'controlled_terms_violations': 0,
            'mapping_efficiency': 0.0
        }
        
        # Parse raw data
        csv_reader = csv.DictReader(StringIO(raw_data))
        raw_records = list(csv_reader)
        statistics['total_records'] = len(raw_records)
        
        if not raw_records:
            return {
                'success': False,
                'sdtm_data': [],
                'errors': ['Raw data is empty'],
                'warnings': [],
                'statistics': statistics,
                'domain_compliance': {}
            }
        
        # Get SDTM domain specification
        domain_spec = get_sdtm_domain_spec(target_domain)
        if not domain_spec:
            return {
                'success': False,
                'sdtm_data': [],
                'errors': [f'Unsupported SDTM domain: {target_domain}'],
                'warnings': [],
                'statistics': statistics,
                'domain_compliance': {}
            }
        
        # Validate mapping configuration
        config_validation = validate_mapping_config(mapping_config, domain_spec, target_domain)
        errors.extend(config_validation['errors'])
        warnings.extend(config_validation['warnings'])
        
        # Map data
        sdtm_records = []
        for i, raw_record in enumerate(raw_records):
            try:
                mapped_record = map_record(
                    raw_record, mapping_config, domain_spec, target_domain
                )
                
                # Validate mapped record
                validation_result = validate_sdtm_record(mapped_record, domain_spec, validation_mode)
                
                if validation_result['valid']:
                    sdtm_records.append(mapped_record)
                    statistics['mapped_records'] += 1
                    statistics['derived_fields'] += validation_result['derived_fields']
                else:
                    statistics['failed_records'] += 1
                    for error in validation_result['errors']:
                        errors.append(f"Record {i+1}: {error}")
                
                # Add warnings
                for warning in validation_result['warnings']:
                    warnings.append(f"Record {i+1}: {warning}")
                
                statistics['missing_required_fields'] += validation_result['missing_required']
                statistics['controlled_terms_violations'] += validation_result['ct_violations']
                
            except Exception as e:
                errors.append(f"Record {i+1}: Mapping failed - {str(e)}")
                statistics['failed_records'] += 1
        
        # Calculate mapping efficiency
        statistics['mapping_efficiency'] = (statistics['mapped_records'] / statistics['total_records'] * 100) if statistics['total_records'] > 0 else 0
        
        # Generate domain compliance metrics
        domain_compliance = generate_compliance_metrics(sdtm_records, domain_spec, target_domain)
        
        # Determine success
        success = (
            statistics['failed_records'] == 0 if validation_mode == 'strict' 
            else statistics['mapped_records'] > 0
        )
        
        return {
            'success': success,
            'sdtm_data': sdtm_records,
            'errors': errors[:100],  # Limit to prevent huge responses
            'warnings': warnings[:50],
            'statistics': statistics,
            'domain_compliance': domain_compliance,
            'mapping_summary': {
                'target_domain': target_domain,
                'mapping_rate': f"{statistics['mapping_efficiency']:.2f}%",
                'total_errors': len(errors),
                'total_warnings': len(warnings),
                'compliance_score': domain_compliance.get('overall_score', 0)
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'sdtm_data': [],
            'errors': [f"SDTM mapping failed: {str(e)}"],
            'warnings': [],
            'statistics': {},
            'domain_compliance': {}
        }


def get_sdtm_domain_spec(domain: str) -> Dict[str, Any]:
    """Get SDTM domain specification"""
    
    # Standard SDTM domain specifications
    specs = {
        'DM': {  # Demographics
            'required_vars': ['STUDYID', 'DOMAIN', 'USUBJID', 'SUBJID'],
            'expected_vars': ['RFSTDTC', 'RFENDTC', 'SITEID', 'AGE', 'AGEU', 'SEX', 'RACE', 'ETHNIC'],
            'controlled_terms': {
                'SEX': ['M', 'F', 'U', 'UNDIFFERENTIATED'],
                'AGEU': ['YEARS', 'MONTHS', 'WEEKS', 'DAYS'],
                'RACE': ['WHITE', 'BLACK OR AFRICAN AMERICAN', 'ASIAN', 'AMERICAN INDIAN OR ALASKA NATIVE', 'NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER', 'OTHER', 'MULTIPLE', 'UNKNOWN'],
                'ETHNIC': ['HISPANIC OR LATINO', 'NOT HISPANIC OR LATINO', 'NOT REPORTED', 'UNKNOWN']
            },
            'derived_vars': ['RFSTDTC', 'RFENDTC', 'AGEU'],
            'domain_key': 'USUBJID'
        },
        'AE': {  # Adverse Events
            'required_vars': ['STUDYID', 'DOMAIN', 'USUBJID', 'AESEQ'],
            'expected_vars': ['AETERM', 'AEDECOD', 'AEBODSYS', 'AESEV', 'AESER', 'AEREL', 'AEACN', 'AEOUT', 'AESTDTC', 'AEENDTC'],
            'controlled_terms': {
                'AESEV': ['MILD', 'MODERATE', 'SEVERE'],
                'AESER': ['Y', 'N'],
                'AEREL': ['RELATED', 'NOT RELATED', 'POSSIBLY RELATED', 'PROBABLY RELATED'],
                'AEACN': ['DOSE NOT CHANGED', 'DOSE REDUCED', 'DOSE INCREASED', 'DRUG INTERRUPTED', 'DRUG WITHDRAWN', 'UNKNOWN', 'NOT APPLICABLE'],
                'AEOUT': ['RECOVERED/RESOLVED', 'RECOVERING/RESOLVING', 'NOT RECOVERED/NOT RESOLVED', 'RECOVERED/RESOLVED WITH SEQUELAE', 'FATAL', 'UNKNOWN']
            },
            'derived_vars': ['AESEQ', 'AEDECOD', 'AEBODSYS'],
            'domain_key': ['USUBJID', 'AESEQ']
        },
        'CM': {  # Concomitant Medications
            'required_vars': ['STUDYID', 'DOMAIN', 'USUBJID', 'CMSEQ'],
            'expected_vars': ['CMTRT', 'CMDECOD', 'CMATC1', 'CMATC2', 'CMATC3', 'CMATC4', 'CMDOSE', 'CMDOSU', 'CMDOSFRM', 'CMDOSFRQ', 'CMROUTE', 'CMSTDTC', 'CMENDTC'],
            'controlled_terms': {
                'CMDOSU': ['ng', 'ug', 'mg', 'g', 'ng/kg', 'ug/kg', 'mg/kg', 'g/kg'],
                'CMDOSFRM': ['TABLET', 'CAPSULE', 'SOLUTION', 'INJECTION', 'CREAM', 'OINTMENT'],
                'CMROUTE': ['ORAL', 'INTRAVENOUS', 'INTRAMUSCULAR', 'SUBCUTANEOUS', 'TOPICAL', 'INHALATION']
            },
            'derived_vars': ['CMSEQ', 'CMDECOD'],
            'domain_key': ['USUBJID', 'CMSEQ']
        },
        'VS': {  # Vital Signs
            'required_vars': ['STUDYID', 'DOMAIN', 'USUBJID', 'VSSEQ'],
            'expected_vars': ['VSTESTCD', 'VSTEST', 'VSCAT', 'VSPOS', 'VSORRES', 'VSORRESU', 'VSSTRESC', 'VSSTRESN', 'VSSTRESU', 'VSSTAT', 'VSDTC'],
            'controlled_terms': {
                'VSTESTCD': ['SYSBP', 'DIABP', 'PULSE', 'RESP', 'TEMP', 'HEIGHT', 'WEIGHT'],
                'VSPOS': ['SUPINE', 'SITTING', 'STANDING', 'SEMI-RECUMBENT'],
                'VSORRESU': ['mmHg', 'beats/min', 'breaths/min', 'C', 'F', 'cm', 'kg'],
                'VSSTRESU': ['mmHg', 'beats/min', 'breaths/min', 'C', 'F', 'cm', 'kg'],
                'VSSTAT': ['NOT DONE', 'NOT AVAILABLE']
            },
            'derived_vars': ['VSSEQ', 'VSTEST', 'VSSTRESC', 'VSSTRESN'],
            'domain_key': ['USUBJID', 'VSSEQ']
        }
    }
    
    return specs.get(domain, {})


def validate_mapping_config(config: dict, domain_spec: dict, domain: str) -> dict:
    """Validate mapping configuration"""
    errors = []
    warnings = []
    
    if 'mappings' not in config:
        errors.append("Mapping configuration missing 'mappings' section")
        return {'errors': errors, 'warnings': warnings}
    
    mappings = config['mappings']
    required_vars = domain_spec.get('required_vars', [])
    
    # Check if required SDTM variables have mappings
    for var in required_vars:
        if var not in mappings and var not in ['STUDYID', 'DOMAIN']:  # These are usually constant
            if var == 'USUBJID' and ('subject_id' in mappings or 'SUBJID' in mappings):
                continue  # Can be derived
            errors.append(f"Missing mapping for required SDTM variable: {var}")
    
    # Validate mapping rules
    for sdtm_var, mapping_rule in mappings.items():
        if isinstance(mapping_rule, dict):
            if 'source_field' not in mapping_rule and 'value' not in mapping_rule and 'expression' not in mapping_rule:
                warnings.append(f"Mapping for {sdtm_var} has no source_field, value, or expression")
        elif not isinstance(mapping_rule, str):
            warnings.append(f"Mapping for {sdtm_var} should be string or dict")
    
    return {'errors': errors, 'warnings': warnings}


def map_record(raw_record: dict, mapping_config: dict, domain_spec: dict, domain: str) -> dict:
    """Map a single record from raw data to SDTM format"""
    mapped_record = {}
    mappings = mapping_config['mappings']
    constants = mapping_config.get('constants', {})
    
    # Apply constants (like STUDYID, DOMAIN)
    mapped_record.update(constants)
    mapped_record['DOMAIN'] = domain
    
    # Apply mappings
    for sdtm_var, mapping_rule in mappings.items():
        if isinstance(mapping_rule, str):
            # Simple field mapping
            if mapping_rule in raw_record:
                mapped_record[sdtm_var] = raw_record[mapping_rule]
        elif isinstance(mapping_rule, dict):
            if 'source_field' in mapping_rule:
                # Field mapping with potential transformation
                source_field = mapping_rule['source_field']
                if source_field in raw_record:
                    value = raw_record[source_field]
                    
                    # Apply transformations
                    if 'transform' in mapping_rule:
                        value = apply_transformation(value, mapping_rule['transform'])
                    
                    # Apply value mapping
                    if 'value_map' in mapping_rule:
                        value = mapping_rule['value_map'].get(value, value)
                    
                    mapped_record[sdtm_var] = value
            
            elif 'value' in mapping_rule:
                # Constant value
                mapped_record[sdtm_var] = mapping_rule['value']
            
            elif 'expression' in mapping_rule:
                # Derived value using expression
                mapped_record[sdtm_var] = evaluate_expression(
                    mapping_rule['expression'], raw_record, mapped_record
                )
    
    # Generate sequence numbers if needed
    if domain != 'DM' and f"{domain}SEQ" not in mapped_record:
        # This would need to be handled at a higher level with all records
        mapped_record[f"{domain}SEQ"] = 1
    
    # Generate USUBJID if needed
    if 'USUBJID' not in mapped_record:
        if 'SUBJID' in mapped_record and 'STUDYID' in mapped_record:
            mapped_record['USUBJID'] = f"{mapped_record['STUDYID']}-{mapped_record['SUBJID']}"
        elif 'subject_id' in raw_record:
            study_id = mapped_record.get('STUDYID', 'STUDY')
            mapped_record['USUBJID'] = f"{study_id}-{raw_record['subject_id']}"
    
    return mapped_record


def apply_transformation(value: str, transform: dict) -> str:
    """Apply transformation to a value"""
    transform_type = transform.get('type')
    
    if transform_type == 'upper':
        return value.upper()
    elif transform_type == 'lower':
        return value.lower()
    elif transform_type == 'date_format':
        try:
            input_format = transform.get('input_format', '%Y-%m-%d')
            output_format = transform.get('output_format', '%Y-%m-%dT%H:%M:%S')
            dt = datetime.strptime(value, input_format)
            return dt.strftime(output_format)
        except ValueError:
            return value
    elif transform_type == 'numeric':
        try:
            return str(float(value))
        except ValueError:
            return value
    elif transform_type == 'regex':
        pattern = transform.get('pattern', '')
        replacement = transform.get('replacement', '')
        return re.sub(pattern, replacement, value)
    
    return value


def evaluate_expression(expression: str, raw_record: dict, mapped_record: dict) -> str:
    """Evaluate simple expressions for derived values"""
    # This is a simplified expression evaluator
    # In practice, you might want to use a more robust solution
    
    # Handle common patterns
    if 'age_unit' in expression.lower():
        return 'YEARS'
    elif 'sequence' in expression.lower():
        # This would need proper sequence generation
        return '1'
    elif expression.startswith('concat('):
        # Simple concatenation
        parts = expression[7:-1].split(',')
        result = ''
        for part in parts:
            part = part.strip().strip('"\'')
            if part in raw_record:
                result += raw_record[part]
            elif part in mapped_record:
                result += mapped_record[part]
            else:
                result += part
        return result
    
    return expression


def validate_sdtm_record(record: dict, domain_spec: dict, validation_mode: str) -> dict:
    """Validate SDTM record against domain specification"""
    errors = []
    warnings = []
    missing_required = 0
    ct_violations = 0
    derived_fields = 0
    
    required_vars = domain_spec.get('required_vars', [])
    controlled_terms = domain_spec.get('controlled_terms', {})
    
    # Check required variables
    for var in required_vars:
        if var not in record or not record[var]:
            errors.append(f"Missing required variable: {var}")
            missing_required += 1
    
    # Check controlled terminology
    for var, allowed_values in controlled_terms.items():
        if var in record and record[var]:
            if record[var] not in allowed_values:
                if validation_mode == 'strict':
                    errors.append(f"{var} value '{record[var]}' not in controlled terms: {allowed_values}")
                else:
                    warnings.append(f"{var} value '{record[var]}' not in controlled terms: {allowed_values}")
                ct_violations += 1
    
    # Count derived fields
    derived_vars = domain_spec.get('derived_vars', [])
    for var in derived_vars:
        if var in record:
            derived_fields += 1
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'missing_required': missing_required,
        'ct_violations': ct_violations,
        'derived_fields': derived_fields
    }


def generate_compliance_metrics(records: List[dict], domain_spec: dict, domain: str) -> dict:
    """Generate SDTM compliance metrics"""
    if not records:
        return {'overall_score': 0, 'details': {}}
    
    required_vars = domain_spec.get('required_vars', [])
    expected_vars = domain_spec.get('expected_vars', [])
    controlled_terms = domain_spec.get('controlled_terms', {})
    
    metrics = {
        'required_vars_completeness': 0,
        'expected_vars_completeness': 0,
        'controlled_terms_compliance': 0,
        'overall_score': 0,
        'details': {
            'total_records': len(records),
            'required_vars_missing': {},
            'expected_vars_missing': {},
            'ct_violations': {}
        }
    }
    
    # Calculate required variables completeness
    required_complete = 0
    for var in required_vars:
        complete_count = sum(1 for record in records if var in record and record[var])
        completeness = (complete_count / len(records)) * 100
        metrics['details']['required_vars_missing'][var] = len(records) - complete_count
        if completeness == 100:
            required_complete += 1
    
    metrics['required_vars_completeness'] = (required_complete / len(required_vars)) * 100 if required_vars else 100
    
    # Calculate expected variables completeness
    expected_complete = 0
    for var in expected_vars:
        complete_count = sum(1 for record in records if var in record and record[var])
        completeness = (complete_count / len(records)) * 100
        metrics['details']['expected_vars_missing'][var] = len(records) - complete_count
        if completeness >= 80:  # 80% threshold for expected vars
            expected_complete += 1
    
    metrics['expected_vars_completeness'] = (expected_complete / len(expected_vars)) * 100 if expected_vars else 100
    
    # Calculate controlled terms compliance
    ct_compliant = 0
    for var, allowed_values in controlled_terms.items():
        violations = 0
        for record in records:
            if var in record and record[var] and record[var] not in allowed_values:
                violations += 1
        
        compliance = ((len(records) - violations) / len(records)) * 100 if len(records) > 0 else 100
        metrics['details']['ct_violations'][var] = violations
        if compliance >= 95:  # 95% threshold for CT compliance
            ct_compliant += 1
    
    metrics['controlled_terms_compliance'] = (ct_compliant / len(controlled_terms)) * 100 if controlled_terms else 100
    
    # Calculate overall score
    metrics['overall_score'] = (
        metrics['required_vars_completeness'] * 0.5 +
        metrics['expected_vars_completeness'] * 0.3 +
        metrics['controlled_terms_compliance'] * 0.2
    )
    
    return metrics