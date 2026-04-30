# Clinical Review Draft Generator — Submission Write-up

> Mapped directly to the four deliverables and four grading criteria in the
> assignment brief. Implementation lives in [`clinical_ai/`](clinical_ai/) and
> [`web/`](web/); end-to-end deployment is in [`docker-compose.yml`](docker-compose.yml).

## System overview

```
            ┌─────────────────────────────────────────────────────────────────┐
            │                      Browser (Nginx :8090)                      │
            │  React 19 SPA — input panel · draft sections · validation panel │
            └───────┬─────────────────────────────────────┬───────────────────┘
                    │ /api/*  (reverse-proxy)             │ static
                    ▼                                     ▼
        ┌───────────────────────────┐            ┌────────────────┐
        │  FastAPI (uvicorn :8000)  │            │  dist/ (Vite)  │
        │  api.py: 7 endpoints      │            └────────────────┘
        └───────┬───────────────────┘
                │
                ▼
   pipeline.process(raw_text)
                │
                ├─► detect_direct_identifiers ── PHI? ──► return validation error (NO LLM CALL)
                │
                ├─► split_source_spans          (S1, S2, …)
                │
                ├─► build_prompt                → SYSTEM_INSTRUCTIONS + spans + raw_text
                │
                ├─► LLMClient.generate(prompt)  ──┬─► MockLLMClient    (default)
                │                                 └─► OpenAI Responses API
                │                                     · strict json_schema
                │                                     · gpt-5.4 / gpt-5 / gpt-4.1
                │
                ├─► parse_draft                 (Pydantic validate)
                │
                ├─► SecondPassSafetyReviewer    → validate_evidence
                │                                 validate_ambiguity
                │                                 validate_safety
                │                                 validate_omissions
                │
                └─► DraftResponse {draft, source_spans, validation, metadata}

         Side channel:  POST /v1/reviews ─► JsonlReviewStore (.data/reviews.jsonl, 30-day retention, redacted)
```

**Trust boundaries.** The privacy gate fires *before* any LLM call, so direct
identifiers cannot be exfiltrated even if every later layer fails. The safety
reviewer fires *after* the LLM call, so prescriptive language slipping past
the prompt still gets caught by deterministic Python.

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

## Design trade-offs (deliberate choices)

These are the decisions where I picked one option over another. Each was a
conscious trade-off, not an oversight.

| Decision | Alternative considered | Why I chose it |
|---|---|---|
| **Two-stage validation** (OpenAI Structured Outputs *and* Pydantic + custom safety reviewer) | Trust Structured Outputs alone | `strict: true` only enforces *shape*. It cannot catch unsafe directives, evidence/claim mismatches, or ambiguity violations. Provider failures (rate limits, version regression, fallback to a different model) also need a defence in depth. Cost: a few ms of CPU per request. |
| **Lexical evidence checker** | NLI / clinically-tuned entailment model | Reviewable in ~50 lines, deterministic, zero extra dependency, easy to unit-test. Documented limitation: over-flags e.g. *"diabetes-related labs"* citing a span that only contains HbA1c. **Next step is not "switch to NLI" — it's an alias table** (`diabetes ↔ hba1c, glucose`) which removes 80 % of the false positives at zero inference cost. |
| **9 hard-coded `OmissionSpec`s for the assignment patient** | Generic LLM-judge omission scorer | The assignment provides an explicit input. Hard-coded specs let me ship a deterministic golden set and CI test in a day. A judge LLM would inflate cost and add a second source of hallucination. The generic case is the next iteration. |
| **JSONL audit log on a Docker volume** | SQLite / Postgres / cloud DB | The MVP is a single-tenant local prototype. JSONL is `cat`-able for debugging, easy to redact, easy to back up, and the retention purge is one function. A real deployment would swap this for an authenticated, multi-tenant store before ever touching PHI. |
| **Mock LLM client as the default provider** | Always require `OPENAI_API_KEY` | Reviewers can `docker compose up -d` and demo the full UI without paying or signing up. Tests run offline. The same `LLMClient` Protocol means the OpenAI client is a one-line swap. |
| **Per-item `requires_clinician_review`** is a UI hint, not a safety gate | Treat every `false` as an error | The whole-draft `safety_note` is the gate. Treating per-item `false` as an error caused over-reporting on benign demographics (`58-year-old female...`). The UI now folds `false` items via `<details>` so cognitive load drops on routine items while inferred / risky items stay visible. |
| **No LangChain / no agent framework** | LangChain or Pydantic AI for orchestration | The flow is linear (prompt → LLM → parse → validate → return). A framework adds an abstraction without removing any of the validation code. I'd reach for one when I need tool calling, retrieval, or multi-step planning. |
| **Frontend: no client-side state library beyond TanStack Query** | Redux / Zustand / Jotai | Three top-level state items (`draftResponse`, `selectedItemKey`, `reviews`) live in `useState`. A store would be ceremony. |
| **`gpt-5.4` as default** | Pin to a specific snapshot date | Snapshots fall out of access faster than the rolling alias does. README documents `gpt-5`, `gpt-5-mini`, `gpt-4.1` as drop-in fallbacks for reviewers without `gpt-5.4` access. |

## What I would build next, in order

1. **Synonym table for the lexical evidence checker** (1–2 hours, removes
   the most visible false positives without changing inference cost).
2. **NLI-based entailment reviewer** behind a feature flag, A/B'd against
   the lexical checker on the golden set so the error-rate trade-off is
   measured, not assumed.
3. **Clinician-authenticated review storage** — replace the local JSONL with
   an authenticated multi-tenant store; required before real PHI.
4. **Cost / latency tests** in CI — record `tokens_in / tokens_out / wall_ms`
   per golden case so a model swap is measurable.
5. **Privacy / security / authorization controls** — formal review before any
   real-PHI contact.

---

_Hours spent: ~22_ (≈10 h core engine + tests, ≈6 h frontend, ≈3 h
deployment / Docker, ≈3 h docs + sample outputs). Substantial portions were
drafted with AI assistance (Claude Code) for boilerplate, refactor mechanics,
and Tailwind class wiring; design choices, prompt iteration, validator rules,
and the trade-off table above are mine — happy to walk through any of them
in interview._
