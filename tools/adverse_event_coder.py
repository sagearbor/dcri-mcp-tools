from typing import Dict, List, Optional, Any
import re
from datetime import datetime
import difflib


MEDDRA_TERMS = {
    "headache": {
        "pt": "Headache",
        "llt": ["Headache", "Head pain", "Cephalgia"],
        "soc": "Nervous system disorders",
        "hlgt": "Headaches",
        "hlt": "Headaches NEC",
        "code": "10019211"
    },
    "nausea": {
        "pt": "Nausea",
        "llt": ["Nausea", "Feeling sick", "Queasiness"],
        "soc": "Gastrointestinal disorders",
        "hlgt": "Nausea and vomiting symptoms",
        "hlt": "Nausea and vomiting symptoms",
        "code": "10028813"
    },
    "vomiting": {
        "pt": "Vomiting",
        "llt": ["Vomiting", "Emesis", "Throwing up"],
        "soc": "Gastrointestinal disorders",
        "hlgt": "Nausea and vomiting symptoms",
        "hlt": "Vomiting symptoms",
        "code": "10047700"
    },
    "dizziness": {
        "pt": "Dizziness",
        "llt": ["Dizziness", "Dizzy", "Feeling dizzy", "Lightheadedness", "Giddiness"],
        "soc": "Nervous system disorders",
        "hlgt": "Neurological signs and symptoms NEC",
        "hlt": "Dizziness and giddiness",
        "code": "10013573"
    },
    "fatigue": {
        "pt": "Fatigue",
        "llt": ["Fatigue", "Tiredness", "Weariness", "Exhaustion"],
        "soc": "General disorders and administration site conditions",
        "hlgt": "General system disorders NEC",
        "hlt": "Asthenic conditions",
        "code": "10016256"
    },
    "fever": {
        "pt": "Pyrexia",
        "llt": ["Fever", "Pyrexia", "Febrile", "High temperature"],
        "soc": "General disorders and administration site conditions",
        "hlgt": "Body temperature conditions",
        "hlt": "Febrile disorders",
        "code": "10037660"
    },
    "rash": {
        "pt": "Rash",
        "llt": ["Rash", "Skin rash", "Eruption"],
        "soc": "Skin and subcutaneous tissue disorders",
        "hlgt": "Epidermal and dermal conditions",
        "hlt": "Rashes, eruptions and exanthems NEC",
        "code": "10037844"
    },
    "diarrhea": {
        "pt": "Diarrhoea",
        "llt": ["Diarrhea", "Diarrhoea", "Loose stools"],
        "soc": "Gastrointestinal disorders",
        "hlgt": "Gastrointestinal motility and defaecation conditions",
        "hlt": "Diarrhoea (excl infective)",
        "code": "10012735"
    },
    "cough": {
        "pt": "Cough",
        "llt": ["Cough", "Coughing", "Tussis"],
        "soc": "Respiratory, thoracic and mediastinal disorders",
        "hlgt": "Respiratory signs and symptoms",
        "hlt": "Coughing and associated symptoms",
        "code": "10011224"
    },
    "pain": {
        "pt": "Pain",
        "llt": ["Pain", "Ache", "Discomfort"],
        "soc": "General disorders and administration site conditions",
        "hlgt": "General system disorders NEC",
        "hlt": "Pain and discomfort NEC",
        "code": "10033371"
    },
    "hypertension": {
        "pt": "Hypertension",
        "llt": ["Hypertension", "High blood pressure", "Blood pressure increased"],
        "soc": "Vascular disorders",
        "hlgt": "Vascular hypertensive disorders",
        "hlt": "Vascular hypertensive disorders NEC",
        "code": "10020772"
    },
    "hypotension": {
        "pt": "Hypotension",
        "llt": ["Hypotension", "Low blood pressure", "Blood pressure decreased"],
        "soc": "Vascular disorders",
        "hlgt": "Vascular hypotensive disorders",
        "hlt": "Hypotension NEC",
        "code": "10021097"
    }
}


SEVERITY_GRADES = {
    "mild": {
        "grade": 1,
        "description": "Mild; asymptomatic or mild symptoms; clinical or diagnostic observations only",
        "keywords": ["mild", "slight", "minimal", "minor", "tolerable"]
    },
    "moderate": {
        "grade": 2,
        "description": "Moderate; minimal, local or noninvasive intervention indicated",
        "keywords": ["moderate", "medium", "intermediate", "noticeable"]
    },
    "severe": {
        "grade": 3,
        "description": "Severe or medically significant but not immediately life-threatening",
        "keywords": ["severe", "serious", "significant", "major", "intense"]
    },
    "life-threatening": {
        "grade": 4,
        "description": "Life-threatening consequences; urgent intervention indicated",
        "keywords": ["life-threatening", "critical", "emergency", "urgent"]
    },
    "death": {
        "grade": 5,
        "description": "Death related to AE",
        "keywords": ["death", "fatal", "deceased", "mortality"]
    }
}


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Auto-codes adverse events to MedDRA terms and assigns severity grades.
    
    Args:
        input_data: Dictionary containing:
            - events: List of adverse event dictionaries with:
                - verbatim_term: The verbatim AE term reported
                - severity_description: Optional severity description
                - start_date: Optional start date (YYYY-MM-DD)
                - end_date: Optional end date (YYYY-MM-DD)
                - outcome: Optional outcome
                - subject_id: Optional subject identifier
            - coding_version: Optional MedDRA version (default: "24.0")
            - match_threshold: Optional similarity threshold (0-1, default: 0.7)
    
    Returns:
        Dictionary containing:
            - coded_events: List of coded adverse events
            - summary: Coding summary statistics
            - uncoded_terms: List of terms that couldn't be coded
            - warnings: Any warnings or issues
    """
    try:
        events = input_data.get("events", [])
        if not events:
            return {
                "error": "No adverse events provided",
                "coded_events": [],
                "summary": {},
                "uncoded_terms": [],
                "warnings": []
            }
        
        coding_version = input_data.get("coding_version", "24.0")
        match_threshold = input_data.get("match_threshold", 0.7)
        
        coded_events = []
        uncoded_terms = []
        warnings = []
        soc_counts = {}
        severity_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for event in events:
            verbatim_term = event.get("verbatim_term", "").lower().strip()
            if not verbatim_term:
                warnings.append(f"Empty verbatim term for event: {event}")
                continue
            
            coded_event = {
                "subject_id": event.get("subject_id"),
                "verbatim_term": event.get("verbatim_term"),
                "start_date": event.get("start_date"),
                "end_date": event.get("end_date"),
                "outcome": event.get("outcome")
            }
            
            meddra_match = find_meddra_term(verbatim_term, match_threshold)
            
            if meddra_match:
                coded_event.update({
                    "preferred_term": meddra_match["pt"],
                    "lower_level_term": meddra_match["llt"][0],
                    "system_organ_class": meddra_match["soc"],
                    "high_level_group_term": meddra_match["hlgt"],
                    "high_level_term": meddra_match["hlt"],
                    "meddra_code": meddra_match["code"],
                    "coding_version": coding_version,
                    "match_confidence": meddra_match.get("confidence", 1.0)
                })
                
                soc = meddra_match["soc"]
                soc_counts[soc] = soc_counts.get(soc, 0) + 1
            else:
                uncoded_terms.append(verbatim_term)
                coded_event.update({
                    "preferred_term": None,
                    "coding_status": "UNCODED",
                    "coding_note": "No matching MedDRA term found"
                })
            
            severity = determine_severity(event.get("severity_description", ""))
            coded_event.update({
                "severity_grade": severity["grade"],
                "severity_description": severity["description"]
            })
            severity_counts[severity["grade"]] += 1
            
            if event.get("start_date") and event.get("end_date"):
                try:
                    start = datetime.strptime(event["start_date"], "%Y-%m-%d")
                    end = datetime.strptime(event["end_date"], "%Y-%m-%d")
                    duration_days = (end - start).days
                    coded_event["duration_days"] = duration_days
                except:
                    pass
            
            coded_events.append(coded_event)
        
        summary = {
            "total_events": len(coded_events),
            "coded_events": len(coded_events) - len(uncoded_terms),
            "uncoded_events": len(uncoded_terms),
            "coding_rate": round((len(coded_events) - len(uncoded_terms)) / len(coded_events) * 100, 1) if coded_events else 0,
            "soc_distribution": soc_counts,
            "severity_distribution": {
                f"grade_{k}": v for k, v in severity_counts.items() if v > 0
            },
            "coding_version": coding_version
        }
        
        if uncoded_terms:
            warnings.append(f"{len(uncoded_terms)} terms could not be automatically coded and require manual review")
        
        return {
            "coded_events": coded_events,
            "summary": summary,
            "uncoded_terms": list(set(uncoded_terms)),
            "warnings": warnings
        }
        
    except Exception as e:
        return {
            "error": f"Error coding adverse events: {str(e)}",
            "coded_events": [],
            "summary": {},
            "uncoded_terms": [],
            "warnings": []
        }


def find_meddra_term(verbatim: str, threshold: float) -> Optional[Dict]:
    """Find best matching MedDRA term for verbatim text."""
    verbatim_lower = verbatim.lower()
    
    for term_key, term_data in MEDDRA_TERMS.items():
        if term_key in verbatim_lower:
            return dict(term_data, confidence=1.0)
        
        for llt in term_data["llt"]:
            if llt.lower() in verbatim_lower or verbatim_lower in llt.lower():
                return dict(term_data, confidence=0.95)
    
    best_match = None
    best_score = 0
    
    for term_key, term_data in MEDDRA_TERMS.items():
        for llt in term_data["llt"]:
            score = difflib.SequenceMatcher(None, verbatim_lower, llt.lower()).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = dict(term_data, confidence=score)
    
    return best_match


def determine_severity(description: str) -> Dict:
    """Determine CTCAE severity grade from description."""
    if not description:
        return {"grade": 1, "description": SEVERITY_GRADES["mild"]["description"]}
    
    description_lower = description.lower()
    
    for severity_key, severity_data in SEVERITY_GRADES.items():
        for keyword in severity_data["keywords"]:
            if keyword in description_lower:
                return {
                    "grade": severity_data["grade"],
                    "description": severity_data["description"]
                }
    
    return {"grade": 1, "description": SEVERITY_GRADES["mild"]["description"]}