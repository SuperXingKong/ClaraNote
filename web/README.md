# Clinical AI Web

Safety-first clinical review UI for the FastAPI MVP.

## Setup

```powershell
cd web
npm install
```

## Run

Start the backend:

```powershell
uvicorn claranote.app.main:app --reload
```

Start the frontend:

```powershell
cd web
npm run dev
```

The frontend calls `http://127.0.0.1:8000` by default. Override with:

```powershell
$env:VITE_API_BASE_URL="http://127.0.0.1:8000"
npm run dev
```

## Test

```powershell
cd web
npm run build
npm run test:e2e
npm run test:a11y
```

## Implemented TODOs

- Done: React + TypeScript + Vite frontend shell under `web/`.
- Done: Tailwind CSS v4 CSS-first design tokens for compact clinical dashboard styling.
- Done: Radix UI primitives for tooltip and review dialog interactions.
- Done: API types mirroring backend `DraftResponse`, draft, source span, validation, issue, and metadata schemas.
- Done: Three-panel workspace for patient input, clinical draft, and evidence/validation review.
- Done: Patient input panel with assignment sample loading, clear action, and run-draft action.
- Done: Source span list with selectable stable evidence IDs.
- Done: Draft sections for summary, trends, risk flags, uncertainties, and follow-up areas.
- Done: Evidence badges on every draft item with click-to-highlight source span behavior.
- Done: Validation panel for validity, errors, warnings, structured issues, and metadata.
- Done: Status badges for valid, needs review, missing evidence, unsafe, and ambiguity states.
- Done: Uncertainty styling that uses icon and text in addition to color.
- Done: Frontend-only review controls and reason dialog aligned to backend reason codes.
- Done: Review controls submit redacted review records to the backend audit API.
- Done: API client for `POST /v1/drafts` with loading and error states.
- Done: Optional evaluation report view that points to the backend report command.
- Done: Evaluation report view loads backend golden-case metrics when the backend is running.
- Done: Responsive desktop, tablet, and mobile layout behavior.
- Done: Playwright tests for assignment flow, evidence highlighting, review controls, and mobile layout.
- Done: axe accessibility smoke test for the main workspace.

## Future Production Hardening

- Add persisted clinician review submission once backend review storage is available.
- Replace mock Playwright responses with an end-to-end backend test environment.
- Add visual regression baselines after the first approved design pass.
