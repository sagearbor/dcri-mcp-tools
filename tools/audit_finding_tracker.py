from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manages audit findings and tracks CAPA (Corrective and Preventive Actions) completion status.
    
    Example:
        Input: List of audit findings with CAPA status and due dates
        Output: CAPA status summary with completion rates and overdue actions tracking
    
    Parameters:
        findings : list
            List of audit findings with CAPA data
    """
    try:
        findings = input_data.get("findings", [])
        if not findings:
            return {"error": "No findings provided"}
        
        capa_status = {}
        overdue_capas = []
        
        for finding in findings:
            finding_id = finding.get("finding_id")
            capa = finding.get("capa", {})
            
            if capa:
                due_date = datetime.fromisoformat(capa.get("due_date", "2099-01-01"))
                status = capa.get("status", "pending")
                
                capa_status[finding_id] = status
                
                if status != "completed" and due_date < datetime.now():
                    overdue_capas.append({
                        "finding_id": finding_id,
                        "days_overdue": (datetime.now() - due_date).days
                    })
        
        return {
            "total_findings": len(findings),
            "capa_status": capa_status,
            "overdue_capas": overdue_capas,
            "completion_rate": sum(1 for s in capa_status.values() if s == "completed") / len(capa_status) * 100 if capa_status else 0
        }
    except Exception as e:
        return {"error": str(e)}
