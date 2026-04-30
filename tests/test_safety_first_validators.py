from claranote.app.schemas import ClinicalReviewDraft, EvidenceBackedItem, SourceSpan
from claranote.app.validators import validate_all


def test_evidence_semantic_mismatch_fails():
    spans = [SourceSpan(id="S1", text="LDL: 4.2 mmol/L", start=0, end=15)]
    draft = ClinicalReviewDraft(
        key_clinical_summary=[
            EvidenceBackedItem(
                text="Patient has hypertension.",
                evidence_ids=["S1"],
                confidence="high",
            )
        ],
        trends=[],
        risk_flags=[],
        uncertainties=[],
        suggested_follow_up_areas=[],
        safety_note="Draft for clinician review only.",
    )

    result = validate_all(draft=draft, source_spans=spans, raw_text=spans[0].text)

    assert not result.is_valid
    assert any(issue.code in {"unsupported_claim", "unsupported_condition"} for issue in result.issues)


def test_assignment_omission_checker_catches_missing_ldl():
    raw_text = "LDL: 4.2 mmol/L"
    spans = [SourceSpan(id="S1", text=raw_text, start=0, end=len(raw_text))]
    draft = ClinicalReviewDraft(
        key_clinical_summary=[],
        trends=[],
        risk_flags=[],
        uncertainties=[],
        suggested_follow_up_areas=[],
        safety_note="Draft for clinician review only.",
    )

    result = validate_all(draft=draft, source_spans=spans, raw_text=raw_text)

    assert not result.is_valid
    assert any(issue.code == "omission" for issue in result.issues)


def test_pipeline_can_return_redacted_debug_payload(openai_pipeline):
    response = openai_pipeline.process(
        "58-year-old female with type 2 diabetes.",
        include_debug=True,
    )

    assert response.debug is not None
    assert response.debug.first_pass_payload is not None


def test_validation_issues_carry_section_and_item_index():
    spans = [SourceSpan(id="S1", text="LDL: 4.2 mmol/L", start=0, end=15)]
    draft = ClinicalReviewDraft(
        key_clinical_summary=[
            EvidenceBackedItem(
                text="Patient has hypertension.",
                evidence_ids=["S1"],
                confidence="high",
            ),
            EvidenceBackedItem(
                text="LDL is 4.2 mmol/L.",
                evidence_ids=["S1"],
                confidence="high",
            ),
        ],
        trends=[],
        risk_flags=[],
        uncertainties=[],
        suggested_follow_up_areas=[],
        safety_note="Draft for clinician review only.",
    )

    result = validate_all(draft=draft, source_spans=spans, raw_text=spans[0].text)

    keyed = [
        (issue.section, issue.item_index)
        for issue in result.issues
        if issue.section == "key_clinical_summary"
    ]
    assert ("key_clinical_summary", 0) in keyed


def test_routine_item_does_not_raise_validation_issue():
    spans = [SourceSpan(id="S1", text="LDL: 4.2 mmol/L", start=0, end=15)]
    draft = ClinicalReviewDraft(
        key_clinical_summary=[
            EvidenceBackedItem(
                text="LDL is 4.2 mmol/L.",
                evidence_ids=["S1"],
                confidence="high",
                requires_clinician_review=False,
            )
        ],
        trends=[],
        risk_flags=[],
        uncertainties=[],
        suggested_follow_up_areas=[],
        safety_note="Draft for clinician review only.",
    )

    result = validate_all(draft=draft, source_spans=spans, raw_text=spans[0].text)

    assert all(
        "not marked for clinician review" not in issue.message for issue in result.issues
    )

