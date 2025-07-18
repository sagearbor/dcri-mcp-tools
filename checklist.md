DCRI MCP Tools – Phased Development Checklist (V3)
This checklist is structured into sequential and parallel stages to get a Minimum Viable Product (MVP) running as quickly as possible. Use the checkboxes [ ] to track your progress.

Development Strategy:

Critical Path (Stage 1): Complete Stage 1 first. This will give you a working server with a simple test tool that can be deployed to prove the core architecture.

Parallel Work (Stages 2 & 3): Once Stage 1 is done, development can be split. One track can focus on building the SharePoint services (Stage 2), while another track can build all the standalone tools (Stage 3) in parallel.

Dependent Tools (Stage 4): The tools in Stage 4 depend on the SharePoint services from Stage 2.

Stage 1: Core Server & MVP (Critical Path)
Goal: Get a basic, runnable server with one simple tool working.

[x] 0. Project Setup: Run ./setup.sh to create the project structure. This also creates tools/test_echo.py which we'll use for initial testing.

[x] 1. Environment & Dependencies: Populate requirements.txt and install dependencies.

[x] 2. Core Server (server.py): Implement the Flask server to dynamically load and run tools.

[x] 3. Server Tests (tests/test_server.py): Write tests to confirm the /health endpoint and tool-running logic work correctly using the test_echo tool.

Stage 2: Foundational Services (Parallel Track 1)
Goal: Build the services required for interacting with SharePoint.

[ ] 1. Authentication (auth/graph_auth.py): Implement the logic to get Microsoft Graph API tokens.

[ ] 2. Auth Tests (tests/test_auth.py): Test the authentication module.

[ ] 3. SharePoint Client (sharepoint/sharepoint_client.py): Depends on auth/graph_auth.py. Implement the client for listing and downloading files from SharePoint.

[ ] 4. SharePoint Client Tests (tests/test_sharepoint_client.py): Test the SharePoint client.

Stage 3: Standalone Tools (Parallel Track 2)
Goal: Build all tools that do not depend on the SharePoint client. These can be developed in any order, in parallel with Stage 2.

[ ] 1. SQL Reviewer (tools/sql_reviewer.py): Reviews a SQL query for common issues and suggests improvements.

[ ] Test (tests/test_sql_reviewer.py)

[ ] 2. Data Dictionary Validator (tools/data_dictionary_validator.py): Validates a CSV file against a JSON data dictionary schema.

[ ] Test (tests/test_data_dictionary_validator.py)

[ ] 3. Project Timeline Generator (tools/project_timeline_generator.py): Creates a sequential project timeline from a list of milestones and their durations.

[ ] Test (tests/test_project_timeline_generator.py)

[ ] 4. Document De-identifier (tools/document_deidentifier.py): Scrubs text to remove Personally Identifiable Information (PII) like SSNs and emails.

[ ] Test (tests/test_document_deidentifier.py)

[ ] 5. Test Case Generator (tools/test_case_generator.py): Generates test case ideas from a feature description.

[ ] Test (tests/test_test_case_generator.py)

[ ] 6. Consent Grade Checker (tools/consent_grade_checker.py): Checks the reading grade level of a consent form or other text.

[ ] Test (tests/test_consent_grade_checker.py)

[ ] 7. Meeting Summarizer (tools/meeting_summarizer.py): Creates a brief summary and extracts action items from a meeting transcript.

[ ] Test (tests/test_meeting_summarizer.py)

Stage 4: Dependent Tools
Goal: Build tools that rely on the foundational services created in Stage 2.

[ ] 1. Clinical Protocol Q&A (tools/clinical_protocol_qa.py): Depends on sharepoint/sharepoint_client.py. Answers questions based on the latest clinical protocol document in SharePoint.

[ ] Test (tests/test_clinical_protocol_qa.py)

[ ] 2. Glossary Explainer (tools/glossary_explainer.py): Depends on sharepoint/sharepoint_client.py. Looks up and explains terms from a glossary file stored in SharePoint.

[ ] Test (tests/test_glossary_explainer.py)

Stage 5: Final Validation & Deployment
Goal: Ensure all components work together and deploy the application.

[ ] 1. Run All Tests: pytest -v

[ ] 2. Run Server Locally: export $(cat .env.example | xargs) && python server.py

[ ] 3. Manually Test Endpoints: Use curl or Postman to hit each tool endpoint.

[ ] 4. Deploy to Azure: Follow your organization's deployment procedures for Azure AI Foundry / App Service.