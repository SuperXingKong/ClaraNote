from clinical_ai.app.schemas import ClinicalReviewDraft, EvidenceBackedItem, SourceSpan
from clinical_ai.app.validators import validate_all


def test_claim_without_evidence_fails():
    draft = ClinicalReviewDraft(
        key_clinical_summary=[
            EvidenceBackedItem(
                text="Patient has type 2 diabetes.",
                evidence_ids=[],
                confidence="high",
            )
        ],
        trends=[],
        risk_flags=[],
        uncertainties=[],
        suggested_follow_up_areas=[],
        safety_note="Draft for clinician review only.",
    )
    spans = [SourceSpan(id="S1", text="History of type 2 diabetes.", start=0, end=27)]

    result = validate_all(draft=draft, source_spans=spans, raw_text=spans[0].text)

    assert not result.is_valid
    assert any("lacks evidence" in error for error in result.errors)


def test_unknown_evidence_id_fails():
    draft = ClinicalReviewDraft(
        key_clinical_summary=[],
        trends=[],
        risk_flags=[
            EvidenceBackedItem(
                text="LDL is elevated for clinician review.",
                evidence_ids=["S99"],
                confidence="medium",
            )
        ],
        uncertainties=[],
        suggested_follow_up_areas=[],
        safety_note="Draft for clinician review only.",
    )
    spans = [SourceSpan(id="S1", text="LDL: 4.2 mmol/L", start=0, end=15)]

    result = validate_all(draft=draft, source_spans=spans, raw_text=spans[0].text)

    assert not result.is_valid
    assert any("unknown evidence IDs" in error for error in result.errors)
