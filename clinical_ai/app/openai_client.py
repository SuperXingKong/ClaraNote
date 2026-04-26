from __future__ import annotations

import json
import re
from typing import Any

from pydantic import BaseModel

from clinical_ai.app.config import DEFAULT_OPENAI_MODEL
from clinical_ai.app.prompt import SYSTEM_INSTRUCTIONS
from clinical_ai.app.schemas import SourceSpan


class OpenAIKeyTestResult(BaseModel):
    ok: bool
    model: str
    message: str


class OpenAIConfigurationError(RuntimeError):
    pass


class OpenAIClinicalReviewClient:
    """OpenAI-backed LLM client and API key smoke tester.

    The SDK import is lazy so local MVP tests can run without the optional
    OpenAI package installed.
    """

    def __init__(
        self,
        api_key: str | None,
        model: str = DEFAULT_OPENAI_MODEL,
        timeout_seconds: float = 30.0,
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._client = client

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self.model

    def test_api_key(self) -> OpenAIKeyTestResult:
        if not self.api_key and self._client is None:
            return OpenAIKeyTestResult(
                ok=False,
                model=self.model,
                message="OPENAI_API_KEY is not set.",
            )

        try:
            response = self._ensure_client().responses.create(
                model=self.model,
                instructions="You are an API connectivity test. Return exactly: ok",
                input="Return exactly: ok",
                max_output_tokens=16,
            )
            output_text = _extract_output_text(response).strip().lower()
        except Exception as exc:  # noqa: BLE001 - return a user-safe diagnostic.
            return OpenAIKeyTestResult(
                ok=False,
                model=self.model,
                message=_sanitize_error(str(exc), self.api_key),
            )

        if "ok" not in output_text:
            return OpenAIKeyTestResult(
                ok=False,
                model=self.model,
                message=f"OpenAI responded, but the smoke-test output was unexpected: {output_text!r}",
            )

        return OpenAIKeyTestResult(
            ok=True,
            model=self.model,
            message=f"OpenAI API key accepted; model '{self.model}' responded.",
        )

    def generate(self, prompt: str, source_spans: list[SourceSpan]) -> dict[str, Any]:
        del source_spans
        response = self._ensure_client().responses.create(
            model=self.model,
            instructions=SYSTEM_INSTRUCTIONS,
            input=prompt,
            max_output_tokens=2500,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "ClinicalReviewDraft",
                    "schema": clinical_review_draft_json_schema(),
                    "strict": True,
                }
            },
        )
        output_text = _extract_output_text(response)
        return _parse_json_object(output_text)

    def _ensure_client(self) -> Any:
        if self._client is not None:
            return self._client
        if not self.api_key:
            raise OpenAIConfigurationError("OPENAI_API_KEY is not set.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise OpenAIConfigurationError(
                "OpenAI SDK is not installed. Run: pip install -e \".[dev]\" or pip install openai"
            ) from exc

        self._client = OpenAI(api_key=self.api_key, timeout=self.timeout_seconds)
        return self._client


def _extract_output_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str):
        return output_text

    if isinstance(response, dict):
        if isinstance(response.get("output_text"), str):
            return response["output_text"]
        output = response.get("output", [])
    else:
        output = getattr(response, "output", [])

    parts: list[str] = []
    for item in output or []:
        content = item.get("content", []) if isinstance(item, dict) else getattr(item, "content", [])
        for block in content or []:
            if isinstance(block, dict):
                text = block.get("text")
            else:
                text = getattr(block, "text", None)
            if isinstance(text, str):
                parts.append(text)

    return "".join(parts)


def _parse_json_object(output_text: str) -> dict[str, Any]:
    stripped = output_text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL)
    if fenced:
        stripped = fenced.group(1).strip()
    return json.loads(stripped)


def _sanitize_error(message: str, api_key: str | None) -> str:
    sanitized = message
    if api_key:
        sanitized = sanitized.replace(api_key, "[REDACTED_OPENAI_API_KEY]")
    sanitized = re.sub(r"sk-[A-Za-z0-9_\-]{12,}", "[REDACTED_OPENAI_API_KEY]", sanitized)
    return sanitized


def clinical_review_draft_json_schema() -> dict[str, Any]:
    evidence_item = {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "text",
            "evidence_ids",
            "confidence",
            "requires_clinician_review",
        ],
        "properties": {
            "text": {"type": "string"},
            "evidence_ids": {"type": "array", "items": {"type": "string"}},
            "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
            "requires_clinician_review": {"type": "boolean"},
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "key_clinical_summary",
            "trends",
            "risk_flags",
            "uncertainties",
            "suggested_follow_up_areas",
            "safety_note",
        ],
        "properties": {
            "key_clinical_summary": {"type": "array", "items": evidence_item},
            "trends": {"type": "array", "items": evidence_item},
            "risk_flags": {"type": "array", "items": evidence_item},
            "uncertainties": {"type": "array", "items": evidence_item},
            "suggested_follow_up_areas": {"type": "array", "items": evidence_item},
            "safety_note": {"type": "string"},
        },
    }
