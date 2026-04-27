import type { DraftResponse } from "../../src/api/types";

export const mockDraftResponse: DraftResponse = {
  source_spans: [
    {
      id: "S1",
      text: "58-year-old female with history of type 2 diabetes and hyperlipidemia.",
      start: 0,
      end: 72,
    },
    {
      id: "S2",
      text: "HbA1c: 7.8% (Jan), 8.4% (March)",
      start: 73,
      end: 112,
    },
    {
      id: "S3",
      text: "Fasting glucose: 6.5 mmol/L, 8.9 mmol/L (unclear which is most recent)",
      start: 113,
      end: 190,
    },
    {
      id: "S4",
      text: "LDL: 4.2 mmol/L",
      start: 191,
      end: 206,
    },
  ],
  draft: {
    key_clinical_summary: [
      {
        text: "58-year-old female with type 2 diabetes and hyperlipidemia.",
        evidence_ids: ["S1"],
        confidence: "high",
        requires_clinician_review: true,
      },
    ],
    trends: [
      {
        text: "HbA1c increased from 7.8% in January to 8.4% in March.",
        evidence_ids: ["S2"],
        confidence: "high",
        requires_clinician_review: true,
      },
    ],
    risk_flags: [
      {
        text: "LDL 4.2 mmol/L is a cardiovascular risk flag for clinician review.",
        evidence_ids: ["S4", "S1"],
        confidence: "medium",
        requires_clinician_review: true,
      },
    ],
    uncertainties: [
      {
        text: "Fasting glucose recency is unclear, so no fasting glucose trend should be inferred.",
        evidence_ids: ["S3"],
        confidence: "high",
        requires_clinician_review: true,
      },
    ],
    suggested_follow_up_areas: [
      {
        text: "Clarify fasting glucose dates and source before interpreting trend.",
        evidence_ids: ["S3"],
        confidence: "high",
        requires_clinician_review: true,
      },
    ],
    safety_note: "Draft for clinician review only.",
  },
  validation: {
    is_valid: true,
    errors: [],
    warnings: [],
    issues: [],
  },
  metadata: {
    prompt_version: "clinical-review-v1",
    model_version: "mock-clinical-review-v1",
    llm_provider: "mock",
  },
  debug: null,
};

export const mockEvaluationReportResponse = {
  result: {
    metrics: {
      total_cases: 5,
      valid_cases: 1,
      hallucination_issue_count: 2,
      omission_issue_count: 0,
      unsafe_directive_count: 0,
      ambiguity_failure_count: 0,
      evidence_issue_count: 1,
      evidence_coverage_rate: 1,
      clinician_edit_rate: null,
    },
    case_results: [],
  },
  report_markdown: "# Safety-first Clinical Summarization Evaluation",
};
