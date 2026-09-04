"""
Mock context processor for Yazeen's side.
Implements context retrieval, compression, explanation generation, and privacy audit.
For MVP, returns hardcoded context based on action type.
"""

def get_context_and_explanation(action_type: str, target: dict, policy: dict) -> dict:
    """
    Returns context output matching CONTEXT OUTPUT specification:
    { "explanation": "string", "privacy_log": { "used": [string], "not_used": [string] } }
    """
    # Hardcoded responses per action type for MVP
    if action_type == "SEND_DOCUMENT":
        recipient = target.get("recipient", "unknown")
        document_id = target.get("document_id", "unknown_doc")
        explanation = f"Before you send: {recipient} requested this document on August 28."
        used = [
            f"1 message: '{recipient} asked for {document_id} on Aug 28'",
            f"Recipient: {recipient}",
            f"Document: {document_id}"
        ]
        not_used = [
            "47 other messages",
            "12 files",
            "8 calendar events",
            "15 contacts"
        ]
    elif action_type == "DELETE_FILE":
        file_id = target.get("document_id", "unknown_file")
        explanation = f"Before you delete: This file was last modified on July 15 for the Henderson project."
        used = [
            f"1 file metadata: '{file_id} last modified Jul 15, 2024'",
            f"File: {file_id}"
        ]
        not_used = [
            "43 other files",
            "20 messages",
            "10 calendar events"
        ]
    elif action_type == "CANCEL_APPT":
        recipient = target.get("recipient", "the clinic")
        explanation = f"Before you cancel: You have an appointment with {recipient} tomorrow at 2:00 PM."
        used = [
            f"1 calendar event: 'Appointment with {recipient} tomorrow at 2:00 PM'",
            f"Participant: {recipient}"
        ]
        not_used = [
            "35 other calendar events",
            "50 messages",
            "12 files"
        ]
    elif action_type == "TRANSFER":
        recipient = target.get("recipient", "unknown")
        amount = target.get("amount", 0)
        explanation = f"Before you transfer: You recently sent ${amount} to {recipient} on August 20."
        used = [
            f"1 message: 'Send ${amount} to {recipient} for invoice #1234'",
            f"Recipient: {recipient}",
            f"Amount: ${amount}"
        ]
        not_used = [
            "30 other messages",
            "10 files",
            "8 calendar events"
        ]
    else:
        # Fallback
        explanation = "Context unavailable."
        used = []
        not_used = ["All data sources"]

    return {
        "explanation": explanation,
        "privacy_log": {
            "used": used,
            "not_used": not_used
        }
    }