import requests
import json

BASE_URL = "http://127.0.0.1:8210"
tools = [
    "adverse_event_coder",
    "amendment_impact_analyzer", 
    "annual_report_generator",
    "audit_finding_tracker",
    "audit_trail_reviewer",
    "baseline_comparability_tester",
    "cfr_part11_validator",
    "clinical_protocol_qa",
    "clinical_text_summarizer",
    "concomitant_med_coder"
]

# Simple test data for each tool
test_data = {
    "adverse_event_coder": {"adverse_events": [{"verbatim": "headache"}]},
    "amendment_impact_analyzer": {"amendments": [{"change": "inclusion criteria update"}]},
    "annual_report_generator": {"study_data": {"title": "Test Study"}},
    "audit_finding_tracker": {"findings": [{"description": "missing consent"}]},
    "audit_trail_reviewer": {"audit_logs": [{"action": "data_entry"}]},
    "baseline_comparability_tester": {"treatment_groups": [{"name": "Group A"}]},
    "cfr_part11_validator": {"records": [{"id": "001", "signature": "valid"}]},
    "clinical_protocol_qa": {"protocol_text": "This is a test protocol"},
    "clinical_text_summarizer": {"text": "Patient presents with chest pain"},
    "concomitant_med_coder": {"medications": [{"name": "aspirin"}]}
}

for i, tool in enumerate(tools, 1):
    try:
        data = test_data.get(tool, {})
        response = requests.post(f"{BASE_URL}/run_tool/{tool}", json=data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            status = "PASS" if not result.get('error') else f"ERROR: {result.get('error')[:50]}..."
        else:
            status = f"HTTP {response.status_code}"
    except Exception as e:
        status = f"FAIL: {str(e)[:50]}..."
    
    print(f"{i:2}. {tool:30} tool={status}")
