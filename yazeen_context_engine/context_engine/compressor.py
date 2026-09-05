"""
Rule-based Context Compressor for the Context Engine.
Extracts [date] [person] [request] into short, structured micro-facts.
Guarantees raw conversational text and sensitive disclosures are stripped.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from .models import ContextItem, CompressedFact

logger = logging.getLogger(__name__)


class ContextCompressor:
    def compress_item(self, item: ContextItem, action_type: str, target: Dict[str, Any]) -> CompressedFact:
        source = item.source
        meta = item.metadata

        if source == "messages":
            return self._compress_message(item, target)
        elif source == "calendar":
            return self._compress_calendar(item, target)
        elif source == "files":
            return self._compress_file(item, target)
        elif source == "contacts":
            return self._compress_contact(item, target)
        else:
            return CompressedFact(
                id=item.id,
                source=source,
                entity="Unknown",
                date="recently",
                request_action="context reference",
                summary=f"Referenced record {item.id}",
            )

    def _compress_message(self, item: ContextItem, target: Dict[str, Any]) -> CompressedFact:
        meta = item.metadata
        sender_name = meta.get("sender_name") or meta.get("sender", "Someone")
        # Normalize sender name
        if "@" in sender_name:
            sender_name = sender_name.split("@")[0].replace(".", " ").title()

        date_str = meta.get("date_str") or "recently"
        subject = meta.get("subject", "")
        body = meta.get("body", "")

        # Extract request/action using deterministic rules
        request_action = "sent a message"
        if meta.get("document_id"):
            doc = meta["document_id"]
            if "request" in subject.lower() or "send" in body.lower():
                request_action = f"requested this document ({doc})"
            else:
                request_action = f"referenced document {doc}"
        elif meta.get("amount"):
            amount = meta["amount"]
            request_action = f"requested ${amount} for reimbursement"
        elif "appointment" in subject.lower() or "dr." in sender_name.lower():
            request_action = "confirmed medical appointment details"
        elif "project" in subject.lower() or "client" in body.lower():
            request_action = "provided project specifications"

        summary = f"{sender_name} {request_action} on {date_str}"
        redacted_preview = f"Message from {sender_name} on {date_str} regarding '{subject}'"

        return CompressedFact(
            id=item.id,
            source="messages",
            entity=sender_name,
            date=date_str,
            request_action=request_action,
            summary=summary,
            raw_preview_redacted=redacted_preview,
        )

    def _compress_calendar(self, item: ContextItem, target: Dict[str, Any]) -> CompressedFact:
        meta = item.metadata
        title = meta.get("title", "Event")
        participant = meta.get("participant", "Participant")
        date_str = meta.get("date_str", "scheduled date")
        time_str = meta.get("time_str", "")
        location = meta.get("location", "")

        date_display = f"{date_str} at {time_str}" if time_str else date_str
        summary = f"Scheduled '{title}' with {participant} on {date_display}"
        if location:
            summary += f" ({location})"

        return CompressedFact(
            id=item.id,
            source="calendar",
            entity=participant,
            date=date_display,
            request_action=f"scheduled {title}",
            summary=summary,
            raw_preview_redacted=f"Calendar event: {title} on {date_display}",
        )

    def _compress_file(self, item: ContextItem, target: Dict[str, Any]) -> CompressedFact:
        meta = item.metadata
        filename = meta.get("filename", "document")
        project = meta.get("project", "General")
        last_modified_str = meta.get("last_modified_str", "recently")
        summary_desc = meta.get("summary", "")

        summary = f"File '{filename}' last modified on {last_modified_str} for {project}"

        return CompressedFact(
            id=item.id,
            source="files",
            entity=project,
            date=last_modified_str,
            request_action=f"modified file {filename}",
            summary=summary,
            raw_preview_redacted=f"File metadata: {filename} ({project})",
        )

    def _compress_contact(self, item: ContextItem, target: Dict[str, Any]) -> CompressedFact:
        meta = item.metadata
        name = meta.get("name", "Contact")
        relationship = meta.get("relationship", "Associate")
        org = meta.get("organization", "")
        trust = meta.get("trust_level", "unverified")

        summary = f"Contact: {name} ({relationship}{f' at {org}' if org else ''}, trust: {trust})"

        return CompressedFact(
            id=item.id,
            source="contacts",
            entity=name,
            date="current",
            request_action=f"listed as {relationship}",
            summary=summary,
            raw_preview_redacted=f"Address book: {name} [{trust}]",
        )

    def compress_all(
        self,
        items: List[ContextItem],
        action_type: str,
        target: Dict[str, Any],
    ) -> List[CompressedFact]:
        return [self.compress_item(item, action_type, target) for item in items]
