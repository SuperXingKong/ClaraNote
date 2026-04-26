from __future__ import annotations

import re


REDACTION_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9_\-]{12,}"), "[REDACTED_API_KEY]"),
    (
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "[REDACTED_EMAIL]",
    ),
    (
        re.compile(r"\b(?:\+?\d[\s.-]?){7,}\b"),
        "[REDACTED_NUMBER]",
    ),
    (
        re.compile(r"\b(?:MRN|medical record number)\s*[:#]?\s*[A-Za-z0-9-]+\b", re.IGNORECASE),
        "[REDACTED_MRN]",
    ),
]


def redact_text(text: str | None) -> str | None:
    if text is None:
        return None

    redacted = text
    for pattern, replacement in REDACTION_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def redact_payload(payload: object) -> object:
    if isinstance(payload, str):
        return redact_text(payload)
    if isinstance(payload, list):
        return [redact_payload(item) for item in payload]
    if isinstance(payload, tuple):
        return tuple(redact_payload(item) for item in payload)
    if isinstance(payload, dict):
        return {key: redact_payload(value) for key, value in payload.items()}
    return payload

