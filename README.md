# ClaraNote — Clinical Review Draft Generator

This MVP turns a plain-text patient summary into a structured clinician-review draft. It demonstrates:

- Structured output with Pydantic schemas
- Evidence-backed clinical summary items
- Explicit uncertainty handling
- Safety validation that blocks direct diagnosis or treatment instructions
- A minimal FastAPI endpoint at `POST /v1/drafts`

## Assignment submission

For the AI Engineer assignment review, the four deliverables are:

| # | Deliverable | Where |
|---|---|---|
| 1 | Prompt | [`claranote/app/prompt.py`](claranote/app/prompt.py) |
| 2 | Output structure | [`claranote/app/schemas.py`](claranote/app/schemas.py) (`ClinicalReviewDraft`) |
| 3 | Sample output | [`samples/assignment_output.openai.json`](samples/assignment_output.openai.json) (real `gpt-5.4`) plus two failure-case samples in [`samples/`](samples/) |
| 4 | Failure modes & write-up | [`WRITEUP.md`](WRITEUP.md) |

Total time spent: about 24 hours over 4 days (2026-04-27 → 2026-04-30, SGT).

## Run with Docker (recommended)

The repository ships with a two-service compose stack:

- `backend` — FastAPI/uvicorn on port `8000` (loopback-only host binding).
- `web` — Vite-built SPA served by Nginx on port `8080` (overridable). Nginx reverse-proxies `/api/...` to the backend over the compose network so the browser only ever talks to the web container.

```bash
# 1. Configure OpenAI key (required — there is no mock provider)
cp .env.example .env
# edit .env and set OPENAI_API_KEY=sk-...

# 2. Build images and start the stack
docker compose up -d --build

# 3. Open the app
xdg-open http://localhost:8080   # or just visit it in your browser
```

Health checks (do not require an OpenAI key):

```bash
curl http://localhost:8080/healthz          # web (nginx)
curl http://localhost:8080/api/healthz      # backend via reverse-proxy → reports openai_key_configured
curl http://127.0.0.1:8000/healthz          # backend direct (loopback only)
```

`POST /v1/drafts` and `POST /v1/drafts/fhir` will fail fast with
`OpenAIConfigurationError` if `OPENAI_API_KEY` is not set.

Tear down:

```bash
docker compose down            # keep the redacted review JSONL volume
docker compose down -v         # also drop the audit volume
```

## Run locally without Docker

```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn claranote.app.main:app --reload

# Frontend (separate shell)
cd web
npm install
npm run dev          # http://127.0.0.1:5173, talks to backend at 127.0.0.1:8000
```

PowerShell equivalent for the backend env vars:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
uvicorn claranote.app.main:app --reload
```

## Test an OpenAI API key

OpenAI is the only LLM provider — `OPENAI_API_KEY` is required to generate drafts.
You can sanity-check the key without spending tokens on a draft:

```bash
export OPENAI_API_KEY="your_api_key_here"
python -m claranote.app.openai_key_test
```

The default model is `gpt-5.4`. Override:

```bash
export OPENAI_MODEL="gpt-5.4"
python -m claranote.app.openai_key_test --model gpt-5.4
```

The key test uses the OpenAI Responses API for a tiny connectivity request. The
OpenAI-backed draft client also requests structured JSON output and still passes
the result through the local Pydantic and safety validators.

### Model selection

The default `OPENAI_MODEL` is `gpt-5.4`. The OpenAI client uses the **Responses API**
with strict JSON Schema (Structured Outputs), which is supported on the
`gpt-5.x` and `gpt-4.1` families. If your account does not have access to `gpt-5.4`,
override with any model that supports Structured Outputs:

```bash
export OPENAI_MODEL="gpt-5"           # most accounts
export OPENAI_MODEL="gpt-5-mini"      # cheaper, slightly weaker
export OPENAI_MODEL="gpt-4.1"         # legacy fallback
```

You can sanity-check connectivity without spending tokens on a draft:

```bash
python -m claranote.app.openai_key_test --model "$OPENAI_MODEL"
```

This calls the Responses API once with `max_output_tokens=16` and prints
`ok` on success.

## Test

Tests that exercise the LLM pipeline call the real OpenAI API. They are
auto-skipped when `OPENAI_API_KEY` is absent so validator-only tests still
run offline.

```bash
export OPENAI_API_KEY=sk-...   # required for full coverage; otherwise some tests skip
pytest
```

## Run the safety-first evaluation report

```bash
python -m claranote.app.evaluate
```

The report runs the golden-case set and summarizes evidence coverage, hallucination-related issues, omission issues, unsafe directive issues, ambiguity failures, and human-in-the-loop review notes.

## Frontend

The safety-first review UI lives in [web](web/README.md). It provides the three-panel clinical review workspace, evidence highlighting, validation panel, review controls, and Playwright accessibility checks.

## Iteration Rule: Reference-backed Features

Every new feature must include authoritative references before implementation. The expected loop is:

1. Research papers, medical authorities, standards bodies, or official vendor documentation.
2. A short design rationale tied to the assignment risk being addressed.
3. TODOs in README or web README.
4. Code and tests implementing the TODO.
5. A commit whose scope matches the completed iteration.

### Completed Iteration: Research-backed Design Controls

- Done: Add backend design-control metadata that maps each safety feature to authoritative references.
- Done: Expose design controls through a read-only API endpoint.
- Done: Keep references internal to README/API metadata rather than displaying them in the frontend.
- Done: Test that the API returns authoritative references.

### Completed Iteration: Persisted Clinician Review Feedback

References:
- FDA Clinical Decision Support Software guidance: HCPs should be able to independently review the basis of recommendations.
- WHO LMM health guidance: health AI should include human oversight and governance.
- CHAI Responsible AI Guide: transparency and accountability are part of responsible health AI lifecycle practice.

Done:
- Done: Add a backend review submission API for `accept`, `edit`, and `reject` decisions.
- Done: Persist review records locally as redacted JSONL so reviewer feedback can be audited without storing raw secrets.
- Done: Wire frontend review controls to submit records to the backend while keeping local UI feedback.
- Done: Test review storage, API submission, and frontend request behavior.

### Completed Iteration: Evaluation Report API

References:
- FDA Good Machine Learning Practice: AI/ML systems should be considered across the total product lifecycle.
- CHAI Responsible AI Guide: responsible health AI requires lifecycle testing, monitoring, reporting, and accountability.
- CREOLA: clinical summarisation should track hallucinations, omissions, and safety-relevant errors.

Done:
- Done: Add a backend endpoint that returns golden-case evaluation metrics and a markdown report.
- Done: Display the evaluation metrics in the existing frontend report card without showing source references.
- Done: Test the endpoint and the frontend rendering path.

### Completed Iteration: FHIR Bundle Input Adapter

References:
- HL7 FHIR R4 Bundle: Bundle is the resource container used to group clinical resources for exchange.
- HL7 FHIR R4 Observation: observations represent measurements and simple assertions such as labs and symptoms.
- HL7 FHIR R4 MedicationStatement: medication statements represent reported medication use and may be incomplete or patient-reported.
- HL7 FHIR R4 Condition: conditions represent problems, diagnoses, or clinically relevant concerns.

Done:
- Done: Add a backend adapter for Patient, Condition, Observation, and MedicationStatement resources in a FHIR Bundle.
- Done: Add `POST /v1/drafts/fhir` so structured bundles can run through the same source-span, prompt, validation, and safety pipeline.
- Done: Preserve FHIR resource IDs and multi-clinic provenance inside generated source text for evidence review.
- Done: Test valid assignment-style FHIR input and invalid bundle handling.

### Completed Iteration: Pre-LLM Privacy Gate

References:
- HHS HIPAA de-identification guidance: protected health information includes individually identifiable health information, and Safe Harbor de-identification removes specified identifiers.
- NIST AI Risk Management Framework: trustworthy AI risk management should consider risks to individuals and organizations across design, development, use, and evaluation.

Done:
- Done: Detect direct identifiers before prompt construction or model invocation.
- Done: Block generation and return a validation error when patient names, emails, phone numbers, SSNs, MRNs, street addresses, or API keys are present.
- Done: Return only redacted source spans for blocked requests.
- Done: Test that the privacy gate blocks model calls and that redaction covers the detected identifier classes.

### Completed Iteration: Review Audit Retention

References:
- HHS HIPAA Minimum Necessary Requirement: covered entities should limit use or disclosure of PHI to the minimum necessary for the intended purpose.
- HHS HIPAA Audit Protocol: information system activity records such as audit logs should be regularly reviewed.

Done:
- Done: Add a default bounded retention period for redacted clinician review JSONL records.
- Done: Purge expired review records automatically during review reads and writes.
- Done: Keep current review API behavior unchanged for non-expired records.
- Done: Test old-record purging and retention-disabled behavior.

### Completed Iteration: Citation-sized Source Spans

References:
- Perplexity API Quickstart: web-grounded answers expose citations and search results separately from generated text.
- Perplexity Output Control: valid source links should come from API citation/search-result fields rather than being generated inside model output.
- AIS attribution framework: generated statements should be evaluated against identified supporting sources.

Done:
- Done: Replace line-by-line source span splitting with section-aware citation chunks.
- Done: Keep headings such as `Latest labs:` as context inside a section, but do not expose heading-only lines as standalone evidence.
- Done: Preserve source offsets and stable `S1`, `S2`, ... IDs.
- Done: Test assignment-style spans, heading-only filtering, and single-paragraph sentence fallback.

## MVP Scope

The MVP runs against the OpenAI Responses API. The `LLMClient` Protocol in
[`claranote/app/llm_client.py`](claranote/app/llm_client.py) is the
extension point for adding additional providers (Anthropic, Gemini, on-prem,
…) without touching the pipeline.

## Implemented Extensions: Safety-first Clinical Summarization

- Done: Stricter evidence coverage validation checks that every clinical claim cites source spans and flags unsupported evidence.
- Done: Assignment-critical omission checks for HbA1c trend, LDL value, fasting glucose recency uncertainty, atorvastatin uncertainty, adherence uncertainty, symptoms, diet change, and multi-clinic provenance.
- Done: Hallucination taxonomy for unsupported condition, medication, lab trend, symptom, recommendation, incorrect temporality, unsupported claim, and omission.
- Done: Clinician review record model for `accept`, `edit`, and `reject`, with reason codes such as factual error, missing risk flag, unsafe recommendation, unclear wording, and wrong evidence.
- Done: Golden-case evaluation set covering ambiguous, conflicting, missing-date, medication-adherence, and multi-source lab examples.
- Done: Evaluation metrics for hallucination-related issues, omission issues, evidence coverage, unsafe-directive issues, ambiguity failures, and clinician edit rate.
- Done: Second-pass safety reviewer that checks the generated draft before returning it, with optional redacted first-pass debug payload.
- Done: Prompt-version and model-version metadata on every response for traceability.
- Done: Assignment-focused evaluation report generator for failure modes, mitigations, and human-in-the-loop review notes.
- Done: Privacy and log-redaction helpers for raw text, prompts, model outputs, and review comments.

## Future Production Hardening

- Add real clinician-authenticated review storage instead of in-memory schema-only records.
- Replace lexical evidence support checks with an NLI or clinically tuned entailment reviewer.
- Add privacy, security, authorization, and retention controls before processing real patient data.
