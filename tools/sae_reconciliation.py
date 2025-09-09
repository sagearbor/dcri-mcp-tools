from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import difflib


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reconciles Serious Adverse Events (SAEs) across multiple data sources.
    
    Args:
        input_data: Dictionary containing:
            - edc_saes: List of SAEs from EDC system
            - safety_db_saes: List of SAEs from safety database
            - regulatory_saes: Optional list of SAEs from regulatory reports
            - reconciliation_rules: Optional reconciliation parameters:
                - date_tolerance_days: Days tolerance for date matching (default: 3)
                - term_match_threshold: Similarity threshold for term matching (default: 0.85)
                - subject_id_exact: Require exact subject ID match (default: True)
            
            Each SAE should contain:
                - subject_id: Subject identifier
                - event_term: Event description/term
                - onset_date: SAE onset date (YYYY-MM-DD)
                - report_date: Date reported (YYYY-MM-DD)
                - outcome: Event outcome
                - severity: Severity/grade
                - causality: Relationship to study drug
                - sae_number: Optional unique SAE identifier
    
    Returns:
        Dictionary containing:
            - matched_saes: List of reconciled SAEs across systems
            - discrepancies: List of identified discrepancies
            - unmatched_edc: SAEs only in EDC
            - unmatched_safety_db: SAEs only in safety database
            - unmatched_regulatory: SAEs only in regulatory reports
            - summary: Reconciliation summary statistics
            - recommendations: List of recommended actions
    """
    try:
        edc_saes = input_data.get("edc_saes", [])
        safety_db_saes = input_data.get("safety_db_saes", [])
        regulatory_saes = input_data.get("regulatory_saes", [])
        
        if not edc_saes and not safety_db_saes:
            return {
                "error": "No SAE data provided from any source",
                "matched_saes": [],
                "discrepancies": [],
                "unmatched_edc": [],
                "unmatched_safety_db": [],
                "unmatched_regulatory": [],
                "summary": {},
                "recommendations": []
            }
        
        rules = input_data.get("reconciliation_rules", {})
        date_tolerance = rules.get("date_tolerance_days", 3)
        term_threshold = rules.get("term_match_threshold", 0.85)
        exact_subject = rules.get("subject_id_exact", True)
        
        matched_saes = []
        discrepancies = []
        recommendations = []
        
        edc_matched = set()
        safety_matched = set()
        regulatory_matched = set()
        
        for i, edc_sae in enumerate(edc_saes):
            best_safety_match = None
            best_safety_score = 0
            best_safety_idx = -1
            
            for j, safety_sae in enumerate(safety_db_saes):
                if j in safety_matched:
                    continue
                
                match_score = calculate_match_score(
                    edc_sae, safety_sae, date_tolerance, term_threshold, exact_subject
                )
                
                if match_score > best_safety_score:
                    best_safety_score = match_score
                    best_safety_match = safety_sae
                    best_safety_idx = j
            
            if best_safety_score >= 0.7:
                edc_matched.add(i)
                safety_matched.add(best_safety_idx)
                
                matched_sae = {
                    "subject_id": edc_sae["subject_id"],
                    "event_term": edc_sae["event_term"],
                    "match_confidence": best_safety_score,
                    "sources": ["EDC", "Safety DB"]
                }
                
                field_discrepancies = find_field_discrepancies(edc_sae, best_safety_match)
                if field_discrepancies:
                    matched_sae["field_discrepancies"] = field_discrepancies
                    for disc in field_discrepancies:
                        discrepancies.append({
                            "subject_id": edc_sae["subject_id"],
                            "event_term": edc_sae["event_term"],
                            "discrepancy_type": disc["field"],
                            "edc_value": disc["edc_value"],
                            "safety_db_value": disc["safety_db_value"],
                            "severity": classify_discrepancy_severity(disc["field"])
                        })
                
                if regulatory_saes:
                    reg_match = find_regulatory_match(
                        edc_sae, regulatory_saes, regulatory_matched,
                        date_tolerance, term_threshold, exact_subject
                    )
                    if reg_match:
                        matched_sae["sources"].append("Regulatory")
                        regulatory_matched.add(reg_match["index"])
                        
                        reg_discrepancies = find_field_discrepancies(edc_sae, reg_match["sae"])
                        if reg_discrepancies:
                            for disc in reg_discrepancies:
                                discrepancies.append({
                                    "subject_id": edc_sae["subject_id"],
                                    "event_term": edc_sae["event_term"],
                                    "discrepancy_type": disc["field"],
                                    "edc_value": disc["edc_value"],
                                    "regulatory_value": disc["safety_db_value"],
                                    "severity": classify_discrepancy_severity(disc["field"])
                                })
                
                matched_saes.append(matched_sae)
        
        unmatched_edc = [edc_saes[i] for i in range(len(edc_saes)) if i not in edc_matched]
        unmatched_safety = [safety_db_saes[i] for i in range(len(safety_db_saes)) if i not in safety_matched]
        unmatched_regulatory = [regulatory_saes[i] for i in range(len(regulatory_saes)) if i not in regulatory_matched] if regulatory_saes else []
        
        critical_discrepancies = [d for d in discrepancies if d["severity"] == "critical"]
        major_discrepancies = [d for d in discrepancies if d["severity"] == "major"]
        
        if unmatched_edc:
            recommendations.append({
                "priority": "HIGH",
                "action": f"Review {len(unmatched_edc)} SAEs present only in EDC",
                "details": "These SAEs need to be entered into the safety database"
            })
        
        if unmatched_safety:
            recommendations.append({
                "priority": "HIGH",
                "action": f"Review {len(unmatched_safety)} SAEs present only in safety database",
                "details": "Verify if these SAEs are correctly recorded in EDC"
            })
        
        if critical_discrepancies:
            recommendations.append({
                "priority": "CRITICAL",
                "action": f"Resolve {len(critical_discrepancies)} critical discrepancies",
                "details": "Critical fields like outcome and causality must be consistent"
            })
        
        if major_discrepancies:
            recommendations.append({
                "priority": "MEDIUM",
                "action": f"Review {len(major_discrepancies)} major discrepancies",
                "details": "Important fields like severity and dates should be aligned"
            })
        
        summary = {
            "total_edc_saes": len(edc_saes),
            "total_safety_db_saes": len(safety_db_saes),
            "total_regulatory_saes": len(regulatory_saes) if regulatory_saes else 0,
            "matched_saes": len(matched_saes),
            "unmatched_edc": len(unmatched_edc),
            "unmatched_safety_db": len(unmatched_safety),
            "unmatched_regulatory": len(unmatched_regulatory),
            "total_discrepancies": len(discrepancies),
            "critical_discrepancies": len(critical_discrepancies),
            "major_discrepancies": len(major_discrepancies),
            "reconciliation_rate": round(len(matched_saes) / max(len(edc_saes), len(safety_db_saes)) * 100, 1)
        }
        
        return {
            "matched_saes": matched_saes,
            "discrepancies": discrepancies,
            "unmatched_edc": unmatched_edc,
            "unmatched_safety_db": unmatched_safety,
            "unmatched_regulatory": unmatched_regulatory,
            "summary": summary,
            "recommendations": recommendations
        }
        
    except Exception as e:
        return {
            "error": f"Error during SAE reconciliation: {str(e)}",
            "matched_saes": [],
            "discrepancies": [],
            "unmatched_edc": [],
            "unmatched_safety_db": [],
            "unmatched_regulatory": [],
            "summary": {},
            "recommendations": []
        }


def calculate_match_score(sae1: Dict, sae2: Dict, date_tolerance: int, 
                         term_threshold: float, exact_subject: bool) -> float:
    """Calculate similarity score between two SAEs."""
    score = 0.0
    weights = {
        "subject_id": 0.3,
        "event_term": 0.3,
        "onset_date": 0.25,
        "severity": 0.15
    }
    
    if exact_subject:
        if sae1.get("subject_id") == sae2.get("subject_id"):
            score += weights["subject_id"]
    else:
        if similar_subject_id(sae1.get("subject_id", ""), sae2.get("subject_id", "")):
            score += weights["subject_id"]
    
    term1 = sae1.get("event_term", "").lower()
    term2 = sae2.get("event_term", "").lower()
    term_similarity = difflib.SequenceMatcher(None, term1, term2).ratio()
    if term_similarity >= term_threshold:
        score += weights["event_term"] * term_similarity
    
    if sae1.get("onset_date") and sae2.get("onset_date"):
        try:
            date1 = datetime.strptime(sae1["onset_date"], "%Y-%m-%d")
            date2 = datetime.strptime(sae2["onset_date"], "%Y-%m-%d")
            days_diff = abs((date1 - date2).days)
            if days_diff <= date_tolerance:
                date_score = 1.0 - (days_diff / date_tolerance) * 0.5
                score += weights["onset_date"] * date_score
        except:
            pass
    
    if sae1.get("severity") == sae2.get("severity"):
        score += weights["severity"]
    
    return score


def similar_subject_id(id1: str, id2: str) -> bool:
    """Check if subject IDs are similar (handles minor variations)."""
    id1 = str(id1).strip().upper()
    id2 = str(id2).strip().upper()
    
    if id1 == id2:
        return True
    
    id1_clean = id1.replace("-", "").replace("_", "")
    id2_clean = id2.replace("-", "").replace("_", "")
    
    return id1_clean == id2_clean


def find_field_discrepancies(sae1: Dict, sae2: Dict) -> List[Dict]:
    """Find discrepancies between matching SAEs."""
    discrepancies = []
    fields_to_check = [
        ("severity", "Severity"),
        ("outcome", "Outcome"),
        ("causality", "Causality"),
        ("onset_date", "Onset Date"),
        ("resolution_date", "Resolution Date")
    ]
    
    for field, label in fields_to_check:
        val1 = sae1.get(field)
        val2 = sae2.get(field)
        
        if val1 and val2 and val1 != val2:
            discrepancies.append({
                "field": label,
                "edc_value": val1,
                "safety_db_value": val2
            })
    
    return discrepancies


def classify_discrepancy_severity(field: str) -> str:
    """Classify the severity of a discrepancy."""
    critical_fields = ["Outcome", "Causality"]
    major_fields = ["Severity", "Onset Date"]
    
    if field in critical_fields:
        return "critical"
    elif field in major_fields:
        return "major"
    else:
        return "minor"


def find_regulatory_match(sae: Dict, regulatory_saes: List[Dict], 
                         matched_indices: set, date_tolerance: int,
                         term_threshold: float, exact_subject: bool) -> Optional[Dict]:
    """Find matching SAE in regulatory reports."""
    best_match = None
    best_score = 0
    best_idx = -1
    
    for i, reg_sae in enumerate(regulatory_saes):
        if i in matched_indices:
            continue
        
        score = calculate_match_score(
            sae, reg_sae, date_tolerance, term_threshold, exact_subject
        )
        
        if score > best_score and score >= 0.7:
            best_score = score
            best_match = reg_sae
            best_idx = i
    
    if best_match:
        return {"sae": best_match, "index": best_idx, "score": best_score}
    
    return None