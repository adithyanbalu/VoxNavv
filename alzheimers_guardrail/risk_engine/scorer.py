"""
Transparent risk scorer and policy engine for Context Before Consequence.
Implements Section 15 (risk scoring formula) and Section 9 (permission filtering).
"""

# Weights for each factor (must sum to 1.0 per action type)
# These are example weights; can be tuned based on domain expertise.
FACTOR_WEIGHTS = {
    "SEND_DOCUMENT": {
        "financial_impact": 0.10,
        "data_sensitivity": 0.25,
        "irreversibility": 0.20,
        "external_recipient": 0.20,
        "destructive_operation": 0.05,
        "context_dependency": 0.20,
    },
    "DELETE_FILE": {
        "financial_impact": 0.05,
        "data_sensitivity": 0.20,
        "irreversibility": 0.30,
        "external_recipient": 0.05,
        "destructive_operation": 0.25,
        "context_dependency": 0.15,
    },
    "CANCEL_APPT": {
        "financial_impact": 0.15,
        "data_sensitivity": 0.10,
        "irreversibility": 0.10,
        "external_recipient": 0.25,
        "destructive_operation": 0.05,
        "context_dependency": 0.35,
    },
    "TRANSFER": {
        "financial_impact": 0.30,
        "data_sensitivity": 0.20,
        "irreversibility": 0.15,
        "external_recipient": 0.15,
        "destructive_operation": 0.05,
        "context_dependency": 0.15,
    },
}

# Default weights if action type not found (safe fallback)
DEFAULT_WEIGHTS = {
    "financial_impact": 0.166,
    "data_sensitivity": 0.166,
    "irreversibility": 0.166,
    "external_recipient": 0.166,
    "destructive_operation": 0.166,
    "context_dependency": 0.166,
}

# Factor values computation (simplified heuristics for MVP)
def _compute_factors(action_type: str, target: dict) -> dict:
    """
    Compute factor values (0.0-1.0) based on action and target.
    Uses simple heuristics; can be replaced with learned models.
    """
    # Initialize all factors to 0.0
    factors = {f: 0.0 for f in DEFAULT_WEIGHTS.keys()}

    recipient = target.get("recipient", "")
    document_id = target.get("document_id", "")
    amount = target.get("amount", 0)

    # Financial impact: higher for TRANSFER with large amount, also for SEND_DOCUMENT if sensitive doc
    if action_type == "TRANSFER":
        # Normalize amount assuming typical range 0-10000
        factors["financial_impact"] = min(amount / 10000.0, 1.0)
    elif action_type == "SEND_DOCUMENT":
        # Assume document sensitivity based on filename keywords
        sensitive_keywords = ["medical", "bank", "ssn", "passport", "confidential"]
        if any(kw in document_id.lower() for kw in sensitive_keywords):
            factors["financial_impact"] = 0.7  # potential financial loss from leaked sensitive doc
        else:
            factors["financial_impact"] = 0.2

    # Data sensitivity: higher if document contains personal data
    if action_type in ["SEND_DOCUMENT", "DELETE_FILE"]:
        if document_id:
            sensitive_keywords = ["medical", "health", "prescription", "therapy", "counseling"]
            if any(kw in document_id.lower() for kw in sensitive_keywords):
                factors["data_sensitivity"] = 0.9
            else:
                factors["data_sensitivity"] = 0.4
        else:
            factors["data_sensitivity"] = 0.2
    elif action_type == "TRANSFER":
        factors["data_sensitivity"] = 0.6  # financial data is sensitive

    # Irreversibility: how hard to undo the action
    if action_type == "DELETE_FILE":
        factors["irreversibility"] = 0.9  # file deletion is hard to undo
    elif action_type == "SEND_DOCUMENT":
        factors["irreversibility"] = 0.8  # sent document cannot be unsent
    elif action_type == "CANCEL_APPT":
        factors["irreversibility"] = 0.5  # appointment can often be rescheduled
    elif action_type == "TRANSFER":
        factors["irreversibility"] = 0.6  # transfer may be reversible but with effort

    # External recipient: 1.0 if recipient is outside trusted domain/contacts
    # Simple heuristic: consider external if not containing '@trusted.com' or not in a list of trusted contacts
    trusted_domains = ["trusted.com", "family.com", "clinic.com"]
    if recipient and "@" in recipient:
        domain = recipient.split("@")[1]
        if any(trusted in domain for trusted in trusted_domains):
            factors["external_recipient"] = 0.1
        else:
            factors["external_recipient"] = 1.0
    elif recipient:
        # If recipient looks like a phone number or name without @, assume internal?
        # For simplicity, treat as external if not empty
        factors["external_recipient"] = 0.5
    else:
        factors["external_recipient"] = 0.0

    # Destructive operation: 1.0 for DELETE_FILE, else 0.0
    if action_type == "DELETE_FILE":
        factors["destructive_operation"] = 1.0

    # Context dependency: how much the action depends on contextual information
    # All actions benefit from context, but some more than others
    if action_type == "SEND_DOCUMENT":
        factors["context_dependency"] = 0.8  # need to know if recipient is correct
    elif action_type == "DELETE_FILE":
        factors["context_dependency"] = 0.6  # need to confirm file is correct version
    elif action_type == "CANCEL_APPT":
        factors["context_dependency"] = 0.9  # need to know appointment details and alternatives
    elif action_type == "TRANSFER":
        factors["context_dependency"] = 0.7  # need to verify recipient and purpose

    return factors

def calculate_risk(action_type: str, target: dict) -> dict:
    """
    Calculate risk score using weighted sum formula (Section 15).
    Returns dict matching RISK OUTPUT specification.
    """
    # Compute factor values based on action and target
    factors = _compute_factors(action_type, target)

    # Get weights for this action type, fallback to default
    weights = FACTOR_WEIGHTS.get(action_type, DEFAULT_WEIGHTS)

    # Weighted sum
    score = sum(weights[f] * factors[f] for f in factors)
    # Clamp to [0,1]
    score = max(0.0, min(1.0, score))

    # Determine risk level
    if score < 0.33:
        level = "LOW"
    elif score < 0.66:
        level = "MEDIUM"
    else:
        level = "HIGH"

    # Context gate triggers if risk is medium or higher (can be tuned)
    triggers_context_gate = score >= 0.33

    return {
        "score": round(score, 3),
        "level": level,
        "factors": {k: round(v, 3) for k, v in factors.items()},
        "triggers_context_gate": triggers_context_gate,
    }


# Policy engine (Section 9: permission filtering)
def get_policy(action_type: str) -> dict:
    """
    Return policy requirements for given action type.
    Matches POLICY OUTPUT specification.
    """
    POLICIES = {
        "SEND_DOCUMENT": {
            "requiredContext": ["recipient", "document", "previous_request"],
            "allowedSources": ["messages", "calendar", "files"],
            "maxContextItems": 3,
        },
        "DELETE_FILE": {
            "requiredContext": ["file", "modification_history", "backup_status"],
            "allowedSources": ["files", "messages", "system_logs"],
            "maxContextItems": 3,
        },
        "CANCEL_APPT": {
            "requiredContext": ["appointment_time", "participant", "reason"],
            "allowedSources": ["calendar", "messages", "contacts"],
            "maxContextItems": 3,
        },
        "TRANSFER": {
            "requiredContext": ["recipient", "purpose", "source_account"],
            "allowedSources": ["messages", "contacts", "files"],
            "maxContextItems": 3,
        },
    }

    # Default policy (conservative)
    default_policy = {
        "requiredContext": ["action_details"],
        "allowedSources": ["messages", "calendar", "files", "contacts"],
        "maxContextItems": 3,
    }

    return POLICIES.get(action_type, default_policy)