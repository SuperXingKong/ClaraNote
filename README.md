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

## Test

```powershell
pytest
```

## MVP Scope

The default `MockLLMClient` is deterministic and designed for local testing without an API key. Replace it with a real provider behind the `LLMClient` protocol when integrating an actual model.

## TODO Extensions

- TODO: Add real EHR / FHIR Bundle ingestion for `Observation`, `MedicationStatement`, and `Condition`.
- TODO: Add a clinician review UI with accept, edit, and reject actions.
- TODO: Add SQLite/Postgres persistence for audit logs and review feedback.
- TODO: Add CDS Hooks or SMART on FHIR workflow integration.
- TODO: Add guideline retrieval as evidence/context only, not as automatic treatment generation.
- TODO: Add an evaluation dashboard for hallucination rate, omission rate, and clinician edit rate.
- TODO: Add multiple model providers such as OpenAI, Azure OpenAI, and AWS Bedrock.
- TODO: Add production privacy, security, authorization, log redaction, and compliance controls.

