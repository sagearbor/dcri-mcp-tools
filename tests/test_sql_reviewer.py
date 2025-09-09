"""
Tests for SQL Reviewer Tool
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.sql_reviewer import run


def test_safe_sql_query():
    """Test review of safe SQL query"""
    sql_query = "SELECT subject_id, age FROM subjects WHERE age > 18"
    
    result = run({
        "sql_query": sql_query,
        "review_level": "standard"
    })
    
    assert result["success"] == True
    assert result["risk_score"] < 20
    assert len(result["security_issues"]) == 0


def test_sql_injection_detection():
    """Test detection of SQL injection patterns"""
    sql_query = "SELECT * FROM users WHERE name = 'admin' OR '1'='1'"
    
    result = run({
        "sql_query": sql_query,
        "review_level": "standard"
    })
    
    assert result["success"] == True
    assert len(result["security_issues"]) > 0
    assert any("injection" in issue["message"].lower() for issue in result["security_issues"])
    assert result["risk_score"] > 20


def test_performance_issues():
    """Test detection of performance issues"""
    sql_query = "SELECT * FROM large_table"
    
    result = run({
        "sql_query": sql_query,
        "review_level": "standard"
    })
    
    assert result["success"] == True
    assert len(result["performance_issues"]) > 0
    assert any("SELECT *" in issue["message"] for issue in result["performance_issues"])


def test_dangerous_update_without_where():
    """Test detection of dangerous UPDATE without WHERE"""
    sql_query = "UPDATE patients SET status = 'INACTIVE'"
    
    result = run({
        "sql_query": sql_query,
        "review_level": "standard"
    })
    
    assert result["success"] == True
    assert len(result["performance_issues"]) > 0
    assert any("WHERE clause" in issue["message"] for issue in result["performance_issues"])
    assert result["risk_score"] > 40


def test_hipaa_compliance():
    """Test detection of HIPAA/PII concerns"""
    sql_query = "SELECT patient_name, ssn, date_of_birth FROM patients"
    
    result = run({
        "sql_query": sql_query,
        "review_level": "standard"
    })
    
    assert result["success"] == True
    assert len(result["compliance_issues"]) > 0
    assert any("PII" in issue["message"] or "PHI" in issue["message"] for issue in result["compliance_issues"])


def test_query_complexity_assessment():
    """Test query complexity assessment"""
    simple_query = "SELECT id FROM table1"
    complex_query = """
    SELECT t1.id, t2.name, t3.value 
    FROM table1 t1 
    JOIN table2 t2 ON t1.id = t2.id 
    JOIN table3 t3 ON t2.id = t3.id 
    WHERE t1.status IN (SELECT status FROM status_table WHERE active = 1)
    """
    
    result_simple = run({"sql_query": simple_query})
    result_complex = run({"sql_query": complex_query})
    
    assert result_simple["review_results"]["query_complexity"] == "LOW"
    assert result_complex["review_results"]["query_complexity"] in ["MEDIUM", "HIGH"]


def test_table_extraction():
    """Test table name extraction"""
    sql_query = """
    SELECT u.name, p.age 
    FROM users u 
    JOIN profiles p ON u.id = p.user_id 
    WHERE u.active = 1
    """
    
    result = run({"sql_query": sql_query})
    
    tables = result["review_results"]["tables_referenced"]
    assert "users" in tables
    assert "profiles" in tables


def test_recommendations_generation():
    """Test recommendations generation"""
    sql_query = "SELECT * FROM users WHERE name = '' OR 1=1"
    
    result = run({
        "sql_query": sql_query,
        "review_level": "standard"
    })
    
    assert len(result["recommendations"]) > 0
    # Should have security recommendations
    assert any(rec["category"] == "Security" for rec in result["recommendations"])


def test_empty_query():
    """Test handling of empty query"""
    result = run({"sql_query": ""})
    
    assert result["success"] == False
    assert result["risk_score"] == 0


def test_comprehensive_review():
    """Test comprehensive review level"""
    sql_query = """
    SELECT * FROM patients p 
    JOIN medical_records m ON p.id = m.patient_id 
    WHERE p.name LIKE '%test%' AND m.date > '2020-01-01'
    """
    
    result = run({
        "sql_query": sql_query,
        "review_level": "comprehensive"
    })
    
    assert result["success"] == True
    # Comprehensive should find more issues
    total_issues = len(result["security_issues"]) + len(result["performance_issues"]) + len(result["compliance_issues"])
    assert total_issues > 0


def test_risk_score_calculation():
    """Test risk score calculation"""
    # Low risk query
    safe_query = "SELECT id, name FROM products WHERE category = 'electronics'"
    
    # High risk query
    dangerous_query = "DELETE FROM patients; DROP TABLE medical_records; --"
    
    result_safe = run({"sql_query": safe_query})
    result_dangerous = run({"sql_query": dangerous_query})
    
    assert result_safe["risk_score"] < result_dangerous["risk_score"]
    assert result_dangerous["risk_score"] > 50