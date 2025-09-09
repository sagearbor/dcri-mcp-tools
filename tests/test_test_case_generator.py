import pytest
from tools.test_case_generator import run


def test_test_case_generator_basic():
    """Test basic test case generation."""
    input_data = {
        "feature_specification": """
        User Story: As a clinical investigator, I want to enter patient adverse events 
        so that I can track safety data for the study.
        
        Acceptance Criteria:
        - System shall allow entry of AE description
        - System shall capture AE severity grade
        - System shall record AE start and stop dates
        """,
        "feature_type": "system",
        "test_types": ["functional", "negative"],
        "coverage_level": "comprehensive"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["test_generation_summary"]["total_test_cases"] > 0
    assert len(result["test_cases"]) > 0
    
    # Check for both functional and negative test cases
    functional_cases = [tc for tc in result["test_cases"] if tc["type"] == "functional"]
    negative_cases = [tc for tc in result["test_cases"] if tc["type"] == "negative"]
    
    assert len(functional_cases) > 0
    assert len(negative_cases) > 0


def test_test_case_generator_functional_tests():
    """Test functional test case generation."""
    input_data = {
        "feature_specification": """
        The system shall validate patient eligibility based on inclusion criteria:
        - Age between 18-75 years
        - Confirmed diagnosis of the target condition
        - Signed informed consent form
        """,
        "test_types": ["functional"],
        "feature_type": "protocol"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    functional_cases = [tc for tc in result["test_cases"] if tc["type"] == "functional"]
    assert len(functional_cases) > 0
    
    # Check that test cases cover the requirements
    test_titles = [tc["title"] for tc in functional_cases]
    assert any("eligibility" in title.lower() for title in test_titles)


def test_test_case_generator_negative_tests():
    """Test negative test case generation."""
    input_data = {
        "feature_specification": """
        Patient registration form with the following required fields:
        - Patient ID (must be unique, 8 characters)
        - Date of birth (must be valid date)
        - Gender (M/F/Other)
        
        Business Rules:
        - Patient ID cannot be duplicate
        - Age must be >= 18 years
        """,
        "test_types": ["negative"],
        "feature_type": "system"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    negative_cases = [tc for tc in result["test_cases"] if tc["type"] == "negative"]
    assert len(negative_cases) > 0
    
    # Should include tests for invalid inputs
    test_descriptions = [tc["objective"] for tc in negative_cases]
    assert any("invalid" in desc.lower() for desc in test_descriptions)


def test_test_case_generator_boundary_tests():
    """Test boundary test case generation."""
    input_data = {
        "feature_specification": """
        Drug dosing calculator with the following constraints:
        - Patient weight: 40-150 kg
        - Age: 18-85 years
        - Dose calculation: weight × 5mg/kg (max 750mg)
        """,
        "test_types": ["boundary"],
        "coverage_level": "comprehensive"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    boundary_cases = [tc for tc in result["test_cases"] if tc["type"] == "boundary"]
    assert len(boundary_cases) > 0
    
    # Should test edge values
    test_data = [tc["test_data_needed"] for tc in boundary_cases]
    assert any("minimum" in str(data).lower() or "maximum" in str(data).lower() for data in test_data)


def test_test_case_generator_security_tests():
    """Test security test case generation."""
    input_data = {
        "feature_specification": """
        User authentication system for clinical trial portal:
        - Users must login with username and password
        - System shall lock account after 3 failed attempts
        - Passwords must meet complexity requirements
        - Session timeout after 30 minutes of inactivity
        """,
        "test_types": ["security"],
        "risk_level": "high"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    security_cases = [tc for tc in result["test_cases"] if tc["type"] == "security"]
    assert len(security_cases) > 0
    
    # Should include authentication and authorization tests
    test_titles = [tc["title"] for tc in security_cases]
    assert any("authentication" in title.lower() or "authorization" in title.lower() for title in test_titles)


def test_test_case_generator_regulatory_tests():
    """Test regulatory compliance test generation."""
    input_data = {
        "feature_specification": """
        Electronic data capture system for clinical trials must comply with:
        - 21 CFR Part 11 for electronic signatures
        - Audit trail requirements for all data changes
        - User access controls and permissions
        """,
        "regulatory_context": ["21CFR11", "GCP"],
        "test_types": ["functional", "regulatory"]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    regulatory_cases = [tc for tc in result["test_cases"] if tc["type"] == "regulatory"]
    assert len(regulatory_cases) > 0
    
    # Should include CFR Part 11 compliance tests
    test_titles = [tc["title"] for tc in regulatory_cases]
    assert any("21cfr11" in title.lower() or "audit" in title.lower() for title in test_titles)


def test_test_case_generator_performance_tests():
    """Test performance test case generation."""
    input_data = {
        "feature_specification": """
        Clinical data reporting system requirements:
        - Generate safety reports within 2 minutes
        - Support 100 concurrent users
        - Process batch data uploads up to 10MB
        """,
        "test_types": ["performance"],
        "coverage_level": "comprehensive"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    performance_cases = [tc for tc in result["test_cases"] if tc["type"] == "performance"]
    assert len(performance_cases) > 0
    
    # Should include load and response time tests
    objectives = [tc["objective"] for tc in performance_cases]
    assert any("performance" in obj.lower() or "load" in obj.lower() for obj in objectives)


def test_test_case_generator_integration_tests():
    """Test integration test case generation."""
    input_data = {
        "feature_specification": """
        Clinical trial management system integration with:
        - Electronic Data Capture (EDC) system
        - Randomization and Trial Supply Management (RTSM)
        - Safety database for adverse event reporting
        """,
        "test_types": ["integration"],
        "feature_type": "system"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    integration_cases = [tc for tc in result["test_cases"] if tc["type"] == "integration"]
    assert len(integration_cases) > 0
    
    # Should test system interactions
    test_titles = [tc["title"] for tc in integration_cases]
    assert any("integration" in title.lower() for title in test_titles)


def test_test_case_generator_coverage_analysis():
    """Test coverage analysis functionality."""
    input_data = {
        "feature_specification": """
        Patient screening module requirements:
        1. Check inclusion criteria compliance
        2. Verify exclusion criteria not met
        3. Record screening decision and rationale
        4. Generate screening log report
        """,
        "test_types": ["functional", "negative", "boundary"],
        "coverage_level": "exhaustive"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "coverage_analysis" in result
    
    coverage = result["coverage_analysis"]
    assert "requirements_coverage" in coverage
    assert coverage["requirements_coverage"]["total_requirements"] > 0
    assert "coverage_percentage" in coverage["requirements_coverage"]


def test_test_case_generator_traceability_matrix():
    """Test traceability matrix generation."""
    input_data = {
        "feature_specification": """
        Requirements:
        - REQ-001: System shall capture adverse event severity
        - REQ-002: System shall validate AE dates
        - REQ-003: System shall allow AE narrative entry
        
        Acceptance Criteria:
        - Given AE form is open, when severity is selected, then it is saved
        - Given dates are entered, when form is saved, then dates are validated
        """,
        "test_types": ["functional"]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "traceability_matrix" in result
    
    traceability = result["traceability_matrix"]["traceability_matrix"]
    assert len(traceability) > 0
    
    # Each requirement should have associated test cases
    for req, info in traceability.items():
        if info["coverage_status"] == "covered":
            assert len(info["test_cases"]) > 0


def test_test_case_generator_test_data_requirements():
    """Test test data requirements generation."""
    input_data = {
        "feature_specification": """
        Patient demographics form testing:
        - Patient data with various ages, genders, races
        - Valid and invalid date formats
        - Boundary conditions for numeric fields
        """,
        "test_types": ["functional", "negative", "boundary"]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "test_data_requirements" in result
    
    data_requirements = result["test_data_requirements"]
    assert "data_categories" in data_requirements
    assert len(data_requirements["data_categories"]) > 0


def test_test_case_generator_execution_plan():
    """Test execution plan generation."""
    input_data = {
        "feature_specification": """
        Clinical trial randomization system testing requirements:
        - Functional testing of randomization algorithm
        - Security testing of access controls
        - Performance testing under load
        - Integration testing with RTSM system
        """,
        "test_types": ["functional", "security", "performance", "integration"],
        "coverage_level": "comprehensive",
        "risk_level": "high"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "execution_plan" in result
    
    plan = result["execution_plan"]
    assert "execution_phases" in plan
    assert "total_estimated_duration" in plan
    assert "resource_requirements" in plan
    assert len(plan["execution_phases"]) > 0


def test_test_case_generator_quality_metrics():
    """Test quality metrics calculation."""
    input_data = {
        "feature_specification": """
        Comprehensive adverse event reporting system with:
        - AE data capture and validation
        - Severity grading according to CTCAE
        - Causality assessment workflow
        - Regulatory reporting requirements
        """,
        "test_types": ["functional", "negative", "regulatory"],
        "coverage_level": "comprehensive",
        "risk_level": "high",
        "regulatory_context": ["21CFR11", "GCP"]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "quality_metrics" in result
    
    metrics = result["quality_metrics"]
    assert "completeness_score" in metrics
    assert "risk_coverage_score" in metrics
    assert "regulatory_compliance_score" in metrics
    assert all(0 <= score <= 100 for score in metrics.values())


def test_test_case_generator_empty_specification():
    """Test handling of empty feature specification."""
    input_data = {
        "feature_specification": "",
        "test_types": ["functional"]
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert "No feature specification provided" in result["error"]


def test_test_case_generator_recommendations():
    """Test testing recommendations generation."""
    input_data = {
        "feature_specification": """
        Basic patient registration form with minimal validation.
        Only captures patient ID and date of birth.
        """,
        "test_types": ["functional"],
        "coverage_level": "basic",
        "risk_level": "low"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "recommendations" in result
    assert len(result["recommendations"]) > 0
    
    # Should suggest improvements for better coverage
    recommendations = result["recommendations"]
    assert any("test" in rec.lower() for rec in recommendations)


def test_test_case_generator_risk_based_prioritization():
    """Test risk-based test case prioritization."""
    input_data = {
        "feature_specification": """
        Drug dosing calculation system:
        - Calculate dose based on patient weight and indication
        - Apply dose modification rules for organ impairment
        - Generate dosing schedule for study visits
        """,
        "test_types": ["functional", "negative", "boundary"],
        "risk_level": "high"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    
    # High-risk features should have more high-priority test cases
    high_priority_cases = [tc for tc in result["test_cases"] if tc["priority"] == "high"]
    assert len(high_priority_cases) > 0
    
    # Test cases should be prioritized (have execution_sequence)
    assert all("execution_sequence" in tc for tc in result["test_cases"])


def test_test_case_generator_complex_specification():
    """Test with complex feature specification."""
    input_data = {
        "feature_specification": """
        Multi-module clinical trial management system:
        
        Module 1: Patient Management
        - Patient registration and demographics
        - Medical history capture
        - Concomitant medications tracking
        
        Module 2: Visit Management  
        - Visit scheduling and tracking
        - Procedure checklist management
        - Visit window calculations
        
        Module 3: Safety Management
        - Adverse event capture and coding
        - Serious AE reporting workflow
        - Safety signal detection
        
        Integration Requirements:
        - Real-time data synchronization between modules
        - Audit trail for all data changes
        - Role-based access control across modules
        """,
        "test_types": ["functional", "integration", "security", "negative"],
        "coverage_level": "exhaustive",
        "risk_level": "high",
        "regulatory_context": ["21CFR11", "GCP", "HIPAA"]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["test_generation_summary"]["total_test_cases"] > 20
    
    # Should cover all test types
    test_types = set(tc["type"] for tc in result["test_cases"])
    expected_types = {"functional", "integration", "security", "negative"}
    assert expected_types.issubset(test_types)
    
    # Should have high coverage
    coverage = result["coverage_analysis"]["requirements_coverage"]
    assert coverage["coverage_percentage"] > 80


def test_test_case_generator_usability_tests():
    """Test usability test case generation."""
    input_data = {
        "feature_specification": """
        Patient portal interface for clinical trial participants:
        - View study information and schedule
        - Complete patient-reported outcome questionnaires
        - Access educational materials
        - Contact study team
        """,
        "test_types": ["usability"],
        "target_audience": "patients"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    usability_cases = [tc for tc in result["test_cases"] if tc["type"] == "usability"]
    assert len(usability_cases) > 0
    
    # Should include user experience testing
    objectives = [tc["objective"] for tc in usability_cases]
    assert any("usability" in obj.lower() or "user" in obj.lower() for obj in objectives)