from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


Confidence = Literal["low", "medium", "high"]
ReviewDecision = Literal["accept", "edit", "reject"]
ReviewReasonCode = Literal[
    "factual_error",
    "missing_risk_flag",
    "unsafe_recommendation",
    "unclear_wording",
    "wrong_evidence",
    "other",
]


class InputType(str, Enum):
    PLAIN_TEXT = "plain_text"


class DraftRequest(BaseModel):
    raw_text: str = Field(..., min_length=1)


class SourceSpan(BaseModel):
    id: str
    text: str
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)


class EvidenceBackedItem(BaseModel):
    text: str = Field(..., min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: Confidence = "medium"
    requires_clinician_review: bool = True


class ClinicalReviewDraft(BaseModel):
    key_clinical_summary: list[EvidenceBackedItem]
    trends: list[EvidenceBackedItem]
    risk_flags: list[EvidenceBackedItem]
    uncertainties: list[EvidenceBackedItem]
    suggested_follow_up_areas: list[EvidenceBackedItem]
    safety_note: str


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ResponseMetadata(BaseModel):
    prompt_version: str
    model_version: str
    llm_provider: str


class DraftResponse(BaseModel):
    draft: ClinicalReviewDraft | None
    source_spans: list[SourceSpan]
    validation: ValidationResult
    metadata: ResponseMetadata


class ClinicianReviewRecord(BaseModel):
    draft_id: str
    decision: ReviewDecision
    reason_codes: list[ReviewReasonCode] = Field(default_factory=list)
    edited_text: str | None = None
    comments: str | None = None
