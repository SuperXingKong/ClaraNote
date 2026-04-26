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

## MVP Scope

The default `MockLLMClient` is deterministic and designed for local testing without an API key. Replace it with a real provider behind the `LLMClient` protocol when integrating an actual model.

## TODO Extensions: Safety-first Clinical Summarization

- TODO: Add a stricter evidence coverage validator that requires every clinical claim to reference a source span and flags claims whose evidence text does not semantically support the claim.
- TODO: Add an omission checker for assignment-critical facts, starting with HbA1c trend, LDL value, fasting glucose recency uncertainty, atorvastatin uncertainty, adherence uncertainty, symptoms, diet change, and multi-clinic data provenance.
- TODO: Add a hallucination taxonomy aligned with clinical summarization risks: unsupported condition, unsupported medication, unsupported lab trend, unsupported symptom, unsupported recommendation, and incorrect temporality.
- TODO: Add a clinician review record model for `accept`, `edit`, and `reject`, plus reason codes such as factual error, missing risk flag, unsafe recommendation, unclear wording, or wrong evidence.
- TODO: Add a golden-case evaluation set with ambiguous, conflicting, missing-date, missing-medication-adherence, and multi-source lab examples.
- TODO: Add evaluation metrics for hallucination rate, omission rate, evidence coverage, unsafe-directive rate, ambiguity-handling pass rate, and clinician edit rate.
- TODO: Add a second-pass safety reviewer that checks the generated draft before returning it, while keeping the first-pass output available for debugging and audit.
- TODO: Add prompt-version and model-version metadata to every response so failures can be traced back to a specific prompt/model combination.
- TODO: Add an assignment-focused evaluation report generator that summarizes failure modes, mitigations, and human-in-the-loop review results for documentation.
- TODO: Add privacy and log-redaction controls before storing raw patient text, prompts, model outputs, or clinician review comments.
