# ClaraNote — Sample outputs

Each file is a complete `DraftResponse` for a representative input. Together
they demonstrate both the happy path and the safety system catching real
failures. The MVP runs against the OpenAI Responses API only — there is no
mock provider.

| File | Input scenario | `validation.is_valid` | What it shows |
|---|---|---|---|
| [`assignment_output.openai.json`](assignment_output.openai.json) | Assignment patient summary, real `gpt-5.4` via Structured Outputs | `true` | Happy path: HbA1c trend captured, fasting-glucose trend correctly **declined** (recency unclear), LDL flagged as cardiovascular risk, multi-clinic provenance + adherence uncertainty surfaced. |
| [`assignment_output.privacy_blocked.json`](assignment_output.privacy_blocked.json) | Same patient but prefixed with name / MRN / email / phone (synthetic PHI) | `false` | **Pre-LLM privacy gate**: the pipeline detects 4 direct-identifier classes, **never calls the model**, and returns redacted source spans. `draft` is `null` — no LLM output exists to leak. |
| [`assignment_output.unsafe_directive_blocked.json`](assignment_output.unsafe_directive_blocked.json) | Hand-constructed draft mimicking an over-confident LLM that recommended a dose increase + new prescription | `false` | **Second-pass safety reviewer**: regex matches `"Increase ... dose"` and prescriptive `"should start"` patterns; raises `unsupported_recommendation` (severity `error`) so `is_valid` becomes `false`. |

## Reproducing each sample

```bash
# 1. Happy path (real OpenAI). Requires OPENAI_API_KEY.
export OPENAI_API_KEY=sk-...
curl -X POST http://localhost:8090/api/v1/drafts \
  -H 'content-type: application/json' \
  -d "$(jq -n --arg s "$(cat assignment_input.txt)" '{raw_text:$s}')"

# 2. Privacy gate trigger (no LLM call needed)
curl -X POST http://localhost:8090/api/v1/drafts \
  -H 'content-type: application/json' \
  -d '{"raw_text":"Patient name: Jane Smith\nMRN: ABC-123-456\nEmail: jane.smith@example.com\n..."}'

# 3. Unsafe-directive trigger — see tests/test_safety.py for the regex set
```

## Why these specific failure samples

A reviewer looking at only `is_valid: true` outputs cannot tell whether the
validation system is real or vacuous. The two `*_blocked.json` samples make
it concrete:

- **Privacy gate** runs **before** any LLM call, so accidentally pasting PHI
  cannot be exfiltrated to the provider — even if the rest of the pipeline
  had bugs.
- **Safety reviewer** runs **after** the LLM call as a deterministic Python
  layer, so prescriptive language slipping past the prompt still gets caught.
