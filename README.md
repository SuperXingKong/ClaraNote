# Clinical Review Draft Generator MVP

This MVP turns a plain-text patient summary into a structured clinician-review draft. It demonstrates:

- Structured output with Pydantic schemas
- Evidence-backed clinical summary items
- Explicit uncertainty handling
- Safety validation that blocks direct diagnosis or treatment instructions
- A minimal FastAPI endpoint at `POST /v1/drafts`

## Run

```powershell
pip install -e ".[dev]"
uvicorn clinical_ai.app.main:app --reload
```

## Test an OpenAI API key

The MVP keeps `MockLLMClient` as the default local provider. To test a real OpenAI key explicitly:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
python -m clinical_ai.app.openai_key_test
```

The default model is `gpt-5.4`. Override it with either:

```powershell
$env:OPENAI_MODEL="gpt-5.4"
python -m clinical_ai.app.openai_key_test --model gpt-5.4
```

The key test uses the OpenAI Responses API for a tiny connectivity request. The OpenAI-backed draft client also requests structured JSON output and still passes the result through the local Pydantic and safety validators.

## Test

```powershell
pytest
```

## Run the safety-first evaluation report

```powershell
python -m clinical_ai.app.evaluate
```

The report runs the golden-case set and summarizes evidence coverage, hallucination-related issues, omission issues, unsafe directive issues, ambiguity failures, and human-in-the-loop review notes.

## MVP Scope

The default `MockLLMClient` is deterministic and designed for local testing without an API key. Replace it with a real provider behind the `LLMClient` protocol when integrating an actual model.

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
