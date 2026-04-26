from __future__ import annotations

import re

from clinical_ai.app.llm_client import LLMClient, MockLLMClient
from clinical_ai.app.prompt import PROMPT_VERSION, build_prompt
from clinical_ai.app.privacy import redact_payload
from clinical_ai.app.safety_reviewer import SecondPassSafetyReviewer
from clinical_ai.app.schemas import (
    DraftDebugInfo,
    DraftResponse,
    ResponseMetadata,
    SourceSpan,
    ValidationResult,
)
from clinical_ai.app.validators import parse_draft


class DraftPipeline:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or MockLLMClient()
        self.safety_reviewer = SecondPassSafetyReviewer()

    def process(self, raw_text: str, include_debug: bool = False) -> DraftResponse:
        source_spans = split_source_spans(raw_text)
        if not source_spans:
            return DraftResponse(
                draft=None,
                source_spans=[],
                validation=ValidationResult(
                    is_valid=False,
                    errors=["raw_text has no usable clinical content."],
                ),
                metadata=self._metadata(),
            )

        prompt = build_prompt(raw_text=raw_text, source_spans=source_spans)
        payload = self.llm_client.generate(prompt=prompt, source_spans=source_spans)
        draft, parse_errors = parse_draft(payload)
        validation = self.safety_reviewer.review(
            draft=draft,
            source_spans=source_spans,
            raw_text=raw_text,
        )

        if parse_errors:
            validation.errors.extend(parse_errors)
            validation.is_valid = False

        debug = None
        if include_debug:
            debug = DraftDebugInfo(first_pass_payload=redact_payload(payload))

        return DraftResponse(
            draft=draft,
            source_spans=source_spans,
            validation=validation,
            metadata=self._metadata(),
            debug=debug,
        )

    def _metadata(self) -> ResponseMetadata:
        return ResponseMetadata(
            prompt_version=PROMPT_VERSION,
            model_version=str(getattr(self.llm_client, "model_name", "unknown")),
            llm_provider=str(getattr(self.llm_client, "provider_name", "unknown")),
        )


def split_source_spans(raw_text: str) -> list[SourceSpan]:
    """Split input into auditable source spans while preserving offsets."""
    normalized = raw_text.strip()
    if not normalized:
        return []

    candidates = list(_line_spans(normalized))
    if len(candidates) <= 1:
        candidates = list(_sentence_spans(normalized))

    return [
        SourceSpan(id=f"S{index}", text=text.strip(), start=start, end=end)
        for index, (text, start, end) in enumerate(candidates, start=1)
        if text.strip()
    ]


def _line_spans(text: str):
    cursor = 0
    for raw_line in text.splitlines():
        start = cursor
        end = cursor + len(raw_line)
        cursor = end + 1
        cleaned = raw_line.strip(" \t-*")
        if cleaned.startswith("\u2022"):
            cleaned = cleaned[1:].strip()
        if cleaned:
            yield cleaned, start, end


def _sentence_spans(text: str):
    for match in re.finditer(r"[^.!?\n]+(?:[.!?]|$)", text):
        sentence = match.group(0).strip()
        if sentence:
            yield sentence, match.start(), match.end()
