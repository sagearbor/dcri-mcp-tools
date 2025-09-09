from typing import Dict, List, Optional, Any
from datetime import datetime


# CTCAE v5.0 Lab Value Ranges
LAB_REFERENCE_RANGES = {
    "hemoglobin": {
        "unit": "g/dL",
        "normal_range": {"male": (13.5, 17.5), "female": (12.0, 15.5)},
        "grades": {
            1: (10.0, "LLN"),  # LLN = Lower Limit of Normal
            2: (8.0, 10.0),
            3: (6.5, 8.0),
            4: ("<", 6.5)
        }
    },
    "platelet_count": {
        "unit": "x10^9/L",
        "normal_range": {"all": (150, 400)},
        "grades": {
            1: (75, 150),
            2: (50, 75),
            3: (25, 50),
            4: ("<", 25)
        }
    },
    "neutrophil_count": {
        "unit": "x10^9/L",
        "normal_range": {"all": (2.0, 7.5)},
        "grades": {
            1: (1.5, 2.0),
            2: (1.0, 1.5),
            3: (0.5, 1.0),
            4: ("<", 0.5)
        }
    },
    "alt": {
        "unit": "U/L",
        "normal_range": {"all": (7, 56)},
        "grades": {
            1: ("ULN", 3.0),  # ULN = Upper Limit of Normal
            2: (3.0, 5.0),
            3: (5.0, 20.0),
            4: (">", 20.0)
        },
        "multiplier": "ULN"
    },
    "ast": {
        "unit": "U/L",
        "normal_range": {"all": (10, 40)},
        "grades": {
            1: ("ULN", 3.0),
            2: (3.0, 5.0),
            3: (5.0, 20.0),
            4: (">", 20.0)
        },
        "multiplier": "ULN"
    },
    "total_bilirubin": {
        "unit": "mg/dL",
        "normal_range": {"all": (0.3, 1.2)},
        "grades": {
            1: ("ULN", 1.5),
            2: (1.5, 3.0),
            3: (3.0, 10.0),
            4: (">", 10.0)
        },
        "multiplier": "ULN"
    },
    "creatinine": {
        "unit": "mg/dL",
        "normal_range": {"male": (0.7, 1.3), "female": (0.6, 1.1)},
        "grades": {
            1: ("ULN", 1.5),
            2: (1.5, 3.0),
            3: (3.0, 6.0),
            4: (">", 6.0)
        },
        "multiplier": "ULN"
    },
    "potassium": {
        "unit": "mmol/L",
        "normal_range": {"all": (3.5, 5.0)},
        "grades_high": {
            1: (5.5, 6.0),
            2: (6.0, 6.5),
            3: (6.5, 7.0),
            4: (">", 7.0)
        },
        "grades_low": {
            1: (3.0, 3.5),
            2: (2.5, 3.0),
            3: (2.0, 2.5),
            4: ("<", 2.0)
        }
    },
    "sodium": {
        "unit": "mmol/L",
        "normal_range": {"all": (136, 145)},
        "grades_high": {
            1: (146, 150),
            2: (151, 155),
            3: (156, 160),
            4: (">", 160)
        },
        "grades_low": {
            1: (130, 135),
            2: (125, 129),
            3: (120, 124),
            4: ("<", 120)
        }
    }
}


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flags critical lab values and generates alerts based on CTCAE criteria.
    
    Args:
        input_data: Dictionary containing:
            - lab_results: List of lab result dictionaries with:
                - subject_id: Subject identifier
                - lab_test: Test name (e.g., "hemoglobin", "alt")
                - value: Numeric result value
                - unit: Unit of measurement
                - date: Collection date (YYYY-MM-DD)
                - sex: Patient sex (for sex-specific ranges)
                - baseline_value: Optional baseline value
            - alert_threshold: Grade threshold for alerts (default: 3)
            - include_trends: Flag to analyze trends (default: True)
            - hy_law_check: Check for Hy's Law (default: True)
    
    Returns:
        Dictionary containing:
            - alerts: List of critical lab alerts
            - graded_results: All results with CTCAE grades
            - trends: Trend analysis if requested
            - hy_law_cases: Potential Hy's Law cases
            - summary: Alert summary statistics
            - recommendations: Clinical recommendations
    """
    try:
        lab_results = input_data.get("lab_results", [])
        if not lab_results:
            return {
                "error": "No lab results provided",
                "alerts": [],
                "graded_results": [],
                "trends": [],
                "hy_law_cases": [],
                "summary": {},
                "recommendations": []
            }
        
        alert_threshold = input_data.get("alert_threshold", 3)
        include_trends = input_data.get("include_trends", True)
        hy_law_check = input_data.get("hy_law_check", True)
        
        alerts = []
        graded_results = []
        subject_labs = {}
        
        for result in lab_results:
            lab_test = result.get("lab_test", "").lower().replace(" ", "_")
            value = result.get("value")
            subject_id = result.get("subject_id")
            date = result.get("date")
            sex = result.get("sex", "all").lower()
            
            if not lab_test or value is None:
                continue
            
            # Store for trend analysis
            if subject_id not in subject_labs:
                subject_labs[subject_id] = {}
            if lab_test not in subject_labs[subject_id]:
                subject_labs[subject_id][lab_test] = []
            subject_labs[subject_id][lab_test].append({
                "value": value,
                "date": date
            })
            
            # Grade the result
            grade_info = grade_lab_value(lab_test, value, sex)
            
            if grade_info:
                graded_result = {
                    "subject_id": subject_id,
                    "lab_test": result.get("lab_test"),
                    "value": value,
                    "unit": result.get("unit"),
                    "date": date,
                    "grade": grade_info["grade"],
                    "severity": grade_info["severity"],
                    "direction": grade_info.get("direction", "abnormal")
                }
                
                graded_results.append(graded_result)
                
                # Generate alert if above threshold
                if grade_info["grade"] >= alert_threshold:
                    alert = {
                        "alert_level": "CRITICAL" if grade_info["grade"] == 4 else "HIGH",
                        "subject_id": subject_id,
                        "lab_test": result.get("lab_test"),
                        "value": value,
                        "unit": result.get("unit"),
                        "grade": grade_info["grade"],
                        "date": date,
                        "message": f"Grade {grade_info['grade']} {grade_info['severity']} {result.get('lab_test')}",
                        "action_required": get_action_for_grade(lab_test, grade_info["grade"])
                    }
                    
                    # Check if change from baseline
                    if result.get("baseline_value"):
                        baseline_grade = grade_lab_value(lab_test, result["baseline_value"], sex)
                        if baseline_grade and baseline_grade["grade"] < grade_info["grade"]:
                            alert["baseline_change"] = True
                            alert["baseline_grade"] = baseline_grade["grade"]
                    
                    alerts.append(alert)
        
        # Trend analysis
        trends = []
        if include_trends:
            trends = analyze_trends(subject_labs)
        
        # Hy's Law check
        hy_law_cases = []
        if hy_law_check:
            hy_law_cases = check_hys_law(graded_results)
        
        # Generate recommendations
        recommendations = generate_recommendations(alerts, hy_law_cases, trends)
        
        # Summary
        summary = {
            "total_results": len(lab_results),
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a["alert_level"] == "CRITICAL"]),
            "subjects_with_alerts": len(set(a["subject_id"] for a in alerts)),
            "grade_distribution": {
                f"grade_{i}": len([r for r in graded_results if r["grade"] == i])
                for i in range(1, 5)
            },
            "hy_law_cases": len(hy_law_cases)
        }
        
        return {
            "alerts": alerts,
            "graded_results": graded_results,
            "trends": trends,
            "hy_law_cases": hy_law_cases,
            "summary": summary,
            "recommendations": recommendations
        }
        
    except Exception as e:
        return {
            "error": f"Error processing lab alerts: {str(e)}",
            "alerts": [],
            "graded_results": [],
            "trends": [],
            "hy_law_cases": [],
            "summary": {},
            "recommendations": []
        }


def grade_lab_value(lab_test: str, value: float, sex: str = "all") -> Optional[Dict]:
    """Grade a lab value according to CTCAE criteria."""
    if lab_test not in LAB_REFERENCE_RANGES:
        return None
    
    ref = LAB_REFERENCE_RANGES[lab_test]
    normal_range = ref["normal_range"].get(sex, ref["normal_range"].get("all"))
    
    if not normal_range:
        return None
    
    # Check if value is normal
    if normal_range[0] <= value <= normal_range[1]:
        return {"grade": 0, "severity": "normal"}
    
    # Handle tests with ULN/LLN multipliers
    if ref.get("multiplier") == "ULN":
        uln = normal_range[1]
        factor = value / uln
        
        for grade in [4, 3, 2, 1]:
            grade_range = ref["grades"][grade]
            if grade_range[0] == ">" and factor > grade_range[1]:
                return {"grade": grade, "severity": get_severity_description(grade), "direction": "high"}
            elif grade_range[0] == "ULN" and factor <= grade_range[1]:
                return {"grade": grade, "severity": get_severity_description(grade), "direction": "high"}
            elif isinstance(grade_range[0], (int, float)) and grade_range[0] <= factor <= grade_range[1]:
                return {"grade": grade, "severity": get_severity_description(grade), "direction": "high"}
    
    # Handle tests with separate high/low grades
    elif "grades_high" in ref and "grades_low" in ref:
        if value > normal_range[1]:
            for grade in [4, 3, 2, 1]:
                grade_range = ref["grades_high"][grade]
                if grade_range[0] == ">" and value > grade_range[1]:
                    return {"grade": grade, "severity": get_severity_description(grade), "direction": "high"}
                elif isinstance(grade_range[0], (int, float)) and grade_range[0] <= value <= grade_range[1]:
                    return {"grade": grade, "severity": get_severity_description(grade), "direction": "high"}
        else:
            for grade in [4, 3, 2, 1]:
                grade_range = ref["grades_low"][grade]
                if grade_range[0] == "<" and value < grade_range[1]:
                    return {"grade": grade, "severity": get_severity_description(grade), "direction": "low"}
                elif isinstance(grade_range[0], (int, float)) and grade_range[0] <= value <= grade_range[1]:
                    return {"grade": grade, "severity": get_severity_description(grade), "direction": "low"}
    
    # Handle standard grade ranges
    else:
        for grade in [4, 3, 2, 1]:
            grade_range = ref["grades"][grade]
            if grade_range[0] == "<" and value < grade_range[1]:
                return {"grade": grade, "severity": get_severity_description(grade), "direction": "low"}
            elif grade_range[0] == "LLN":
                if value < normal_range[0]:
                    return {"grade": grade, "severity": get_severity_description(grade), "direction": "low"}
            elif isinstance(grade_range[0], (int, float)) and grade_range[0] <= value <= grade_range[1]:
                return {"grade": grade, "severity": get_severity_description(grade), "direction": "low"}
    
    return {"grade": 1, "severity": "mild"}


def get_severity_description(grade: int) -> str:
    """Get severity description for grade."""
    descriptions = {
        0: "normal",
        1: "mild",
        2: "moderate",
        3: "severe",
        4: "life-threatening"
    }
    return descriptions.get(grade, "unknown")


def get_action_for_grade(lab_test: str, grade: int) -> str:
    """Get recommended action for lab grade."""
    if grade == 4:
        return "Immediate medical review required. Consider hospitalization."
    elif grade == 3:
        if lab_test in ["neutrophil_count", "platelet_count"]:
            return "Consider dose modification or treatment delay. Monitor closely."
        elif lab_test in ["alt", "ast", "total_bilirubin"]:
            return "Evaluate for drug-induced liver injury. Consider treatment interruption."
        else:
            return "Medical review required within 24 hours."
    elif grade == 2:
        return "Monitor closely. Repeat lab in 3-7 days."
    else:
        return "Continue monitoring per protocol."


def analyze_trends(subject_labs: Dict) -> List[Dict]:
    """Analyze trends in lab values."""
    trends = []
    
    for subject_id, labs in subject_labs.items():
        for lab_test, values in labs.items():
            if len(values) < 2:
                continue
            
            # Sort by date
            sorted_values = sorted(values, key=lambda x: x["date"] or "")
            
            # Calculate trend
            first_value = sorted_values[0]["value"]
            last_value = sorted_values[-1]["value"]
            
            if first_value and last_value:
                change_percent = ((last_value - first_value) / first_value) * 100
                
                if abs(change_percent) > 50:
                    trends.append({
                        "subject_id": subject_id,
                        "lab_test": lab_test,
                        "trend": "increasing" if change_percent > 0 else "decreasing",
                        "change_percent": round(change_percent, 1),
                        "first_value": first_value,
                        "last_value": last_value,
                        "num_measurements": len(values)
                    })
    
    return trends


def check_hys_law(graded_results: List[Dict]) -> List[Dict]:
    """Check for potential Hy's Law cases."""
    hy_law_cases = []
    subject_liver_labs = {}
    
    for result in graded_results:
        subject_id = result["subject_id"]
        lab_test = result["lab_test"].lower() if result["lab_test"] else ""
        
        if subject_id not in subject_liver_labs:
            subject_liver_labs[subject_id] = {}
        
        if "alt" in lab_test or "ast" in lab_test:
            subject_liver_labs[subject_id]["transaminase"] = max(
                subject_liver_labs[subject_id].get("transaminase", 0),
                result["grade"]
            )
        elif "bilirubin" in lab_test and "total" in lab_test:
            subject_liver_labs[subject_id]["bilirubin"] = max(
                subject_liver_labs[subject_id].get("bilirubin", 0),
                result["grade"]
            )
    
    # Hy's Law: ALT/AST >3x ULN + Total Bilirubin >2x ULN
    for subject_id, labs in subject_liver_labs.items():
        if labs.get("transaminase", 0) >= 2 and labs.get("bilirubin", 0) >= 2:
            hy_law_cases.append({
                "subject_id": subject_id,
                "criteria_met": "Hy's Law criteria met",
                "transaminase_grade": labs["transaminase"],
                "bilirubin_grade": labs["bilirubin"],
                "recommendation": "Urgent hepatology consultation required"
            })
    
    return hy_law_cases


def generate_recommendations(alerts: List[Dict], hy_law_cases: List[Dict], 
                            trends: List[Dict]) -> List[Dict]:
    """Generate clinical recommendations based on alerts."""
    recommendations = []
    
    if hy_law_cases:
        recommendations.append({
            "priority": "URGENT",
            "type": "Hy's Law",
            "action": f"Evaluate {len(hy_law_cases)} potential Hy's Law case(s)",
            "details": "Immediate hepatology consultation and treatment discontinuation required"
        })
    
    critical_alerts = [a for a in alerts if a["alert_level"] == "CRITICAL"]
    if critical_alerts:
        recommendations.append({
            "priority": "CRITICAL",
            "type": "Lab Alert",
            "action": f"Review {len(critical_alerts)} critical lab value(s)",
            "details": "Immediate medical review and intervention required"
        })
    
    concerning_trends = [t for t in trends if abs(t["change_percent"]) > 100]
    if concerning_trends:
        recommendations.append({
            "priority": "HIGH",
            "type": "Trend Alert",
            "action": f"Review {len(concerning_trends)} concerning lab trend(s)",
            "details": "Significant changes detected requiring clinical evaluation"
        })
    
    return recommendations