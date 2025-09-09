from typing import Dict, List, Optional, Any
import re
import difflib


WHO_DRUG_DICTIONARY = {
    "aspirin": {
        "drug_name": "ASPIRIN",
        "atc_code": "B01AC06",
        "atc_text": "Aspirin",
        "drug_code": "00002701",
        "therapeutic_class": "Antithrombotic agents",
        "anatomical_class": "Blood and blood forming organs",
        "route": ["oral", "rectal"],
        "indications": ["Pain", "Fever", "Antiplatelet"]
    },
    "acetaminophen": {
        "drug_name": "PARACETAMOL",
        "atc_code": "N02BE01",
        "atc_text": "Paracetamol",
        "drug_code": "00003301",
        "therapeutic_class": "Analgesics",
        "anatomical_class": "Nervous system",
        "route": ["oral", "rectal", "intravenous"],
        "indications": ["Pain", "Fever"]
    },
    "paracetamol": {
        "drug_name": "PARACETAMOL",
        "atc_code": "N02BE01",
        "atc_text": "Paracetamol",
        "drug_code": "00003301",
        "therapeutic_class": "Analgesics",
        "anatomical_class": "Nervous system",
        "route": ["oral", "rectal", "intravenous"],
        "indications": ["Pain", "Fever"]
    },
    "ibuprofen": {
        "drug_name": "IBUPROFEN",
        "atc_code": "M01AE01",
        "atc_text": "Ibuprofen",
        "drug_code": "00004201",
        "therapeutic_class": "Anti-inflammatory and antirheumatic products",
        "anatomical_class": "Musculo-skeletal system",
        "route": ["oral", "topical"],
        "indications": ["Pain", "Inflammation", "Fever"]
    },
    "metformin": {
        "drug_name": "METFORMIN",
        "atc_code": "A10BA02",
        "atc_text": "Metformin",
        "drug_code": "00005101",
        "therapeutic_class": "Drugs used in diabetes",
        "anatomical_class": "Alimentary tract and metabolism",
        "route": ["oral"],
        "indications": ["Type 2 diabetes mellitus"]
    },
    "lisinopril": {
        "drug_name": "LISINOPRIL",
        "atc_code": "C09AA03",
        "atc_text": "Lisinopril",
        "drug_code": "00006001",
        "therapeutic_class": "ACE inhibitors",
        "anatomical_class": "Cardiovascular system",
        "route": ["oral"],
        "indications": ["Hypertension", "Heart failure"]
    },
    "atorvastatin": {
        "drug_name": "ATORVASTATIN",
        "atc_code": "C10AA05",
        "atc_text": "Atorvastatin",
        "drug_code": "00007001",
        "therapeutic_class": "Lipid modifying agents",
        "anatomical_class": "Cardiovascular system",
        "route": ["oral"],
        "indications": ["Hyperlipidemia", "Cardiovascular prevention"]
    },
    "omeprazole": {
        "drug_name": "OMEPRAZOLE",
        "atc_code": "A02BC01",
        "atc_text": "Omeprazole",
        "drug_code": "00008001",
        "therapeutic_class": "Proton pump inhibitors",
        "anatomical_class": "Alimentary tract and metabolism",
        "route": ["oral", "intravenous"],
        "indications": ["GERD", "Peptic ulcer", "Dyspepsia"]
    },
    "warfarin": {
        "drug_name": "WARFARIN",
        "atc_code": "B01AA03",
        "atc_text": "Warfarin",
        "drug_code": "00009001",
        "therapeutic_class": "Antithrombotic agents",
        "anatomical_class": "Blood and blood forming organs",
        "route": ["oral"],
        "indications": ["Anticoagulation", "DVT prevention", "Atrial fibrillation"]
    },
    "prednisone": {
        "drug_name": "PREDNISONE",
        "atc_code": "H02AB07",
        "atc_text": "Prednisone",
        "drug_code": "00010001",
        "therapeutic_class": "Corticosteroids for systemic use",
        "anatomical_class": "Systemic hormonal preparations",
        "route": ["oral"],
        "indications": ["Inflammation", "Immunosuppression", "Allergy"]
    },
    "insulin": {
        "drug_name": "INSULIN HUMAN",
        "atc_code": "A10AB01",
        "atc_text": "Insulin (human)",
        "drug_code": "00011001",
        "therapeutic_class": "Insulins and analogues",
        "anatomical_class": "Alimentary tract and metabolism",
        "route": ["subcutaneous", "intravenous"],
        "indications": ["Diabetes mellitus"]
    }
}


BRAND_TO_GENERIC = {
    "tylenol": "acetaminophen",
    "advil": "ibuprofen",
    "motrin": "ibuprofen",
    "glucophage": "metformin",
    "lipitor": "atorvastatin",
    "prilosec": "omeprazole",
    "coumadin": "warfarin",
    "deltasone": "prednisone",
    "panadol": "paracetamol",
    "brufen": "ibuprofen"
}


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maps concomitant medications to WHO Drug Dictionary codes.
    
    Args:
        input_data: Dictionary containing:
            - medications: List of medication dictionaries with:
                - verbatim_name: The verbatim medication name reported
                - dose: Optional dose information
                - unit: Optional dose unit
                - frequency: Optional frequency
                - route: Optional route of administration
                - indication: Optional indication for use
                - start_date: Optional start date (YYYY-MM-DD)
                - stop_date: Optional stop date (YYYY-MM-DD)
                - subject_id: Optional subject identifier
            - coding_version: Optional WHO Drug version (default: "2024Q1")
            - match_threshold: Optional similarity threshold (0-1, default: 0.7)
            - include_interactions: Optional flag to check interactions (default: False)
    
    Returns:
        Dictionary containing:
            - coded_medications: List of coded medications
            - summary: Coding summary statistics
            - uncoded_medications: List of medications that couldn't be coded
            - potential_interactions: List of potential drug interactions (if requested)
            - warnings: Any warnings or issues
    """
    try:
        medications = input_data.get("medications", [])
        if not medications:
            return {
                "error": "No medications provided",
                "coded_medications": [],
                "summary": {},
                "uncoded_medications": [],
                "potential_interactions": [],
                "warnings": []
            }
        
        coding_version = input_data.get("coding_version", "2024Q1")
        match_threshold = input_data.get("match_threshold", 0.7)
        include_interactions = input_data.get("include_interactions", False)
        
        coded_medications = []
        uncoded_medications = []
        warnings = []
        therapeutic_classes = {}
        anatomical_classes = {}
        
        for med in medications:
            verbatim_name = med.get("verbatim_name", "").lower().strip()
            if not verbatim_name:
                warnings.append(f"Empty medication name for entry: {med}")
                continue
            
            coded_med = {
                "subject_id": med.get("subject_id"),
                "verbatim_name": med.get("verbatim_name"),
                "dose": med.get("dose"),
                "unit": med.get("unit"),
                "frequency": med.get("frequency"),
                "route": med.get("route"),
                "indication": med.get("indication"),
                "start_date": med.get("start_date"),
                "stop_date": med.get("stop_date")
            }
            
            who_match = find_who_drug(verbatim_name, match_threshold)
            
            if who_match:
                coded_med.update({
                    "drug_name": who_match["drug_name"],
                    "atc_code": who_match["atc_code"],
                    "atc_text": who_match["atc_text"],
                    "drug_code": who_match["drug_code"],
                    "therapeutic_class": who_match["therapeutic_class"],
                    "anatomical_class": who_match["anatomical_class"],
                    "coding_version": coding_version,
                    "match_confidence": who_match.get("confidence", 1.0)
                })
                
                if med.get("route") and med["route"].lower() not in who_match["route"]:
                    warnings.append(f"Route '{med['route']}' not standard for {who_match['drug_name']}")
                
                tc = who_match["therapeutic_class"]
                therapeutic_classes[tc] = therapeutic_classes.get(tc, 0) + 1
                
                ac = who_match["anatomical_class"]
                anatomical_classes[ac] = anatomical_classes.get(ac, 0) + 1
            else:
                uncoded_medications.append(verbatim_name)
                coded_med.update({
                    "drug_name": None,
                    "coding_status": "UNCODED",
                    "coding_note": "No matching WHO Drug entry found"
                })
            
            if med.get("start_date") and med.get("stop_date"):
                coded_med["ongoing"] = False
            elif med.get("start_date"):
                coded_med["ongoing"] = True
            
            coded_medications.append(coded_med)
        
        potential_interactions = []
        if include_interactions:
            potential_interactions = check_drug_interactions(coded_medications)
        
        summary = {
            "total_medications": len(coded_medications),
            "coded_medications": len(coded_medications) - len(uncoded_medications),
            "uncoded_medications": len(uncoded_medications),
            "coding_rate": round((len(coded_medications) - len(uncoded_medications)) / len(coded_medications) * 100, 1) if coded_medications else 0,
            "therapeutic_class_distribution": therapeutic_classes,
            "anatomical_class_distribution": anatomical_classes,
            "coding_version": coding_version,
            "unique_drugs": len(set(m["drug_name"] for m in coded_medications if m.get("drug_name")))
        }
        
        if uncoded_medications:
            warnings.append(f"{len(uncoded_medications)} medications could not be automatically coded")
        
        return {
            "coded_medications": coded_medications,
            "summary": summary,
            "uncoded_medications": list(set(uncoded_medications)),
            "potential_interactions": potential_interactions,
            "warnings": warnings
        }
        
    except Exception as e:
        return {
            "error": f"Error coding medications: {str(e)}",
            "coded_medications": [],
            "summary": {},
            "uncoded_medications": [],
            "potential_interactions": [],
            "warnings": []
        }


def find_who_drug(verbatim: str, threshold: float) -> Optional[Dict]:
    """Find best matching WHO Drug entry for verbatim text."""
    verbatim_lower = verbatim.lower()
    
    if verbatim_lower in BRAND_TO_GENERIC:
        generic_name = BRAND_TO_GENERIC[verbatim_lower]
        if generic_name in WHO_DRUG_DICTIONARY:
            return dict(WHO_DRUG_DICTIONARY[generic_name], confidence=0.95)
    
    for drug_key, drug_data in WHO_DRUG_DICTIONARY.items():
        if drug_key in verbatim_lower or verbatim_lower in drug_key:
            return dict(drug_data, confidence=1.0)
        
        if drug_data["drug_name"].lower() in verbatim_lower:
            return dict(drug_data, confidence=0.95)
    
    best_match = None
    best_score = 0
    
    for drug_key, drug_data in WHO_DRUG_DICTIONARY.items():
        score = difflib.SequenceMatcher(None, verbatim_lower, drug_key).ratio()
        if score > best_score and score >= threshold:
            best_score = score
            best_match = dict(drug_data, confidence=score)
        
        score = difflib.SequenceMatcher(None, verbatim_lower, drug_data["drug_name"].lower()).ratio()
        if score > best_score and score >= threshold:
            best_score = score
            best_match = dict(drug_data, confidence=score)
    
    return best_match


def check_drug_interactions(coded_medications: List[Dict]) -> List[Dict]:
    """Check for potential drug interactions."""
    interactions = []
    
    interaction_pairs = [
        ("WARFARIN", "ASPIRIN", "Increased bleeding risk"),
        ("WARFARIN", "IBUPROFEN", "Increased bleeding risk"),
        ("METFORMIN", "PREDNISONE", "May affect glucose control"),
        ("LISINOPRIL", "IBUPROFEN", "May reduce antihypertensive effect"),
        ("ATORVASTATIN", "WARFARIN", "May increase INR")
    ]
    
    drug_names = [m.get("drug_name", "") for m in coded_medications if m.get("drug_name")]
    
    for drug1, drug2, interaction_type in interaction_pairs:
        if drug1 in drug_names and drug2 in drug_names:
            interactions.append({
                "drug1": drug1,
                "drug2": drug2,
                "interaction_type": interaction_type,
                "severity": "moderate",
                "recommendation": "Monitor closely"
            })
    
    return interactions