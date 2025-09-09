from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepares comprehensive DSMB (Data Safety Monitoring Board) packages.
    
    Args:
        input_data: Dictionary containing:
            - meeting_details: DSMB meeting information:
                - meeting_date: Scheduled meeting date
                - meeting_type: Type ("scheduled", "ad-hoc", "emergency")
                - review_period: Data review period
            - enrollment_data: Study enrollment statistics
            - safety_data: Safety summary including:
                - adverse_events: AE summary
                - serious_adverse_events: SAE details
                - deaths: Death reports
                - discontinuations: Discontinuation summary
            - efficacy_data: Efficacy endpoints (if applicable)
            - protocol_deviations: List of protocol deviations
            - data_cutoff_date: Database cutoff date
            - unblinding_level: Level of unblinding ("blinded", "partial", "full")
            - additional_analyses: List of additional requested analyses
    
    Returns:
        Dictionary containing:
            - package_contents: List of prepared documents/sections
            - executive_summary: High-level summary
            - safety_summary: Comprehensive safety overview
            - enrollment_summary: Enrollment and retention metrics
            - recommendations: Preliminary recommendations
            - open_issues: Issues requiring DSMB attention
            - appendices: Additional supporting materials
    """
    try:
        meeting_details = input_data.get("meeting_details", {})
        if not meeting_details:
            return {
                "error": "No meeting details provided",
                "package_contents": [],
                "executive_summary": {},
                "safety_summary": {},
                "enrollment_summary": {},
                "recommendations": [],
                "open_issues": [],
                "appendices": []
            }
        
        enrollment_data = input_data.get("enrollment_data", {})
        safety_data = input_data.get("safety_data", {})
        efficacy_data = input_data.get("efficacy_data", {})
        protocol_deviations = input_data.get("protocol_deviations", [])
        data_cutoff_date = input_data.get("data_cutoff_date", datetime.now().strftime("%Y-%m-%d"))
        unblinding_level = input_data.get("unblinding_level", "blinded")
        additional_analyses = input_data.get("additional_analyses", [])
        
        # Prepare package contents
        package_contents = prepare_package_contents(
            meeting_details, unblinding_level, additional_analyses
        )
        
        # Generate executive summary
        executive_summary = generate_executive_summary(
            enrollment_data, safety_data, efficacy_data, data_cutoff_date
        )
        
        # Prepare safety summary
        safety_summary = prepare_safety_summary(safety_data, unblinding_level)
        
        # Prepare enrollment summary
        enrollment_summary = prepare_enrollment_summary(enrollment_data)
        
        # Generate recommendations
        recommendations = generate_recommendations(
            safety_data, enrollment_data, protocol_deviations
        )
        
        # Identify open issues
        open_issues = identify_open_issues(
            safety_data, enrollment_data, protocol_deviations
        )
        
        # Prepare appendices
        appendices = prepare_appendices(
            protocol_deviations, additional_analyses, meeting_details
        )
        
        return {
            "package_contents": package_contents,
            "executive_summary": executive_summary,
            "safety_summary": safety_summary,
            "enrollment_summary": enrollment_summary,
            "recommendations": recommendations,
            "open_issues": open_issues,
            "appendices": appendices
        }
        
    except Exception as e:
        return {
            "error": f"Error preparing DSMB package: {str(e)}",
            "package_contents": [],
            "executive_summary": {},
            "safety_summary": {},
            "enrollment_summary": {},
            "recommendations": [],
            "open_issues": [],
            "appendices": []
        }


def prepare_package_contents(meeting_details: Dict, unblinding_level: str,
                            additional_analyses: List) -> List[Dict]:
    """Prepare list of package contents."""
    contents = [
        {
            "section": "Cover Letter",
            "description": "Meeting logistics and agenda",
            "pages": "1-2"
        },
        {
            "section": "Executive Summary",
            "description": "High-level overview of study status",
            "pages": "3-5"
        },
        {
            "section": "Enrollment Status",
            "description": "Recruitment, retention, and demographic data",
            "pages": "6-10"
        },
        {
            "section": "Safety Data",
            "description": "Comprehensive safety analysis",
            "pages": "11-25"
        },
        {
            "section": "Protocol Deviations",
            "description": "Summary of protocol compliance",
            "pages": "26-28"
        }
    ]
    
    if unblinding_level in ["partial", "full"]:
        contents.append({
            "section": "Efficacy Data",
            "description": "Interim efficacy analysis",
            "pages": "29-35"
        })
    
    if additional_analyses:
        contents.append({
            "section": "Additional Analyses",
            "description": f"Requested analyses: {', '.join(additional_analyses[:3])}",
            "pages": "36-40"
        })
    
    contents.append({
        "section": "Appendices",
        "description": "Supporting documents and detailed listings",
        "pages": "41+"
    })
    
    return contents


def generate_executive_summary(enrollment_data: Dict, safety_data: Dict,
                              efficacy_data: Dict, data_cutoff_date: str) -> Dict:
    """Generate executive summary for DSMB."""
    total_enrolled = enrollment_data.get("total_enrolled", 0)
    target_enrollment = enrollment_data.get("target_enrollment", 0)
    
    total_aes = sum(safety_data.get("adverse_events", {}).get("by_severity", {}).values())
    total_saes = len(safety_data.get("serious_adverse_events", []))
    total_deaths = len(safety_data.get("deaths", []))
    
    summary = {
        "study_status": determine_study_status(enrollment_data),
        "data_cutoff_date": data_cutoff_date,
        "enrollment_progress": {
            "enrolled": total_enrolled,
            "target": target_enrollment,
            "percent_complete": round((total_enrolled / target_enrollment * 100), 1) if target_enrollment > 0 else 0
        },
        "safety_overview": {
            "total_aes": total_aes,
            "total_saes": total_saes,
            "deaths": total_deaths,
            "discontinuations_safety": safety_data.get("discontinuations", {}).get("due_to_ae", 0)
        },
        "key_findings": [],
        "data_quality": {
            "database_lock": "Partial",
            "query_rate": enrollment_data.get("data_quality", {}).get("query_rate", "N/A"),
            "monitoring_coverage": enrollment_data.get("data_quality", {}).get("monitoring_coverage", "N/A")
        }
    }
    
    # Add key findings
    if total_deaths > 0:
        summary["key_findings"].append(f"{total_deaths} death(s) reported")
    
    if total_saes > 5:
        summary["key_findings"].append(f"Elevated SAE rate ({total_saes} events)")
    
    enrollment_rate = enrollment_data.get("monthly_enrollment_rate", 0)
    if enrollment_rate < enrollment_data.get("target_monthly_rate", 999):
        summary["key_findings"].append("Enrollment below target rate")
    
    if efficacy_data:
        if efficacy_data.get("stopping_boundary_crossed", False):
            summary["key_findings"].append("Efficacy stopping boundary crossed")
    
    return summary


def determine_study_status(enrollment_data: Dict) -> str:
    """Determine overall study status."""
    total_enrolled = enrollment_data.get("total_enrolled", 0)
    target_enrollment = enrollment_data.get("target_enrollment", 1)
    percent_complete = (total_enrolled / target_enrollment) * 100
    
    if percent_complete >= 100:
        return "Enrollment complete"
    elif percent_complete >= 75:
        return "Nearing enrollment completion"
    elif percent_complete >= 50:
        return "Enrollment ongoing"
    elif percent_complete >= 25:
        return "Early enrollment phase"
    else:
        return "Study initiation"


def prepare_safety_summary(safety_data: Dict, unblinding_level: str) -> Dict:
    """Prepare comprehensive safety summary."""
    ae_data = safety_data.get("adverse_events", {})
    sae_data = safety_data.get("serious_adverse_events", [])
    
    summary = {
        "overview": {
            "subjects_with_ae": ae_data.get("subjects_with_ae", 0),
            "subjects_with_sae": ae_data.get("subjects_with_sae", 0),
            "subjects_with_death": len(safety_data.get("deaths", [])),
            "subjects_discontinued_ae": safety_data.get("discontinuations", {}).get("due_to_ae", 0)
        },
        "ae_by_severity": ae_data.get("by_severity", {}),
        "ae_by_relationship": ae_data.get("by_relationship", {}),
        "most_common_aes": ae_data.get("most_common", []),
        "sae_summary": [],
        "deaths_summary": [],
        "safety_signals": []
    }
    
    # Process SAEs
    for sae in sae_data[:10]:  # Top 10 SAEs
        summary["sae_summary"].append({
            "event": sae.get("event_term"),
            "severity": sae.get("severity"),
            "outcome": sae.get("outcome"),
            "relationship": sae.get("relationship")
        })
    
    # Process deaths
    for death in safety_data.get("deaths", []):
        summary["deaths_summary"].append({
            "subject": death.get("subject_id"),
            "cause": death.get("cause"),
            "relationship": death.get("relationship"),
            "days_from_treatment": death.get("days_from_last_dose")
        })
    
    # Add treatment group comparison if unblinded
    if unblinding_level in ["partial", "full"]:
        summary["by_treatment_group"] = safety_data.get("by_treatment_group", {})
    
    # Identify safety signals
    if ae_data.get("signals", []):
        summary["safety_signals"] = ae_data["signals"]
    
    return summary


def prepare_enrollment_summary(enrollment_data: Dict) -> Dict:
    """Prepare enrollment and retention summary."""
    summary = {
        "overall_enrollment": {
            "screened": enrollment_data.get("total_screened", 0),
            "screen_failures": enrollment_data.get("screen_failures", 0),
            "enrolled": enrollment_data.get("total_enrolled", 0),
            "randomized": enrollment_data.get("total_randomized", 0),
            "active": enrollment_data.get("currently_active", 0),
            "completed": enrollment_data.get("completed", 0),
            "discontinued": enrollment_data.get("discontinued", 0)
        },
        "enrollment_rate": {
            "current_month": enrollment_data.get("current_month_enrolled", 0),
            "average_monthly": enrollment_data.get("average_monthly_rate", 0),
            "target_monthly": enrollment_data.get("target_monthly_rate", 0),
            "projected_completion": calculate_enrollment_projection(enrollment_data)
        },
        "by_site": enrollment_data.get("by_site", {}),
        "by_country": enrollment_data.get("by_country", {}),
        "demographics": enrollment_data.get("demographics", {}),
        "retention_metrics": {
            "retention_rate": enrollment_data.get("retention_rate", 0),
            "median_time_in_study": enrollment_data.get("median_days_in_study", 0),
            "completion_rate": calculate_completion_rate(enrollment_data)
        }
    }
    
    # Add recruitment challenges if any
    if enrollment_data.get("recruitment_challenges"):
        summary["recruitment_challenges"] = enrollment_data["recruitment_challenges"]
    
    return summary


def calculate_enrollment_projection(enrollment_data: Dict) -> str:
    """Calculate projected enrollment completion date."""
    remaining = enrollment_data.get("target_enrollment", 0) - enrollment_data.get("total_enrolled", 0)
    monthly_rate = enrollment_data.get("average_monthly_rate", 1)
    
    if remaining <= 0:
        return "Complete"
    
    if monthly_rate > 0:
        months_remaining = remaining / monthly_rate
        projected_date = datetime.now() + timedelta(days=months_remaining * 30)
        return projected_date.strftime("%B %Y")
    
    return "Unable to project"


def calculate_completion_rate(enrollment_data: Dict) -> float:
    """Calculate study completion rate."""
    completed = enrollment_data.get("completed", 0)
    discontinued = enrollment_data.get("discontinued", 0)
    
    total_ended = completed + discontinued
    if total_ended > 0:
        return round((completed / total_ended) * 100, 1)
    return 0


def generate_recommendations(safety_data: Dict, enrollment_data: Dict,
                            protocol_deviations: List) -> List[Dict]:
    """Generate recommendations for DSMB consideration."""
    recommendations = []
    
    # Safety recommendations
    total_saes = len(safety_data.get("serious_adverse_events", []))
    total_deaths = len(safety_data.get("deaths", []))
    
    if total_deaths > 0:
        recommendations.append({
            "category": "Safety",
            "priority": "HIGH",
            "recommendation": "Review all death narratives and causality assessments",
            "rationale": f"{total_deaths} death(s) reported requiring detailed review"
        })
    
    if total_saes > 10:
        recommendations.append({
            "category": "Safety",
            "priority": "MEDIUM",
            "recommendation": "Consider additional safety monitoring measures",
            "rationale": f"Elevated SAE rate with {total_saes} events"
        })
    
    # Enrollment recommendations
    enrollment_rate = enrollment_data.get("average_monthly_rate", 0)
    target_rate = enrollment_data.get("target_monthly_rate", 999)
    
    if enrollment_rate < target_rate * 0.75:
        recommendations.append({
            "category": "Enrollment",
            "priority": "MEDIUM",
            "recommendation": "Implement recruitment enhancement strategies",
            "rationale": "Enrollment rate 25% below target"
        })
    
    # Protocol compliance recommendations
    major_deviations = [d for d in protocol_deviations if d.get("severity") == "major"]
    if len(major_deviations) > 5:
        recommendations.append({
            "category": "Protocol Compliance",
            "priority": "MEDIUM",
            "recommendation": "Enhance site training on protocol procedures",
            "rationale": f"{len(major_deviations)} major protocol deviations identified"
        })
    
    # Study continuation recommendation
    recommendations.append({
        "category": "Study Conduct",
        "priority": "STANDARD",
        "recommendation": "Continue study as planned with routine monitoring",
        "rationale": "No critical safety or efficacy concerns identified"
    })
    
    return recommendations


def identify_open_issues(safety_data: Dict, enrollment_data: Dict,
                        protocol_deviations: List) -> List[Dict]:
    """Identify issues requiring DSMB attention."""
    open_issues = []
    
    # Check for deaths
    deaths = safety_data.get("deaths", [])
    if deaths:
        open_issues.append({
            "issue": "Deaths reported",
            "count": len(deaths),
            "action_needed": "Review death narratives and causality",
            "priority": "CRITICAL"
        })
    
    # Check for high SAE count
    saes = safety_data.get("serious_adverse_events", [])
    if len(saes) >= 10:
        open_issues.append({
            "issue": "High SAE count",
            "count": len(saes),
            "action_needed": "Review SAE patterns and safety profile",
            "priority": "HIGH"
        })
    
    # Check for unresolved SAEs
    unresolved_saes = [sae for sae in saes
                      if sae.get("outcome") == "ongoing"]
    if unresolved_saes:
        open_issues.append({
            "issue": "Unresolved SAEs",
            "count": len(unresolved_saes),
            "action_needed": "Review ongoing SAE management",
            "priority": "HIGH"
        })
    
    # Check for site performance issues
    poor_performing_sites = [site for site, data in enrollment_data.get("by_site", {}).items()
                            if data.get("enrollment") == 0 and data.get("months_active", 0) > 3]
    if poor_performing_sites:
        open_issues.append({
            "issue": "Non-enrolling sites",
            "count": len(poor_performing_sites),
            "action_needed": "Consider site closure or remediation",
            "priority": "MEDIUM"
        })
    
    # Check for stopping rules
    if safety_data.get("stopping_rule_triggered", False):
        open_issues.append({
            "issue": "Stopping rule triggered",
            "count": 1,
            "action_needed": "Evaluate study continuation",
            "priority": "CRITICAL"
        })
    
    # Check for regulatory issues
    regulatory_issues = [d for d in protocol_deviations 
                        if d.get("reportable_to_regulatory", False)]
    if regulatory_issues:
        open_issues.append({
            "issue": "Regulatory reportable deviations",
            "count": len(regulatory_issues),
            "action_needed": "Ensure regulatory compliance",
            "priority": "HIGH"
        })
    
    return open_issues


def prepare_appendices(protocol_deviations: List, additional_analyses: List,
                      meeting_details: Dict) -> List[Dict]:
    """Prepare appendices for DSMB package."""
    appendices = [
        {
            "title": "Appendix A: Detailed Safety Listings",
            "content": "Complete listing of all adverse events",
            "format": "Table"
        },
        {
            "title": "Appendix B: SAE Narratives",
            "content": "Detailed narratives for all serious adverse events",
            "format": "Text"
        },
        {
            "title": "Appendix C: Protocol Deviation Listing",
            "content": "Complete listing of protocol deviations",
            "format": "Table"
        },
        {
            "title": "Appendix D: Site Performance Metrics",
            "content": "Detailed site-by-site performance data",
            "format": "Table/Charts"
        }
    ]
    
    # Add additional analyses if requested
    for i, analysis in enumerate(additional_analyses, 1):
        appendices.append({
            "title": f"Appendix {chr(68+i)}: {analysis}",
            "content": f"Additional analysis: {analysis}",
            "format": "Mixed"
        })
    
    # Add meeting-specific materials
    if meeting_details.get("meeting_type") == "ad-hoc":
        appendices.append({
            "title": "Appendix: Ad-hoc Review Materials",
            "content": "Materials specific to ad-hoc review request",
            "format": "Mixed"
        })
    
    return appendices