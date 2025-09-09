from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assists with Source Data Verification (SDV) process.
    
    Args:
        input_data: Dictionary containing:
            - sdv_items: List of items to verify:
                - subject_id: Subject identifier
                - visit: Visit name/number
                - form: CRF form name
                - field: Field name
                - edc_value: Value in EDC
                - source_value: Value in source (if available)
                - critical_field: Boolean for critical fields
            - sdv_strategy: SDV approach ("100%", "risk-based", "targeted")
            - sdv_percentage: Target SDV percentage
            - risk_factors: Risk-based SDV criteria
            - completed_sdv: List of already verified items
    
    Returns:
        Dictionary containing:
            - sdv_plan: Prioritized SDV plan
            - verification_results: Results of verification checks
            - discrepancies: Identified discrepancies
            - sdv_metrics: SDV completion metrics
            - recommendations: SDV recommendations
            - risk_assessment: Risk-based assessment
    """
    try:
        sdv_items = input_data.get("sdv_items", [])
        if not sdv_items:
            return {
                "error": "No SDV items provided",
                "sdv_plan": [],
                "verification_results": [],
                "discrepancies": [],
                "sdv_metrics": {},
                "recommendations": [],
                "risk_assessment": {}
            }
        
        sdv_strategy = input_data.get("sdv_strategy", "risk-based")
        sdv_percentage = input_data.get("sdv_percentage", 20)
        risk_factors = input_data.get("risk_factors", {})
        completed_sdv = input_data.get("completed_sdv", [])
        
        # Generate SDV plan
        sdv_plan = generate_sdv_plan(sdv_items, sdv_strategy, sdv_percentage, risk_factors)
        
        # Perform verification
        verification_results = perform_verification(sdv_items, completed_sdv)
        
        # Identify discrepancies
        discrepancies = identify_discrepancies(verification_results)
        
        # Calculate metrics
        sdv_metrics = calculate_sdv_metrics(sdv_items, verification_results, completed_sdv)
        
        # Risk assessment
        risk_assessment = assess_sdv_risk(sdv_items, discrepancies, risk_factors)
        
        # Generate recommendations
        recommendations = generate_sdv_recommendations(sdv_metrics, risk_assessment, discrepancies)
        
        return {
            "sdv_plan": sdv_plan,
            "verification_results": verification_results,
            "discrepancies": discrepancies,
            "sdv_metrics": sdv_metrics,
            "recommendations": recommendations,
            "risk_assessment": risk_assessment
        }
        
    except Exception as e:
        return {
            "error": f"Error in SDV process: {str(e)}",
            "sdv_plan": [],
            "verification_results": [],
            "discrepancies": [],
            "sdv_metrics": {},
            "recommendations": [],
            "risk_assessment": {}
        }


def generate_sdv_plan(sdv_items: List[Dict], strategy: str, percentage: int, 
                      risk_factors: Dict) -> List[Dict]:
    """Generate prioritized SDV plan based on strategy."""
    plan = []
    
    if strategy == "100%":
        # All items need SDV
        for item in sdv_items:
            plan.append({
                "subject_id": item["subject_id"],
                "visit": item["visit"],
                "form": item["form"],
                "field": item["field"],
                "priority": "high" if item.get("critical_field") else "standard",
                "reason": "100% SDV strategy"
            })
    
    elif strategy == "risk-based":
        # Prioritize based on risk factors
        for item in sdv_items:
            risk_score = calculate_risk_score(item, risk_factors)
            
            if risk_score >= 7 or item.get("critical_field"):
                plan.append({
                    "subject_id": item["subject_id"],
                    "visit": item["visit"],
                    "form": item["form"],
                    "field": item["field"],
                    "priority": "high" if risk_score >= 8 else "medium",
                    "risk_score": risk_score,
                    "reason": "Risk-based selection"
                })
        
        # Add random sampling to meet percentage
        remaining = int(len(sdv_items) * percentage / 100) - len(plan)
        if remaining > 0:
            unselected = [i for i in sdv_items if not any(
                p["subject_id"] == i["subject_id"] and p["field"] == i["field"] 
                for p in plan
            )]
            sampled = random.sample(unselected, min(remaining, len(unselected)))
            for item in sampled:
                plan.append({
                    "subject_id": item["subject_id"],
                    "visit": item["visit"],
                    "form": item["form"],
                    "field": item["field"],
                    "priority": "low",
                    "reason": "Random sampling"
                })
    
    elif strategy == "targeted":
        # Focus on critical fields and specific forms
        critical_forms = risk_factors.get("critical_forms", ["eligibility", "primary_endpoint", "sae"])
        
        for item in sdv_items:
            if item.get("critical_field") or item.get("form", "").lower() in critical_forms:
                plan.append({
                    "subject_id": item["subject_id"],
                    "visit": item["visit"],
                    "form": item["form"],
                    "field": item["field"],
                    "priority": "high" if item.get("critical_field") else "medium",
                    "reason": "Targeted SDV"
                })
    
    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "standard": 2, "low": 3}
    plan.sort(key=lambda x: priority_order.get(x["priority"], 4))
    
    return plan


def calculate_risk_score(item: Dict, risk_factors: Dict) -> int:
    """Calculate risk score for an SDV item."""
    score = 0
    
    # Critical field
    if item.get("critical_field"):
        score += 5
    
    # Primary endpoint related
    if "primary" in item.get("form", "").lower() or "endpoint" in item.get("field", "").lower():
        score += 4
    
    # Safety related
    if any(term in item.get("form", "").lower() for term in ["ae", "sae", "safety"]):
        score += 3
    
    # First subject at site
    if item.get("subject_id", "").endswith("001"):
        score += 2
    
    # Early visits
    if item.get("visit", "").lower() in ["screening", "baseline", "visit 1"]:
        score += 2
    
    # Site risk level
    site_risk = risk_factors.get("site_risk", {}).get(item.get("site_id"), "low")
    if site_risk == "high":
        score += 3
    elif site_risk == "medium":
        score += 1
    
    return score


def perform_verification(sdv_items: List[Dict], completed_sdv: List) -> List[Dict]:
    """Perform source data verification."""
    results = []
    
    for item in sdv_items:
        # Check if already verified
        is_verified = any(
            c.get("subject_id") == item["subject_id"] and 
            c.get("field") == item["field"]
            for c in completed_sdv
        )
        
        if is_verified:
            status = "completed"
            match_status = "previously_verified"
        elif item.get("source_value") is not None:
            # Compare EDC and source values
            edc_value = str(item.get("edc_value", "")).strip()
            source_value = str(item.get("source_value", "")).strip()
            
            if edc_value == source_value:
                status = "verified"
                match_status = "match"
            else:
                status = "discrepancy"
                match_status = "mismatch"
        else:
            status = "pending"
            match_status = "source_not_available"
        
        results.append({
            "subject_id": item["subject_id"],
            "visit": item["visit"],
            "form": item["form"],
            "field": item["field"],
            "edc_value": item.get("edc_value"),
            "source_value": item.get("source_value"),
            "status": status,
            "match_status": match_status,
            "critical_field": item.get("critical_field", False),
            "verification_date": datetime.now().isoformat() if status == "verified" else None
        })
    
    return results


def identify_discrepancies(verification_results: List[Dict]) -> List[Dict]:
    """Identify and categorize discrepancies."""
    discrepancies = []
    
    for result in verification_results:
        if result["match_status"] == "mismatch":
            discrepancy = {
                "subject_id": result["subject_id"],
                "visit": result["visit"],
                "form": result["form"],
                "field": result["field"],
                "edc_value": result["edc_value"],
                "source_value": result["source_value"],
                "severity": classify_discrepancy_severity(result),
                "type": classify_discrepancy_type(result),
                "critical": result.get("critical_field", False)
            }
            discrepancies.append(discrepancy)
    
    return discrepancies


def classify_discrepancy_severity(result: Dict) -> str:
    """Classify the severity of a discrepancy."""
    if result.get("critical_field"):
        return "critical"
    
    # Check for safety-related fields
    if any(term in result.get("form", "").lower() for term in ["ae", "sae", "safety"]):
        return "major"
    
    # Check for primary endpoint fields
    if "primary" in result.get("form", "").lower() or "endpoint" in result.get("field", "").lower():
        return "major"
    
    # Check for significant value differences
    try:
        edc = float(result.get("edc_value", 0))
        source = float(result.get("source_value", 0))
        if abs(edc - source) / max(abs(source), 1) > 0.2:  # >20% difference
            return "major"
    except (ValueError, TypeError):
        pass
    
    return "minor"


def classify_discrepancy_type(result: Dict) -> str:
    """Classify the type of discrepancy."""
    edc = str(result.get("edc_value", ""))
    source = str(result.get("source_value", ""))
    
    # Missing in source
    if not source and edc:
        return "missing_in_source"
    
    # Missing in EDC
    if source and not edc:
        return "missing_in_edc"
    
    # Transcription error (similar but not exact)
    if edc.lower() == source.lower() and edc != source:
        return "transcription_error"
    
    # Date format issue
    if "/" in edc and "-" in source or "-" in edc and "/" in source:
        return "date_format"
    
    # Numeric difference
    try:
        float(edc)
        float(source)
        return "numeric_difference"
    except ValueError:
        pass
    
    return "value_mismatch"


def calculate_sdv_metrics(sdv_items: List[Dict], verification_results: List[Dict],
                         completed_sdv: List) -> Dict:
    """Calculate SDV completion and quality metrics."""
    total_items = len(sdv_items)
    verified_items = len([r for r in verification_results if r["status"] in ["verified", "completed"]])
    discrepancy_items = len([r for r in verification_results if r["status"] == "discrepancy"])
    
    # Calculate by form type
    form_metrics = {}
    forms = set(item["form"] for item in sdv_items)
    
    for form in forms:
        form_items = [i for i in sdv_items if i["form"] == form]
        form_verified = len([r for r in verification_results 
                           if r["form"] == form and r["status"] in ["verified", "completed"]])
        form_discrepancies = len([r for r in verification_results 
                                if r["form"] == form and r["status"] == "discrepancy"])
        
        form_metrics[form] = {
            "total": len(form_items),
            "verified": form_verified,
            "completion_rate": (form_verified / len(form_items) * 100) if form_items else 0,
            "discrepancy_rate": (form_discrepancies / form_verified * 100) if form_verified else 0
        }
    
    return {
        "total_items": total_items,
        "verified_items": verified_items,
        "pending_items": total_items - verified_items,
        "completion_rate": (verified_items / total_items * 100) if total_items else 0,
        "discrepancy_count": discrepancy_items,
        "discrepancy_rate": (discrepancy_items / verified_items * 100) if verified_items else 0,
        "form_metrics": form_metrics,
        "critical_fields_verified": len([r for r in verification_results 
                                        if r.get("critical_field") and r["status"] in ["verified", "completed"]])
    }


def assess_sdv_risk(sdv_items: List[Dict], discrepancies: List[Dict], 
                    risk_factors: Dict) -> Dict:
    """Assess overall SDV risk level."""
    risk_score = 0
    risk_factors_identified = []
    
    # High discrepancy rate
    if len(discrepancies) > len(sdv_items) * 0.1:
        risk_score += 3
        risk_factors_identified.append("High discrepancy rate (>10%)")
    
    # Critical discrepancies
    critical_disc = [d for d in discrepancies if d["severity"] == "critical"]
    if critical_disc:
        risk_score += 4
        risk_factors_identified.append(f"{len(critical_disc)} critical discrepancies")
    
    # Unverified critical fields
    critical_unverified = [i for i in sdv_items 
                          if i.get("critical_field") and not i.get("source_value")]
    if critical_unverified:
        risk_score += 3
        risk_factors_identified.append(f"{len(critical_unverified)} critical fields unverified")
    
    # Systematic patterns
    if has_systematic_issues(discrepancies):
        risk_score += 2
        risk_factors_identified.append("Systematic data entry issues detected")
    
    # Determine risk level
    if risk_score >= 7:
        risk_level = "high"
    elif risk_score >= 4:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_factors": risk_factors_identified,
        "high_risk_subjects": identify_high_risk_subjects(discrepancies),
        "high_risk_forms": identify_high_risk_forms(discrepancies)
    }


def has_systematic_issues(discrepancies: List[Dict]) -> bool:
    """Check for systematic data entry issues."""
    if len(discrepancies) < 5:
        return False
    
    # Check for repeated discrepancy types
    type_counts = {}
    for d in discrepancies:
        disc_type = d.get("type")
        type_counts[disc_type] = type_counts.get(disc_type, 0) + 1
    
    # If one type represents >50% of discrepancies, it's systematic
    max_count = max(type_counts.values()) if type_counts else 0
    return max_count > len(discrepancies) * 0.5


def identify_high_risk_subjects(discrepancies: List[Dict]) -> List[str]:
    """Identify subjects with high discrepancy rates."""
    subject_counts = {}
    for d in discrepancies:
        subject = d["subject_id"]
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
    
    # Subjects with 3+ discrepancies
    return [s for s, count in subject_counts.items() if count >= 3]


def identify_high_risk_forms(discrepancies: List[Dict]) -> List[str]:
    """Identify forms with high discrepancy rates."""
    form_counts = {}
    for d in discrepancies:
        form = d["form"]
        form_counts[form] = form_counts.get(form, 0) + 1
    
    # Forms with 5+ discrepancies
    return [f for f, count in form_counts.items() if count >= 5]


def generate_sdv_recommendations(metrics: Dict, risk_assessment: Dict, 
                                discrepancies: List[Dict]) -> List[Dict]:
    """Generate SDV recommendations."""
    recommendations = []
    
    # Based on risk level
    if risk_assessment["risk_level"] == "high":
        recommendations.append({
            "priority": "CRITICAL",
            "action": "Increase SDV coverage",
            "description": "High risk detected - consider 100% SDV for critical data",
            "target_forms": risk_assessment.get("high_risk_forms", [])
        })
    
    # Based on discrepancy rate
    if metrics["discrepancy_rate"] > 5:
        recommendations.append({
            "priority": "HIGH",
            "action": "Site retraining required",
            "description": f"Discrepancy rate of {metrics['discrepancy_rate']:.1f}% exceeds threshold",
            "focus_areas": list(set(d["form"] for d in discrepancies))
        })
    
    # Based on completion rate
    if metrics["completion_rate"] < 80:
        recommendations.append({
            "priority": "MEDIUM",
            "action": "Accelerate SDV activities",
            "description": f"SDV completion at {metrics['completion_rate']:.1f}% - below target",
            "pending_items": metrics["pending_items"]
        })
    
    # Critical fields
    critical_disc = [d for d in discrepancies if d.get("critical")]
    if critical_disc:
        recommendations.append({
            "priority": "CRITICAL",
            "action": "Resolve critical discrepancies immediately",
            "description": f"{len(critical_disc)} critical field discrepancies require resolution",
            "affected_subjects": list(set(d["subject_id"] for d in critical_disc))
        })
    
    return recommendations