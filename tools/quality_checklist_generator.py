from typing import Dict, List, Optional, Any


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates customized quality review checklists."""
    try:
        review_type = input_data.get("review_type", "general")
        study_phase = input_data.get("study_phase", "ongoing")
        
        checklist_items = []
        
        # Base items for all reviews
        base_items = [
            {"category": "Documentation", "item": "Protocol compliance verified", "critical": True},
            {"category": "Data Quality", "item": "Source data verification completed", "critical": True},
            {"category": "Safety", "item": "All SAEs reported within timeline", "critical": True}
        ]
        checklist_items.extend(base_items)
        
        # Phase-specific items
        if study_phase == "startup":
            checklist_items.extend([
                {"category": "Site Readiness", "item": "Staff training completed", "critical": True},
                {"category": "Regulatory", "item": "All approvals obtained", "critical": True}
            ])
        elif study_phase == "closeout":
            checklist_items.extend([
                {"category": "Data", "item": "Database lock criteria met", "critical": True},
                {"category": "Documentation", "item": "TMF complete", "critical": True}
            ])
        
        # Type-specific items
        if review_type == "monitoring_visit":
            checklist_items.extend([
                {"category": "Site", "item": "Drug accountability verified", "critical": False},
                {"category": "Subject", "item": "Consent forms reviewed", "critical": True}
            ])
        
        return {
            "checklist": checklist_items,
            "total_items": len(checklist_items),
            "critical_items": sum(1 for i in checklist_items if i.get("critical")),
            "review_type": review_type,
            "study_phase": study_phase
        }
    except Exception as e:
        return {"error": str(e)}
