import subprocess
import sys

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

for i, tool in enumerate(tools, 1):
    cmd = f"python -m pytest tests/test_{tool}.py -q 2>&1"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Parse test results
    passed = "passed" in result.stdout
    failed = "failed" in result.stdout or "FAILED" in result.stdout
    
    if passed and not failed:
        status = "PASS"
    elif failed:
        status = "FAIL"
    else:
        status = "UNKNOWN"
    
    print(f"{i:2}. {tool:30} pytest={status}")
