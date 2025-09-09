"""
Test Case Generator Tool
AI-powered test case generation for clinical trial features and specifications
"""

from typing import Dict, List, Any
import re
from datetime import datetime
import json

def run(input_data: Dict) -> Dict:
    """
    Generate comprehensive test cases for clinical trial features and specifications
    
    Args:
        input_data: Dictionary containing:
            - feature_specification: The feature or requirement to test
            - feature_type: Type of feature (protocol, system, process, etc.)
            - test_types: Types of tests to generate (functional, negative, boundary, etc.)
            - coverage_level: Level of test coverage (basic, comprehensive, exhaustive)
            - regulatory_context: Regulatory requirements to consider
            - risk_level: Risk level of the feature (low, medium, high)
    
    Returns:
        Dictionary with generated test cases, coverage analysis, and test execution guidance
    """
    try:
        feature_spec = input_data.get('feature_specification', '').strip()
        feature_type = input_data.get('feature_type', 'general')
        test_types = input_data.get('test_types', ['functional', 'negative', 'boundary'])
        coverage_level = input_data.get('coverage_level', 'comprehensive')
        regulatory_context = input_data.get('regulatory_context', [])
        risk_level = input_data.get('risk_level', 'medium')
        
        if not feature_spec:
            return {
                'success': False,
                'error': 'No feature specification provided'
            }
        
        # Parse and analyze the feature specification
        parsed_feature = parse_feature_specification(feature_spec, feature_type)
        
        # Generate test cases based on specification and requirements
        test_cases = []
        
        for test_type in test_types:
            type_cases = generate_test_cases_by_type(
                parsed_feature, test_type, coverage_level, risk_level
            )
            test_cases.extend(type_cases)
        
        # Add regulatory-specific test cases
        if regulatory_context:
            regulatory_cases = generate_regulatory_test_cases(
                parsed_feature, regulatory_context
            )
            test_cases.extend(regulatory_cases)
        
        # Generate edge cases and boundary conditions
        edge_cases = generate_edge_cases(parsed_feature, coverage_level)
        test_cases.extend(edge_cases)
        
        # Generate integration test cases if applicable
        integration_cases = generate_integration_test_cases(parsed_feature, feature_type)
        test_cases.extend(integration_cases)
        
        # Prioritize and organize test cases
        prioritized_cases = prioritize_test_cases(test_cases, risk_level)
        
        # Generate test data requirements
        test_data_requirements = generate_test_data_requirements(prioritized_cases)
        
        # Create test execution plan
        execution_plan = create_test_execution_plan(prioritized_cases, coverage_level)
        
        # Analyze coverage
        coverage_analysis = analyze_test_coverage(prioritized_cases, parsed_feature)
        
        # Generate traceability matrix
        traceability = create_traceability_matrix(prioritized_cases, parsed_feature)
        
        return {
            'success': True,
            'test_generation_summary': {
                'feature_analyzed': feature_spec[:100] + '...' if len(feature_spec) > 100 else feature_spec,
                'feature_type': feature_type,
                'total_test_cases': len(prioritized_cases),
                'test_types_covered': test_types,
                'coverage_level': coverage_level,
                'risk_level': risk_level,
                'generated_at': datetime.now().isoformat()
            },
            'test_cases': prioritized_cases,
            'test_data_requirements': test_data_requirements,
            'execution_plan': execution_plan,
            'coverage_analysis': coverage_analysis,
            'traceability_matrix': traceability,
            'quality_metrics': {
                'completeness_score': calculate_completeness_score(prioritized_cases, parsed_feature),
                'risk_coverage_score': calculate_risk_coverage(prioritized_cases, risk_level),
                'regulatory_compliance_score': calculate_regulatory_compliance(prioritized_cases, regulatory_context)
            },
            'recommendations': generate_testing_recommendations(
                prioritized_cases, coverage_analysis, risk_level
            )
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error generating test cases: {str(e)}'
        }

def parse_feature_specification(spec: str, feature_type: str) -> Dict:
    """Parse and analyze the feature specification."""
    parsed = {
        'original_text': spec,
        'feature_type': feature_type,
        'requirements': [],
        'acceptance_criteria': [],
        'business_rules': [],
        'input_parameters': [],
        'expected_outputs': [],
        'dependencies': [],
        'constraints': [],
        'user_roles': [],
        'data_elements': []
    }
    
    # Extract requirements
    req_patterns = [
        r'(?:shall|must|should|will)\s+(.+?)(?:\.|$)',
        r'requirement:?\s*(.+?)(?:\.|$)',
        r'the system\s+(.+?)(?:\.|$)'
    ]
    
    for pattern in req_patterns:
        matches = re.finditer(pattern, spec, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            requirement = match.group(1).strip()
            if len(requirement) > 5:
                parsed['requirements'].append(requirement)
    
    # Extract acceptance criteria
    ac_patterns = [
        r'given\s+(.+?)(?:when|then|$)',
        r'when\s+(.+?)(?:then|$)',
        r'then\s+(.+?)(?:\.|$)',
        r'acceptance criteria:?\s*(.+?)(?:\.|$)',
        r'verify that\s+(.+?)(?:\.|$)'
    ]
    
    for pattern in ac_patterns:
        matches = re.finditer(pattern, spec, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            criteria = match.group(1).strip()
            if len(criteria) > 5:
                parsed['acceptance_criteria'].append(criteria)
    
    # Extract input parameters and data elements
    input_patterns = [
        r'input:?\s*(.+?)(?:\.|$)',
        r'parameter:?\s*(.+?)(?:\.|$)',
        r'field:?\s*(.+?)(?:\.|$)',
        r'data:?\s*(.+?)(?:\.|$)'
    ]
    
    for pattern in input_patterns:
        matches = re.finditer(pattern, spec, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            input_item = match.group(1).strip()
            if len(input_item) > 2:
                parsed['input_parameters'].append(input_item)
    
    # Extract expected outputs
    output_patterns = [
        r'output:?\s*(.+?)(?:\.|$)',
        r'result:?\s*(.+?)(?:\.|$)',
        r'expected:?\s*(.+?)(?:\.|$)',
        r'display:?\s*(.+?)(?:\.|$)'
    ]
    
    for pattern in output_patterns:
        matches = re.finditer(pattern, spec, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            output_item = match.group(1).strip()
            if len(output_item) > 2:
                parsed['expected_outputs'].append(output_item)
    
    # Extract business rules
    rule_patterns = [
        r'rule:?\s*(.+?)(?:\.|$)',
        r'business rule:?\s*(.+?)(?:\.|$)',
        r'constraint:?\s*(.+?)(?:\.|$)',
        r'validation:?\s*(.+?)(?:\.|$)'
    ]
    
    for pattern in rule_patterns:
        matches = re.finditer(pattern, spec, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            rule = match.group(1).strip()
            if len(rule) > 5:
                parsed['business_rules'].append(rule)
    
    # Extract user roles
    role_patterns = [
        r'user:?\s*(.+?)(?:\.|$)',
        r'role:?\s*(.+?)(?:\.|$)',
        r'actor:?\s*(.+?)(?:\.|$)',
        r'investigator|coordinator|monitor|sponsor|subject|patient'
    ]
    
    for pattern in role_patterns:
        matches = re.finditer(pattern, spec, re.IGNORECASE)
        for match in matches:
            if match.groups():
                role = match.group(1).strip()
            else:
                role = match.group(0)
            if role and role not in parsed['user_roles']:
                parsed['user_roles'].append(role)
    
    # If no specific items found, create general items based on feature type
    if not any([parsed['requirements'], parsed['acceptance_criteria'], parsed['input_parameters']]):
        parsed = create_default_parsed_structure(spec, feature_type)
    
    return parsed

def create_default_parsed_structure(spec: str, feature_type: str) -> Dict:
    """Create default parsed structure when specific elements aren't found."""
    return {
        'original_text': spec,
        'feature_type': feature_type,
        'requirements': [f"Implement {feature_type} functionality as described"],
        'acceptance_criteria': [f"Verify {feature_type} works according to specification"],
        'business_rules': [],
        'input_parameters': ["User input", "System data"],
        'expected_outputs': ["Expected result", "System response"],
        'dependencies': [],
        'constraints': [],
        'user_roles': get_default_roles_by_type(feature_type),
        'data_elements': []
    }

def get_default_roles_by_type(feature_type: str) -> List[str]:
    """Get default user roles based on feature type."""
    role_mappings = {
        'protocol': ['Principal Investigator', 'Study Coordinator', 'Monitor'],
        'system': ['User', 'Administrator', 'System'],
        'safety': ['Safety Monitor', 'Investigator', 'Sponsor'],
        'data': ['Data Manager', 'Statistician', 'Monitor'],
        'regulatory': ['Regulatory Affairs', 'Quality Assurance', 'Auditor'],
        'general': ['User', 'Administrator']
    }
    
    return role_mappings.get(feature_type, role_mappings['general'])

def generate_test_cases_by_type(parsed_feature: Dict, test_type: str, 
                              coverage_level: str, risk_level: str) -> List[Dict]:
    """Generate test cases based on test type."""
    test_cases = []
    
    if test_type == 'functional':
        test_cases.extend(generate_functional_test_cases(parsed_feature, coverage_level))
    elif test_type == 'negative':
        test_cases.extend(generate_negative_test_cases(parsed_feature, coverage_level))
    elif test_type == 'boundary':
        test_cases.extend(generate_boundary_test_cases(parsed_feature, coverage_level))
    elif test_type == 'security':
        test_cases.extend(generate_security_test_cases(parsed_feature, coverage_level))
    elif test_type == 'performance':
        test_cases.extend(generate_performance_test_cases(parsed_feature, coverage_level))
    elif test_type == 'usability':
        test_cases.extend(generate_usability_test_cases(parsed_feature, coverage_level))
    elif test_type == 'integration':
        test_cases.extend(generate_integration_test_cases(parsed_feature, parsed_feature['feature_type']))
    
    return test_cases

def generate_functional_test_cases(parsed_feature: Dict, coverage_level: str) -> List[Dict]:
    """Generate functional test cases."""
    test_cases = []
    
    # Test each requirement
    for i, requirement in enumerate(parsed_feature['requirements']):
        test_case = {
            'id': f'FUNC_{i+1:03d}',
            'type': 'functional',
            'priority': 'high',
            'title': f'Verify {requirement[:50]}...' if len(requirement) > 50 else f'Verify {requirement}',
            'objective': f'Test that the system {requirement}',
            'preconditions': ['System is available', 'User has appropriate permissions'],
            'test_steps': generate_functional_test_steps(requirement, parsed_feature),
            'expected_result': f'System successfully {requirement}',
            'test_data_needed': determine_test_data_needed(requirement),
            'user_role': determine_user_role(requirement, parsed_feature['user_roles']),
            'requirements_covered': [requirement],
            'risk_level': 'medium'
        }
        test_cases.append(test_case)
    
    # Test acceptance criteria
    for i, criteria in enumerate(parsed_feature['acceptance_criteria']):
        test_case = {
            'id': f'FUNC_{len(test_cases)+1:03d}',
            'type': 'functional',
            'priority': 'high',
            'title': f'Verify acceptance criteria: {criteria[:50]}...' if len(criteria) > 50 else f'Verify {criteria}',
            'objective': f'Validate that {criteria}',
            'preconditions': ['System meets all prerequisites'],
            'test_steps': generate_acceptance_criteria_steps(criteria),
            'expected_result': criteria,
            'test_data_needed': ['Valid test data'],
            'user_role': 'Tester',
            'requirements_covered': [criteria],
            'risk_level': 'medium'
        }
        test_cases.append(test_case)
    
    return test_cases

def generate_negative_test_cases(parsed_feature: Dict, coverage_level: str) -> List[Dict]:
    """Generate negative test cases."""
    test_cases = []
    
    # Test with invalid inputs
    for i, input_param in enumerate(parsed_feature['input_parameters']):
        test_case = {
            'id': f'NEG_{i+1:03d}',
            'type': 'negative',
            'priority': 'medium',
            'title': f'Test invalid input for {input_param}',
            'objective': f'Verify system handles invalid {input_param} appropriately',
            'preconditions': ['System is available'],
            'test_steps': [
                f'1. Navigate to feature requiring {input_param}',
                f'2. Enter invalid data for {input_param}',
                f'3. Attempt to proceed',
                f'4. Verify error handling'
            ],
            'expected_result': 'System displays appropriate error message and prevents invalid operation',
            'test_data_needed': [f'Invalid {input_param} data'],
            'user_role': determine_user_role(input_param, parsed_feature['user_roles']),
            'requirements_covered': [f'Error handling for {input_param}'],
            'risk_level': 'medium'
        }
        test_cases.append(test_case)
    
    # Test business rule violations
    for i, rule in enumerate(parsed_feature['business_rules']):
        test_case = {
            'id': f'NEG_{len(test_cases)+1:03d}',
            'type': 'negative',
            'priority': 'high',
            'title': f'Test violation of business rule: {rule[:50]}...',
            'objective': f'Verify system prevents violation of rule: {rule}',
            'preconditions': ['System is available'],
            'test_steps': generate_rule_violation_steps(rule),
            'expected_result': 'System prevents rule violation and displays appropriate message',
            'test_data_needed': ['Data that violates business rule'],
            'user_role': 'Tester',
            'requirements_covered': [rule],
            'risk_level': 'high'
        }
        test_cases.append(test_case)
    
    return test_cases

def generate_boundary_test_cases(parsed_feature: Dict, coverage_level: str) -> List[Dict]:
    """Generate boundary test cases."""
    test_cases = []
    
    # Common boundary scenarios for clinical trials
    boundary_scenarios = [
        {
            'scenario': 'Date boundaries',
            'test_data': ['Past dates', 'Future dates', 'Current date', 'Invalid dates'],
            'description': 'Test date field boundaries and validations'
        },
        {
            'scenario': 'Numeric boundaries',
            'test_data': ['Minimum values', 'Maximum values', 'Zero', 'Negative numbers'],
            'description': 'Test numeric field boundaries'
        },
        {
            'scenario': 'Text length boundaries',
            'test_data': ['Empty strings', 'Single character', 'Maximum length', 'Exceeds maximum'],
            'description': 'Test text field length boundaries'
        },
        {
            'scenario': 'Subject ID boundaries',
            'test_data': ['Valid IDs', 'Duplicate IDs', 'Invalid format', 'Special characters'],
            'description': 'Test subject identification boundaries'
        }
    ]
    
    for i, scenario in enumerate(boundary_scenarios):
        for j, test_data in enumerate(scenario['test_data']):
            test_case = {
                'id': f'BOUND_{i+1:02d}_{j+1:02d}',
                'type': 'boundary',
                'priority': 'medium',
                'title': f'{scenario["scenario"]} - {test_data}',
                'objective': f'Test {scenario["description"]} using {test_data.lower()}',
                'preconditions': ['System is available', 'Valid user session'],
                'test_steps': [
                    f'1. Navigate to feature with {scenario["scenario"].lower()}',
                    f'2. Enter {test_data.lower()}',
                    f'3. Attempt to save/proceed',
                    f'4. Verify system behavior'
                ],
                'expected_result': f'System handles {test_data.lower()} according to specifications',
                'test_data_needed': [test_data],
                'user_role': 'Tester',
                'requirements_covered': [f'{scenario["scenario"]} validation'],
                'risk_level': 'medium'
            }
            test_cases.append(test_case)
    
    return test_cases

def generate_security_test_cases(parsed_feature: Dict, coverage_level: str) -> List[Dict]:
    """Generate security test cases."""
    test_cases = []
    
    security_scenarios = [
        {
            'type': 'Authentication',
            'tests': ['Valid credentials', 'Invalid credentials', 'Locked accounts', 'Session timeout']
        },
        {
            'type': 'Authorization',
            'tests': ['Role-based access', 'Unauthorized access attempts', 'Privilege escalation']
        },
        {
            'type': 'Data Protection',
            'tests': ['PHI encryption', 'Data masking', 'Audit trail logging']
        },
        {
            'type': 'Input Validation',
            'tests': ['SQL injection', 'XSS attacks', 'Malicious file uploads']
        }
    ]
    
    for sec_type in security_scenarios:
        for i, test in enumerate(sec_type['tests']):
            test_case = {
                'id': f'SEC_{sec_type["type"][:3].upper()}_{i+1:02d}',
                'type': 'security',
                'priority': 'high',
                'title': f'Security test: {sec_type["type"]} - {test}',
                'objective': f'Verify {sec_type["type"].lower()} security for {test.lower()}',
                'preconditions': ['Security testing environment', 'Test accounts available'],
                'test_steps': generate_security_test_steps(sec_type['type'], test),
                'expected_result': f'System properly handles {test.lower()} security scenario',
                'test_data_needed': [f'Security test data for {test}'],
                'user_role': 'Security Tester',
                'requirements_covered': [f'{sec_type["type"]} security'],
                'risk_level': 'high'
            }
            test_cases.append(test_case)
    
    return test_cases

def generate_performance_test_cases(parsed_feature: Dict, coverage_level: str) -> List[Dict]:
    """Generate performance test cases."""
    test_cases = []
    
    performance_scenarios = [
        {
            'type': 'Load Testing',
            'objective': 'Verify system performance under normal load',
            'load_condition': 'Expected concurrent users'
        },
        {
            'type': 'Stress Testing',
            'objective': 'Verify system behavior under peak load',
            'load_condition': 'Maximum expected load + 20%'
        },
        {
            'type': 'Volume Testing',
            'objective': 'Verify system handles large data volumes',
            'load_condition': 'Large dataset processing'
        },
        {
            'type': 'Response Time Testing',
            'objective': 'Verify system meets response time requirements',
            'load_condition': 'Standard user operations'
        }
    ]
    
    for i, scenario in enumerate(performance_scenarios):
        test_case = {
            'id': f'PERF_{i+1:03d}',
            'type': 'performance',
            'priority': 'medium',
            'title': f'Performance test: {scenario["type"]}',
            'objective': scenario['objective'],
            'preconditions': ['Performance testing environment', 'Monitoring tools available'],
            'test_steps': [
                f'1. Set up {scenario["load_condition"]}',
                f'2. Execute test scenario',
                f'3. Monitor system performance metrics',
                f'4. Record results and analyze'
            ],
            'expected_result': 'System meets performance requirements',
            'test_data_needed': ['Performance test data'],
            'user_role': 'Performance Tester',
            'requirements_covered': [f'Performance - {scenario["type"]}'],
            'risk_level': 'medium'
        }
        test_cases.append(test_case)
    
    return test_cases

def generate_usability_test_cases(parsed_feature: Dict, coverage_level: str) -> List[Dict]:
    """Generate usability test cases."""
    test_cases = []
    
    usability_scenarios = [
        'Navigation ease and intuitiveness',
        'Error message clarity and helpfulness',
        'Screen layout and information organization',
        'Workflow efficiency and logical flow',
        'Accessibility compliance (508, WCAG)',
        'Mobile responsiveness and cross-browser compatibility'
    ]
    
    for i, scenario in enumerate(usability_scenarios):
        test_case = {
            'id': f'USAB_{i+1:03d}',
            'type': 'usability',
            'priority': 'medium',
            'title': f'Usability test: {scenario}',
            'objective': f'Evaluate {scenario.lower()}',
            'preconditions': ['Representative test users', 'Various devices/browsers'],
            'test_steps': [
                f'1. Brief test users on task objectives',
                f'2. Observe users performing typical tasks',
                f'3. Note usability issues and user feedback',
                f'4. Measure task completion times and success rates'
            ],
            'expected_result': f'Users can efficiently complete tasks with good {scenario.lower()}',
            'test_data_needed': ['Realistic test scenarios'],
            'user_role': 'End User',
            'requirements_covered': [f'Usability - {scenario}'],
            'risk_level': 'low'
        }
        test_cases.append(test_case)
    
    return test_cases

def generate_integration_test_cases(parsed_feature: Dict, feature_type: str) -> List[Dict]:
    """Generate integration test cases."""
    test_cases = []
    
    # Common clinical trial integrations
    integration_scenarios = {
        'protocol': ['EDC system', 'CTMS', 'Randomization system'],
        'system': ['Database', 'External APIs', 'File systems'],
        'safety': ['Adverse event system', 'SUSAR reporting', 'Medical coding'],
        'data': ['EDC', 'Central lab', 'Statistical software'],
        'general': ['User management', 'Audit logging', 'Notification system']
    }
    
    scenarios = integration_scenarios.get(feature_type, integration_scenarios['general'])
    
    for i, integration in enumerate(scenarios):
        test_case = {
            'id': f'INTEG_{i+1:03d}',
            'type': 'integration',
            'priority': 'high',
            'title': f'Integration test with {integration}',
            'objective': f'Verify proper integration and data flow with {integration}',
            'preconditions': [f'{integration} system available', 'Integration endpoints configured'],
            'test_steps': [
                f'1. Initiate process requiring {integration} interaction',
                f'2. Verify data is sent to {integration} correctly',
                f'3. Verify response from {integration} is handled properly',
                f'4. Verify error scenarios and fallback mechanisms'
            ],
            'expected_result': f'System integrates properly with {integration}',
            'test_data_needed': ['Integration test data'],
            'user_role': 'System Tester',
            'requirements_covered': [f'{integration} integration'],
            'risk_level': 'high'
        }
        test_cases.append(test_case)
    
    return test_cases

def generate_regulatory_test_cases(parsed_feature: Dict, regulatory_context: List[str]) -> List[Dict]:
    """Generate regulatory-specific test cases."""
    test_cases = []
    
    regulatory_scenarios = {
        '21CFR11': [
            'Electronic signature validation',
            'Audit trail completeness',
            'User access controls',
            'Data integrity checks'
        ],
        'GCP': [
            'Protocol compliance verification',
            'Data quality checks',
            'Source data verification',
            'Investigator oversight'
        ],
        'HIPAA': [
            'PHI protection',
            'Access logging',
            'Data encryption',
            'Breach notification'
        ],
        'GDPR': [
            'Consent management',
            'Right to erasure',
            'Data portability',
            'Privacy by design'
        ]
    }
    
    for reg_context in regulatory_context:
        if reg_context in regulatory_scenarios:
            scenarios = regulatory_scenarios[reg_context]
            for i, scenario in enumerate(scenarios):
                test_case = {
                    'id': f'REG_{reg_context}_{i+1:02d}',
                    'type': 'regulatory',
                    'priority': 'high',
                    'title': f'{reg_context} compliance: {scenario}',
                    'objective': f'Verify {reg_context} compliance for {scenario.lower()}',
                    'preconditions': ['Compliance testing environment'],
                    'test_steps': generate_regulatory_test_steps(reg_context, scenario),
                    'expected_result': f'System meets {reg_context} requirements for {scenario.lower()}',
                    'test_data_needed': [f'{reg_context} compliance test data'],
                    'user_role': 'Compliance Tester',
                    'requirements_covered': [f'{reg_context} - {scenario}'],
                    'risk_level': 'high'
                }
                test_cases.append(test_case)
    
    return test_cases

def generate_edge_cases(parsed_feature: Dict, coverage_level: str) -> List[Dict]:
    """Generate edge case test scenarios."""
    test_cases = []
    
    edge_scenarios = [
        {
            'name': 'Concurrent user access',
            'description': 'Multiple users accessing same data simultaneously'
        },
        {
            'name': 'Network interruption',
            'description': 'Connection loss during critical operations'
        },
        {
            'name': 'Database lock scenarios',
            'description': 'Database unavailable during operations'
        },
        {
            'name': 'Large dataset handling',
            'description': 'Processing unusually large amounts of data'
        },
        {
            'name': 'Time zone edge cases',
            'description': 'Operations across different time zones'
        },
        {
            'name': 'System resource exhaustion',
            'description': 'Operations when system resources are limited'
        }
    ]
    
    for i, scenario in enumerate(edge_scenarios):
        test_case = {
            'id': f'EDGE_{i+1:03d}',
            'type': 'edge_case',
            'priority': 'low' if coverage_level == 'basic' else 'medium',
            'title': f'Edge case: {scenario["name"]}',
            'objective': f'Test system behavior for {scenario["description"]}',
            'preconditions': ['Test environment with controllable conditions'],
            'test_steps': generate_edge_case_steps(scenario),
            'expected_result': 'System handles edge case gracefully without data loss',
            'test_data_needed': ['Edge case test data'],
            'user_role': 'System Tester',
            'requirements_covered': [f'Edge case - {scenario["name"]}'],
            'risk_level': 'medium'
        }
        test_cases.append(test_case)
    
    return test_cases

def generate_functional_test_steps(requirement: str, parsed_feature: Dict) -> List[str]:
    """Generate functional test steps for a requirement."""
    steps = [
        '1. Log in to the system with appropriate user credentials',
        '2. Navigate to the relevant feature/module',
    ]
    
    # Add requirement-specific steps
    if 'input' in requirement.lower():
        steps.append('3. Enter valid input data as specified')
    if 'process' in requirement.lower():
        steps.append('4. Initiate the process/operation')
    if 'validate' in requirement.lower():
        steps.append('5. Verify validation logic is applied')
    if 'save' in requirement.lower():
        steps.append('6. Save the data/configuration')
    
    steps.extend([
        f'{len(steps)+1}. Verify the expected result',
        f'{len(steps)+2}. Log out and verify session cleanup'
    ])
    
    return steps

def generate_acceptance_criteria_steps(criteria: str) -> List[str]:
    """Generate test steps for acceptance criteria."""
    steps = []
    
    if criteria.lower().startswith('given'):
        steps.append('1. Set up the given preconditions')
    if 'when' in criteria.lower():
        steps.append(f'{len(steps)+1}. Perform the action described in "when" clause')
    if 'then' in criteria.lower():
        steps.append(f'{len(steps)+1}. Verify the "then" condition is met')
    
    if not steps:
        steps = [
            '1. Set up test preconditions',
            '2. Execute the test scenario',
            '3. Verify acceptance criteria is met'
        ]
    
    return steps

def generate_rule_violation_steps(rule: str) -> List[str]:
    """Generate steps to test business rule violations."""
    return [
        '1. Set up test data that would violate the business rule',
        '2. Attempt to perform the operation that should trigger the rule',
        '3. Verify the system prevents the operation',
        '4. Verify appropriate error/warning message is displayed',
        '5. Confirm system state remains consistent'
    ]

def generate_security_test_steps(sec_type: str, test: str) -> List[str]:
    """Generate security test steps."""
    step_mappings = {
        'Authentication': [
            '1. Attempt login with test credentials',
            '2. Verify authentication response',
            '3. Check session establishment/rejection',
            '4. Verify audit logging of authentication attempt'
        ],
        'Authorization': [
            '1. Login with user having specific role/permissions',
            '2. Attempt to access restricted functionality',
            '3. Verify access is granted/denied appropriately',
            '4. Check authorization audit trail'
        ],
        'Data Protection': [
            '1. Access sensitive data through the system',
            '2. Verify data encryption in transit and at rest',
            '3. Check data masking for unauthorized users',
            '4. Verify audit logging of data access'
        ],
        'Input Validation': [
            '1. Prepare malicious input payloads',
            '2. Attempt to input malicious data',
            '3. Verify system rejects malicious input',
            '4. Confirm no system compromise occurred'
        ]
    }
    
    return step_mappings.get(sec_type, ['1. Perform security test', '2. Verify security behavior'])

def generate_regulatory_test_steps(reg_context: str, scenario: str) -> List[str]:
    """Generate regulatory test steps."""
    return [
        f'1. Set up test scenario for {reg_context} {scenario.lower()}',
        f'2. Execute operations that must comply with {reg_context}',
        f'3. Verify {scenario.lower()} requirements are met',
        f'4. Document compliance evidence',
        f'5. Review audit trail for {reg_context} requirements'
    ]

def generate_edge_case_steps(scenario: Dict) -> List[str]:
    """Generate edge case test steps."""
    return [
        f'1. Set up conditions to simulate {scenario["description"]}',
        '2. Initiate normal system operations',
        f'3. Trigger the edge case scenario ({scenario["name"]})',
        '4. Monitor system behavior and response',
        '5. Verify data integrity and system recovery'
    ]

def determine_test_data_needed(requirement: str) -> List[str]:
    """Determine what test data is needed for a requirement."""
    req_lower = requirement.lower()
    test_data = []
    
    if any(word in req_lower for word in ['subject', 'patient']):
        test_data.extend(['Subject data', 'Patient demographics'])
    if any(word in req_lower for word in ['visit', 'assessment']):
        test_data.extend(['Visit data', 'Assessment forms'])
    if any(word in req_lower for word in ['adverse', 'event', 'safety']):
        test_data.extend(['AE data', 'Safety information'])
    if any(word in req_lower for word in ['protocol', 'study']):
        test_data.extend(['Protocol data', 'Study configuration'])
    if any(word in req_lower for word in ['user', 'login', 'access']):
        test_data.extend(['User accounts', 'Permission data'])
    
    return test_data if test_data else ['Valid test data']

def determine_user_role(requirement: str, available_roles: List[str]) -> str:
    """Determine appropriate user role for testing a requirement."""
    req_lower = requirement.lower()
    
    role_mappings = {
        'investigator': 'Principal Investigator',
        'coordinator': 'Study Coordinator',
        'monitor': 'Monitor',
        'admin': 'Administrator',
        'sponsor': 'Sponsor',
        'patient': 'Patient',
        'subject': 'Subject'
    }
    
    for keyword, role in role_mappings.items():
        if keyword in req_lower and role in available_roles:
            return role
    
    return available_roles[0] if available_roles else 'Tester'

def prioritize_test_cases(test_cases: List[Dict], risk_level: str) -> List[Dict]:
    """Prioritize and organize test cases."""
    # Define priority weights
    priority_weights = {'high': 3, 'medium': 2, 'low': 1}
    type_weights = {
        'functional': 3, 'security': 3, 'regulatory': 3,
        'integration': 2, 'negative': 2, 'boundary': 2,
        'performance': 1, 'usability': 1, 'edge_case': 1
    }
    
    # Calculate priority scores
    for test_case in test_cases:
        priority_score = priority_weights.get(test_case['priority'], 1)
        type_score = type_weights.get(test_case['type'], 1)
        risk_adjustment = 1.5 if risk_level == 'high' else 1.0
        
        test_case['priority_score'] = priority_score * type_score * risk_adjustment
    
    # Sort by priority score (highest first)
    test_cases.sort(key=lambda x: x['priority_score'], reverse=True)
    
    # Add execution sequence
    for i, test_case in enumerate(test_cases):
        test_case['execution_sequence'] = i + 1
    
    return test_cases

def generate_test_data_requirements(test_cases: List[Dict]) -> Dict:
    """Generate comprehensive test data requirements."""
    data_categories = {}
    
    for test_case in test_cases:
        for data_item in test_case.get('test_data_needed', []):
            if data_item not in data_categories:
                data_categories[data_item] = {
                    'description': f'Test data for {data_item}',
                    'required_by_tests': [],
                    'data_volume': 'Small',
                    'data_characteristics': [],
                    'generation_method': 'Manual'
                }
            
            data_categories[data_item]['required_by_tests'].append(test_case['id'])
    
    # Enhance data requirements based on clinical trial context
    enhanced_requirements = {}
    for data_type, requirements in data_categories.items():
        enhanced = enhance_test_data_requirements(data_type, requirements)
        enhanced_requirements[data_type] = enhanced
    
    return {
        'data_categories': enhanced_requirements,
        'data_privacy_requirements': [
            'All test data must be de-identified',
            'PHI must not be used in test environments',
            'Test data must comply with privacy regulations'
        ],
        'data_management_requirements': [
            'Test data must be version controlled',
            'Test data refresh procedures must be documented',
            'Test data cleanup procedures must be defined'
        ]
    }

def enhance_test_data_requirements(data_type: str, basic_requirements: Dict) -> Dict:
    """Enhance test data requirements with clinical trial specifics."""
    enhanced = basic_requirements.copy()
    
    if 'subject' in data_type.lower() or 'patient' in data_type.lower():
        enhanced['data_characteristics'] = [
            'Valid subject IDs',
            'Demographic variations',
            'Different enrollment statuses'
        ]
        enhanced['data_volume'] = 'Medium'
        enhanced['generation_method'] = 'Synthetic data generator'
    
    elif 'adverse' in data_type.lower() or 'safety' in data_type.lower():
        enhanced['data_characteristics'] = [
            'Various AE severities',
            'Different MedDRA terms',
            'Related/unrelated classifications'
        ]
    
    elif 'protocol' in data_type.lower():
        enhanced['data_characteristics'] = [
            'Different study phases',
            'Various indication areas',
            'Multiple visit schedules'
        ]
    
    elif 'user' in data_type.lower():
        enhanced['data_characteristics'] = [
            'Different user roles',
            'Various permission levels',
            'Active/inactive statuses'
        ]
    
    return enhanced

def create_test_execution_plan(test_cases: List[Dict], coverage_level: str) -> Dict:
    """Create a comprehensive test execution plan."""
    # Group test cases by type
    grouped_tests = {}
    for test_case in test_cases:
        test_type = test_case['type']
        if test_type not in grouped_tests:
            grouped_tests[test_type] = []
        grouped_tests[test_type].append(test_case)
    
    # Define execution phases
    execution_phases = [
        {
            'phase': 'Smoke Testing',
            'types': ['functional'],
            'criteria': 'High priority functional tests only',
            'estimated_duration': '1-2 days'
        },
        {
            'phase': 'Core Functionality',
            'types': ['functional', 'integration'],
            'criteria': 'All functional and integration tests',
            'estimated_duration': '3-5 days'
        },
        {
            'phase': 'Negative Testing',
            'types': ['negative', 'boundary', 'edge_case'],
            'criteria': 'Error handling and boundary conditions',
            'estimated_duration': '2-3 days'
        },
        {
            'phase': 'Non-Functional Testing',
            'types': ['security', 'performance', 'usability'],
            'criteria': 'Security, performance, and usability tests',
            'estimated_duration': '2-4 days'
        },
        {
            'phase': 'Regulatory Compliance',
            'types': ['regulatory'],
            'criteria': 'All regulatory compliance tests',
            'estimated_duration': '1-2 days'
        }
    ]
    
    return {
        'execution_phases': execution_phases,
        'test_groups': grouped_tests,
        'total_estimated_duration': calculate_total_duration(test_cases, coverage_level),
        'resource_requirements': calculate_resource_requirements(test_cases),
        'environment_requirements': [
            'Test environment with representative data',
            'Integration with external systems (if applicable)',
            'Performance testing tools and monitoring',
            'Security testing tools',
            'Various browser and device configurations'
        ],
        'entry_criteria': [
            'Feature development complete',
            'Unit tests passing',
            'Test environment configured',
            'Test data prepared'
        ],
        'exit_criteria': [
            'All high-priority tests executed',
            'Critical defects resolved',
            'Acceptance criteria met',
            'Regulatory requirements satisfied'
        ]
    }

def calculate_total_duration(test_cases: List[Dict], coverage_level: str) -> str:
    """Calculate total estimated test execution duration."""
    base_duration_per_test = {
        'basic': 0.5,      # 30 minutes per test
        'comprehensive': 1, # 1 hour per test
        'exhaustive': 2     # 2 hours per test
    }
    
    duration_per_test = base_duration_per_test.get(coverage_level, 1)
    total_hours = len(test_cases) * duration_per_test
    total_days = max(1, round(total_hours / 8))  # 8 hours per day
    
    return f"{total_days} days ({total_hours} hours)"

def calculate_resource_requirements(test_cases: List[Dict]) -> Dict:
    """Calculate resource requirements for test execution."""
    role_requirements = {}
    
    for test_case in test_cases:
        role = test_case.get('user_role', 'Tester')
        test_type = test_case['type']
        
        if role not in role_requirements:
            role_requirements[role] = {'count': 0, 'types': set()}
        
        role_requirements[role]['count'] += 1
        role_requirements[role]['types'].add(test_type)
    
    # Convert sets to lists for JSON serialization
    for role, requirements in role_requirements.items():
        requirements['types'] = list(requirements['types'])
    
    return {
        'role_requirements': role_requirements,
        'specialized_skills_needed': [
            'Clinical trial domain knowledge',
            'Regulatory compliance understanding',
            'Security testing expertise',
            'Performance testing tools proficiency'
        ],
        'infrastructure_needs': [
            'Test data management system',
            'Test automation framework',
            'Defect tracking system',
            'Test reporting tools'
        ]
    }

def analyze_test_coverage(test_cases: List[Dict], parsed_feature: Dict) -> Dict:
    """Analyze test coverage across different dimensions."""
    coverage_analysis = {
        'requirements_coverage': {},
        'test_type_coverage': {},
        'risk_coverage': {},
        'user_role_coverage': {},
        'gaps_identified': []
    }
    
    # Requirements coverage
    all_requirements = (parsed_feature['requirements'] + 
                       parsed_feature['acceptance_criteria'] + 
                       parsed_feature['business_rules'])
    
    covered_requirements = set()
    for test_case in test_cases:
        for req in test_case.get('requirements_covered', []):
            covered_requirements.add(req)
    
    coverage_analysis['requirements_coverage'] = {
        'total_requirements': len(all_requirements),
        'covered_requirements': len(covered_requirements),
        'coverage_percentage': round((len(covered_requirements) / max(len(all_requirements), 1)) * 100, 1),
        'uncovered_requirements': [req for req in all_requirements if req not in covered_requirements]
    }
    
    # Test type coverage
    type_counts = {}
    for test_case in test_cases:
        test_type = test_case['type']
        type_counts[test_type] = type_counts.get(test_type, 0) + 1
    
    coverage_analysis['test_type_coverage'] = type_counts
    
    # Risk coverage
    risk_counts = {'high': 0, 'medium': 0, 'low': 0}
    for test_case in test_cases:
        risk_level = test_case.get('risk_level', 'medium')
        risk_counts[risk_level] += 1
    
    coverage_analysis['risk_coverage'] = risk_counts
    
    # User role coverage
    role_counts = {}
    for test_case in test_cases:
        role = test_case.get('user_role', 'Unknown')
        role_counts[role] = role_counts.get(role, 0) + 1
    
    coverage_analysis['user_role_coverage'] = role_counts
    
    # Identify gaps
    gaps = []
    if coverage_analysis['requirements_coverage']['coverage_percentage'] < 80:
        gaps.append(f"Requirements coverage below 80% ({coverage_analysis['requirements_coverage']['coverage_percentage']}%)")
    
    if 'security' not in type_counts:
        gaps.append("No security test cases identified")
    
    if 'regulatory' not in type_counts and parsed_feature.get('regulatory_requirements'):
        gaps.append("No regulatory compliance test cases for regulated feature")
    
    coverage_analysis['gaps_identified'] = gaps
    
    return coverage_analysis

def create_traceability_matrix(test_cases: List[Dict], parsed_feature: Dict) -> Dict:
    """Create traceability matrix linking requirements to test cases."""
    matrix = {}
    
    # Build requirement to test case mapping
    all_requirements = (parsed_feature['requirements'] + 
                       parsed_feature['acceptance_criteria'] + 
                       parsed_feature['business_rules'])
    
    for requirement in all_requirements:
        matrix[requirement] = {
            'requirement_type': determine_requirement_type(requirement, parsed_feature),
            'test_cases': [],
            'coverage_status': 'not_covered'
        }
    
    # Map test cases to requirements
    for test_case in test_cases:
        for req in test_case.get('requirements_covered', []):
            if req in matrix:
                matrix[req]['test_cases'].append({
                    'test_id': test_case['id'],
                    'test_title': test_case['title'],
                    'test_type': test_case['type'],
                    'priority': test_case['priority']
                })
                matrix[req]['coverage_status'] = 'covered'
    
    return {
        'traceability_matrix': matrix,
        'summary': {
            'total_requirements': len(matrix),
            'covered_requirements': len([r for r in matrix.values() if r['coverage_status'] == 'covered']),
            'test_to_requirement_ratio': round(len(test_cases) / max(len(matrix), 1), 2)
        }
    }

def determine_requirement_type(requirement: str, parsed_feature: Dict) -> str:
    """Determine the type of requirement."""
    if requirement in parsed_feature['requirements']:
        return 'functional_requirement'
    elif requirement in parsed_feature['acceptance_criteria']:
        return 'acceptance_criteria'
    elif requirement in parsed_feature['business_rules']:
        return 'business_rule'
    else:
        return 'derived_requirement'

def calculate_completeness_score(test_cases: List[Dict], parsed_feature: Dict) -> float:
    """Calculate completeness score based on test coverage."""
    scores = []
    
    # Requirements coverage score (40% weight)
    all_requirements = (parsed_feature['requirements'] + 
                       parsed_feature['acceptance_criteria'] + 
                       parsed_feature['business_rules'])
    
    covered_reqs = set()
    for test_case in test_cases:
        covered_reqs.update(test_case.get('requirements_covered', []))
    
    req_score = len(covered_reqs) / max(len(all_requirements), 1) * 40
    scores.append(req_score)
    
    # Test type diversity score (30% weight)
    expected_types = ['functional', 'negative', 'boundary']
    actual_types = set(tc['type'] for tc in test_cases)
    type_score = len(actual_types & set(expected_types)) / len(expected_types) * 30
    scores.append(type_score)
    
    # Risk coverage score (20% weight)
    high_risk_tests = len([tc for tc in test_cases if tc.get('priority') == 'high'])
    risk_score = min(high_risk_tests / max(len(test_cases) * 0.3, 1), 1) * 20
    scores.append(risk_score)
    
    # Documentation quality score (10% weight)
    documented_tests = len([tc for tc in test_cases if len(tc.get('test_steps', [])) > 2])
    doc_score = documented_tests / max(len(test_cases), 1) * 10
    scores.append(doc_score)
    
    return round(sum(scores), 1)

def calculate_risk_coverage(test_cases: List[Dict], risk_level: str) -> float:
    """Calculate how well the test cases cover the specified risk level."""
    risk_weights = {'high': 1.0, 'medium': 0.7, 'low': 0.5}
    expected_weight = risk_weights.get(risk_level, 0.7)
    
    actual_coverage = 0
    total_tests = len(test_cases)
    
    for test_case in test_cases:
        test_priority = test_case.get('priority', 'medium')
        test_weight = risk_weights.get(test_priority, 0.5)
        actual_coverage += test_weight
    
    if total_tests == 0:
        return 0.0
    
    average_coverage = actual_coverage / total_tests
    coverage_score = min(average_coverage / expected_weight, 1.0) * 100
    
    return round(coverage_score, 1)

def calculate_regulatory_compliance(test_cases: List[Dict], regulatory_context: List[str]) -> float:
    """Calculate regulatory compliance coverage score."""
    if not regulatory_context:
        return 100.0  # No regulatory requirements
    
    regulatory_tests = [tc for tc in test_cases if tc['type'] == 'regulatory']
    
    if not regulatory_tests:
        return 0.0  # No regulatory tests for regulated feature
    
    # Calculate coverage per regulatory context
    contexts_covered = set()
    for test_case in regulatory_tests:
        test_id = test_case['id']
        for context in regulatory_context:
            if context.upper() in test_id:
                contexts_covered.add(context)
    
    coverage_score = len(contexts_covered) / len(regulatory_context) * 100
    return round(coverage_score, 1)

def generate_testing_recommendations(test_cases: List[Dict], coverage_analysis: Dict, 
                                   risk_level: str) -> List[str]:
    """Generate recommendations for improving test coverage and effectiveness."""
    recommendations = []
    
    # Coverage recommendations
    req_coverage = coverage_analysis.get('requirements_coverage', {})
    if req_coverage.get('coverage_percentage', 0) < 90:
        recommendations.append(
            f"Increase requirements coverage from {req_coverage.get('coverage_percentage', 0)}% to 90%+"
        )
    
    # Test type recommendations
    type_coverage = coverage_analysis.get('test_type_coverage', {})
    missing_types = []
    
    expected_types = ['functional', 'negative', 'boundary', 'security']
    for expected_type in expected_types:
        if expected_type not in type_coverage:
            missing_types.append(expected_type)
    
    if missing_types:
        recommendations.append(f"Add {', '.join(missing_types)} test cases")
    
    # Risk-based recommendations
    if risk_level == 'high' and len([tc for tc in test_cases if tc['priority'] == 'high']) < len(test_cases) * 0.6:
        recommendations.append("Increase high-priority test coverage for high-risk feature")
    
    # Test automation recommendations
    automatable_types = ['functional', 'boundary', 'integration']
    automatable_tests = [tc for tc in test_cases if tc['type'] in automatable_types]
    if len(automatable_tests) > 10:
        recommendations.append("Consider test automation for repetitive test cases")
    
    # Data recommendations
    if len(set(tc.get('user_role') for tc in test_cases)) < 3:
        recommendations.append("Include tests for additional user roles and personas")
    
    return recommendations[:5]  # Return top 5 recommendations