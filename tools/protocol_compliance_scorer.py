from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scores protocol adherence and compliance.
    
    Args:
        input_data: Dictionary containing:
            - compliance_data: Protocol compliance records:
                - subject_id: Subject identifier
                - site_id: Site identifier
                - visit_data: Visit compliance information
                - procedure_compliance: Procedure completion data
                - eligibility_violations: Any eligibility violations
                - protocol_deviations: List of deviations
            - protocol_requirements: Protocol-specific requirements
            - scoring_weights: Weights for different compliance aspects
    
    Returns:
        Dictionary containing:
            - overall_score: Overall compliance score
            - site_scores: Compliance scores by site
            - subject_scores: Individual subject compliance
            - compliance_breakdown: Detailed compliance metrics
            - risk_areas: Identified risk areas
            - recommendations: Compliance recommendations
    """
    try:
        compliance_data = input_data.get("compliance_data", [])
        if not compliance_data:
            return {
                "error": "No compliance data provided",
                "overall_score": 0,
                "site_scores": {},
                "subject_scores": {},
                "compliance_breakdown": {},
                "risk_areas": [],
                "recommendations": []
            }
        
        protocol_requirements = input_data.get("protocol_requirements", {})
        scoring_weights = input_data.get("scoring_weights", {
            "visit_compliance": 0.3,
            "procedure_compliance": 0.3,
            "eligibility": 0.2,
            "deviations": 0.2
        })
        
        # Calculate scores
        subject_scores = calculate_subject_scores(compliance_data, scoring_weights)
        site_scores = calculate_site_scores(compliance_data, subject_scores)
        overall_score = calculate_overall_score(site_scores)
        compliance_breakdown = analyze_compliance_breakdown(compliance_data)
        risk_areas = identify_risk_areas(compliance_breakdown, site_scores)
        recommendations = generate_compliance_recommendations(risk_areas, overall_score)
        
        return {
            "overall_score": overall_score,
            "site_scores": site_scores,
            "subject_scores": subject_scores,
            "compliance_breakdown": compliance_breakdown,
            "risk_areas": risk_areas,
            "recommendations": recommendations
        }
        
    except Exception as e:
        return {
            "error": f"Error scoring protocol compliance: {str(e)}",
            "overall_score": 0,
            "site_scores": {},
            "subject_scores": {},
            "compliance_breakdown": {},
            "risk_areas": [],
            "recommendations": []
        }


def calculate_subject_scores(compliance_data: List[Dict], weights: Dict) -> Dict:
    """Calculate compliance scores for individual subjects."""
    scores = {}
    
    for record in compliance_data:
        subject_id = record.get("subject_id")
        
        # Visit compliance score
        visit_score = calculate_visit_compliance_score(record.get("visit_data", {}))
        
        # Procedure compliance score
        procedure_score = calculate_procedure_compliance_score(record.get("procedure_compliance", {}))
        
        # Eligibility score
        eligibility_score = 100 if not record.get("eligibility_violations") else 0
        
        # Deviation score
        deviation_score = calculate_deviation_score(record.get("protocol_deviations", []))
        
        # Weighted total
        total_score = (
            visit_score * weights["visit_compliance"] +
            procedure_score * weights["procedure_compliance"] +
            eligibility_score * weights["eligibility"] +
            deviation_score * weights["deviations"]
        )
        
        scores[subject_id] = {
            "total_score": round(total_score, 1),
            "visit_compliance": visit_score,
            "procedure_compliance": procedure_score,
            "eligibility_compliance": eligibility_score,
            "deviation_score": deviation_score
        }
    
    return scores


def calculate_visit_compliance_score(visit_data: Dict) -> float:
    """Calculate visit compliance score."""
    if not visit_data:
        return 100.0
    
    total_visits = visit_data.get("total_visits", 0)
    completed_visits = visit_data.get("completed_visits", 0)
    on_time_visits = visit_data.get("on_time_visits", 0)
    
    if total_visits == 0:
        return 100.0
    
    completion_rate = (completed_visits / total_visits) * 50
    timeliness_rate = (on_time_visits / total_visits) * 50
    
    return completion_rate + timeliness_rate


def calculate_procedure_compliance_score(procedure_data: Dict) -> float:
    """Calculate procedure compliance score."""
    if not procedure_data:
        return 100.0
    
    required_procedures = procedure_data.get("required", 0)
    completed_procedures = procedure_data.get("completed", 0)
    
    if required_procedures == 0:
        return 100.0
    
    return (completed_procedures / required_procedures) * 100


def calculate_deviation_score(deviations: List[Dict]) -> float:
    """Calculate score based on protocol deviations."""
    if not deviations:
        return 100.0
    
    # Deduct points based on deviation severity
    score = 100.0
    for deviation in deviations:
        severity = deviation.get("severity", "minor")
        if severity == "major":
            score -= 20
        elif severity == "minor":
            score -= 5
    
    return max(0, score)


def calculate_site_scores(compliance_data: List[Dict], subject_scores: Dict) -> Dict:
    """Calculate compliance scores by site."""
    site_subjects = defaultdict(list)
    
    for record in compliance_data:
        site_id = record.get("site_id")
        subject_id = record.get("subject_id")
        if subject_id in subject_scores:
            site_subjects[site_id].append(subject_scores[subject_id]["total_score"])
    
    site_scores = {}
    for site_id, scores in site_subjects.items():
        if scores:
            site_scores[site_id] = {
                "average_score": sum(scores) / len(scores),
                "min_score": min(scores),
                "max_score": max(scores),
                "subject_count": len(scores)
            }
    
    return site_scores


def calculate_overall_score(site_scores: Dict) -> float:
    """Calculate overall study compliance score."""
    if not site_scores:
        return 0.0
    
    total_score = sum(s["average_score"] for s in site_scores.values())
    return round(total_score / len(site_scores), 1)


def analyze_compliance_breakdown(compliance_data: List[Dict]) -> Dict:
    """Analyze detailed compliance breakdown."""
    breakdown = {
        "visit_compliance": {"compliant": 0, "total": 0},
        "procedure_compliance": {"compliant": 0, "total": 0},
        "eligibility_compliance": {"compliant": 0, "violations": 0},
        "deviation_summary": {"major": 0, "minor": 0}
    }
    
    for record in compliance_data:
        # Visit compliance
        visit_data = record.get("visit_data", {})
        if visit_data:
            breakdown["visit_compliance"]["total"] += visit_data.get("total_visits", 0)
            breakdown["visit_compliance"]["compliant"] += visit_data.get("on_time_visits", 0)
        
        # Procedure compliance
        proc_data = record.get("procedure_compliance", {})
        if proc_data:
            breakdown["procedure_compliance"]["total"] += proc_data.get("required", 0)
            breakdown["procedure_compliance"]["compliant"] += proc_data.get("completed", 0)
        
        # Eligibility
        if record.get("eligibility_violations"):
            breakdown["eligibility_compliance"]["violations"] += 1
        else:
            breakdown["eligibility_compliance"]["compliant"] += 1
        
        # Deviations
        for deviation in record.get("protocol_deviations", []):
            severity = deviation.get("severity", "minor")
            breakdown["deviation_summary"][severity] = breakdown["deviation_summary"].get(severity, 0) + 1
    
    return breakdown


def identify_risk_areas(compliance_breakdown: Dict, site_scores: Dict) -> List[Dict]:
    """Identify compliance risk areas."""
    risk_areas = []
    
    # Check visit compliance
    visit_comp = compliance_breakdown.get("visit_compliance", {})
    if visit_comp.get("total", 0) > 0:
        visit_rate = visit_comp["compliant"] / visit_comp["total"] * 100
        if visit_rate < 80:
            risk_areas.append({
                "area": "Visit Compliance",
                "risk_level": "high" if visit_rate < 70 else "medium",
                "compliance_rate": visit_rate,
                "description": f"Visit compliance at {visit_rate:.1f}%"
            })
    
    # Check procedure compliance
    proc_comp = compliance_breakdown.get("procedure_compliance", {})
    if proc_comp.get("total", 0) > 0:
        proc_rate = proc_comp["compliant"] / proc_comp["total"] * 100
        if proc_rate < 90:
            risk_areas.append({
                "area": "Procedure Compliance",
                "risk_level": "medium",
                "compliance_rate": proc_rate,
                "description": f"Procedure completion at {proc_rate:.1f}%"
            })
    
    # Check eligibility violations
    elig_comp = compliance_breakdown.get("eligibility_compliance", {})
    if elig_comp.get("violations", 0) > 0:
        risk_areas.append({
            "area": "Eligibility",
            "risk_level": "high",
                "violation_count": elig_comp["violations"],
            "description": f"{elig_comp['violations']} eligibility violations"
        })
    
    # Check for low-performing sites
    low_sites = [site for site, score in site_scores.items() 
                 if score["average_score"] < 70]
    if low_sites:
        risk_areas.append({
            "area": "Site Performance",
            "risk_level": "high",
            "affected_sites": low_sites,
            "description": f"{len(low_sites)} sites with score <70%"
        })
    
    return risk_areas


def generate_compliance_recommendations(risk_areas: List[Dict], overall_score: float) -> List[Dict]:
    """Generate compliance improvement recommendations."""
    recommendations = []
    
    if overall_score < 80:
        recommendations.append({
            "priority": "HIGH",
            "action": "Implement compliance improvement plan",
            "description": f"Overall compliance score {overall_score:.1f}% below target"
        })
    
    for risk in risk_areas:
        if risk["risk_level"] == "high":
            if risk["area"] == "Visit Compliance":
                recommendations.append({
                    "priority": "CRITICAL",
                    "action": "Review visit scheduling processes",
                    "description": "Implement visit reminder systems and window monitoring"
                })
            elif risk["area"] == "Eligibility":
                recommendations.append({
                    "priority": "CRITICAL",
                    "action": "Retrain sites on eligibility criteria",
                    "description": "Implement pre-screening checklists"
                })
    
    return recommendations
