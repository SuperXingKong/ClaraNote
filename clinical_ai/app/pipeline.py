from __future__ import annotations

import re
from dataclasses import dataclass

from clinical_ai.app.llm_client import LLMClient, MockLLMClient
from clinical_ai.app.prompt import PROMPT_VERSION, build_prompt
from clinical_ai.app.privacy import detect_direct_identifiers, redact_payload, redact_text
from clinical_ai.app.safety_reviewer import SecondPassSafetyReviewer
from clinical_ai.app.schemas import (
    DraftDebugInfo,
    DraftResponse,
    ResponseMetadata,
    SourceSpan,
    ValidationIssue,
    ValidationResult,
)
from clinical_ai.app.validators import parse_draft


@dataclass(frozen=True)
class LineUnit:
    text: str
    start: int
    end: int
    is_heading: bool


class DraftPipeline:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or MockLLMClient()
        self.safety_reviewer = SecondPassSafetyReviewer()

    def process(self, raw_text: str, include_debug: bool = False) -> DraftResponse:
        privacy_findings = detect_direct_identifiers(raw_text)
        if privacy_findings:
            finding_labels = ", ".join(finding.label for finding in privacy_findings)
            redacted_text = redact_text(raw_text) or ""
            message = (
                "Potential direct identifiers detected before LLM processing: "
                f"{finding_labels}. Remove or de-identify identifiers before generating a draft."
            )
            return DraftResponse(
                draft=None,
                source_spans=split_source_spans(redacted_text),
                validation=ValidationResult(
                    is_valid=False,
                    errors=[message],
                    issues=[
                        ValidationIssue(
                            code="privacy_direct_identifier",
                            severity="error",
                            message=message,
                        )
                    ],
                ),
                metadata=self._metadata(),
            )

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
    """Split input into citation-sized source spans while preserving offsets."""
    normalized = raw_text.strip()
    if not normalized:
        return []

    line_units = list(_line_units(normalized))
    candidates = list(_section_spans(line_units))
    if not candidates:
        candidates = list(_sentence_spans(normalized))

    return [
        SourceSpan(id=f"S{index}", text=text.strip(), start=start, end=end)
        for index, (text, start, end) in enumerate(candidates, start=1)
        if text.strip()
    ]


def _line_units(text: str) -> list[LineUnit]:
    units: list[LineUnit] = []
    cursor = 0
    for raw_line in text.splitlines():
        start = cursor
        end = cursor + len(raw_line)
        cursor = end + 1
        cleaned = _clean_line(raw_line)
        if cleaned:
            units.append(
                LineUnit(
                    text=cleaned,
                    start=start,
                    end=end,
                    is_heading=_looks_like_heading(cleaned),
                )
            )
    return units


def _section_spans(units: list[LineUnit]) -> list[tuple[str, int, int]]:
    if not units:
        return []

    if not any(unit.is_heading for unit in units):
        if len(units) <= 1:
            return []
        return [(unit.text, unit.start, unit.end) for unit in units if _is_informative_text(unit.text)]

    sections: list[tuple[list[str], int, int]] = []
    pending_heading: LineUnit | None = None
    current_lines: list[str] = []
    current_start = 0
    current_end = 0

    def flush_current() -> None:
        nonlocal current_lines, current_start, current_end
        if current_lines and any(_is_informative_text(line) for line in current_lines):
            sections.append((current_lines, current_start, current_end))
        current_lines = []
        current_start = 0
        current_end = 0

    for unit in units:
        if unit.is_heading:
            flush_current()
            pending_heading = unit
            continue

        if pending_heading is not None:
            current_lines = [pending_heading.text, unit.text]
            current_start = pending_heading.start
            current_end = unit.end
            pending_heading = None
        elif current_lines:
            current_lines.append(unit.text)
            current_end = unit.end
        else:
            current_lines = [unit.text]
            current_start = unit.start
            current_end = unit.end

    flush_current()

    return [
        (_format_section_text(lines), start, end)
        for lines, start, end in sections
        if _is_informative_text(_format_section_text(lines))
    ]


def _clean_line(raw_line: str) -> str:
    cleaned = raw_line.strip(" \t-*")
    if cleaned.startswith("\u2022"):
        cleaned = cleaned[1:].strip()
    return cleaned


def _looks_like_heading(text: str) -> bool:
    return text.endswith(":")


def _is_informative_text(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if _looks_like_heading(stripped):
        return False
    return bool(re.search(r"[A-Za-z0-9]", stripped))


def _format_section_text(lines: list[str]) -> str:
    if len(lines) <= 1:
        return "".join(lines)
    heading, *body = lines
    if _looks_like_heading(heading):
        return heading + "\n" + "\n".join(body)
    return "\n".join(lines)


def _sentence_spans(text: str):
    for match in re.finditer(r".+?(?:[.!?](?=\s|$)|$)", text):
        sentence = match.group(0).strip()
        if sentence:
            yield sentence, match.start(), match.end()
