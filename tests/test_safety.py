from clinical_ai.app.schemas import ClinicalReviewDraft, EvidenceBackedItem, SourceSpan
from clinical_ai.app.validators import validate_all


def test_prescriptive_instruction_fails_safety_validation():
    spans = [SourceSpan(id="S1", text="LDL: 4.2 mmol/L", start=0, end=15)]
    draft = ClinicalReviewDraft(
        key_clinical_summary=[],
        trends=[],
        risk_flags=[],
        uncertainties=[],
        suggested_follow_up_areas=[
            EvidenceBackedItem(
                text="Increase atorvastatin dose.",
                evidence_ids=["S1"],
                confidence="medium",
            )
        ],
        safety_note="Draft for clinician review only.",
    )

    result = validate_all(draft=draft, source_spans=spans, raw_text=spans[0].text)

    assert not result.is_valid
    assert any("Unsafe directive" in error for error in result.errors)
