from typing import Dict, List, Optional, Any
import math
from collections import defaultdict


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identifies potential safety signals using statistical methods.
    
    Args:
        input_data: Dictionary containing:
            - adverse_events: List of AE dictionaries with:
                - event_term: Adverse event term
                - treatment_group: Treatment group (e.g., "drug", "placebo")
                - subject_id: Subject identifier
                - severity: Optional severity grade
                - serious: Optional boolean for SAE
            - total_subjects: Dictionary with group sizes:
                - drug: Number of subjects in drug group
                - placebo: Number of subjects in placebo group
            - signal_threshold: Optional RR threshold (default: 2.0)
            - min_cases: Minimum cases for signal (default: 3)
            - methods: List of detection methods (default: ["RR", "PRR"])
    
    Returns:
        Dictionary containing:
            - signals: List of detected safety signals
            - statistics: Statistical measures for each AE
            - high_priority_signals: Signals requiring immediate attention
            - summary: Analysis summary
            - recommendations: Recommended actions
    """
    try:
        adverse_events = input_data.get("adverse_events", [])
        total_subjects = input_data.get("total_subjects", {})
        
        if not adverse_events or not total_subjects:
            return {
                "error": "Missing adverse events or subject counts",
                "signals": [],
                "statistics": [],
                "high_priority_signals": [],
                "summary": {},
                "recommendations": []
            }
        
        signal_threshold = input_data.get("signal_threshold", 2.0)
        min_cases = input_data.get("min_cases", 3)
        methods = input_data.get("methods", ["RR", "PRR"])
        
        # Count events by term and group
        event_counts = defaultdict(lambda: {"drug": 0, "placebo": 0})
        serious_counts = defaultdict(lambda: {"drug": 0, "placebo": 0})
        subject_events = defaultdict(lambda: {"drug": set(), "placebo": set()})
        
        for ae in adverse_events:
            term = ae.get("event_term", "")
            group = ae.get("treatment_group", "")
            subject = ae.get("subject_id", "")
            
            if term and group in ["drug", "placebo"]:
                event_counts[term][group] += 1
                subject_events[term][group].add(subject)
                
                if ae.get("serious", False):
                    serious_counts[term][group] += 1
        
        signals = []
        statistics = []
        high_priority_signals = []
        
        drug_total = total_subjects.get("drug", 1)
        placebo_total = total_subjects.get("placebo", 1)
        
        for term, counts in event_counts.items():
            drug_count = counts["drug"]
            placebo_count = counts["placebo"]
            
            # Skip if below minimum case threshold
            if drug_count < min_cases:
                continue
            
            # Calculate incidence rates
            drug_rate = drug_count / drug_total
            placebo_rate = placebo_count / placebo_total if placebo_count > 0 else 0.001
            
            # Relative Risk (RR)
            rr = drug_rate / placebo_rate if placebo_rate > 0 else float('inf')
            
            # Calculate 95% CI for RR
            if drug_count > 0 and placebo_count > 0:
                ln_rr = math.log(rr)
                se_ln_rr = math.sqrt(1/drug_count - 1/drug_total + 1/placebo_count - 1/placebo_total)
                ci_lower = math.exp(ln_rr - 1.96 * se_ln_rr)
                ci_upper = math.exp(ln_rr + 1.96 * se_ln_rr)
            else:
                ci_lower = 0
                ci_upper = float('inf')
            
            # Proportional Reporting Ratio (PRR) if requested
            prr = None
            if "PRR" in methods:
                total_drug_events = sum(c["drug"] for c in event_counts.values())
                total_placebo_events = sum(c["placebo"] for c in event_counts.values())
                
                if total_drug_events > 0 and total_placebo_events > 0:
                    prr = (drug_count / total_drug_events) / (placebo_count / total_placebo_events) if placebo_count > 0 else float('inf')
            
            stat_entry = {
                "event_term": term,
                "drug_cases": drug_count,
                "placebo_cases": placebo_count,
                "drug_rate": round(drug_rate * 100, 2),
                "placebo_rate": round(placebo_rate * 100, 2),
                "relative_risk": round(rr, 2),
                "rr_ci_lower": round(ci_lower, 2),
                "rr_ci_upper": round(ci_upper, 2),
                "serious_drug": serious_counts[term]["drug"],
                "serious_placebo": serious_counts[term]["placebo"]
            }
            
            if prr is not None:
                stat_entry["prr"] = round(prr, 2)
            
            statistics.append(stat_entry)
            
            # Determine if signal
            is_signal = False
            signal_entry = {
                "event_term": term,
                "signal_strength": "none",
                "criteria_met": []
            }
            
            if rr >= signal_threshold and ci_lower > 1.0:
                is_signal = True
                signal_entry["signal_strength"] = "strong" if rr >= 3.0 else "moderate"
                signal_entry["criteria_met"].append(f"RR={round(rr, 2)} (CI: {round(ci_lower, 2)}-{round(ci_upper, 2)})")
            
            if prr and prr >= signal_threshold:
                is_signal = True
                signal_entry["criteria_met"].append(f"PRR={round(prr, 2)}")
            
            if is_signal:
                signal_entry.update(stat_entry)
                signals.append(signal_entry)
                
                # High priority if serious events or very high RR
                if serious_counts[term]["drug"] > 0 or rr >= 5.0:
                    high_priority_signals.append(signal_entry)
        
        # Generate recommendations
        recommendations = []
        
        if high_priority_signals:
            recommendations.append({
                "priority": "URGENT",
                "action": f"Review {len(high_priority_signals)} high-priority safety signals",
                "details": "Signals involve serious events or very high relative risks"
            })
        
        if signals:
            recommendations.append({
                "priority": "HIGH",
                "action": f"Investigate {len(signals)} potential safety signals",
                "details": "Conduct medical review and consider regulatory reporting"
            })
        
        # Summary
        summary = {
            "total_events_analyzed": len(event_counts),
            "signals_detected": len(signals),
            "high_priority_signals": len(high_priority_signals),
            "strongest_signal": max(signals, key=lambda x: x.get("relative_risk", 0))["event_term"] if signals else None,
            "analysis_methods": methods,
            "signal_threshold": signal_threshold
        }
        
        return {
            "signals": signals,
            "statistics": statistics,
            "high_priority_signals": high_priority_signals,
            "summary": summary,
            "recommendations": recommendations
        }
        
    except Exception as e:
        return {
            "error": f"Error detecting safety signals: {str(e)}",
            "signals": [],
            "statistics": [],
            "high_priority_signals": [],
            "summary": {},
            "recommendations": []
        }