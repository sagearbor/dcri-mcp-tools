# DCRI MCP Tools - User Training Guide

## Introduction

Welcome to the DCRI MCP Tools platform! This comprehensive suite provides 80+ clinical research tools designed to streamline clinical trial operations, enhance data quality, and ensure regulatory compliance.

## Quick Start Guide

### 1. Accessing the Platform

- **Development Environment**: `http://127.0.0.1:8210`
- **Production Environment**: Contact your system administrator for the URL

### 2. Basic Concepts

#### MCP (Model Context Protocol)
- Industry-standard protocol for tool execution
- Enables seamless integration with various clients
- Provides consistent interface across all tools

#### Tool Categories
The platform organizes tools into functional categories:
- **Data Management & Quality**: Data validation and quality assurance
- **Safety & Medical Coding**: Adverse event coding and safety monitoring
- **Regulatory & Compliance**: FDA submissions and compliance checking
- **Protocol & Study Design**: Sample size calculations and study planning
- **Site Management**: Site performance monitoring and management
- **Statistical & Reporting**: Statistical analysis and report generation
- **Quality & Audit**: Audit trails and quality metrics

## Common Workflows

### 1. Data Quality Workflow

**Step 1: Validate Data Dictionary**
```bash
curl -X POST http://127.0.0.1:8210/run_tool/data_dictionary_validator \
  -H "Content-Type: application/json" \
  -d '{"csv_data": [...], "schema": {...}}'
```

**Step 2: Check for Duplicates**
```bash
curl -X POST http://127.0.0.1:8210/run_tool/duplicate_subject_detector \
  -H "Content-Type: application/json" \
  -d '{"subjects": [...], "matching_criteria": [...]}'
```

**Step 3: Generate Data Queries**
```bash
curl -X POST http://127.0.0.1:8210/run_tool/data_query_generator \
  -H "Content-Type: application/json" \
  -d '{"data": [...], "logic_checks": [...]}'
```

### 2. Safety Monitoring Workflow

**Step 1: Code Adverse Events**
```bash
curl -X POST http://127.0.0.1:8210/run_tool/adverse_event_coder \
  -H "Content-Type: application/json" \
  -d '{"events": [{"verbatim_term": "headache", "severity_description": "mild"}]}'
```

**Step 2: Detect Safety Signals**
```bash
curl -X POST http://127.0.0.1:8210/run_tool/safety_signal_detector \
  -H "Content-Type: application/json" \
  -d '{"adverse_events": [...], "total_subjects": {...}}'
```

**Step 3: Generate Patient Narratives**
```bash
curl -X POST http://127.0.0.1:8210/run_tool/patient_narrative_generator \
  -H "Content-Type: application/json" \
  -d '{"patient_data": {...}, "adverse_events": [...]}'
```

### 3. Study Design Workflow

**Step 1: Calculate Sample Size**
```bash
curl -X POST http://127.0.0.1:8210/run_tool/sample_size_calculator \
  -H "Content-Type: application/json" \
  -d '{"alpha": 0.05, "power": 0.8, "effect_size": 0.5}'
```

**Step 2: Generate Randomization List**
```bash
curl -X POST http://127.0.0.1:8210/run_tool/randomization_generator \
  -H "Content-Type: application/json" \
  -d '{"total_subjects": 100, "allocation_ratio": [1, 1]}'
```

**Step 3: Assess Study Complexity**
```bash
curl -X POST http://127.0.0.1:8210/run_tool/study_complexity_calculator \
  -H "Content-Type: application/json" \
  -d '{"protocol_features": {...}}'
```

## Tool-Specific Training

### High-Priority Tools (Quick Wins)

#### 1. Consent Grade Checker
**Purpose**: Ensures informed consent forms meet readability requirements

**Usage Example**:
```json
{
  "document_text": "Your participation in this study is voluntary...",
  "target_grade_level": 8,
  "assessment_method": "flesch_kincaid"
}
```

**Key Features**:
- Multiple readability algorithms
- Grade level recommendations
- Improvement suggestions

#### 2. Sample Size Calculator
**Purpose**: Determines appropriate sample sizes for statistical power

**Usage Example**:
```json
{
  "study_type": "two_sample_t_test",
  "alpha": 0.05,
  "power": 0.8,
  "effect_size": 0.5,
  "allocation_ratio": 1
}
```

**Key Features**:
- Multiple statistical test types
- Power curves
- Sensitivity analysis

#### 3. Document De-identifier
**Purpose**: Removes personally identifiable information from documents

**Usage Example**:
```json
{
  "documents": [
    {"content": "Patient John Doe (DOB: 01/01/1980)..."}
  ],
  "redaction_rules": {
    "names": true,
    "dates": true,
    "addresses": true
  }
}
```

**Key Features**:
- HIPAA-compliant redaction
- Custom redaction rules
- Audit trail of changes

### Advanced Tools

#### Risk-Benefit Analyzer
**Purpose**: Calculates comprehensive risk-benefit ratios

**Complex Usage**:
```json
{
  "efficacy_data": {
    "primary_endpoint": {
      "treatment_effect": 25,
      "p_value": 0.001
    }
  },
  "safety_data": {
    "serious_adverse_events": {"rate": 0.05},
    "discontinuations": {"due_to_ae_rate": 5}
  },
  "population_characteristics": {
    "median_age": 65,
    "comorbidity_index": 2
  }
}
```

#### DSMB Packager
**Purpose**: Prepares comprehensive DSMB meeting packages

**Complex Usage**:
```json
{
  "meeting_details": {
    "meeting_date": "2024-03-15",
    "meeting_type": "scheduled"
  },
  "enrollment_data": {
    "total_enrolled": 150,
    "target_enrollment": 200
  },
  "safety_data": {
    "adverse_events": {...},
    "serious_adverse_events": [...],
    "deaths": []
  }
}
```

## Best Practices

### 1. Data Preparation
- Always validate input data format before tool execution
- Use consistent date formats (YYYY-MM-DD)
- Ensure required fields are populated
- Test with sample data first

### 2. Error Handling
- Check response status codes
- Review error messages for specific guidance
- Validate input parameters match tool requirements
- Use appropriate timeout values for long-running processes

### 3. Security Considerations
- Never include actual patient data in test environments
- Use de-identified or synthetic data for testing
- Implement appropriate access controls in production
- Regularly audit tool usage logs

### 4. Performance Optimization
- Process data in appropriate batch sizes
- Use appropriate timeout values
- Monitor system resources during large operations
- Implement caching where appropriate

## Troubleshooting

### Common Issues

#### Tool Not Found (404 Error)
```json
{"error": "Tool 'tool_name' not found", "status": 404}
```
**Solution**: Verify tool name spelling and availability

#### Invalid Input Parameters (400 Error)
```json
{"error": "Missing required parameter: 'data'", "status": 400}
```
**Solution**: Review tool documentation for required parameters

#### Tool Execution Error (500 Error)
```json
{"error": "Error processing data: Invalid date format", "status": 500}
```
**Solution**: Check data format and validate input parameters

### Getting Help

1. **Check API Documentation**: Review detailed parameter requirements
2. **Validate Input Data**: Ensure data meets tool specifications
3. **Review Error Messages**: Error messages provide specific guidance
4. **Contact Support**: Reach out to the DCRI development team

## Advanced Features

### Batch Processing
Some tools support batch processing for large datasets:

```bash
# Process multiple subjects at once
curl -X POST http://127.0.0.1:8210/run_tool/adverse_event_coder \
  -H "Content-Type: application/json" \
  -d '{"events": [{"verbatim_term": "event1"}, {"verbatim_term": "event2"}]}'
```

### Custom Configurations
Many tools accept custom configuration parameters:

```json
{
  "data": [...],
  "configuration": {
    "custom_thresholds": {...},
    "analysis_options": {...}
  }
}
```

### Quality Metrics
Tools provide quality metrics for validation:

```json
{
  "output": {...},
  "quality_metrics": {
    "completeness_rate": 95.2,
    "accuracy_score": 0.98,
    "processing_time": "2.3s"
  }
}
```

## Conclusion

The DCRI MCP Tools platform provides a comprehensive suite of clinical research tools designed to improve efficiency, quality, and compliance. This training guide covers the essential workflows and best practices for effective tool usage.

For additional support or advanced training, please contact the DCRI development team.