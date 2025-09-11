"""
Compliance Knowledge Base tool for validating clinical trial schedules against compliance rules.
Supports multiple data schemas through configurable mappings.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add lib directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.compliance.schema_adapter import SchemaAdapter
from lib.compliance.rules_engine import RulesEngine


def run(input_data: Dict) -> Dict:
    """
    Validate clinical trial schedule against compliance rules.
    
    Example:
        Input: Schedule data with visits and procedures, schema type identifier, and optional rule category filters
        Output: List of compliance findings with severity levels, affected items, and recommendations for resolution
    
    Parameters:
        schedule_data : dict
            The trial schedule/protocol data to validate
        schema_type : str, optional
            Identifier for data schema format (default: "generic")
        rule_categories : list, optional
            Filter which rule types to apply - options: logistics, equipment, regulatory, safety (default: all)
        include_warnings : bool, optional
            Include warning-level findings in results (default: True)
        study_start_date : str, optional
            ISO format date for study start, used for visit window calculations
    """
    
    try:
        # Extract parameters
        schedule_data = input_data.get("schedule_data")
        if not schedule_data:
            return {
                "status": "error",
                "message": "Missing required parameter: schedule_data"
            }
        
        schema_type = input_data.get("schema_type", "generic")
        rule_categories = input_data.get("rule_categories", None)
        include_warnings = input_data.get("include_warnings", True)
        study_start_date = input_data.get("study_start_date")
        
        # Initialize components
        adapter = SchemaAdapter(schema_type)
        engine = RulesEngine()
        
        # Load rules
        engine.load_rules(rule_categories)
        
        # Extract data using schema adapter
        extracted_data = {
            "visits": adapter.extract_visits(schedule_data),
            "participants": adapter.extract_participants(schedule_data),
            "sites": adapter.extract_sites(schedule_data)
        }
        
        # Add study start date if provided
        if study_start_date:
            # Inject into the data for rules that need it
            schedule_data["study_start_date"] = study_start_date
        
        # Apply compliance rules
        findings = engine.apply_rules(schedule_data, extracted_data)
        
        # Filter findings if needed
        if not include_warnings:
            findings = [f for f in findings if f.severity != "warning"]
        
        # Convert findings to dict format
        findings_dict = [f.to_dict() for f in findings]
        
        # Generate summary statistics
        error_count = sum(1 for f in findings if f.severity == "error")
        warning_count = sum(1 for f in findings if f.severity == "warning")
        info_count = sum(1 for f in findings if f.severity == "info")
        
        # Categorize findings by type
        findings_by_type = {}
        for finding in findings:
            rule_type = finding.rule_id.split("-")[0] if "-" in finding.rule_id else "OTHER"
            if rule_type not in findings_by_type:
                findings_by_type[rule_type] = []
            findings_by_type[rule_type].append(finding.to_dict())
        
        return {
            "status": "success",
            "compliance_status": "FAIL" if error_count > 0 else ("WARNING" if warning_count > 0 else "PASS"),
            "summary": {
                "total_findings": len(findings),
                "errors": error_count,
                "warnings": warning_count,
                "info": info_count,
                "visits_analyzed": len(extracted_data.get("visits", [])),
                "rules_applied": len(engine.rules)
            },
            "findings": findings_dict,
            "findings_by_category": findings_by_type,
            "metadata": {
                "schema_type": schema_type,
                "rule_categories": rule_categories or "all",
                "available_schemas": adapter.get_available_schemas()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error during compliance validation: {str(e)}",
            "error_type": type(e).__name__
        }


# Example usage for testing
if __name__ == "__main__":
    # Example schedule data in generic format
    test_data = {
        "schedule_data": {
            "study_id": "TRIAL-001",
            "visits": [
                {
                    "id": "V1",
                    "day": 0,
                    "date": "2024-02-01",
                    "type": "Screening",
                    "site": "SITE-001",
                    "procedures": ["informed_consent", "blood_draw", "ecg"]
                },
                {
                    "id": "V2",
                    "day": 7,
                    "date": "2024-02-10",  # This is a Saturday - should trigger business hours rule
                    "type": "Baseline",
                    "site": "SITE-001",
                    "procedures": ["blood_draw", "MRI"]  # MRI at site without capability
                },
                {
                    "id": "V3",
                    "day": 14,
                    "date": "2024-02-15",
                    "type": "Treatment",
                    "site": "SITE-002",
                    "procedures": ["biopsy"]  # Should require safety follow-up
                },
                {
                    "id": "V4",
                    "day": 28,
                    "date": "2024-02-29",
                    "type": "Follow-up",
                    "site": "SITE-002",
                    "procedures": ["blood_draw", "ecg"]
                }
            ],
            "sites": [
                {"id": "SITE-001", "name": "Clinical Center A"},
                {"id": "SITE-002", "name": "Hospital B"}
            ]
        },
        "schema_type": "generic",
        "study_start_date": "2024-02-01"
    }
    
    result = run(test_data)
    
    # Print results
    import json
    print(json.dumps(result, indent=2))