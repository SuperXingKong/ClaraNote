from claranote.app.schemas import ClinicalReviewDraft, EvidenceBackedItem, SourceSpan
from claranote.app.validators import validate_all


def test_unclear_fasting_glucose_recency_blocks_trend_claim():
    raw_text = "Fasting glucose: 6.5 mmol/L, 8.9 mmol/L (unclear which is most recent)"
    spans = [SourceSpan(id="S1", text=raw_text, start=0, end=len(raw_text))]
    draft = ClinicalReviewDraft(
        key_clinical_summary=[],
        trends=[
            EvidenceBackedItem(
                text="Fasting glucose increased from 6.5 to 8.9 mmol/L.",
                evidence_ids=["S1"],
                confidence="high",
            )
        ],
        risk_flags=[],
        uncertainties=[],
        suggested_follow_up_areas=[],
        safety_note="Draft for clinician review only.",
    )

    result = validate_all(draft=draft, source_spans=spans, raw_text=raw_text)

    assert not result.is_valid
    assert any("must not infer a fasting glucose trend" in error for error in result.errors)
