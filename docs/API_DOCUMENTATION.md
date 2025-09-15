# DCRI MCP Tools - API Documentation

## Overview

The DCRI MCP Tools server provides REST API endpoints for clinical research tools. The server dynamically loads tool modules and executes them via HTTP POST requests.

## Base URL

- **Local Development**: `http://127.0.0.1:8210`
- **Production**: `https://your-azure-app-service.azurewebsites.net`

## Authentication

Currently, the API does not require authentication for local development. Production deployments should implement appropriate security measures.

## Common Response Format

All tool endpoints return JSON responses with the following structure:

```json
{
  "output": "result_data",
  "error": "error_message_if_any",
  "execution_time": "time_in_milliseconds"
}
```

## Health Check Endpoint

### GET /health

Returns server status information.

**Response:**
```json
{
  "status": "ok"
}
```

## Tool Execution Endpoint

### POST /run_tool/{tool_name}

Executes a specific clinical research tool.

**Parameters:**
- `tool_name` (path): Name of the tool to execute (e.g., `adverse_event_coder`)

**Request Body:** 
JSON object containing tool-specific input parameters.

**Response:**
Tool-specific output in JSON format.

## Available Tools

### Stage 3: Data Management & Quality Tools

#### 1. Data Dictionary Validator
- **Endpoint**: `/run_tool/data_dictionary_validator`
- **Purpose**: Validates CSV data against JSON schema
- **Input**: `{"csv_data": [...], "schema": {...}}`

#### 2. EDC Data Validator
- **Endpoint**: `/run_tool/edc_data_validator`
- **Purpose**: Validates EDC exports against study specifications
- **Input**: `{"edc_data": [...], "study_specifications": {...}}`

#### 3. SDTM Mapper
- **Endpoint**: `/run_tool/sdtm_mapper`
- **Purpose**: Maps raw data to SDTM domains
- **Input**: `{"raw_data": [...], "domain_mapping": {...}}`

### Stage 4: Safety & Medical Coding Tools

#### 1. Adverse Event Coder
- **Endpoint**: `/run_tool/adverse_event_coder`
- **Purpose**: Auto-codes AEs to MedDRA
- **Input**: `{"events": [{"verbatim_term": "headache", "severity_description": "mild"}]}`

#### 2. Concomitant Med Coder
- **Endpoint**: `/run_tool/concomitant_med_coder`
- **Purpose**: Maps medications to WHO Drug Dictionary
- **Input**: `{"medications": [{"verbatim_name": "aspirin", "dose": "81mg"}]}`

#### 3. SAE Reconciliation
- **Endpoint**: `/run_tool/sae_reconciliation`
- **Purpose**: Reconciles SAEs across systems
- **Input**: `{"edc_saes": [...], "safety_db_saes": [...]}`

### Stage 5: Regulatory & Compliance Tools

#### 1. Document De-identifier
- **Endpoint**: `/run_tool/document_deidentifier`
- **Purpose**: Removes PII from documents
- **Input**: `{"documents": [...], "redaction_rules": {...}}`

#### 2. FDA Submission Checker
- **Endpoint**: `/run_tool/fda_submission_checker`
- **Purpose**: Validates submission packages
- **Input**: `{"submission_package": {...}, "regulatory_requirements": {...}}`

### Stage 6: Protocol & Study Design Tools

#### 1. Sample Size Calculator
- **Endpoint**: `/run_tool/sample_size_calculator`
- **Purpose**: Statistical power calculations
- **Input**: `{"alpha": 0.05, "power": 0.8, "effect_size": 0.5}`

#### 2. Randomization Generator
- **Endpoint**: `/run_tool/randomization_generator`
- **Purpose**: Creates randomization schemes
- **Input**: `{"total_subjects": 100, "allocation_ratio": [1, 1], "block_sizes": [4, 6]}`

### Stage 7: Site Management Tools

#### 1. Site Performance Dashboard
- **Endpoint**: `/run_tool/site_performance_dashboard`
- **Purpose**: Enrollment and quality metrics
- **Input**: `{"sites": [...], "enrollment_data": {...}}`

### Stage 8: Statistical & Reporting Tools

#### 1. Interim Analysis Preparer
- **Endpoint**: `/run_tool/interim_analysis_preparer`
- **Purpose**: Prepares interim analysis data
- **Input**: `{"study_data": {...}, "analysis_plan": {...}}`

### Stage 9: Quality & Audit Tools

#### 1. Audit Trail Reviewer
- **Endpoint**: `/run_tool/audit_trail_reviewer`
- **Purpose**: Analyzes audit trails
- **Input**: `{"audit_entries": [...], "analysis_period": 30}`

#### 2. SDV Tool
- **Endpoint**: `/run_tool/sdv_tool`
- **Purpose**: Assists with Source Data Verification
- **Input**: `{"sdv_items": [...], "sdv_strategy": "risk-based"}`

## Error Handling

The API returns standard HTTP status codes:

- **200 OK**: Successful tool execution
- **400 Bad Request**: Invalid input parameters
- **404 Not Found**: Tool not found
- **500 Internal Server Error**: Tool execution error

Error responses include detailed error messages:

```json
{
  "error": "Tool 'nonexistent_tool' not found",
  "status": 404
}
```

## Rate Limiting

Currently no rate limiting is implemented. Production deployments should implement appropriate rate limiting.

## Deployment

### Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure
3. Run server: `python server.py`

### Azure App Service Deployment

1. Set `KEY_VAULT_URI` environment variable
2. Configure Azure Key Vault with required secrets
3. Deploy using Azure App Service

## Support

For technical support, please refer to the project documentation or contact the DCRI development team.