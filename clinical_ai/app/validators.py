from __future__ import annotations

import re

from pydantic import ValidationError

from clinical_ai.app.schemas import (
    ClinicalReviewDraft,
    SourceSpan,
    ValidationResult,
)


SAFETY_PATTERNS = [
    r"\bdiagnose\b",
    r"\bprescribe\b",
    r"\bincrease\s+(?:the\s+)?(?:dose|dosage)\b",
    r"\bincrease\s+(?:atorvastatin|metformin)\b",
    r"\bstart\s+(?:a\s+)?(?:medication|statin|atorvastatin|metformin)\b",
    r"\bstop\s+(?:a\s+)?(?:medication|statin|atorvastatin|metformin)\b",
    r"\bmust\s+take\b",
    r"\bshould\s+take\b",
]

TREND_TERMS = [
    "trend",
    "increased",
    "increase",
    "decreased",
    "decrease",
    "worsening",
    "worsened",
    "improving",
    "improved",
    "rising",
    "falling",
]

EVIDENCE_REQUIRED_SECTIONS = [
    "key_clinical_summary",
    "trends",
    "risk_flags",
    "uncertainties",
    "suggested_follow_up_areas",
]


def parse_draft(payload: object) -> tuple[ClinicalReviewDraft | None, list[str]]:
    try:
        return ClinicalReviewDraft.model_validate(payload), []
    except ValidationError as exc:
        return None, [f"Schema validation failed: {exc}"]


def validate_all(
    draft: ClinicalReviewDraft | None,
    source_spans: list[SourceSpan],
    raw_text: str,
) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if draft is None:
        return ValidationResult(is_valid=False, errors=["Draft is missing or invalid."])

    errors.extend(validate_evidence(draft, source_spans))
    errors.extend(validate_clinician_review_required(draft))
    errors.extend(validate_ambiguity(draft, raw_text))
    errors.extend(validate_safety(draft))

    if not draft.safety_note.lower().startswith("draft for clinician review"):
        warnings.append("Safety note should clearly state that the output is a clinician-review draft.")

    return ValidationResult(is_valid=not errors, errors=errors, warnings=warnings)


def validate_evidence(
    draft: ClinicalReviewDraft,
    source_spans: list[SourceSpan],
) -> list[str]:
    errors: list[str] = []
    valid_ids = {span.id for span in source_spans}

    for section_name, item in iter_evidence_items(draft):
        if not item.evidence_ids:
            errors.append(f"{section_name} item lacks evidence_ids: {item.text}")
            continue

        unknown_ids = [evidence_id for evidence_id in item.evidence_ids if evidence_id not in valid_ids]
        if unknown_ids:
            errors.append(
                f"{section_name} item references unknown evidence IDs {unknown_ids}: {item.text}"
            )

    return errors


def validate_clinician_review_required(draft: ClinicalReviewDraft) -> list[str]:
    errors: list[str] = []
    for section_name, item in iter_evidence_items(draft):
        if not item.requires_clinician_review:
            errors.append(f"{section_name} item is not marked for clinician review: {item.text}")
    return errors


def validate_ambiguity(draft: ClinicalReviewDraft, raw_text: str) -> list[str]:
    errors: list[str] = []
    lowered_input = raw_text.lower()
    has_unclear_fasting_glucose = (
        "fasting glucose" in lowered_input and "unclear which is most recent" in lowered_input
    )

    if not has_unclear_fasting_glucose:
        return errors

    for item in draft.trends:
        lowered_text = item.text.lower()
        if "fasting glucose" in lowered_text and any(term in lowered_text for term in TREND_TERMS):
            errors.append(
                "Fasting glucose recency is unclear, so the draft must not infer a fasting glucose trend."
            )

    return errors


def validate_safety(draft: ClinicalReviewDraft) -> list[str]:
    errors: list[str] = []
    for section_name, item in iter_evidence_items(draft):
        text = item.text
        for pattern in SAFETY_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                errors.append(f"Unsafe directive in {section_name}: {text}")
                break
    return errors


def iter_evidence_items(draft: ClinicalReviewDraft):
    for section_name in EVIDENCE_REQUIRED_SECTIONS:
        for item in getattr(draft, section_name):
            yield section_name, item

