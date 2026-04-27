from __future__ import annotations

import re
from dataclasses import dataclass


REDACTION_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9_\-]{12,}"), "[REDACTED_API_KEY]"),
    (
        re.compile(
            r"\b(?:patient[ \t]+name|name)[ \t]*[:#][ \t]*[A-Z][A-Za-z]+(?:[ \t]+[A-Z][A-Za-z]+)+\b",
            re.IGNORECASE,
        ),
        "[REDACTED_NAME]",
    ),
    (
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "[REDACTED_EMAIL]",
    ),
    (
        re.compile(r"\b(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b"),
        "[REDACTED_PHONE]",
    ),
    (
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "[REDACTED_SSN]",
    ),
    (
        re.compile(r"\b(?:MRN|medical record number)\s*[:#]?\s*[A-Za-z0-9-]+\b", re.IGNORECASE),
        "[REDACTED_MRN]",
    ),
    (
        re.compile(
            r"\b\d{1,6}\s+[A-Z][A-Za-z0-9.]*\s+"
            r"(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b",
            re.IGNORECASE,
        ),
        "[REDACTED_ADDRESS]",
    ),
]

DIRECT_IDENTIFIER_PATTERNS = [
    ("api_key", "API key", REDACTION_PATTERNS[0][0]),
    ("name", "patient name", REDACTION_PATTERNS[1][0]),
    ("email", "email address", REDACTION_PATTERNS[2][0]),
    ("phone", "phone number", REDACTION_PATTERNS[3][0]),
    ("ssn", "social security number", REDACTION_PATTERNS[4][0]),
    ("medical_record_number", "medical record number", REDACTION_PATTERNS[5][0]),
    ("address", "street address", REDACTION_PATTERNS[6][0]),
]


@dataclass(frozen=True)
class PrivacyFinding:
    code: str
    label: str


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


def detect_direct_identifiers(text: str | None) -> list[PrivacyFinding]:
    if not text:
        return []

    findings: list[PrivacyFinding] = []
    for code, label, pattern in DIRECT_IDENTIFIER_PATTERNS:
        if pattern.search(text):
            findings.append(PrivacyFinding(code=code, label=label))
    return findings
