from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Identifies GCP training gaps and needs."""
    try:
        training_records = input_data.get("training_records", [])
        if not training_records:
            return {"error": "No training records provided"}
        
        staff_roles = input_data.get("staff_roles", {})
        training_requirements = input_data.get("training_requirements", {})
        
        gaps = []
        compliance_status = {}
        
        for record in training_records:
            staff_id = record.get("staff_id")
            role = staff_roles.get(staff_id, "unknown")
            required = training_requirements.get(role, [])
            completed = record.get("completed_trainings", [])
            
            missing = [t for t in required if t not in completed]
            if missing:
                gaps.append({
                    "staff_id": staff_id,
                    "role": role,
                    "missing_trainings": missing
                })
            
            compliance_status[staff_id] = len(missing) == 0
        
        return {
            "training_gaps": gaps,
            "compliance_status": compliance_status,
            "summary": {
                "total_staff": len(training_records),
                "compliant_staff": sum(compliance_status.values()),
                "compliance_rate": sum(compliance_status.values()) / len(compliance_status) * 100 if compliance_status else 0
            }
        }
    except Exception as e:
        return {"error": str(e)}
