# Clinical Review Draft Generator — Submission Write-up

> Mapped directly to the four deliverables and four grading criteria in the
> assignment brief. Implementation lives in [`clinical_ai/`](clinical_ai/) and
> [`web/`](web/); end-to-end deployment is in [`docker-compose.yml`](docker-compose.yml).

## Deliverable 1 — Prompt

[`clinical_ai/app/prompt.py`](clinical_ai/app/prompt.py) — version `clinical-review-v2`.
The system prompt enforces six rules a clinician would expect:

1. Use only information from the input (no external facts).
2. Never diagnose, prescribe, or make treatment decisions.
3. Mark missing, conflicting, or unclear data as unknown / requires verification.
4. Only describe a trend when dates or ordering are clear.
5. Cite source-span IDs (`S1`, `S2`, …) for every clinical claim.
6. Use concise clinician-readable language.

The prompt also explains the per-item `requires_clinician_review` UI hint:
`true` for inference / risk / uncertainty / follow-up, `false` only for
verbatim demographics or transcribed symptom lists. This prioritises clinician
attention without over-flagging routine facts. **Submission-grade outputs from
real `gpt-5.4` calls live at
[`samples/assignment_output.openai.json`](samples/assignment_output.openai.json).**

## Deliverable 2 — Output structure

Pydantic-validated JSON in [`clinical_ai/app/schemas.py`](clinical_ai/app/schemas.py),
projected verbatim into a strict OpenAI Structured Outputs schema in
[`openai_client.py:165`](clinical_ai/app/openai_client.py#L165):

```jsonc
{
  "draft": {
    "key_clinical_summary":      [ EvidenceBackedItem, ... ],
    "trends":                    [ EvidenceBackedItem, ... ],
    "risk_flags":                [ EvidenceBackedItem, ... ],
    "uncertainties":             [ EvidenceBackedItem, ... ],
    "suggested_follow_up_areas": [ EvidenceBackedItem, ... ],
    "safety_note": "Draft for clinician review only."
  },
  "source_spans":  [ {id, text, start, end} ],   // citation-sized chunks
  "validation":    { is_valid, errors[], warnings[], issues[] },
  "metadata":      { draft_id, prompt_version, model_version, llm_provider }
}

// where EvidenceBackedItem = { text, evidence_ids[], confidence, requires_clinician_review }
```

Every required minimum field from the brief is present; `evidence_ids` and
`source_spans` make every claim independently traceable to the input.

## Deliverable 3 — Sample output

Two reproducible samples for the exact assignment patient summary:

| File | Provider | Notes |
|---|---|---|
| [`samples/assignment_output.mock.json`](samples/assignment_output.mock.json) | Deterministic mock | Same output across machines; used in unit tests. |
| [`samples/assignment_output.openai.json`](samples/assignment_output.openai.json) | OpenAI `gpt-5.4` via Structured Outputs | Real-model output; passes the safety reviewer. |

Both:
- correctly carry forward HbA1c trend (Jan → March),
- correctly **decline** to claim a fasting-glucose trend (recency unclear),
- flag LDL 4.2 mmol/L as a cardiovascular risk in a diabetes context,
- surface multi-clinic provenance and adherence uncertainty as data-quality issues,
- cite source spans for every clinical claim.

## Deliverable 4 — Failure modes, mitigation & validation

| Failure mode | Detection | Mitigation |
|---|---|---|
| **Hallucination** (claim with no support in input) | `validate_evidence` lexical overlap + missing/unknown evidence-id check; second-pass safety reviewer in `safety_reviewer.py`. | Issues raised inline on the offending item; clinician must accept/edit/reject before draft is used. |
| **Domain mismatch** (e.g. "diabetes-related" claim citing a labs span without that word) | `classify_domain_specific_mismatch` over `CONDITION/MEDICATION/LAB/SYMPTOM` term sets. | Tagged as `unsupported_condition` etc.; conservative — false-positives prefer over false-negatives in clinical settings. |
| **Inferred trend on ambiguous data** | `validate_ambiguity` rejects fasting-glucose trend statements when the input is "unclear which is most recent". | Hard error; routes the item to the Uncertainties section. |
| **Unsafe directive** ("prescribe", "increase dose", "start statin") | `validate_safety` regex over `SAFETY_PATTERNS`. | Hard error; blocks `is_valid`. |
| **Omission of assignment-critical facts** (HbA1c trend, LDL value, atorvastatin uncertainty, multi-clinic provenance, etc.) | 9 `OmissionSpec` rules in `validators.py:107` cross-check input vs output. | Issue per spec; surfaced in evaluation report (`/v1/evaluation`). |
| **Direct identifiers in input (HIPAA risk)** | `privacy.detect_direct_identifiers` runs **before** the LLM call. | Pipeline returns a redacted span list and refuses to call the model. |
| **Model overconfidence on ambiguous input** | `requires_clinician_review` per-item flag; `safety_note` whole-draft flag; second-pass deterministic reviewer. | UI prioritises non-routine items; routine items collapse via `<details>`. |
| **Schema drift / malformed JSON** | `parse_draft` (Pydantic `model_validate`) + OpenAI Structured Outputs `strict: true`. | Invalid drafts surface as `errors` with `is_valid=false`. |

**Human-in-the-loop design.** The frontend forces a deliberate decision per
item: Accept / Edit / Reject / Wrong evidence / Missing risk, with a reason-code
dialog. Submissions persist to `POST /v1/reviews` as redacted JSONL with a
30-day retention policy (`review_store.py`) — auditable without storing PHI.

**Continuous validation.** A 5-case golden set (`evaluation.py`) covers the
assignment patient plus stress variants (ambiguous fasting glucose, missing
adherence, conflicting LDL context, multi-source labs). The same metrics —
hallucination count, omission count, evidence coverage rate, ambiguity
failures, clinician edit rate — are exposed at `GET /v1/evaluation` and
rendered in the right-hand panel.

---

## Grading criteria — at a glance

| What you're looking for | Where it lives |
|---|---|
| **Handles ambiguity and conflicting data** | `validate_ambiguity` (fasting-glucose recency); 9 `OmissionSpec`s; prompt rules 3–4; UI Uncertainties section |
| **Structures LLM outputs** | Pydantic schema + OpenAI Structured Outputs strict schema; every claim carries evidence IDs + confidence + review flag |
| **Awareness of failure modes** | 8-category hallucination taxonomy; second-pass safety reviewer; pre-LLM privacy gate; design-control registry at `/v1/design-controls` mapping each safeguard to FDA/WHO/HL7/NIST/HHS/W3C/CHAI references |
| **Safe, reliable systems** | Two-stage validation (Pydantic + safety reviewer); deterministic mock fallback; redacted JSONL audit trail with retention; Dockerised reproducible deployment with `/healthz` |

## Implementation notes

- **Reproducible deployment:** `docker compose up -d --build` brings up the
  backend (FastAPI/uvicorn) + frontend (Vite/Nginx with `/api/*` reverse-proxy).
  Defaults to the deterministic mock provider — no API key required to demo.
  Set `LLM_PROVIDER=openai` + `OPENAI_API_KEY` in `.env` to use `gpt-5.4`.
- **Tests:** `pytest` runs 41 backend tests (privacy gate, evidence validation,
  ambiguity, omissions, FHIR adapter, review store retention, evaluation API,
  schema, OpenAI client). Frontend builds with `tsc -b && vite build`.
- **Live UI:** open <http://localhost:8090> after `docker compose up`. Click
  any "Detected issues" card on the right to highlight the offending draft
  item in the centre column.

## What I would add for production

- Replace lexical evidence checks with an NLI / clinically-tuned entailment
  reviewer (current rules over-flag e.g. "diabetes-related labs" when the cited
  span only contains HbA1c).
- Real clinician-authenticated review storage; current JSONL is a local audit
  prototype, not a multi-tenant store.
- Privacy/security/authorization controls before any contact with real PHI.

---

_Hours spent: ~12_ <!-- update before submission -->
