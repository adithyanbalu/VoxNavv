"""
Pydantic data models for Context Engine (Context Before Consequence).
Defines schemas for actions, policies, context items, compressed facts,
sufficiency evaluations, and privacy audit manifests.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TargetData(BaseModel):
    recipient: Optional[str] = None
    document_id: Optional[str] = None
    amount: Optional[float] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class ActionInput(BaseModel):
    action: str
    target: TargetData


class PolicyInput(BaseModel):
    requiredContext: List[str] = Field(default_factory=lambda: ["recipient", "document"])
    allowedSources: List[str] = Field(default_factory=lambda: ["messages", "calendar", "files", "contacts"])
    maxContextItems: int = Field(default=3, ge=1, le=10)


class ContextItem(BaseModel):
    id: str
    source: str  # "messages" | "calendar" | "files" | "contacts"
    timestamp: Optional[str] = None
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    similarity_score: float = 0.0


class CompressedFact(BaseModel):
    id: str
    source: str
    entity: str
    date: str
    request_action: str
    summary: str
    raw_preview_redacted: str = ""
    is_anomaly: bool = False
    anomaly_note: Optional[str] = None


class SufficiencyAssessment(BaseModel):
    is_sufficient: bool
    confidence: float
    reason: str
    anomaly_detected: bool = False
    mismatched_field: Optional[str] = None
    suggested_verification: Optional[str] = None


class PrivacyLog(BaseModel):
    used: List[str] = Field(default_factory=list)
    not_used: List[str] = Field(default_factory=list)
    summary_metrics: Dict[str, Any] = Field(default_factory=dict)


class ContextResponse(BaseModel):
    explanation: str
    privacy_log: Dict[str, Any]
    sufficiency: Optional[Dict[str, Any]] = None
    latency_ms: float = 0.0
