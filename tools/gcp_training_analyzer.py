from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identifies GCP training gaps and needs for clinical trial staff.
    
    Example:
        Input: Staff data with training records, role requirements, and validity periods
        Output: Training gap analysis with compliance status, expiring certifications, and recommendations
    
    Parameters:
        staff_data : list
            List of staff members with training records
        training_requirements : dict
            Required training by role (PI, CRC, CRA, etc.)
        validity_period_months : int
            Training validity period in months (default: 24)
    """
    try:
        staff_data = input_data.get("staff_data", [])
        if not staff_data:
            return {"error": "No staff data provided"}
        
        # Default training requirements by role
        default_requirements = {
            "PI": ["GCP", "Protocol Training", "Site Training", "Safety Reporting"],
            "Co-PI": ["GCP", "Protocol Training", "Site Training", "Safety Reporting"],
            "CRC": ["GCP", "Protocol Training", "Site Training", "EDC Training"],
            "CRA": ["GCP", "Monitoring Training", "Protocol Training"],
            "Study Coordinator": ["GCP", "Protocol Training", "Site Training", "EDC Training"],
            "Pharmacist": ["GCP", "Protocol Training", "Drug Accountability", "Storage Requirements"],
            "Lab Tech": ["GCP", "Lab Manual Training", "Sample Handling"],
            "Nurse": ["GCP", "Protocol Training", "Site Training", "Injection Technique"]
        }
        
        training_requirements = input_data.get("training_requirements", default_requirements)
        validity_months = input_data.get("validity_period_months", 24)
        
        gaps = []
        compliance_status = {}
        expiring_soon = []
        current_date = datetime.now()
        
        for staff_member in staff_data:
            name = staff_member.get("name", "Unknown")
            role = staff_member.get("role", "Unknown")
            training_records = staff_member.get("training_records", [])
            
            required_trainings = training_requirements.get(role, [])
            completed_trainings = {}
            
            # Process training records
            for record in training_records:
                course = record.get("course", "")
                completion_date_str = record.get("completion_date", "")
                
                if completion_date_str:
                    try:
                        completion_date = datetime.strptime(completion_date_str, "%Y-%m-%d")
                        expiry_date = completion_date + timedelta(days=validity_months*30)
                        
                        completed_trainings[course] = {
                            "completion_date": completion_date_str,
                            "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                            "status": "current" if expiry_date > current_date else "expired",
                            "days_until_expiry": (expiry_date - current_date).days
                        }
                        
                        # Check for training expiring soon (within 60 days)
                        if 0 < (expiry_date - current_date).days <= 60:
                            expiring_soon.append({
                                "name": name,
                                "role": role,
                                "course": course,
                                "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                                "days_remaining": (expiry_date - current_date).days
                            })
                            
                    except ValueError:
                        # Invalid date format
                        completed_trainings[course] = {
                            "completion_date": completion_date_str,
                            "status": "invalid_date",
                            "error": "Invalid date format"
                        }
            
            # Identify gaps
            missing_trainings = []
            expired_trainings = []
            
            for required_training in required_trainings:
                if required_training not in completed_trainings:
                    missing_trainings.append(required_training)
                elif completed_trainings[required_training].get("status") == "expired":
                    expired_trainings.append({
                        "course": required_training,
                        "expiry_date": completed_trainings[required_training].get("expiry_date"),
                        "completion_date": completed_trainings[required_training].get("completion_date")
                    })
            
            if missing_trainings or expired_trainings:
                gaps.append({
                    "name": name,
                    "role": role,
                    "missing_trainings": missing_trainings,
                    "expired_trainings": expired_trainings,
                    "training_status": "non-compliant"
                })
                compliance_status[name] = False
            else:
                compliance_status[name] = True
        
        compliant_count = sum(compliance_status.values())
        total_staff = len(staff_data)
        
        return {
            "training_gaps": gaps,
            "compliance_status": compliance_status,
            "expiring_soon": sorted(expiring_soon, key=lambda x: x["days_remaining"]),
            "summary": {
                "total_staff": total_staff,
                "compliant_staff": compliant_count,
                "non_compliant_staff": total_staff - compliant_count,
                "compliance_rate": round((compliant_count / total_staff * 100) if total_staff > 0 else 0, 1),
                "trainings_expiring_soon": len(expiring_soon)
            },
            "recommendations": _generate_recommendations(gaps, expiring_soon)
        }
    except Exception as e:
        return {"error": str(e)}


def _generate_recommendations(gaps: List[Dict], expiring_soon: List[Dict]) -> List[str]:
    """Generate training recommendations based on gaps."""
    recommendations = []
    
    if gaps:
        recommendations.append(f"Immediate action required: {len(gaps)} staff members are non-compliant")
        recommendations.append("Schedule training sessions for staff with missing requirements")
        recommendations.append("Update delegation logs to remove non-compliant staff from critical tasks")
    
    if expiring_soon:
        recommendations.append(f"Schedule renewal training for {len(expiring_soon)} expiring certifications")
        recommendations.append("Set up automated reminders for training renewals")
    
    # Role-specific recommendations
    role_gaps = {}
    for gap in gaps:
        role = gap["role"]
        if role not in role_gaps:
            role_gaps[role] = 0
        role_gaps[role] += 1
    
    for role, count in role_gaps.items():
        if count > 1:
            recommendations.append(f"Consider group training session for {role} role ({count} staff affected)")
    
    if not gaps and not expiring_soon:
        recommendations.append("All staff training is current - maintain regular monitoring schedule")
    
    return recommendations
