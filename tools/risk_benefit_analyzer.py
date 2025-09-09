from typing import Dict, List, Optional, Any
import math


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates and analyzes risk-benefit ratios for clinical trials.
    
    Args:
        input_data: Dictionary containing:
            - efficacy_data: Efficacy outcomes:
                - primary_endpoint: Primary endpoint results
                - secondary_endpoints: Secondary endpoint results
                - responder_rate: Response rate data
                - clinical_benefit: Clinical benefit metrics
            - safety_data: Safety profile:
                - adverse_events: AE summary by severity
                - serious_adverse_events: SAE details
                - discontinuations: Discontinuation data
                - deaths: Mortality data
            - quality_of_life: Optional QoL data
            - comparator_data: Optional comparator arm data
            - population_characteristics: Patient population details
            - analysis_type: Type of analysis ("interim", "final", "ongoing")
    
    Returns:
        Dictionary containing:
            - risk_benefit_ratio: Calculated risk-benefit metrics
            - benefit_assessment: Detailed benefit analysis
            - risk_assessment: Detailed risk analysis
            - overall_assessment: Overall risk-benefit conclusion
            - subgroup_analyses: Subgroup-specific assessments
            - recommendations: Clinical recommendations
            - visualization_data: Data for risk-benefit plots
    """
    try:
        efficacy_data = input_data.get("efficacy_data", {})
        safety_data = input_data.get("safety_data", {})
        
        if not efficacy_data or not safety_data:
            return {
                "error": "Both efficacy and safety data required",
                "risk_benefit_ratio": {},
                "benefit_assessment": {},
                "risk_assessment": {},
                "overall_assessment": {},
                "subgroup_analyses": [],
                "recommendations": [],
                "visualization_data": {}
            }
        
        quality_of_life = input_data.get("quality_of_life", {})
        comparator_data = input_data.get("comparator_data", {})
        population_characteristics = input_data.get("population_characteristics", {})
        analysis_type = input_data.get("analysis_type", "ongoing")
        
        # Assess benefits
        benefit_assessment = assess_benefits(efficacy_data, quality_of_life, comparator_data)
        
        # Assess risks
        risk_assessment = assess_risks(safety_data, comparator_data)
        
        # Calculate risk-benefit ratio
        risk_benefit_ratio = calculate_risk_benefit_ratio(
            benefit_assessment, risk_assessment, population_characteristics
        )
        
        # Perform overall assessment
        overall_assessment = perform_overall_assessment(
            risk_benefit_ratio, benefit_assessment, risk_assessment, analysis_type
        )
        
        # Subgroup analyses
        subgroup_analyses = perform_subgroup_analyses(
            efficacy_data, safety_data, population_characteristics
        )
        
        # Generate recommendations
        recommendations = generate_recommendations(
            overall_assessment, risk_benefit_ratio, subgroup_analyses
        )
        
        # Prepare visualization data
        visualization_data = prepare_visualization_data(
            benefit_assessment, risk_assessment, risk_benefit_ratio
        )
        
        return {
            "risk_benefit_ratio": risk_benefit_ratio,
            "benefit_assessment": benefit_assessment,
            "risk_assessment": risk_assessment,
            "overall_assessment": overall_assessment,
            "subgroup_analyses": subgroup_analyses,
            "recommendations": recommendations,
            "visualization_data": visualization_data
        }
        
    except Exception as e:
        return {
            "error": f"Error analyzing risk-benefit: {str(e)}",
            "risk_benefit_ratio": {},
            "benefit_assessment": {},
            "risk_assessment": {},
            "overall_assessment": {},
            "subgroup_analyses": [],
            "recommendations": [],
            "visualization_data": {}
        }


def assess_benefits(efficacy_data: Dict, quality_of_life: Dict, 
                   comparator_data: Dict) -> Dict:
    """Assess clinical benefits."""
    benefits = {
        "primary_benefit": {},
        "secondary_benefits": [],
        "clinical_relevance": "",
        "magnitude_of_effect": {},
        "durability": {},
        "quality_of_life_impact": {},
        "benefit_score": 0
    }
    
    # Primary endpoint benefit
    primary = efficacy_data.get("primary_endpoint", {})
    if primary:
        treatment_effect = primary.get("treatment_effect", 0)
        p_value = primary.get("p_value", 1)
        ci_lower = primary.get("ci_lower", 0)
        ci_upper = primary.get("ci_upper", 0)
        
        benefits["primary_benefit"] = {
            "endpoint": primary.get("name", "Primary endpoint"),
            "effect_size": treatment_effect,
            "statistical_significance": p_value < 0.05,
            "confidence_interval": (ci_lower, ci_upper),
            "clinical_significance": determine_clinical_significance(treatment_effect, primary.get("name"))
        }
        
        # Calculate benefit score component
        if p_value < 0.05:
            benefits["benefit_score"] += min(50, abs(treatment_effect) * 10)
    
    # Secondary endpoints
    for secondary in efficacy_data.get("secondary_endpoints", []):
        sec_benefit = {
            "endpoint": secondary.get("name"),
            "effect_size": secondary.get("treatment_effect"),
            "p_value": secondary.get("p_value"),
            "supportive": secondary.get("p_value", 1) < 0.05
        }
        benefits["secondary_benefits"].append(sec_benefit)
        
        if sec_benefit["supportive"]:
            benefits["benefit_score"] += 5
    
    # Response rate
    responder_rate = efficacy_data.get("responder_rate", {})
    if responder_rate:
        treatment_rate = responder_rate.get("treatment", 0)
        control_rate = responder_rate.get("control", 0) if comparator_data else 0
        
        benefits["magnitude_of_effect"] = {
            "absolute_difference": treatment_rate - control_rate,
            "relative_difference": ((treatment_rate - control_rate) / control_rate * 100) if control_rate > 0 else 0,
            "nnt": calculate_nnt(treatment_rate, control_rate)
        }
        
        benefits["benefit_score"] += (treatment_rate - control_rate) * 100
    
    # Quality of life
    if quality_of_life:
        qol_improvement = quality_of_life.get("improvement_percent", 0)
        benefits["quality_of_life_impact"] = {
            "improvement": qol_improvement,
            "domains_improved": quality_of_life.get("domains_improved", []),
            "clinically_meaningful": qol_improvement > 10
        }
        
        if qol_improvement > 10:
            benefits["benefit_score"] += qol_improvement
    
    # Clinical relevance assessment
    benefits["clinical_relevance"] = assess_clinical_relevance(benefits)
    
    # Normalize benefit score (0-100)
    benefits["benefit_score"] = min(100, max(0, benefits["benefit_score"]))
    
    return benefits


def assess_risks(safety_data: Dict, comparator_data: Dict) -> Dict:
    """Assess safety risks."""
    risks = {
        "serious_risks": [],
        "common_risks": [],
        "rare_risks": [],
        "discontinuation_risk": {},
        "mortality_risk": {},
        "risk_score": 0,
        "tolerability": ""
    }
    
    # Serious adverse events
    sae_rate = safety_data.get("serious_adverse_events", {}).get("rate", 0)
    comparator_sae_rate = comparator_data.get("serious_adverse_events", {}).get("rate", 0) if comparator_data else 0
    
    if sae_rate > 0:
        risks["serious_risks"].append({
            "type": "Serious adverse events",
            "incidence": sae_rate,
            "excess_risk": sae_rate - comparator_sae_rate,
            "nnh": calculate_nnh(sae_rate, comparator_sae_rate)
        })
        risks["risk_score"] += sae_rate * 100
    
    # Common adverse events (>10%)
    ae_by_frequency = safety_data.get("adverse_events", {}).get("by_frequency", {})
    for ae, rate in ae_by_frequency.items():
        if rate > 10:
            risks["common_risks"].append({
                "event": ae,
                "incidence": rate,
                "impact": "Common"
            })
            risks["risk_score"] += rate * 0.5
    
    # Rare but serious events (<1% but serious)
    rare_serious = safety_data.get("rare_serious_events", [])
    for event in rare_serious:
        risks["rare_risks"].append({
            "event": event.get("name"),
            "incidence": event.get("rate", 0),
            "severity": event.get("severity"),
            "reversible": event.get("reversible", True)
        })
        if not event.get("reversible", True):
            risks["risk_score"] += 10
    
    # Discontinuation risk
    disc_rate = safety_data.get("discontinuations", {}).get("due_to_ae_rate", 0)
    risks["discontinuation_risk"] = {
        "rate": disc_rate,
        "main_reasons": safety_data.get("discontinuations", {}).get("main_reasons", []),
        "impact": "High" if disc_rate > 20 else "Moderate" if disc_rate > 10 else "Low"
    }
    risks["risk_score"] += disc_rate
    
    # Mortality risk
    death_rate = safety_data.get("deaths", {}).get("rate", 0)
    if death_rate > 0:
        risks["mortality_risk"] = {
            "rate": death_rate,
            "related_deaths": safety_data.get("deaths", {}).get("related", 0),
            "excess_mortality": death_rate - comparator_data.get("deaths", {}).get("rate", 0) if comparator_data else death_rate
        }
        risks["risk_score"] += death_rate * 200
    
    # Tolerability assessment
    risks["tolerability"] = assess_tolerability(risks["risk_score"], disc_rate)
    
    # Normalize risk score (0-100)
    risks["risk_score"] = min(100, max(0, risks["risk_score"]))
    
    return risks


def calculate_risk_benefit_ratio(benefit_assessment: Dict, risk_assessment: Dict,
                                population_characteristics: Dict) -> Dict:
    """Calculate risk-benefit ratio and metrics."""
    benefit_score = benefit_assessment.get("benefit_score", 0)
    risk_score = risk_assessment.get("risk_score", 0)
    
    # Basic ratio
    if risk_score > 0:
        simple_ratio = benefit_score / risk_score
    else:
        simple_ratio = float('inf') if benefit_score > 0 else 1
    
    # Weighted ratio (considering population vulnerability)
    vulnerability_factor = assess_population_vulnerability(population_characteristics)
    weighted_ratio = simple_ratio / vulnerability_factor
    
    # Calculate composite score
    composite_score = (benefit_score - risk_score * vulnerability_factor) / 2 + 50
    composite_score = max(0, min(100, composite_score))
    
    # Determine favorability
    if weighted_ratio > 2:
        favorability = "Highly favorable"
    elif weighted_ratio > 1.5:
        favorability = "Favorable"
    elif weighted_ratio > 1:
        favorability = "Marginally favorable"
    elif weighted_ratio > 0.75:
        favorability = "Marginally unfavorable"
    else:
        favorability = "Unfavorable"
    
    return {
        "simple_ratio": round(simple_ratio, 2),
        "weighted_ratio": round(weighted_ratio, 2),
        "benefit_score": benefit_score,
        "risk_score": risk_score,
        "composite_score": round(composite_score, 1),
        "favorability": favorability,
        "interpretation": generate_ratio_interpretation(weighted_ratio, favorability),
        "confidence": assess_confidence_in_ratio(benefit_assessment, risk_assessment)
    }


def perform_overall_assessment(risk_benefit_ratio: Dict, benefit_assessment: Dict,
                              risk_assessment: Dict, analysis_type: str) -> Dict:
    """Perform overall risk-benefit assessment."""
    assessment = {
        "conclusion": "",
        "strength_of_evidence": "",
        "key_considerations": [],
        "uncertainties": [],
        "recommendation": ""
    }
    
    # Determine conclusion
    favorability = risk_benefit_ratio["favorability"]
    if "favorable" in favorability.lower():
        assessment["conclusion"] = "The benefit-risk profile supports treatment use"
    elif "unfavorable" in favorability.lower():
        assessment["conclusion"] = "The benefit-risk profile does not support treatment use"
    else:
        assessment["conclusion"] = "The benefit-risk profile requires careful consideration"
    
    # Assess strength of evidence
    if analysis_type == "final":
        assessment["strength_of_evidence"] = "Strong"
    elif analysis_type == "interim":
        assessment["strength_of_evidence"] = "Moderate"
    else:
        assessment["strength_of_evidence"] = "Preliminary"
    
    # Key considerations
    if benefit_assessment["primary_benefit"].get("statistical_significance"):
        assessment["key_considerations"].append("Statistically significant primary endpoint")
    
    if risk_assessment["mortality_risk"].get("rate", 0) > 0:
        assessment["key_considerations"].append("Mortality risk requires careful monitoring")
    
    if risk_assessment["discontinuation_risk"]["impact"] == "High":
        assessment["key_considerations"].append("High discontinuation rate affects practical utility")
    
    # Uncertainties
    if analysis_type != "final":
        assessment["uncertainties"].append("Final analysis pending")
    
    if not benefit_assessment.get("quality_of_life_impact"):
        assessment["uncertainties"].append("Quality of life impact not fully characterized")
    
    # Generate recommendation
    assessment["recommendation"] = generate_overall_recommendation(
        risk_benefit_ratio, assessment["conclusion"], analysis_type
    )
    
    return assessment


def perform_subgroup_analyses(efficacy_data: Dict, safety_data: Dict,
                             population_characteristics: Dict) -> List[Dict]:
    """Perform subgroup-specific risk-benefit analyses."""
    subgroups = []
    
    # Age subgroups
    age_groups = population_characteristics.get("age_distribution", {})
    for age_group, data in age_groups.items():
        if data.get("n", 0) > 10:
            subgroup_benefit = data.get("efficacy", {}).get("response_rate", 0)
            subgroup_risk = data.get("safety", {}).get("ae_rate", 0)
            
            subgroups.append({
                "subgroup": f"Age {age_group}",
                "n": data.get("n"),
                "benefit_risk_ratio": subgroup_benefit / subgroup_risk if subgroup_risk > 0 else float('inf'),
                "recommendation": "Favorable" if subgroup_benefit > subgroup_risk else "Use with caution"
            })
    
    # Disease severity subgroups
    severity_groups = population_characteristics.get("disease_severity", {})
    for severity, data in severity_groups.items():
        if data.get("n", 0) > 10:
            subgroups.append({
                "subgroup": f"{severity} disease",
                "n": data.get("n"),
                "benefit_risk_ratio": data.get("benefit_risk_ratio", 1),
                "special_considerations": data.get("considerations", [])
            })
    
    # Comorbidity subgroups
    if population_characteristics.get("with_comorbidities"):
        comorbid_data = population_characteristics["with_comorbidities"]
        subgroups.append({
            "subgroup": "With comorbidities",
            "n": comorbid_data.get("n"),
            "benefit_risk_ratio": comorbid_data.get("benefit_risk_ratio", 1),
            "recommendation": "Requires careful monitoring"
        })
    
    return subgroups


def generate_recommendations(overall_assessment: Dict, risk_benefit_ratio: Dict,
                            subgroup_analyses: List) -> List[Dict]:
    """Generate clinical recommendations."""
    recommendations = []
    
    # Primary recommendation
    if risk_benefit_ratio["favorability"] in ["Highly favorable", "Favorable"]:
        recommendations.append({
            "type": "Primary",
            "recommendation": "Treatment is recommended for appropriate patients",
            "strength": "Strong" if risk_benefit_ratio["weighted_ratio"] > 2 else "Moderate",
            "rationale": f"Risk-benefit ratio of {risk_benefit_ratio['weighted_ratio']:.1f}"
        })
    elif risk_benefit_ratio["favorability"] == "Marginally favorable":
        recommendations.append({
            "type": "Primary",
            "recommendation": "Treatment may be considered with careful patient selection",
            "strength": "Conditional",
            "rationale": "Marginal benefit-risk profile"
        })
    else:
        recommendations.append({
            "type": "Primary",
            "recommendation": "Treatment is not recommended",
            "strength": "Strong",
            "rationale": "Unfavorable risk-benefit profile"
        })
    
    # Monitoring recommendations
    if risk_benefit_ratio["risk_score"] > 50:
        recommendations.append({
            "type": "Safety Monitoring",
            "recommendation": "Implement intensive safety monitoring",
            "frequency": "Weekly for first month, then monthly",
            "parameters": ["Liver function", "Cardiac markers", "Clinical symptoms"]
        })
    
    # Subgroup recommendations
    for subgroup in subgroup_analyses:
        if subgroup.get("benefit_risk_ratio", 0) < 1:
            recommendations.append({
                "type": "Subgroup",
                "recommendation": f"Use with caution in {subgroup['subgroup']}",
                "rationale": "Unfavorable risk-benefit in this subgroup"
            })
    
    return recommendations


def prepare_visualization_data(benefit_assessment: Dict, risk_assessment: Dict,
                              risk_benefit_ratio: Dict) -> Dict:
    """Prepare data for risk-benefit visualizations."""
    return {
        "scatter_plot": {
            "x": risk_assessment["risk_score"],
            "y": benefit_assessment["benefit_score"],
            "label": f"RB Ratio: {risk_benefit_ratio['weighted_ratio']:.2f}"
        },
        "bar_chart": {
            "categories": ["Benefit Score", "Risk Score", "Composite Score"],
            "values": [
                benefit_assessment["benefit_score"],
                risk_assessment["risk_score"],
                risk_benefit_ratio["composite_score"]
            ]
        },
        "risk_profile": {
            "serious_risks": len(risk_assessment["serious_risks"]),
            "common_risks": len(risk_assessment["common_risks"]),
            "rare_risks": len(risk_assessment["rare_risks"])
        },
        "benefit_profile": {
            "primary_significant": benefit_assessment["primary_benefit"].get("statistical_significance", False),
            "secondary_supportive": len([s for s in benefit_assessment["secondary_benefits"] if s.get("supportive")]),
            "qol_improved": benefit_assessment["quality_of_life_impact"].get("clinically_meaningful", False)
        }
    }


# Helper functions
def determine_clinical_significance(effect_size: float, endpoint_name: str) -> str:
    """Determine clinical significance of effect size."""
    # Simplified logic - would be more sophisticated in practice
    if abs(effect_size) > 20:
        return "Highly clinically significant"
    elif abs(effect_size) > 10:
        return "Clinically significant"
    elif abs(effect_size) > 5:
        return "Marginally clinically significant"
    else:
        return "Not clinically significant"


def calculate_nnt(treatment_rate: float, control_rate: float) -> float:
    """Calculate Number Needed to Treat."""
    if treatment_rate > control_rate:
        return 1 / (treatment_rate - control_rate)
    return float('inf')


def calculate_nnh(treatment_rate: float, control_rate: float) -> float:
    """Calculate Number Needed to Harm."""
    if treatment_rate > control_rate:
        return 1 / (treatment_rate - control_rate)
    return float('inf')


def assess_clinical_relevance(benefits: Dict) -> str:
    """Assess overall clinical relevance."""
    if benefits["benefit_score"] > 70:
        return "Highly clinically relevant"
    elif benefits["benefit_score"] > 50:
        return "Clinically relevant"
    elif benefits["benefit_score"] > 30:
        return "Moderately clinically relevant"
    else:
        return "Limited clinical relevance"


def assess_tolerability(risk_score: float, discontinuation_rate: float) -> str:
    """Assess treatment tolerability."""
    if risk_score < 30 and discontinuation_rate < 10:
        return "Well tolerated"
    elif risk_score < 50 and discontinuation_rate < 20:
        return "Moderately tolerated"
    else:
        return "Poorly tolerated"


def assess_population_vulnerability(population_characteristics: Dict) -> float:
    """Assess vulnerability of study population."""
    vulnerability = 1.0
    
    # Age factors
    if population_characteristics.get("median_age", 0) > 65:
        vulnerability *= 1.2
    
    # Comorbidity factors
    if population_characteristics.get("comorbidity_index", 0) > 2:
        vulnerability *= 1.3
    
    # Disease severity
    if population_characteristics.get("severe_disease_percent", 0) > 50:
        vulnerability *= 1.2
    
    return vulnerability


def generate_ratio_interpretation(ratio: float, favorability: str) -> str:
    """Generate interpretation of risk-benefit ratio."""
    if ratio > 3:
        return "Benefits substantially outweigh risks"
    elif ratio > 2:
        return "Benefits clearly outweigh risks"
    elif ratio > 1.5:
        return "Benefits outweigh risks"
    elif ratio > 1:
        return "Benefits marginally outweigh risks"
    elif ratio > 0.75:
        return "Risks and benefits are comparable"
    else:
        return "Risks outweigh benefits"


def assess_confidence_in_ratio(benefit_assessment: Dict, risk_assessment: Dict) -> str:
    """Assess confidence in risk-benefit ratio."""
    confidence_factors = 0
    
    # Check primary endpoint
    if benefit_assessment["primary_benefit"].get("statistical_significance"):
        confidence_factors += 1
    
    # Check sample size (implied by CI width)
    ci = benefit_assessment["primary_benefit"].get("confidence_interval", (0, 0))
    if ci[1] - ci[0] < 10:
        confidence_factors += 1
    
    # Check safety database size
    if risk_assessment.get("total_exposed", 0) > 500:
        confidence_factors += 1
    
    if confidence_factors >= 3:
        return "High confidence"
    elif confidence_factors >= 2:
        return "Moderate confidence"
    else:
        return "Low confidence"


def generate_overall_recommendation(risk_benefit_ratio: Dict, conclusion: str,
                                   analysis_type: str) -> str:
    """Generate overall recommendation statement."""
    if risk_benefit_ratio["favorability"] in ["Highly favorable", "Favorable"]:
        if analysis_type == "final":
            return "Recommend approval/continuation with standard monitoring"
        else:
            return "Continue development/study with ongoing monitoring"
    elif risk_benefit_ratio["favorability"] == "Marginally favorable":
        return "Consider restricted use or additional risk mitigation measures"
    else:
        if analysis_type == "final":
            return "Do not recommend approval without significant restrictions"
        else:
            return "Re-evaluate development strategy or consider early termination"