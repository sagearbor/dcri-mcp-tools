from typing import Dict, List, Optional, Any


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates quality KPIs and indicators dashboard."""
    try:
        metrics_data = input_data.get("metrics_data", {})
        if not metrics_data:
            return {"error": "No metrics data provided"}
        
        kpis = {}
        
        # Calculate various KPIs
        if "enrollment" in metrics_data:
            kpis["enrollment_rate"] = metrics_data["enrollment"].get("actual", 0) / metrics_data["enrollment"].get("target", 1) * 100
        
        if "data_quality" in metrics_data:
            kpis["query_rate"] = metrics_data["data_quality"].get("queries", 0) / metrics_data["data_quality"].get("data_points", 1) * 100
        
        if "protocol_compliance" in metrics_data:
            kpis["compliance_rate"] = metrics_data["protocol_compliance"].get("compliant", 0) / metrics_data["protocol_compliance"].get("total", 1) * 100
        
        # Determine overall quality score
        quality_score = sum(kpis.values()) / len(kpis) if kpis else 0
        
        return {
            "kpis": kpis,
            "quality_score": quality_score,
            "status": "good" if quality_score > 80 else "needs_improvement"
        }
    except Exception as e:
        return {"error": str(e)}
