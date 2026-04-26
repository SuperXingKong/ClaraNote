from __future__ import annotations

from clinical_ai.app.schemas import ClinicalReviewDraft, SourceSpan, ValidationResult
from clinical_ai.app.validators import validate_all


class SecondPassSafetyReviewer:
    """Runs deterministic safety checks after the model produces a first-pass draft."""

    def review(
        self,
        draft: ClinicalReviewDraft | None,
        source_spans: list[SourceSpan],
        raw_text: str,
    ) -> ValidationResult:
        return validate_all(draft=draft, source_spans=source_spans, raw_text=raw_text)
