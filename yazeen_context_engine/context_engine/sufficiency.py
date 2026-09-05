"""
Context Sufficiency Engine (Section 14).
Rules-based evaluation of whether retrieved context adequately explains the action,
with anomaly detection for mismatched recipients, unknown destinations, or stale records.
"""

import logging
from typing import List, Dict, Any, Optional
from .models import CompressedFact, SufficiencyAssessment

logger = logging.getLogger(__name__)


class ContextSufficiencyEngine:
    def _matches_recipient(self, target_recipient: str, text: str) -> bool:
        if not target_recipient or not target_recipient.strip():
            return False
        text_lower = text.lower()
        t_clean = target_recipient.lower().replace("+", " ").replace(".", " ").replace("_", " ").replace("-", " ")
        email_prefix = target_recipient.split("@")[0].lower().replace("+", " ").replace(".", " ")
        if target_recipient.lower() in text_lower or (len(email_prefix) >= 3 and email_prefix in text_lower):
            return True
        tokens = [
            t for t in t_clean.split()
            if len(t) >= 3 and t not in ["com", "org", "net", "edu", "clinic", "example"]
        ]
        if tokens and any(t in text_lower for t in tokens):
            return True
        return False

    def evaluate(
        self,
        action_type: str,
        target: Dict[str, Any],
        facts: List[CompressedFact],
    ) -> SufficiencyAssessment:
        if not facts:
            return SufficiencyAssessment(
                is_sufficient=False,
                confidence=0.1,
                reason="No matching contextual records found in permitted sources.",
                anomaly_detected=True,
                suggested_verification="Verify recipient and details before proceeding.",
            )

        recipient = str(target.get("recipient", "") or "").lower().strip()
        document_id = str(target.get("document_id", "") or "").lower().strip()
        amount = target.get("amount")

        # 1. SEND_DOCUMENT evaluation
        if action_type == "SEND_DOCUMENT":
            doc_matched = False
            recipient_matched = False
            for f in facts:
                f_summary_lower = f.summary.lower() + " " + f.entity.lower()
                if document_id and document_id in f_summary_lower:
                    doc_matched = True
                if recipient and self._matches_recipient(recipient, f_summary_lower):
                    recipient_matched = True

            if doc_matched and recipient_matched:
                return SufficiencyAssessment(
                    is_sufficient=True,
                    confidence=0.95,
                    reason=f"Found explicit prior request for '{target.get('document_id')}' matching recipient.",
                    anomaly_detected=False,
                )
            elif doc_matched and not recipient_matched:
                return SufficiencyAssessment(
                    is_sufficient=False,
                    confidence=0.40,
                    reason=f"Document '{target.get('document_id')}' was identified, but no prior communication found with '{target.get('recipient')}'.",
                    anomaly_detected=True,
                    mismatched_field="recipient",
                    suggested_verification="Verify recipient address to prevent misdirected sensitive documents.",
                )
            elif not doc_matched and recipient_matched:
                return SufficiencyAssessment(
                    is_sufficient=True,
                    confidence=0.75,
                    reason=f"Prior communication found with {target.get('recipient')}, but document is newly referenced.",
                    anomaly_detected=False,
                )
            else:
                return SufficiencyAssessment(
                    is_sufficient=False,
                    confidence=0.20,
                    reason="No matching document or recipient communication found in permitted context.",
                    anomaly_detected=True,
                    suggested_verification="Verify recipient and document details before sending.",
                )

        # 2. DELETE_FILE evaluation
        elif action_type == "DELETE_FILE":
            file_found = any(document_id in f.summary.lower() for f in facts)
            is_temp = "temp" in document_id or any("safe to delete" in f.summary.lower() for f in facts)
            if file_found:
                return SufficiencyAssessment(
                    is_sufficient=True,
                    confidence=0.90,
                    reason="Identified file project origin and modification history." if not is_temp else "Identified file as temporary disposable cache.",
                    anomaly_detected=False,
                )
            return SufficiencyAssessment(
                is_sufficient=False,
                confidence=0.30,
                reason=f"Could not locate project or modification records for '{target.get('document_id')}'.",
                anomaly_detected=True,
                suggested_verification="Verify file backup status before irreversible deletion.",
            )

        # 3. CANCEL_APPT evaluation
        elif action_type == "CANCEL_APPT":
            appt_found = False
            for f in facts:
                if self._matches_recipient(recipient, f.summary.lower() + " " + f.entity.lower()):
                    appt_found = True
                    break
            if appt_found:
                return SufficiencyAssessment(
                    is_sufficient=True,
                    confidence=0.92,
                    reason=f"Confirmed active upcoming appointment details with {target.get('recipient')}.",
                    anomaly_detected=False,
                )
            return SufficiencyAssessment(
                is_sufficient=False,
                confidence=0.35,
                reason=f"No upcoming appointment found matching '{target.get('recipient')}'.",
                anomaly_detected=True,
                suggested_verification="Check calendar schedule before cancelling.",
            )

        # 4. TRANSFER evaluation
        elif action_type == "TRANSFER":
            amount_matched = False
            recipient_matched = False
            for f in facts:
                f_full = f.summary.lower() + " " + f.entity.lower()
                if recipient and self._matches_recipient(recipient, f_full):
                    recipient_matched = True
                if amount and f"${amount}" in f.summary:
                    amount_matched = True

            if recipient_matched and amount_matched:
                return SufficiencyAssessment(
                    is_sufficient=True,
                    confidence=0.95,
                    reason=f"Found explicit prior request for ${amount} from {target.get('recipient')}.",
                    anomaly_detected=False,
                )
            elif recipient_matched and not amount_matched:
                return SufficiencyAssessment(
                    is_sufficient=True,
                    confidence=0.75,
                    reason=f"Recognized recipient {target.get('recipient')}, but transfer amount differs from past requests.",
                    anomaly_detected=False,
                )
            else:
                return SufficiencyAssessment(
                    is_sufficient=False,
                    confidence=0.25,
                    reason=f"No prior transaction history or request found for '{target.get('recipient')}'.",
                    anomaly_detected=True,
                    mismatched_field="recipient",
                    suggested_verification="Verify recipient details and payment account.",
                )

        return SufficiencyAssessment(
            is_sufficient=True,
            confidence=0.80,
            reason="Context matches action parameters.",
            anomaly_detected=False,
        )
