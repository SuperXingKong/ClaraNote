from __future__ import annotations

import re
from dataclasses import dataclass

from pydantic import ValidationError

from clinical_ai.app.schemas import (
    ClinicalReviewDraft,
    SourceSpan,
    ValidationIssue,
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

SECTION_LABELS: dict[str, str] = {
    "key_clinical_summary": "Key clinical summary",
    "trends": "Trends",
    "risk_flags": "Risk flags",
    "uncertainties": "Uncertainties",
    "suggested_follow_up_areas": "Suggested follow-up",
}


def section_label(section_name: str) -> str:
    return SECTION_LABELS.get(section_name, section_name.replace("_", " ").capitalize())


CODE_LABELS: dict[str, str] = {
    "unsupported_condition": "an unsupported condition",
    "unsupported_medication": "an unsupported medication",
    "unsupported_lab_trend": "an unsupported lab trend",
    "unsupported_symptom": "an unsupported symptom",
    "unsupported_recommendation": "an unsafe recommendation",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "before",
    "being",
    "by",
    "current",
    "for",
    "from",
    "given",
    "has",
    "have",
    "in",
    "include",
    "including",
    "is",
    "may",
    "of",
    "or",
    "patient",
    "reported",
    "review",
    "should",
    "so",
    "the",
    "to",
    "use",
    "with",
}

CONDITION_TERMS = {
    "diabetes",
    "hyperlipidemia",
    "hypertension",
    "ckd",
    "neuropathy",
    "retinopathy",
    "stroke",
    "myocardial",
    "cardiovascular",
}
MEDICATION_TERMS = {"metformin", "atorvastatin", "insulin", "aspirin", "lisinopril"}
LAB_TERMS = {"hba1c", "glucose", "ldl"}
SYMPTOM_TERMS = {"fatigue", "blurred vision", "vision", "pain", "dyspnea"}


@dataclass(frozen=True)
class OmissionSpec:
    code: str
    input_terms: tuple[str, ...]
    output_terms: tuple[str, ...]
    message: str


OMISSION_SPECS = [
    OmissionSpec(
        code="omission_hba1c_trend",
        input_terms=("hba1c", "7.8", "8.4"),
        output_terms=("hba1c", "increased"),
        message="HbA1c values and upward trend should be represented.",
    ),
    OmissionSpec(
        code="omission_ldl",
        input_terms=("ldl", "4.2"),
        output_terms=("ldl", "4.2"),
        message="LDL value should be represented as a clinician-review risk flag.",
    ),
    OmissionSpec(
        code="omission_fasting_glucose_uncertainty",
        input_terms=("fasting glucose", "unclear which is most recent"),
        output_terms=("fasting glucose", "unclear"),
        message="Fasting glucose recency uncertainty should be explicit.",
    ),
    OmissionSpec(
        code="omission_atorvastatin_uncertainty",
        input_terms=("atorvastatin", "unsure"),
        output_terms=("atorvastatin", "unsure"),
        message="Atorvastatin uncertainty should be explicit.",
    ),
    OmissionSpec(
        code="omission_adherence_uncertainty",
        input_terms=("adherence unclear",),
        output_terms=("adherence", "unclear"),
        message="Medication adherence uncertainty should be explicit.",
    ),
    OmissionSpec(
        code="omission_fatigue",
        input_terms=("fatigue",),
        output_terms=("fatigue",),
        message="Fatigue should be included as a reported symptom.",
    ),
    OmissionSpec(
        code="omission_blurred_vision",
        input_terms=("blurred vision",),
        output_terms=("blurred vision",),
        message="Blurred vision should be included as a reported symptom.",
    ),
    OmissionSpec(
        code="omission_diet_change",
        input_terms=("improving diet",),
        output_terms=("diet",),
        message="Recent diet improvement should be represented for clinician review.",
    ),
    OmissionSpec(
        code="omission_multi_clinic_provenance",
        input_terms=("different clinics",),
        output_terms=("different clinics",),
        message="Multi-clinic lab provenance should be represented as a data-quality issue.",
    ),
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

    issues: list[ValidationIssue] = []
    issues.extend(validate_evidence(draft, source_spans))
    issues.extend(validate_ambiguity(draft, raw_text))
    issues.extend(validate_safety(draft))
    issues.extend(validate_omissions(draft, raw_text))

    for issue in issues:
        if issue.severity == "error":
            errors.append(issue.message)
        else:
            warnings.append(issue.message)

    if not draft.safety_note.lower().startswith("draft for clinician review"):
        warnings.append("Safety note should clearly state that the output is a clinician-review draft.")

    return ValidationResult(is_valid=not errors, errors=errors, warnings=warnings, issues=issues)


def validate_evidence(
    draft: ClinicalReviewDraft,
    source_spans: list[SourceSpan],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    valid_ids = {span.id for span in source_spans}
    span_by_id = {span.id: span for span in source_spans}

    for section_name, item_index, item in iter_evidence_items(draft):
        label = section_label(section_name)
        if not item.evidence_ids:
            issues.append(
                ValidationIssue(
                    code="unsupported_claim",
                    severity="error",
                    section=section_name,
                    item_index=item_index,
                    message=f"{label} item lacks evidence: {item.text}",
                )
            )
            continue

        unknown_ids = [evidence_id for evidence_id in item.evidence_ids if evidence_id not in valid_ids]
        if unknown_ids:
            issues.append(
                ValidationIssue(
                    code="unsupported_claim",
                    severity="error",
                    section=section_name,
                    item_index=item_index,
                    evidence_ids=unknown_ids,
                    message=(
                        f"{label} item references unknown evidence IDs "
                        f"{', '.join(unknown_ids)}: {item.text}"
                    ),
                )
            )
            continue

        evidence_text = " ".join(span_by_id[evidence_id].text for evidence_id in item.evidence_ids)
        support_issue = classify_evidence_support(
            section_name, item_index, item.text, evidence_text, item.evidence_ids
        )
        if support_issue is not None:
            issues.append(support_issue)

    return issues


def validate_ambiguity(draft: ClinicalReviewDraft, raw_text: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    lowered_input = raw_text.lower()
    has_unclear_fasting_glucose = (
        "fasting glucose" in lowered_input and "unclear which is most recent" in lowered_input
    )

    if not has_unclear_fasting_glucose:
        return issues

    for index, item in enumerate(draft.trends):
        lowered_text = item.text.lower()
        if "fasting glucose" in lowered_text and any(term in lowered_text for term in TREND_TERMS):
            issues.append(
                ValidationIssue(
                    code="incorrect_temporality",
                    severity="error",
                    section="trends",
                    item_index=index,
                    evidence_ids=item.evidence_ids,
                    message="Fasting glucose recency is unclear, so the draft must not infer a fasting glucose trend.",
                )
            )

    return issues


def validate_safety(draft: ClinicalReviewDraft) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for section_name, item_index, item in iter_evidence_items(draft):
        text = item.text
        for pattern in SAFETY_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                issues.append(
                    ValidationIssue(
                        code="unsupported_recommendation",
                        severity="error",
                        section=section_name,
                        item_index=item_index,
                        evidence_ids=item.evidence_ids,
                        message=f"Unsafe directive in {section_label(section_name)}: {text}",
                    )
                )
                break
    return issues


def validate_omissions(draft: ClinicalReviewDraft, raw_text: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    lowered_input = raw_text.lower()
    output_text = draft_text(draft).lower()

    for spec in OMISSION_SPECS:
        if all(term in lowered_input for term in spec.input_terms) and not all(
            term in output_text for term in spec.output_terms
        ):
            issues.append(
                ValidationIssue(
                    code="omission",
                    severity="error",
                    message=spec.message,
                )
            )

    return issues


def classify_evidence_support(
    section_name: str,
    item_index: int,
    claim_text: str,
    evidence_text: str,
    evidence_ids: list[str],
) -> ValidationIssue | None:
    claim_tokens = content_tokens(claim_text)
    evidence_tokens = content_tokens(evidence_text)
    overlap = claim_tokens & evidence_tokens

    if not claim_tokens:
        return None

    if overlap:
        return classify_domain_specific_mismatch(
            section_name, item_index, claim_text, evidence_text, evidence_ids
        )

    return ValidationIssue(
        code="unsupported_claim",
        severity="error",
        section=section_name,
        item_index=item_index,
        evidence_ids=evidence_ids,
        message=(
            f"{section_label(section_name)} item may not be supported by its cited "
            f"evidence: {claim_text}"
        ),
    )


def classify_domain_specific_mismatch(
    section_name: str,
    item_index: int,
    claim_text: str,
    evidence_text: str,
    evidence_ids: list[str],
) -> ValidationIssue | None:
    lowered_claim = claim_text.lower()
    lowered_evidence = evidence_text.lower()

    for term in CONDITION_TERMS:
        if term in lowered_claim and term not in lowered_evidence and term not in {"cardiovascular"}:
            return issue_for("unsupported_condition", section_name, item_index, claim_text, evidence_ids)

    for term in MEDICATION_TERMS:
        if term in lowered_claim and term not in lowered_evidence:
            return issue_for("unsupported_medication", section_name, item_index, claim_text, evidence_ids)

    for term in LAB_TERMS:
        if term in lowered_claim and term not in lowered_evidence:
            return issue_for("unsupported_lab_trend", section_name, item_index, claim_text, evidence_ids)

    for term in SYMPTOM_TERMS:
        if term in lowered_claim and term not in lowered_evidence:
            return issue_for("unsupported_symptom", section_name, item_index, claim_text, evidence_ids)

    return None


def issue_for(
    code: str,
    section_name: str,
    item_index: int,
    claim_text: str,
    evidence_ids: list[str],
) -> ValidationIssue:
    label = section_label(section_name)
    code_phrase = CODE_LABELS.get(code, code.replace("_", " "))
    return ValidationIssue(
        code=code,
        severity="error",
        section=section_name,
        item_index=item_index,
        evidence_ids=evidence_ids,
        message=f"{label} item appears to contain {code_phrase}: {claim_text}",
    )


def content_tokens(text: str) -> set[str]:
    raw_tokens = re.findall(r"[A-Za-z0-9.]+", text.lower())
    return {
        token
        for token in raw_tokens
        if len(token) > 1 and token not in STOPWORDS and not token.endswith("ly")
    }


def draft_text(draft: ClinicalReviewDraft) -> str:
    return " ".join(item.text for _, _, item in iter_evidence_items(draft))


def iter_evidence_items(draft: ClinicalReviewDraft):
    for section_name in EVIDENCE_REQUIRED_SECTIONS:
        for index, item in enumerate(getattr(draft, section_name)):
            yield section_name, index, item
