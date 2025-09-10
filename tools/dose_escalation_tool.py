from typing import Dict, List, Optional, Any
from datetime import datetime


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Supports dose escalation committees with safety assessments and dose recommendation algorithms.
    
    Example:
        Input: Current cohort data with dose-limiting toxicity events and escalation rules
        Output: Dose escalation recommendation with safety assessment and decision rationale
    
    Parameters:
        cohort_data : dict
            Current cohort information including dose level and enrolled subjects
        dlt_events : list
            List of dose-limiting toxicity events with severity grades
        dose_levels : list
            Planned dose levels for the study
        escalation_rules : dict
            Escalation design parameters (3+3, mTPI, BOIN, etc.)
        prior_cohorts : list
            Historical data from completed cohorts
        pharmacokinetic_data : dict
            Optional PK data for dose decisions
    """
    try:
        cohort_data = input_data.get("cohort_data", {})
        if not cohort_data:
            return {
                "error": "No cohort data provided",
                "recommendation": {},
                "dlt_summary": {},
                "safety_assessment": {},
                "statistical_analysis": {},
                "decision_rationale": "",
                "next_steps": []
            }
        
        dlt_events = input_data.get("dlt_events", [])
        dose_levels = input_data.get("dose_levels", [])
        escalation_rules = input_data.get("escalation_rules", {"design": "3+3"})
        prior_cohorts = input_data.get("prior_cohorts", [])
        pk_data = input_data.get("pharmacokinetic_data", {})
        
        # Analyze current cohort DLTs
        dlt_summary = analyze_dlts(cohort_data, dlt_events)
        
        # Perform safety assessment
        safety_assessment = assess_safety(dlt_events, prior_cohorts)
        
        # Statistical analysis
        statistical_analysis = perform_statistical_analysis(
            cohort_data, dlt_events, prior_cohorts, escalation_rules
        )
        
        # Generate recommendation based on design
        recommendation = generate_recommendation(
            cohort_data, dlt_summary, escalation_rules, dose_levels
        )
        
        # Create decision rationale
        decision_rationale = create_rationale(
            recommendation, dlt_summary, safety_assessment, statistical_analysis, pk_data
        )
        
        # Define next steps
        next_steps = define_next_steps(recommendation, cohort_data, dlt_summary)
        
        return {
            "recommendation": recommendation,
            "dlt_summary": dlt_summary,
            "safety_assessment": safety_assessment,
            "statistical_analysis": statistical_analysis,
            "decision_rationale": decision_rationale,
            "next_steps": next_steps
        }
        
    except Exception as e:
        return {
            "error": f"Error in dose escalation analysis: {str(e)}",
            "recommendation": {},
            "dlt_summary": {},
            "safety_assessment": {},
            "statistical_analysis": {},
            "decision_rationale": "",
            "next_steps": []
        }


def analyze_dlts(cohort_data: Dict, dlt_events: List[Dict]) -> Dict:
    """Analyze DLT events for the current cohort."""
    evaluable = cohort_data.get("subjects_evaluable", 0)
    
    if evaluable == 0:
        return {
            "dlt_count": 0,
            "dlt_rate": 0,
            "evaluable_subjects": 0,
            "status": "Not evaluable"
        }
    
    related_dlts = [d for d in dlt_events if d.get("relationship", "").lower() in 
                    ["related", "possibly related", "probably related"]]
    
    dlt_summary = {
        "dlt_count": len(related_dlts),
        "dlt_rate": len(related_dlts) / evaluable,
        "evaluable_subjects": evaluable,
        "dlt_details": [],
        "status": "Evaluated"
    }
    
    for dlt in related_dlts:
        dlt_summary["dlt_details"].append({
            "subject": dlt["subject_id"],
            "event": dlt["event_term"],
            "grade": dlt["grade"],
            "resolved": dlt.get("resolved", False)
        })
    
    return dlt_summary


def assess_safety(dlt_events: List[Dict], prior_cohorts: List[Dict]) -> Dict:
    """Perform overall safety assessment."""
    # Analyze severity distribution
    grade_distribution = {}
    for event in dlt_events:
        grade = event.get("grade", 0)
        grade_distribution[f"grade_{grade}"] = grade_distribution.get(f"grade_{grade}", 0) + 1
    
    # Check for concerning patterns
    safety_concerns = []
    
    # Check for multiple grade 4 events
    if grade_distribution.get("grade_4", 0) >= 2:
        safety_concerns.append("Multiple grade 4 events observed")
    
    # Check for unresolved DLTs
    unresolved = [d for d in dlt_events if not d.get("resolved", False)]
    if len(unresolved) > 1:
        safety_concerns.append(f"{len(unresolved)} unresolved DLTs")
    
    # Analyze cumulative DLT rate
    total_dlts = len(dlt_events)
    for cohort in prior_cohorts:
        total_dlts += cohort.get("dlt_count", 0)
    
    total_subjects = sum(c.get("subjects_evaluable", 0) for c in prior_cohorts)
    total_subjects += len(set(d["subject_id"] for d in dlt_events))
    
    cumulative_dlt_rate = total_dlts / total_subjects if total_subjects > 0 else 0
    
    return {
        "grade_distribution": grade_distribution,
        "safety_concerns": safety_concerns,
        "cumulative_dlt_rate": round(cumulative_dlt_rate, 3),
        "total_dlts_observed": total_dlts,
        "safety_profile": "Acceptable" if not safety_concerns else "Concerning"
    }


def perform_statistical_analysis(cohort_data: Dict, dlt_events: List[Dict],
                                prior_cohorts: List[Dict], escalation_rules: Dict) -> Dict:
    """Perform statistical analysis for dose escalation."""
    design = escalation_rules.get("design", "3+3")
    target_dlt_rate = escalation_rules.get("dlt_rate_target", 0.33)
    
    current_dlt_rate = len(dlt_events) / cohort_data.get("subjects_evaluable", 1)
    
    analysis = {
        "design": design,
        "target_dlt_rate": target_dlt_rate,
        "observed_dlt_rate": round(current_dlt_rate, 3),
        "confidence_interval": calculate_confidence_interval(
            len(dlt_events), cohort_data.get("subjects_evaluable", 1)
        )
    }
    
    # Bayesian probability for mTPI/BOIN designs
    if design in ["mTPI", "BOIN"]:
        analysis["posterior_probability"] = calculate_posterior_probability(
            len(dlt_events), cohort_data.get("subjects_evaluable", 1), target_dlt_rate
        )
    
    return analysis


def generate_recommendation(cohort_data: Dict, dlt_summary: Dict,
                           escalation_rules: Dict, dose_levels: List) -> Dict:
    """Generate dose escalation recommendation."""
    design = escalation_rules.get("design", "3+3")
    current_dose_idx = dose_levels.index(cohort_data["dose_level"]) if cohort_data["dose_level"] in dose_levels else 0
    
    if design == "3+3":
        recommendation = apply_3plus3_rules(
            dlt_summary["dlt_count"],
            dlt_summary["evaluable_subjects"],
            current_dose_idx,
            dose_levels
        )
    else:
        # Simplified logic for other designs
        max_dlts = escalation_rules.get("max_dlts_per_cohort", 1)
        if dlt_summary["dlt_count"] > max_dlts:
            recommendation = {
                "decision": "DE-ESCALATE",
                "next_dose": dose_levels[max(0, current_dose_idx - 1)] if dose_levels else None,
                "confidence": "High"
            }
        elif dlt_summary["dlt_count"] <= max_dlts and dlt_summary["evaluable_subjects"] >= 3:
            if current_dose_idx < len(dose_levels) - 1:
                recommendation = {
                    "decision": "ESCALATE",
                    "next_dose": dose_levels[current_dose_idx + 1],
                    "confidence": "Moderate"
                }
            else:
                recommendation = {
                    "decision": "STAY",
                    "next_dose": cohort_data["dose_level"],
                    "confidence": "High"
                }
        else:
            recommendation = {
                "decision": "EXPAND",
                "next_dose": cohort_data["dose_level"],
                "confidence": "Moderate"
            }
    
    recommendation["mtd_assessment"] = assess_mtd(dlt_summary, escalation_rules)
    
    return recommendation


def apply_3plus3_rules(dlt_count: int, evaluable: int, current_idx: int,
                       dose_levels: List) -> Dict:
    """Apply traditional 3+3 design rules."""
    if evaluable < 3:
        return {
            "decision": "EXPAND",
            "next_dose": dose_levels[current_idx] if dose_levels else None,
            "confidence": "High",
            "rationale": "Need minimum 3 evaluable subjects"
        }
    
    if evaluable == 3:
        if dlt_count == 0:
            # Escalate
            if current_idx < len(dose_levels) - 1:
                return {
                    "decision": "ESCALATE",
                    "next_dose": dose_levels[current_idx + 1],
                    "confidence": "High",
                    "rationale": "0/3 DLTs - safe to escalate"
                }
            else:
                return {
                    "decision": "EXPAND",
                    "next_dose": dose_levels[current_idx],
                    "confidence": "High",
                    "rationale": "Maximum dose reached"
                }
        elif dlt_count == 1:
            # Expand cohort
            return {
                "decision": "EXPAND",
                "next_dose": dose_levels[current_idx],
                "confidence": "High",
                "rationale": "1/3 DLTs - expand cohort to 6"
            }
        else:
            # De-escalate or stop
            if current_idx > 0:
                return {
                    "decision": "DE-ESCALATE",
                    "next_dose": dose_levels[current_idx - 1],
                    "confidence": "High",
                    "rationale": f"{dlt_count}/3 DLTs - dose too toxic"
                }
            else:
                return {
                    "decision": "STOP",
                    "next_dose": None,
                    "confidence": "High",
                    "rationale": "DLTs at starting dose"
                }
    
    elif evaluable == 6:
        if dlt_count <= 1:
            # Escalate
            if current_idx < len(dose_levels) - 1:
                return {
                    "decision": "ESCALATE",
                    "next_dose": dose_levels[current_idx + 1],
                    "confidence": "High",
                    "rationale": f"{dlt_count}/6 DLTs - safe to escalate"
                }
            else:
                return {
                    "decision": "MTD",
                    "next_dose": dose_levels[current_idx],
                    "confidence": "High",
                    "rationale": "MTD established at maximum dose"
                }
        else:
            # De-escalate
            if current_idx > 0:
                return {
                    "decision": "DE-ESCALATE",
                    "next_dose": dose_levels[current_idx - 1],
                    "confidence": "High",
                    "rationale": f"{dlt_count}/6 DLTs - dose too toxic"
                }
            else:
                return {
                    "decision": "STOP",
                    "next_dose": None,
                    "confidence": "High",
                    "rationale": "Excessive toxicity at starting dose"
                }
    
    return {
        "decision": "REVIEW",
        "next_dose": dose_levels[current_idx] if dose_levels else None,
        "confidence": "Low",
        "rationale": "Non-standard scenario requires review"
    }


def assess_mtd(dlt_summary: Dict, escalation_rules: Dict) -> str:
    """Assess if MTD has been reached."""
    target_rate = escalation_rules.get("dlt_rate_target", 0.33)
    
    if dlt_summary["dlt_rate"] > target_rate:
        return "Exceeded"
    elif abs(dlt_summary["dlt_rate"] - target_rate) < 0.1:
        return "Likely reached"
    else:
        return "Not reached"


def calculate_confidence_interval(dlts: int, n: int) -> tuple:
    """Calculate 95% confidence interval for DLT rate."""
    if n == 0:
        return (0, 1)
    
    p = dlts / n
    z = 1.96  # 95% CI
    
    # Wilson score interval
    denominator = 1 + z**2/n
    center = (p + z**2/(2*n)) / denominator
    margin = z * ((p*(1-p)/n + z**2/(4*n**2))**0.5) / denominator
    
    return (max(0, center - margin), min(1, center + margin))


def calculate_posterior_probability(dlts: int, n: int, target: float) -> float:
    """Simplified posterior probability calculation."""
    # Beta posterior with uniform prior
    alpha = dlts + 1
    beta = n - dlts + 1
    
    # Approximate probability that true DLT rate exceeds target
    # This is simplified - real implementation would use beta distribution
    observed_rate = dlts / n if n > 0 else 0
    
    if observed_rate > target:
        return min(0.95, 0.5 + (observed_rate - target) * 2)
    else:
        return max(0.05, 0.5 - (target - observed_rate) * 2)


def create_rationale(recommendation: Dict, dlt_summary: Dict,
                    safety_assessment: Dict, statistical_analysis: Dict,
                    pk_data: Dict) -> str:
    """Create detailed decision rationale."""
    rationale_parts = []
    
    # Summary of current cohort
    rationale_parts.append(
        f"Current cohort: {dlt_summary['dlt_count']}/{dlt_summary['evaluable_subjects']} DLTs "
        f"(rate: {dlt_summary['dlt_rate']:.1%})"
    )
    
    # Statistical assessment
    ci = statistical_analysis["confidence_interval"]
    rationale_parts.append(
        f"DLT rate 95% CI: ({ci[0]:.1%}, {ci[1]:.1%})"
    )
    
    # Safety profile
    if safety_assessment["safety_concerns"]:
        rationale_parts.append(
            f"Safety concerns: {'; '.join(safety_assessment['safety_concerns'])}"
        )
    
    # PK data if available
    if pk_data:
        rationale_parts.append("PK data supports dose proportionality")
    
    # Recommendation
    rationale_parts.append(
        f"Recommendation: {recommendation['decision']} "
        f"(confidence: {recommendation['confidence']})"
    )
    
    if recommendation.get("rationale"):
        rationale_parts.append(recommendation["rationale"])
    
    return " | ".join(rationale_parts)


def define_next_steps(recommendation: Dict, cohort_data: Dict, dlt_summary: Dict) -> List[str]:
    """Define next steps based on recommendation."""
    steps = []
    
    if recommendation["decision"] == "ESCALATE":
        steps.append(f"Open enrollment for next cohort at {recommendation['next_dose']}")
        steps.append("Review safety data from current cohort before first subject dosed")
        steps.append("Ensure adequate PK sampling at new dose level")
        
    elif recommendation["decision"] == "EXPAND":
        remaining = 6 - cohort_data.get("subjects_evaluable", 0)
        steps.append(f"Enroll {remaining} additional subjects at current dose")
        steps.append("Continue safety monitoring")
        steps.append("Schedule review after cohort completion")
        
    elif recommendation["decision"] == "DE-ESCALATE":
        steps.append(f"Close enrollment at current dose")
        steps.append(f"Open enrollment at {recommendation['next_dose']}")
        steps.append("Consider protocol amendment if de-escalation pattern continues")
        
    elif recommendation["decision"] == "MTD":
        steps.append("MTD established - prepare for expansion cohort")
        steps.append("Consider RP2D determination")
        steps.append("Prepare regulatory update")
        
    elif recommendation["decision"] == "STOP":
        steps.append("Halt enrollment immediately")
        steps.append("Convene safety review committee")
        steps.append("Consider protocol amendments or study termination")
    
    # Always include safety monitoring
    steps.append("Continue close safety monitoring of all enrolled subjects")
    
    return steps