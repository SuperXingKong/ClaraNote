from clinical_ai.app.llm_client import LLMClient
from clinical_ai.app.pipeline import DraftPipeline
from clinical_ai.app.schemas import SourceSpan


class FailingLLMClient:
    provider_name = "test"
    model_name = "must-not-run"

    def generate(self, prompt: str, source_spans: list[SourceSpan]):
        raise AssertionError("LLM client should not be called when direct identifiers are present")


def test_privacy_gate_blocks_direct_identifiers_before_llm_call():
    client: LLMClient = FailingLLMClient()
    pipeline = DraftPipeline(llm_client=client)

    response = pipeline.process(
        "Patient name: Jane Smith\nMRN: ABC-123\nEmail: jane@example.com\n58-year-old female with diabetes."
    )

    assert not response.validation.is_valid
    assert response.draft is None
    assert "Potential direct identifiers detected" in response.validation.errors[0]
    returned_text = " ".join(span.text for span in response.source_spans)
    assert "Jane Smith" not in returned_text
    assert "ABC-123" not in returned_text
    assert "jane@example.com" not in returned_text
