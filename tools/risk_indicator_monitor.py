from typing import Dict, List, Optional, Any


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Monitors Key Risk Indicators (KRIs) for RBQM."""
    try:
        kri_data = input_data.get("kri_data", {})
        if not kri_data:
            return {"error": "No KRI data provided"}
        
        thresholds = input_data.get("thresholds", {})
        alerts = []
        
        for kri_name, value in kri_data.items():
            threshold = thresholds.get(kri_name, {})
            
            if "upper" in threshold and value > threshold["upper"]:
                alerts.append({
                    "kri": kri_name,
                    "value": value,
                    "threshold": threshold["upper"],
                    "type": "exceeded_upper"
                })
            elif "lower" in threshold and value < threshold["lower"]:
                alerts.append({
                    "kri": kri_name,
                    "value": value,
                    "threshold": threshold["lower"],
                    "type": "below_lower"
                })
        
        risk_level = "high" if len(alerts) > 3 else "medium" if alerts else "low"
        
        return {
            "kri_values": kri_data,
            "alerts": alerts,
            "risk_level": risk_level,
            "total_kris": len(kri_data)
        }
    except Exception as e:
        return {"error": str(e)}
