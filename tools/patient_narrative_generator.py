from typing import Dict, List, Optional, Any
from datetime import datetime


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates patient narratives for Clinical Study Reports (CSR).
    
    Args:
        input_data: Dictionary containing:
            - patient_data: Dictionary with patient information:
                - subject_id: Subject identifier
                - age: Age at enrollment
                - sex: Patient sex
                - medical_history: List of relevant conditions
                - enrollment_date: Study enrollment date
                - treatment_group: Assigned treatment
                - completion_status: Study completion status
            - adverse_events: List of AEs for this patient
            - concomitant_meds: List of concomitant medications
            - study_drug_exposure: Drug exposure information
            - key_dates: Important study dates
            - narrative_type: Type of narrative ("sae", "death", "discontinuation")
            - include_sections: Optional list of sections to include
    
    Returns:
        Dictionary containing:
            - narrative: Generated narrative text
            - sections: Individual narrative sections
            - word_count: Total word count
            - key_points: List of key points included
            - metadata: Narrative metadata
    """
    try:
        patient_data = input_data.get("patient_data", {})
        if not patient_data:
            return {
                "error": "No patient data provided",
                "narrative": "",
                "sections": {},
                "word_count": 0,
                "key_points": [],
                "metadata": {}
            }
        
        adverse_events = input_data.get("adverse_events", [])
        concomitant_meds = input_data.get("concomitant_meds", [])
        study_drug_exposure = input_data.get("study_drug_exposure", {})
        key_dates = input_data.get("key_dates", {})
        narrative_type = input_data.get("narrative_type", "standard")
        include_sections = input_data.get("include_sections", 
            ["demographics", "medical_history", "study_treatment", "adverse_events", "outcome"])
        
        sections = {}
        key_points = []
        
        # Demographics section
        if "demographics" in include_sections:
            demographics = generate_demographics_section(patient_data)
            sections["demographics"] = demographics
            key_points.append(f"Patient {patient_data.get('subject_id')}: {patient_data.get('age')}yo {patient_data.get('sex')}")
        
        # Medical history section
        if "medical_history" in include_sections and patient_data.get("medical_history"):
            med_history = generate_medical_history_section(patient_data)
            sections["medical_history"] = med_history
            key_points.append(f"Medical history: {len(patient_data.get('medical_history', []))} conditions")
        
        # Study treatment section
        if "study_treatment" in include_sections:
            treatment = generate_treatment_section(patient_data, study_drug_exposure)
            sections["study_treatment"] = treatment
            key_points.append(f"Treatment group: {patient_data.get('treatment_group')}")
        
        # Adverse events section
        if "adverse_events" in include_sections and adverse_events:
            ae_section = generate_adverse_events_section(adverse_events, narrative_type)
            sections["adverse_events"] = ae_section
            
            serious_aes = [ae for ae in adverse_events if ae.get("serious", False)]
            if serious_aes:
                key_points.append(f"Experienced {len(serious_aes)} SAE(s)")
            else:
                key_points.append(f"Experienced {len(adverse_events)} AE(s)")
        
        # Concomitant medications section
        if "concomitant_meds" in include_sections and concomitant_meds:
            meds_section = generate_conmeds_section(concomitant_meds)
            sections["concomitant_meds"] = meds_section
            key_points.append(f"Concomitant medications: {len(concomitant_meds)}")
        
        # Outcome section
        if "outcome" in include_sections:
            outcome = generate_outcome_section(patient_data, adverse_events)
            sections["outcome"] = outcome
            key_points.append(f"Status: {patient_data.get('completion_status')}")
        
        # Combine sections into full narrative
        narrative_parts = []
        
        # Add header for specific narrative types
        if narrative_type == "sae":
            narrative_parts.append(f"SERIOUS ADVERSE EVENT NARRATIVE\nSubject: {patient_data.get('subject_id')}\n")
        elif narrative_type == "death":
            narrative_parts.append(f"DEATH NARRATIVE\nSubject: {patient_data.get('subject_id')}\n")
        elif narrative_type == "discontinuation":
            narrative_parts.append(f"DISCONTINUATION NARRATIVE\nSubject: {patient_data.get('subject_id')}\n")
        
        # Add sections in logical order
        section_order = ["demographics", "medical_history", "study_treatment", 
                        "adverse_events", "concomitant_meds", "outcome"]
        
        for section_name in section_order:
            if section_name in sections:
                narrative_parts.append(sections[section_name])
        
        narrative = "\n\n".join(narrative_parts)
        word_count = len(narrative.split())
        
        # Generate metadata
        metadata = {
            "generated_date": datetime.now().strftime("%Y-%m-%d"),
            "narrative_type": narrative_type,
            "subject_id": patient_data.get("subject_id"),
            "sections_included": list(sections.keys()),
            "version": "1.0"
        }
        
        return {
            "narrative": narrative,
            "sections": sections,
            "word_count": word_count,
            "key_points": key_points,
            "metadata": metadata
        }
        
    except Exception as e:
        return {
            "error": f"Error generating narrative: {str(e)}",
            "narrative": "",
            "sections": {},
            "word_count": 0,
            "key_points": [],
            "metadata": {}
        }


def generate_demographics_section(patient_data: Dict) -> str:
    """Generate demographics narrative section."""
    age = patient_data.get("age", "unknown")
    sex = patient_data.get("sex", "unknown")
    race = patient_data.get("race", "")
    enrollment_date = patient_data.get("enrollment_date", "")
    
    narrative = f"Subject {patient_data.get('subject_id')} is a {age}-year-old {sex}"
    if race:
        narrative += f" {race}"
    narrative += " patient"
    
    if enrollment_date:
        narrative += f" who was enrolled in the study on {enrollment_date}"
    
    narrative += "."
    return narrative


def generate_medical_history_section(patient_data: Dict) -> str:
    """Generate medical history narrative section."""
    history = patient_data.get("medical_history", [])
    
    if not history:
        return "The patient had no significant medical history."
    
    if len(history) == 1:
        return f"The patient's medical history was significant for {history[0]}."
    
    narrative = "The patient's medical history was significant for "
    if len(history) == 2:
        narrative += f"{history[0]} and {history[1]}."
    else:
        narrative += ", ".join(history[:-1]) + f", and {history[-1]}."
    
    return narrative


def generate_treatment_section(patient_data: Dict, study_drug_exposure: Dict) -> str:
    """Generate study treatment narrative section."""
    treatment_group = patient_data.get("treatment_group", "study treatment")
    
    narrative = f"The patient was randomized to receive {treatment_group}"
    
    if study_drug_exposure:
        start_date = study_drug_exposure.get("start_date")
        end_date = study_drug_exposure.get("end_date")
        total_dose = study_drug_exposure.get("total_dose")
        duration_days = study_drug_exposure.get("duration_days")
        
        if start_date:
            narrative += f" starting on {start_date}"
        
        if duration_days:
            narrative += f" for a total of {duration_days} days"
        
        if total_dose:
            narrative += f" with a cumulative dose of {total_dose}"
        
        if end_date:
            narrative += f". Treatment was discontinued on {end_date}"
    
    narrative += "."
    return narrative


def generate_adverse_events_section(adverse_events: List[Dict], narrative_type: str) -> str:
    """Generate adverse events narrative section."""
    if not adverse_events:
        return "The patient experienced no adverse events during the study."
    
    serious_aes = [ae for ae in adverse_events if ae.get("serious", False)]
    
    if narrative_type == "sae" and serious_aes:
        # Focus on SAEs for SAE narrative
        narrative_parts = []
        for sae in serious_aes:
            sae_text = f"On {sae.get('onset_date', 'unknown date')}, the patient experienced "
            sae_text += f"{sae.get('event_term', 'an adverse event')}"
            
            if sae.get('severity'):
                sae_text += f" ({sae['severity']})"
            
            if sae.get('causality'):
                sae_text += f", assessed as {sae['causality']} to study drug"
            
            if sae.get('outcome'):
                sae_text += f". The event {sae['outcome'].lower()}"
            
            if sae.get('action_taken'):
                sae_text += f". {sae['action_taken']}"
            
            sae_text += "."
            narrative_parts.append(sae_text)
        
        return " ".join(narrative_parts)
    
    # Standard AE narrative
    narrative = f"During the study, the patient experienced {len(adverse_events)} adverse event(s)"
    
    if serious_aes:
        narrative += f", including {len(serious_aes)} serious adverse event(s)"
    
    # List main events
    event_terms = [ae.get('event_term', 'unknown') for ae in adverse_events[:3]]
    if len(adverse_events) <= 3:
        narrative += ": " + ", ".join(event_terms)
    else:
        narrative += " including " + ", ".join(event_terms) + ", among others"
    
    narrative += "."
    return narrative


def generate_conmeds_section(concomitant_meds: List[Dict]) -> str:
    """Generate concomitant medications narrative section."""
    if not concomitant_meds:
        return "The patient received no concomitant medications."
    
    narrative = f"The patient received {len(concomitant_meds)} concomitant medication(s) including "
    
    med_names = [med.get('drug_name', 'unknown') for med in concomitant_meds[:3]]
    
    if len(concomitant_meds) <= 3:
        narrative += ", ".join(med_names)
    else:
        narrative += ", ".join(med_names) + ", among others"
    
    narrative += "."
    return narrative


def generate_outcome_section(patient_data: Dict, adverse_events: List[Dict]) -> str:
    """Generate outcome narrative section."""
    completion_status = patient_data.get("completion_status", "unknown")
    
    if completion_status.lower() == "completed":
        narrative = "The patient completed the study as per protocol."
    elif completion_status.lower() == "discontinued":
        reason = patient_data.get("discontinuation_reason", "unspecified reasons")
        narrative = f"The patient discontinued from the study due to {reason}."
    elif completion_status.lower() == "death":
        narrative = "The patient died during the study."
        death_ae = next((ae for ae in adverse_events if "death" in ae.get("outcome", "").lower()), None)
        if death_ae:
            narrative += f" The cause of death was {death_ae.get('event_term', 'unspecified')}."
    else:
        narrative = f"The patient's study status was {completion_status}."
    
    return narrative