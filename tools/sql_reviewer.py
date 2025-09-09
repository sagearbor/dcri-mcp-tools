"""
SQL Reviewer Tool
Reviews SQL queries for security, performance, and compliance issues
Identifies potential risks and provides improvement recommendations
"""

import json
import re
from typing import Dict, List, Any, Optional


def run(input_data: dict) -> dict:
    """
    Reviews SQL queries for issues and provides recommendations
    
    Args:
        input_data: Dictionary containing:
            - sql_query: SQL query string to review
            - review_level: 'basic', 'standard', or 'comprehensive' (default: 'standard')
            - database_type: Database type for specific checks (optional)
    
    Returns:
        Dictionary containing:
            - success: Boolean indicating if review succeeded
            - review_results: Detailed review results
            - security_issues: Security-related findings
            - performance_issues: Performance-related findings
            - compliance_issues: Compliance-related findings
            - recommendations: Improvement recommendations
            - risk_score: Overall risk assessment
    """
    try:
        sql_query = input_data.get('sql_query', '').strip()
        review_level = input_data.get('review_level', 'standard')
        database_type = input_data.get('database_type', 'generic')
        
        if not sql_query:
            return {
                'success': False,
                'review_results': {},
                'security_issues': [],
                'performance_issues': [],
                'compliance_issues': [],
                'recommendations': [],
                'risk_score': 0
            }
        
        # Initialize results
        security_issues = []
        performance_issues = []
        compliance_issues = []
        recommendations = []
        
        # Normalize SQL for analysis
        normalized_sql = normalize_sql(sql_query)
        
        # Security analysis
        security_issues = analyze_security(normalized_sql, sql_query)
        
        # Performance analysis
        performance_issues = analyze_performance(normalized_sql, sql_query)
        
        # Compliance analysis
        if review_level in ['standard', 'comprehensive']:
            compliance_issues = analyze_compliance(normalized_sql, sql_query)
        
        # Advanced analysis for comprehensive level
        if review_level == 'comprehensive':
            advanced_issues = analyze_advanced_patterns(normalized_sql, sql_query)
            security_issues.extend(advanced_issues.get('security', []))
            performance_issues.extend(advanced_issues.get('performance', []))
        
        # Generate recommendations
        recommendations = generate_recommendations(
            security_issues, performance_issues, compliance_issues, normalized_sql
        )
        
        # Calculate risk score
        risk_score = calculate_risk_score(security_issues, performance_issues, compliance_issues)
        
        # Compile review results
        review_results = {
            'query_length': len(sql_query),
            'query_complexity': assess_complexity(normalized_sql),
            'tables_referenced': extract_table_names(normalized_sql),
            'query_type': identify_query_type(normalized_sql),
            'has_subqueries': normalized_sql.count('select') > 1,
            'has_joins': bool(re.search(r'\b(inner|left|right|full|cross)\s+join\b', normalized_sql, re.IGNORECASE)),
            'uses_functions': bool(re.search(r'\b(count|sum|avg|max|min|upper|lower)\s*\(', normalized_sql, re.IGNORECASE))
        }
        
        return {
            'success': True,
            'review_results': review_results,
            'security_issues': security_issues,
            'performance_issues': performance_issues,
            'compliance_issues': compliance_issues,
            'recommendations': recommendations,
            'risk_score': risk_score,
            'summary': {
                'total_issues': len(security_issues) + len(performance_issues) + len(compliance_issues),
                'high_severity_issues': sum(1 for issue_list in [security_issues, performance_issues, compliance_issues] 
                                          for issue in issue_list if issue.get('severity') == 'HIGH'),
                'review_level': review_level,
                'overall_assessment': get_overall_assessment(risk_score)
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'review_results': {},
            'security_issues': [],
            'performance_issues': [],
            'compliance_issues': [],
            'recommendations': [],
            'risk_score': 0,
            'errors': [f"SQL review failed: {str(e)}"]
        }


def normalize_sql(sql_query: str) -> str:
    """Normalize SQL query for analysis"""
    # Convert to lowercase and remove extra whitespace
    normalized = re.sub(r'\s+', ' ', sql_query.lower().strip())
    
    # Remove comments
    normalized = re.sub(r'--.*?\n', '', normalized)
    normalized = re.sub(r'/\*.*?\*/', '', normalized, flags=re.DOTALL)
    
    return normalized


def analyze_security(normalized_sql: str, original_sql: str) -> List[dict]:
    """Analyze SQL for security issues"""
    issues = []
    
    # SQL Injection patterns
    injection_patterns = [
        (r"'\s*or\s+'", "Potential SQL injection: OR condition in string"),
        (r"';\s*drop\s+", "Potential SQL injection: DROP statement"),
        (r"';\s*delete\s+", "Potential SQL injection: DELETE statement"),
        (r"';\s*insert\s+", "Potential SQL injection: INSERT statement"),
        (r"';\s*update\s+", "Potential SQL injection: UPDATE statement"),
        (r"\bunion\s+select\b", "Potential SQL injection: UNION SELECT"),
        (r"'\s*\+\s*'", "String concatenation that might enable injection")
    ]
    
    for pattern, message in injection_patterns:
        if re.search(pattern, normalized_sql, re.IGNORECASE):
            issues.append({
                'type': 'security',
                'category': 'sql_injection',
                'severity': 'HIGH',
                'message': message,
                'recommendation': 'Use parameterized queries or prepared statements'
            })
    
    # Dynamic SQL construction
    if re.search(r'exec\s*\(', normalized_sql, re.IGNORECASE):
        issues.append({
            'type': 'security',
            'category': 'dynamic_sql',
            'severity': 'MEDIUM',
            'message': 'Dynamic SQL execution detected',
            'recommendation': 'Avoid dynamic SQL construction; use parameterized queries'
        })
    
    # Potentially sensitive data access
    sensitive_patterns = [
        (r'\b(password|ssn|social_security|credit_card|cc_num)\b', 'Accessing potentially sensitive data'),
        (r'\*\s+from\s+\w+', 'SELECT * may expose sensitive columns')
    ]
    
    for pattern, message in sensitive_patterns:
        if re.search(pattern, normalized_sql, re.IGNORECASE):
            issues.append({
                'type': 'security',
                'category': 'data_exposure',
                'severity': 'MEDIUM',
                'message': message,
                'recommendation': 'Explicitly specify required columns; avoid SELECT *'
            })
    
    # Also check for dangerous UPDATE/DELETE without WHERE as security issue
    if re.search(r'\b(update|delete)\b(?!.*\bwhere\b)', normalized_sql, re.IGNORECASE):
        issues.append({
            'type': 'security',
            'category': 'data_loss_risk',
            'severity': 'HIGH',
            'message': 'UPDATE/DELETE without WHERE clause is extremely dangerous',
            'recommendation': 'Always use WHERE clause to prevent accidental data loss'
        })
    
    # Check for OR 1=1 pattern (common SQL injection)
    if re.search(r"or\s+['\"]?\s*1\s*=\s*1", normalized_sql, re.IGNORECASE):
        issues.append({
            'type': 'security',
            'category': 'sql_injection',
            'severity': 'HIGH',
            'message': 'Potential SQL injection pattern detected (OR 1=1)',
            'recommendation': 'Never use user input directly in SQL; use parameterized queries'
        })
    
    return issues


def analyze_performance(normalized_sql: str, original_sql: str) -> List[dict]:
    """Analyze SQL for performance issues"""
    issues = []
    
    # Missing WHERE clause in UPDATE/DELETE - This is CRITICAL for safety
    if re.search(r'\b(update|delete)\b(?!.*\bwhere\b)', normalized_sql, re.IGNORECASE):
        issues.append({
            'type': 'performance',
            'category': 'missing_where',
            'severity': 'CRITICAL',  # Changed to CRITICAL
            'message': 'UPDATE/DELETE without WHERE clause affects all rows',
            'recommendation': 'Add appropriate WHERE clause to limit scope'
        })
    
    # SELECT * usage
    if re.search(r'select\s+\*', normalized_sql, re.IGNORECASE):
        issues.append({
            'type': 'performance',
            'category': 'select_star',
            'severity': 'MEDIUM',
            'message': 'SELECT * retrieves all columns, potentially inefficient',
            'recommendation': 'Specify only required columns'
        })
    
    # Functions in WHERE clause
    function_in_where = re.search(r'where.*\b(upper|lower|substring|convert)\s*\(.*=', normalized_sql, re.IGNORECASE)
    if function_in_where:
        issues.append({
            'type': 'performance',
            'category': 'function_in_where',
            'severity': 'MEDIUM',
            'message': 'Functions in WHERE clause prevent index usage',
            'recommendation': 'Consider restructuring query to avoid functions on columns'
        })
    
    # OR conditions that might prevent index usage
    if re.search(r'where.*\bor\b', normalized_sql, re.IGNORECASE):
        issues.append({
            'type': 'performance',
            'category': 'or_conditions',
            'severity': 'LOW',
            'message': 'OR conditions may prevent efficient index usage',
            'recommendation': 'Consider using UNION for better performance'
        })
    
    # Nested subqueries
    subquery_count = len(re.findall(r'\(\s*select\b', normalized_sql, re.IGNORECASE))
    if subquery_count > 2:
        issues.append({
            'type': 'performance',
            'category': 'complex_subqueries',
            'severity': 'MEDIUM',
            'message': f'Multiple nested subqueries ({subquery_count}) detected',
            'recommendation': 'Consider using JOINs or CTEs for better readability and performance'
        })
    
    # DISTINCT usage
    if re.search(r'select\s+distinct', normalized_sql, re.IGNORECASE):
        issues.append({
            'type': 'performance',
            'category': 'distinct_usage',
            'severity': 'LOW',
            'message': 'DISTINCT requires additional processing',
            'recommendation': 'Ensure DISTINCT is necessary; consider if duplicates can be prevented at source'
        })
    
    return issues


def analyze_compliance(normalized_sql: str, original_sql: str) -> List[dict]:
    """Analyze SQL for compliance issues"""
    issues = []
    
    # Potential HIPAA/PII concerns
    hipaa_patterns = [
        r'\b(patient_name|first_name|last_name|address|phone|email)\b',
        r'\b(dob|date_of_birth|birth_date)\b',
        r'\b(ssn|social_security)\b'
    ]
    
    for pattern in hipaa_patterns:
        if re.search(pattern, normalized_sql, re.IGNORECASE):
            issues.append({
                'type': 'compliance',
                'category': 'hipaa_pii',
                'severity': 'HIGH',
                'message': 'Query may access PII/PHI data',
                'recommendation': 'Ensure proper authorization and data handling procedures'
            })
            break  # Only report once
    
    # Data retention concerns
    if re.search(r'\bdelete\b(?!.*\bwhere\b.*\bdate\b)', normalized_sql, re.IGNORECASE):
        issues.append({
            'type': 'compliance',
            'category': 'data_retention',
            'severity': 'MEDIUM',
            'message': 'DELETE operation without date-based criteria',
            'recommendation': 'Consider data retention policies and add appropriate date filters'
        })
    
    # Audit trail concerns
    if re.search(r'\b(update|delete)\b', normalized_sql, re.IGNORECASE):
        if not re.search(r'\b(audit|log|history)\b', normalized_sql, re.IGNORECASE):
            issues.append({
                'type': 'compliance',
                'category': 'audit_trail',
                'severity': 'LOW',
                'message': 'Data modification without apparent audit logging',
                'recommendation': 'Ensure audit trail is maintained for data changes'
            })
    
    return issues


def analyze_advanced_patterns(normalized_sql: str, original_sql: str) -> dict:
    """Advanced pattern analysis for comprehensive review"""
    advanced_issues = {'security': [], 'performance': []}
    
    # Complex JOIN patterns
    join_count = len(re.findall(r'\bjoin\b', normalized_sql, re.IGNORECASE))
    if join_count > 5:
        advanced_issues['performance'].append({
            'type': 'performance',
            'category': 'complex_joins',
            'severity': 'MEDIUM',
            'message': f'Query has {join_count} JOINs, may impact performance',
            'recommendation': 'Review query design and consider query optimization'
        })
    
    # Potential for SQL injection via LIKE patterns
    if re.search(r"like\s+.*'%.*%'", normalized_sql, re.IGNORECASE):
        advanced_issues['security'].append({
            'type': 'security',
            'category': 'like_injection',
            'severity': 'MEDIUM',
            'message': 'LIKE pattern with wildcards may be vulnerable to injection',
            'recommendation': 'Validate and sanitize LIKE pattern inputs'
        })
    
    return advanced_issues


def extract_table_names(normalized_sql: str) -> List[str]:
    """Extract table names from SQL query"""
    tables = []
    
    # FROM clause
    from_matches = re.findall(r'from\s+(\w+)', normalized_sql, re.IGNORECASE)
    tables.extend(from_matches)
    
    # JOIN clauses
    join_matches = re.findall(r'join\s+(\w+)', normalized_sql, re.IGNORECASE)
    tables.extend(join_matches)
    
    # UPDATE/DELETE
    update_matches = re.findall(r'(?:update|delete\s+from)\s+(\w+)', normalized_sql, re.IGNORECASE)
    tables.extend(update_matches)
    
    # INSERT INTO
    insert_matches = re.findall(r'insert\s+into\s+(\w+)', normalized_sql, re.IGNORECASE)
    tables.extend(insert_matches)
    
    return list(set(tables))  # Remove duplicates


def identify_query_type(normalized_sql: str) -> str:
    """Identify the type of SQL query"""
    if normalized_sql.startswith('select'):
        return 'SELECT'
    elif normalized_sql.startswith('insert'):
        return 'INSERT'
    elif normalized_sql.startswith('update'):
        return 'UPDATE'
    elif normalized_sql.startswith('delete'):
        return 'DELETE'
    elif normalized_sql.startswith('create'):
        return 'CREATE'
    elif normalized_sql.startswith('drop'):
        return 'DROP'
    elif normalized_sql.startswith('alter'):
        return 'ALTER'
    else:
        return 'UNKNOWN'


def assess_complexity(normalized_sql: str) -> str:
    """Assess query complexity"""
    complexity_score = 0
    
    # Base complexity
    if 'select' in normalized_sql:
        complexity_score += 1
    
    # JOINs add complexity
    join_count = len(re.findall(r'\bjoin\b', normalized_sql, re.IGNORECASE))
    complexity_score += join_count
    
    # Subqueries add complexity
    subquery_count = len(re.findall(r'\(\s*select\b', normalized_sql, re.IGNORECASE))
    complexity_score += subquery_count * 2
    
    # Functions add some complexity
    function_count = len(re.findall(r'\b\w+\s*\(', normalized_sql))
    complexity_score += function_count * 0.5
    
    if complexity_score < 3:
        return 'LOW'
    elif complexity_score < 8:
        return 'MEDIUM'
    else:
        return 'HIGH'


def generate_recommendations(security_issues: List[dict], performance_issues: List[dict], 
                           compliance_issues: List[dict], normalized_sql: str) -> List[dict]:
    """Generate overall recommendations"""
    recommendations = []
    
    # Security recommendations
    if security_issues:
        high_security = [i for i in security_issues if i['severity'] == 'HIGH']
        if high_security:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Security',
                'title': 'Address Critical Security Issues',
                'description': f'{len(high_security)} high-severity security issues found',
                'action': 'Review and fix SQL injection vulnerabilities immediately'
            })
    
    # Performance recommendations
    if performance_issues:
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Performance',
            'title': 'Optimize Query Performance',
            'description': f'{len(performance_issues)} performance issues identified',
            'action': 'Review query structure and consider indexing strategies'
        })
    
    # Compliance recommendations
    if compliance_issues:
        hipaa_issues = [i for i in compliance_issues if i['category'] == 'hipaa_pii']
        if hipaa_issues:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Compliance',
                'title': 'Ensure Data Privacy Compliance',
                'description': 'Query may access sensitive patient data',
                'action': 'Verify authorization and implement appropriate data controls'
            })
    
    # General recommendations
    if 'select *' in normalized_sql:
        recommendations.append({
            'priority': 'LOW',
            'category': 'Best Practice',
            'title': 'Specify Required Columns',
            'description': 'Query uses SELECT * which may be inefficient',
            'action': 'List only the columns actually needed'
        })
    
    return recommendations


def calculate_risk_score(security_issues: List[dict], performance_issues: List[dict], 
                        compliance_issues: List[dict]) -> int:
    """Calculate overall risk score (0-100)"""
    risk_score = 0
    
    # Security issues have highest weight
    for issue in security_issues:
        if issue['severity'] == 'HIGH':
            risk_score += 30
        elif issue['severity'] == 'MEDIUM':
            risk_score += 15
        else:
            risk_score += 5
    
    # Compliance issues
    for issue in compliance_issues:
        if issue['severity'] == 'HIGH':
            risk_score += 25
        elif issue['severity'] == 'MEDIUM':
            risk_score += 10
        else:
            risk_score += 3
    
    # Performance issues have lower weight (but CRITICAL is still very high)
    for issue in performance_issues:
        if issue.get('severity') == 'CRITICAL':
            risk_score += 35  # CRITICAL performance issues are very dangerous
        elif issue['severity'] == 'HIGH':
            risk_score += 15
        elif issue['severity'] == 'MEDIUM':
            risk_score += 7
        else:
            risk_score += 2
    
    return min(risk_score, 100)  # Cap at 100


def get_overall_assessment(risk_score: int) -> str:
    """Get overall assessment based on risk score"""
    if risk_score >= 70:
        return 'HIGH_RISK'
    elif risk_score >= 40:
        return 'MEDIUM_RISK'
    elif risk_score >= 15:
        return 'LOW_RISK'
    else:
        return 'MINIMAL_RISK'