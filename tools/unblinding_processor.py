from typing import Dict, List, Optional, Any
from datetime import datetime


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Manages emergency unblinding requests in clinical trials.
    
    Args:
        input_data: Dictionary containing:
            - request_details: Unblinding request information:
                - subject_id: Subject identifier
                - site_id: Site identifier
                - requestor: Person requesting unblinding
                - requestor_role: Role of requestor
                - request_date: Date of request
                - reason: Reason for unblinding
                - urgency: Urgency level ("emergency", "urgent", "routine")
            - subject_data: Subject information:
                - treatment_assignment: Actual treatment
                - randomization_date: Date randomized
                - current_status: Current study status
            - safety_data: Optional safety information
            - approval_chain: List of required approvals
            - documentation_requirements: Required documentation
    
    Returns:
        Dictionary containing:
            - authorization: Authorization decision and details
            - unblinding_code: Treatment assignment (if authorized)
            - audit_trail: Complete audit trail
            - required_actions: Follow-up actions required
            - regulatory_notifications: Required notifications
            - impact_assessment: Impact on study integrity
    """
    try:
        request_details = input_data.get("request_details", {})
        if not request_details:
            return {
                "error": "No request details provided",
                "authorization": {},
                "unblinding_code": None,
                "audit_trail": [],
                "required_actions": [],
                "regulatory_notifications": [],
                "impact_assessment": {}
            }
        
        subject_data = input_data.get("subject_data", {})
        safety_data = input_data.get("safety_data", {})
        approval_chain = input_data.get("approval_chain", ["medical_monitor", "sponsor"])
        documentation_requirements = input_data.get("documentation_requirements", [])
        
        # Validate request
        validation_result = validate_request(request_details, documentation_requirements)
        
        # Check authorization
        authorization = check_authorization(
            request_details, approval_chain, safety_data
        )
        
        # Create audit trail
        audit_trail = create_audit_trail(request_details, authorization, validation_result)
        
        # Determine unblinding code if authorized
        unblinding_code = None
        if authorization["approved"]:
            unblinding_code = process_unblinding(subject_data, request_details)
        
        # Assess impact
        impact_assessment = assess_impact(request_details, subject_data, authorization)
        
        # Define required actions
        required_actions = define_required_actions(
            authorization, request_details, impact_assessment
        )
        
        # Determine regulatory notifications
        regulatory_notifications = determine_notifications(
            request_details, authorization, impact_assessment
        )
        
        return {
            "authorization": authorization,
            "unblinding_code": unblinding_code,
            "audit_trail": audit_trail,
            "required_actions": required_actions,
            "regulatory_notifications": regulatory_notifications,
            "impact_assessment": impact_assessment
        }
        
    except Exception as e:
        return {
            "error": f"Error processing unblinding request: {str(e)}",
            "authorization": {},
            "unblinding_code": None,
            "audit_trail": [],
            "required_actions": [],
            "regulatory_notifications": [],
            "impact_assessment": {}
        }


def validate_request(request_details: Dict, documentation_requirements: List) -> Dict:
    """Validate the unblinding request."""
    validation_errors = []
    validation_warnings = []
    
    # Check required fields
    required_fields = ["subject_id", "requestor", "reason", "urgency"]
    for field in required_fields:
        if not request_details.get(field):
            validation_errors.append(f"Missing required field: {field}")
    
    # Validate urgency level
    urgency = request_details.get("urgency", "").lower()
    if urgency not in ["emergency", "urgent", "routine"]:
        validation_errors.append(f"Invalid urgency level: {urgency}")
    
    # Check requestor authorization
    requestor_role = request_details.get("requestor_role", "").lower()
    authorized_roles = ["physician", "medical_monitor", "safety_officer", "investigator"]
    
    if requestor_role not in authorized_roles:
        validation_warnings.append(f"Requestor role '{requestor_role}' may require additional approval")
    
    # Check documentation
    provided_docs = request_details.get("documentation", [])
    missing_docs = [doc for doc in documentation_requirements if doc not in provided_docs]
    
    if missing_docs:
        validation_warnings.append(f"Missing documentation: {', '.join(missing_docs)}")
    
    return {
        "valid": len(validation_errors) == 0,
        "errors": validation_errors,
        "warnings": validation_warnings,
        "documentation_complete": len(missing_docs) == 0
    }


def check_authorization(request_details: Dict, approval_chain: List, 
                        safety_data: Dict) -> Dict:
    """Check if the request is authorized."""
    urgency = request_details.get("urgency", "").lower()
    reason = request_details.get("reason", "").lower()
    
    # Emergency unblinding criteria
    emergency_criteria = [
        "life-threatening" in reason,
        "emergency" in reason,
        "critical care" in reason,
        "urgent medical" in reason
    ]
    
    is_emergency = urgency == "emergency" or any(emergency_criteria)
    
    # Check if SAE related
    is_sae_related = safety_data.get("active_sae", False) or "serious adverse" in reason
    
    # Determine approval requirements
    if is_emergency:
        required_approvals = ["emergency_approval"]
        approval_level = "Emergency"
        time_limit = "Immediate"
    elif is_sae_related:
        required_approvals = ["medical_monitor"]
        approval_level = "Expedited"
        time_limit = "Within 24 hours"
    else:
        required_approvals = approval_chain
        approval_level = "Standard"
        time_limit = "Within 72 hours"
    
    # Simulate approval (in real system, would check actual approvals)
    approved = is_emergency or is_sae_related or urgency == "urgent"
    
    authorization = {
        "approved": approved,
        "approval_level": approval_level,
        "required_approvals": required_approvals,
        "time_limit": time_limit,
        "approval_timestamp": datetime.now().isoformat() if approved else None,
        "approval_reason": determine_approval_reason(is_emergency, is_sae_related, reason)
    }
    
    if not approved:
        authorization["denial_reason"] = "Request does not meet emergency or safety criteria"
    
    return authorization


def determine_approval_reason(is_emergency: bool, is_sae_related: bool, reason: str) -> str:
    """Determine the reason for approval."""
    if is_emergency:
        return "Emergency medical treatment required"
    elif is_sae_related:
        return "SAE management and patient safety"
    elif "withdrawal" in reason:
        return "Subject withdrawal from study"
    else:
        return "Medical necessity"


def process_unblinding(subject_data: Dict, request_details: Dict) -> Dict:
    """Process the unblinding and return treatment assignment."""
    treatment = subject_data.get("treatment_assignment", "Unknown")
    
    unblinding_code = {
        "subject_id": request_details["subject_id"],
        "treatment_assignment": treatment,
        "unblinding_date": datetime.now().isoformat(),
        "unblinded_by": request_details["requestor"],
        "method": "Emergency unblinding system",
        "confirmation_code": generate_confirmation_code(
            request_details["subject_id"], 
            treatment
        )
    }
    
    # Add additional details based on treatment
    if treatment.lower() != "unknown":
        unblinding_code["dose_information"] = subject_data.get("dose_level", "Standard dose")
        unblinding_code["administration_route"] = subject_data.get("route", "As per protocol")
    
    return unblinding_code


def generate_confirmation_code(subject_id: str, treatment: str) -> str:
    """Generate a confirmation code for the unblinding."""
    # Simple hash-like code (in production, use proper cryptographic methods)
    import hashlib
    combined = f"{subject_id}_{treatment}_{datetime.now().isoformat()}"
    return hashlib.md5(combined.encode()).hexdigest()[:8].upper()


def create_audit_trail(request_details: Dict, authorization: Dict, 
                       validation_result: Dict) -> List[Dict]:
    """Create comprehensive audit trail."""
    audit_trail = []
    
    # Request received
    audit_trail.append({
        "timestamp": request_details.get("request_date", datetime.now().isoformat()),
        "action": "Request received",
        "actor": request_details.get("requestor"),
        "details": f"Unblinding request for subject {request_details.get('subject_id')}"
    })
    
    # Validation
    audit_trail.append({
        "timestamp": datetime.now().isoformat(),
        "action": "Request validated",
        "actor": "System",
        "details": f"Validation {'passed' if validation_result['valid'] else 'failed'}"
    })
    
    # Authorization
    audit_trail.append({
        "timestamp": datetime.now().isoformat(),
        "action": "Authorization check",
        "actor": "System",
        "details": f"Request {'approved' if authorization['approved'] else 'denied'}"
    })
    
    # Unblinding (if approved)
    if authorization["approved"]:
        audit_trail.append({
            "timestamp": datetime.now().isoformat(),
            "action": "Treatment unblinded",
            "actor": request_details.get("requestor"),
            "details": "Treatment assignment revealed"
        })
    
    return audit_trail


def assess_impact(request_details: Dict, subject_data: Dict, 
                 authorization: Dict) -> Dict:
    """Assess impact on study integrity."""
    impact_level = "Low"
    affected_analyses = []
    
    # Check if subject is in primary analysis population
    if subject_data.get("primary_analysis_population", True):
        impact_level = "Medium"
        affected_analyses.append("Primary efficacy analysis")
    
    # Check if early in study
    if subject_data.get("visit_number", 999) < 3:
        impact_level = "High"
        affected_analyses.append("Full treatment period analysis")
    
    # Check if key secondary endpoints affected
    if subject_data.get("key_secondary_evaluable", False):
        affected_analyses.append("Key secondary endpoints")
    
    bias_risk = "Low"
    if authorization["approved"] and request_details.get("urgency") != "emergency":
        bias_risk = "Medium"
    
    return {
        "impact_level": impact_level,
        "affected_analyses": affected_analyses,
        "bias_risk": bias_risk,
        "subject_remains_evaluable": subject_data.get("current_status") != "withdrawn",
        "statistical_considerations": [
            "Consider sensitivity analysis excluding unblinded subjects",
            "Document unblinding in statistical analysis plan"
        ] if impact_level != "Low" else []
    }


def define_required_actions(authorization: Dict, request_details: Dict,
                           impact_assessment: Dict) -> List[Dict]:
    """Define required follow-up actions."""
    actions = []
    
    if authorization["approved"]:
        # Immediate actions
        actions.append({
            "priority": "IMMEDIATE",
            "action": "Document unblinding in subject CRF",
            "responsible": "Site coordinator",
            "deadline": "Within 24 hours"
        })
        
        actions.append({
            "priority": "HIGH",
            "action": "Notify medical monitor",
            "responsible": "Site investigator",
            "deadline": "Within 24 hours"
        })
        
        # Follow-up actions
        actions.append({
            "priority": "MEDIUM",
            "action": "Update randomization system",
            "responsible": "Data management",
            "deadline": "Within 48 hours"
        })
        
        if impact_assessment["impact_level"] in ["Medium", "High"]:
            actions.append({
                "priority": "MEDIUM",
                "action": "Review impact on statistical analysis plan",
                "responsible": "Statistician",
                "deadline": "Within 1 week"
            })
    
    # Documentation actions
    actions.append({
        "priority": "HIGH",
        "action": "File unblinding request documentation",
        "responsible": "Site coordinator",
        "deadline": "Within 48 hours"
    })
    
    return actions


def determine_notifications(request_details: Dict, authorization: Dict,
                           impact_assessment: Dict) -> List[Dict]:
    """Determine required regulatory notifications."""
    notifications = []
    
    urgency = request_details.get("urgency", "").lower()
    
    if urgency == "emergency" and authorization["approved"]:
        notifications.append({
            "recipient": "IRB/Ethics Committee",
            "type": "Emergency unblinding notification",
            "timeline": "Within 7 days",
            "content": "Emergency unblinding report with justification"
        })
    
    if impact_assessment["impact_level"] == "High":
        notifications.append({
            "recipient": "Regulatory authority",
            "type": "Protocol deviation",
            "timeline": "As per local requirements",
            "content": "Impact on study integrity assessment"
        })
    
    # DSMB notification if applicable
    if authorization["approved"]:
        notifications.append({
            "recipient": "DSMB",
            "type": "Unblinding notification",
            "timeline": "Next scheduled meeting",
            "content": "Summary of unblinding event and impact"
        })
    
    return notifications