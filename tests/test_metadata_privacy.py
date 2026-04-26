from clinical_ai.app.pipeline import DraftPipeline
from clinical_ai.app.privacy import redact_payload, redact_text
from clinical_ai.app.schemas import ClinicianReviewRecord


def test_response_includes_prompt_and_model_metadata():
    response = DraftPipeline().process("58-year-old female with type 2 diabetes.")

    assert response.metadata.prompt_version == "clinical-review-v1"
    assert response.metadata.llm_provider == "mock"
    assert response.metadata.model_version == "mock-clinical-review-v1"


def test_clinician_review_record_accepts_reason_codes():
    record = ClinicianReviewRecord(
        draft_id="draft-1",
        decision="edit",
        reason_codes=["wrong_evidence", "unclear_wording"],
        comments="Evidence citation should be clearer.",
    )

    assert record.decision == "edit"
    assert "wrong_evidence" in record.reason_codes


def test_redaction_removes_common_sensitive_values():
    text = "Key sk-testsecret1234567890 email user@example.com MRN: ABC-123 phone +1 555-123-4567"

    redacted = redact_text(text)

    assert "sk-testsecret" not in redacted
    assert "user@example.com" not in redacted
    assert "ABC-123" not in redacted
    assert "555-123" not in redacted


def test_redact_payload_recurses_nested_structures():
    payload = {"comments": ["contact me at user@example.com"]}

    assert redact_payload(payload) == {"comments": ["contact me at [REDACTED_EMAIL]"]}

