"""
Context Engine Package for Context Before Consequence.
"""

from .models import (
    ActionInput,
    TargetData,
    PolicyInput,
    ContextItem,
    CompressedFact,
    SufficiencyAssessment,
    PrivacyLog,
    ContextResponse,
)
from .synthetic_data_loader import SyntheticDataLoader
from .vector_store import get_vector_store
from .retriever import ContextRetriever
from .compressor import ContextCompressor
from .sufficiency import ContextSufficiencyEngine
from .explainer import ExplanationEngine
from .privacy_auditor import PrivacyAuditor
from .personalization import PersonalizationEngine
from .processor import get_context_and_explanation, ContextProcessor

__all__ = [
    "ActionInput",
    "TargetData",
    "PolicyInput",
    "ContextItem",
    "CompressedFact",
    "SufficiencyAssessment",
    "PrivacyLog",
    "ContextResponse",
    "SyntheticDataLoader",
    "get_vector_store",
    "ContextRetriever",
    "ContextCompressor",
    "ContextSufficiencyEngine",
    "ExplanationEngine",
    "PrivacyAuditor",
    "PersonalizationEngine",
    "get_context_and_explanation",
    "ContextProcessor",
]
