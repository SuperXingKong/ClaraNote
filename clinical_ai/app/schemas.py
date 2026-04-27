from __future__ import annotations

from enum import Enum
from typing import Any, Literal
from datetime import datetime, timezone

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
IssueSeverity = Literal["warning", "error"]
HallucinationCategory = Literal[
    "unsupported_condition",
    "unsupported_medication",
    "unsupported_lab_trend",
    "unsupported_symptom",
    "unsupported_recommendation",
    "incorrect_temporality",
    "unsupported_claim",
    "omission",
]


class InputType(str, Enum):
    PLAIN_TEXT = "plain_text"
    FHIR_BUNDLE = "fhir_bundle"


class DraftRequest(BaseModel):
    raw_text: str = Field(..., min_length=1)


class FhirDraftRequest(BaseModel):
    bundle: dict[str, Any]


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
    issues: list[ValidationIssue] = Field(default_factory=list)


class ResponseMetadata(BaseModel):
    prompt_version: str
    model_version: str
    llm_provider: str


class ValidationIssue(BaseModel):
    code: HallucinationCategory | str
    severity: IssueSeverity
    message: str
    section: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class DraftDebugInfo(BaseModel):
    first_pass_payload: object


class DraftResponse(BaseModel):
    draft: ClinicalReviewDraft | None
    source_spans: list[SourceSpan]
    validation: ValidationResult
    metadata: ResponseMetadata
    debug: DraftDebugInfo | None = None


class ClinicianReviewRecord(BaseModel):
    draft_id: str
    item_key: str
    decision: ReviewDecision
    reason_codes: list[ReviewReasonCode] = Field(default_factory=list)
    edited_text: str | None = None
    comments: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReviewSubmissionRequest(BaseModel):
    draft_id: str = "current-draft"
    item_key: str
    decision: ReviewDecision
    reason_codes: list[ReviewReasonCode] = Field(default_factory=list)
    edited_text: str | None = None
    comments: str | None = None


class ReviewSubmissionResponse(BaseModel):
    review: ClinicianReviewRecord


class ReviewListResponse(BaseModel):
    reviews: list[ClinicianReviewRecord]


class DesignReference(BaseModel):
    label: str
    authority: str
    url: str


class DesignControl(BaseModel):
    feature_id: str
    title: str
    summary: str
    rationale: str
    implemented_in: list[str] = Field(default_factory=list)
    references: list[DesignReference]


class DesignControlsResponse(BaseModel):
    controls: list[DesignControl]
