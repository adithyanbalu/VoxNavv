"""
Master Context Processor for Context Before Consequence.
Orchestrates synthetic data loading, vector retrieval, rule-based compression,
sufficiency assessment, explanation generation, and privacy audit logging.
"""

import time
import logging
from typing import Dict, Any, Optional
from .models import PolicyInput, TargetData
from .synthetic_data_loader import SyntheticDataLoader
from .retriever import ContextRetriever
from .compressor import ContextCompressor
from .sufficiency import ContextSufficiencyEngine
from .explainer import ExplanationEngine
from .privacy_auditor import PrivacyAuditor
from .personalization import PersonalizationEngine

logger = logging.getLogger(__name__)


class ContextProcessor:
    def __init__(self):
        start_init = time.time()
        self.data_loader = SyntheticDataLoader()
        self.retriever = ContextRetriever(self.data_loader)
        self.compressor = ContextCompressor()
        self.sufficiency_engine = ContextSufficiencyEngine()
        self.explainer = ExplanationEngine()
        self.privacy_auditor = PrivacyAuditor(self.data_loader)
        self.personalization = PersonalizationEngine()
        init_duration = (time.time() - start_init) * 1000
        logger.info(f"ContextProcessor initialized in {init_duration:.2f}ms.")

    def process(
        self,
        action_type: str,
        target: Dict[str, Any],
        policy_dict: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()

        # Defensive sanitization for edge cases
        if not action_type or not isinstance(action_type, str):
            action_type = "UNKNOWN_ACTION"
        if not isinstance(target, dict):
            target = {}
        if not isinstance(policy_dict, dict):
            policy_dict = {}

        # Parse policy with safe defaults
        policy = PolicyInput(
            requiredContext=policy_dict.get("requiredContext", ["recipient", "document"]),
            allowedSources=policy_dict.get(
                "allowedSources", ["messages", "calendar", "files", "contacts"]
            ),
            maxContextItems=max(1, min(10, int(policy_dict.get("maxContextItems", 3)))),
        )

        # 1. Retrieve context enforcing policy boundary
        retrieved_items = self.retriever.retrieve(action_type, target, policy)

        # 2. Rule-based compression into structured micro-facts
        compressed_facts = self.compressor.compress_all(
            retrieved_items, action_type, target
        )

        # 3. Context sufficiency & anomaly check (Section 14)
        sufficiency = self.sufficiency_engine.evaluate(
            action_type, target, compressed_facts
        )

        # 4. Generate dignity-preserving plain-language explanation
        explanation = self.explainer.generate_explanation(
            action_type, target, compressed_facts, sufficiency
        )

        # 5. Generate verifiable privacy audit log
        audit_log = self.privacy_auditor.generate_audit_log(
            action_type=action_type,
            target=target,
            policy=policy,
            retrieved_items=retrieved_items,
            compressed_facts=compressed_facts,
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Context processed for {action_type} in {elapsed_ms}ms")

        return {
            "explanation": explanation,
            "privacy_log": {
                "used": audit_log["used"],
                "not_used": audit_log["not_used"],
            },
            "sufficiency": {
                "is_sufficient": sufficiency.is_sufficient,
                "confidence": sufficiency.confidence,
                "reason": sufficiency.reason,
                "anomaly_detected": sufficiency.anomaly_detected,
                "suggested_verification": sufficiency.suggested_verification,
            },
            "audit_summary": audit_log["summary_metrics"],
            "latency_ms": elapsed_ms,
        }


# Global cached processor instance for sub-10ms response times
_PROCESSOR_INSTANCE: Optional[ContextProcessor] = None


def get_processor() -> ContextProcessor:
    global _PROCESSOR_INSTANCE
    if _PROCESSOR_INSTANCE is None:
        _PROCESSOR_INSTANCE = ContextProcessor()
    return _PROCESSOR_INSTANCE


def get_context_and_explanation(
    action_type: str,
    target: dict,
    policy: dict,
) -> dict:
    """
    Main entry point invoked by GSK's backend.
    Maintains 100% backwards compatibility with INTERFACES.md specification:
    Returns:
    {
      "explanation": "string",
      "privacy_log": {
        "used": [string],
        "not_used": [string]
      }
    }
    """
    processor = get_processor()
    return processor.process(action_type, target, policy)