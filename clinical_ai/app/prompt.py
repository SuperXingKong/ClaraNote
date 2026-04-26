from __future__ import annotations

from clinical_ai.app.schemas import SourceSpan


PROMPT_VERSION = "clinical-review-v1"


SYSTEM_INSTRUCTIONS = """You are assisting a clinician by transforming a short patient summary into a structured review draft.

Rules:
1. Use only information provided in the input.
2. Do not diagnose, prescribe, or make definitive treatment decisions.
3. Mark missing, conflicting, or unclear information explicitly as unknown or requires clinician verification.
4. Only describe trends when dates or ordering are clear.
5. For each clinical concern, include source evidence IDs from the input.
6. Use concise clinician-readable language.

Return JSON matching this schema:
{
  "key_clinical_summary": [{"text": "...", "evidence_ids": ["S1"], "confidence": "high", "requires_clinician_review": true}],
  "trends": [],
  "risk_flags": [],
  "uncertainties": [],
  "suggested_follow_up_areas": [],
  "safety_note": "Draft for clinician review only."
}
"""


def build_prompt(raw_text: str, source_spans: list[SourceSpan]) -> str:
    sources = "\n".join(f"{span.id}: {span.text}" for span in source_spans)
    return f"{SYSTEM_INSTRUCTIONS}\n\nSource spans:\n{sources}\n\nPatient summary:\n{raw_text}"
