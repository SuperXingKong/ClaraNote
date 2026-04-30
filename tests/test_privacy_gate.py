from clinical_ai.app.pipeline import DraftPipeline


def test_privacy_gate_blocks_direct_identifiers_before_llm_call(openai_client):
    """The pre-LLM privacy gate must intercept direct identifiers BEFORE any
    HTTP call to OpenAI. We assert this by wiring a real `OpenAIClinicalReviewClient`
    into the pipeline: if the gate fails to intercept, the pipeline would call
    OpenAI and we would see a real API response with `draft != None`.
    """
    pipeline = DraftPipeline(llm_client=openai_client)

    response = pipeline.process(
        "Patient name: Jane Smith\nMRN: ABC-123\nEmail: jane@example.com\n"
        "58-year-old female with diabetes."
    )

    assert not response.validation.is_valid
    assert response.draft is None, "LLM was reached despite direct identifiers being present"
    assert "Potential direct identifiers detected" in response.validation.errors[0]
    returned_text = " ".join(span.text for span in response.source_spans)
    assert "Jane Smith" not in returned_text
    assert "ABC-123" not in returned_text
    assert "jane@example.com" not in returned_text
