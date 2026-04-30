from __future__ import annotations

from typing import Any, Protocol

from clinical_ai.app.schemas import SourceSpan


class LLMClient(Protocol):
    """Pluggable LLM provider contract used by `DraftPipeline`.

    The MVP ships with a single OpenAI implementation
    (`clinical_ai.app.openai_client.OpenAIClinicalReviewClient`). This Protocol
    exists so additional providers (Anthropic, Gemini, on-prem, …) can be
    swapped in without touching the pipeline.
    """

    provider_name: str
    model_name: str

    def generate(self, prompt: str, source_spans: list[SourceSpan]) -> dict[str, Any]:
        """Return a draft payload that can be parsed as `ClinicalReviewDraft`."""
