"""
Explanation Engine for Context Before Consequence.
Translates {action, recipient, document, context} into a dignified, fluent human sentence.
Features a high-speed deterministic template engine (<1ms) with an optional Groq LLM fluency enhancer.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from .models import CompressedFact, SufficiencyAssessment

logger = logging.getLogger(__name__)


class ExplanationEngine:
    def __init__(self):
        self.groq_api_key = os.environ.get("GROQ_API_KEY")

    def generate_explanation(
        self,
        action_type: str,
        target: Dict[str, Any],
        facts: List[CompressedFact],
        sufficiency: SufficiencyAssessment,
    ) -> str:
        # If anomaly or insufficient context is detected, surface dignified verification prompt
        if sufficiency.anomaly_detected or not sufficiency.is_sufficient:
            return self._format_anomaly_explanation(action_type, target, sufficiency)

        # Primary deterministic generation
        deterministic_explanation = self._format_deterministic_explanation(
            action_type, target, facts
        )

        # Optional Groq fluency enhancement if API key is configured
        if self.groq_api_key:
            enhanced = self._call_groq_fluency(deterministic_explanation, facts)
            if enhanced:
                return enhanced

        return deterministic_explanation

    def _format_deterministic_explanation(
        self,
        action_type: str,
        target: Dict[str, Any],
        facts: List[CompressedFact],
    ) -> str:
        recipient = target.get("recipient", "")
        document_id = target.get("document_id", "")
        amount = target.get("amount")

        primary_fact = facts[0] if facts else None

        if action_type == "SEND_DOCUMENT":
            if primary_fact:
                entity = primary_fact.entity
                date = primary_fact.date
                return f"Before you send: {entity} requested this document on {date}."
            return f"Before you send: Reviewing document '{document_id}' intended for {recipient}."

        elif action_type == "DELETE_FILE":
            if primary_fact:
                if "temp" in document_id.lower() or "temporary" in primary_fact.summary.lower():
                    return f"Before you delete: This is a temporary scratch file created on {primary_fact.date}."
                # Find file fact if available
                file_fact = next((f for f in facts if f.source == "files"), primary_fact)
                entity_label = file_fact.entity
                prefix = "the " if "project" in entity_label.lower() else ""
                return f"Before you delete: This file was last modified on {file_fact.date} for {prefix}{entity_label}."
            return f"Before you delete: Please confirm if '{document_id}' is no longer needed."

        elif action_type == "CANCEL_APPT":
            if primary_fact:
                return f"Before you cancel: You have an appointment with {primary_fact.entity} on {primary_fact.date}."
            return f"Before you cancel: Please check your schedule with {recipient}."

        elif action_type == "TRANSFER":
            if primary_fact:
                entity = primary_fact.entity
                date = primary_fact.date
                return f"Before you transfer: {entity} requested ${amount} on {date}."
            return f"Before you transfer: You are about to send ${amount} to {recipient}."

        return "Before you proceed: Please review the details of this action."

    def _format_anomaly_explanation(
        self,
        action_type: str,
        target: Dict[str, Any],
        sufficiency: SufficiencyAssessment,
    ) -> str:
        recipient = target.get("recipient", "the recipient")
        document_id = target.get("document_id", "the document")
        amount = target.get("amount", "")

        if action_type == "SEND_DOCUMENT":
            return (
                f"Before you send: We couldn't find a prior message or request from '{recipient}' "
                f"for '{document_id}'. Would you like to double-check the recipient before sending?"
            )
        elif action_type == "TRANSFER":
            return (
                f"Before you transfer: No prior transaction history or request found for '{recipient}'. "
                f"Would you like to verify the transfer of ${amount}?"
            )
        elif action_type == "CANCEL_APPT":
            return (
                f"Before you cancel: We could not find a confirmed upcoming appointment with '{recipient}'. "
                f"Please verify your calendar before proceeding."
            )
        elif action_type == "DELETE_FILE":
            return (
                f"Before you delete: No active project or backup record found for '{document_id}'. "
                f"This action cannot be undone."
            )

        return f"Before you proceed: {sufficiency.reason} Please verify before continuing."

    def _call_groq_fluency(self, baseline_text: str, facts: List[CompressedFact]) -> Optional[str]:
        try:
            from groq import Groq
            client = Groq(api_key=self.groq_api_key)
            fact_points = "\n".join([f"- {f.summary}" for f in facts])
            prompt = (
                "You are an empathetic digital accessibility assistant for an adult who values autonomy. "
                "Rephrase the following context note into one concise, clear, polite sentence. "
                "DO NOT add any new medical labels, do not mention memory or dementia, and do not change dates, names, or amounts.\n\n"
                f"Facts:\n{fact_points}\n\n"
                f"Draft note:\n{baseline_text}\n\n"
                "Refined single-sentence note:"
            )
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                temperature=0.1,
                max_tokens=60,
            )
            enhanced = chat_completion.choices[0].message.content.strip()
            if enhanced and len(enhanced) < 200:
                return enhanced
        except Exception as e:
            logger.debug(f"Groq fluency call skipped/failed: {e}")
        return None
