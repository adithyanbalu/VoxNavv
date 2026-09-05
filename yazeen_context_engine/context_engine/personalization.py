"""
Lightweight personalization and feedback engine for Context Before Consequence.
Stores user decisions and confirmation history locally without leaking behavioral telemetry.
"""

import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

PREF_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "user_preferences.json")
)


class PersonalizationEngine:
    def __init__(self, pref_file: str = PREF_FILE):
        self.pref_file = pref_file
        self.preferences: Dict[str, Any] = {
            "trusted_recipients": {},
            "snoozed_actions": {},
            "feedback_history": [],
            "sensitivity_preference": "medium",
        }
        self._load()

    def _load(self):
        if os.path.exists(self.pref_file):
            try:
                with open(self.pref_file, "r", encoding="utf-8") as f:
                    self.preferences = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load user preferences: {e}")

    def _save(self):
        try:
            with open(self.pref_file, "w", encoding="utf-8") as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save user preferences: {e}")

    def record_user_decision(self, action_type: str, recipient: str, decision: str):
        """
        decision: 'continue' | 'cancel' | 'verify'
        """
        key = recipient.lower() if recipient else "general"
        if key not in self.preferences["trusted_recipients"]:
            self.preferences["trusted_recipients"][key] = {
                "confirm_count": 0,
                "cancel_count": 0,
            }

        if decision == "continue":
            self.preferences["trusted_recipients"][key]["confirm_count"] += 1
        elif decision == "cancel":
            self.preferences["trusted_recipients"][key]["cancel_count"] += 1

        self.preferences["feedback_history"].append({
            "action": action_type,
            "recipient": recipient,
            "decision": decision,
        })
        self._save()

    def get_recipient_trust_bias(self, recipient: str) -> float:
        """
        Returns trust boost between 0.0 and 0.2 if user repeatedly confirms actions for this recipient.
        """
        if not recipient:
            return 0.0
        data = self.preferences["trusted_recipients"].get(recipient.lower())
        if not data:
            return 0.0
        confirms = data.get("confirm_count", 0)
        cancels = data.get("cancel_count", 0)
        if cancels > 0:
            return 0.0
        if confirms > 3:
            return 0.15
        elif confirms > 0:
            return 0.05
        return 0.0
