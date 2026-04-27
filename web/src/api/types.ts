export type Confidence = "low" | "medium" | "high";
export type IssueSeverity = "warning" | "error";
export type ReviewDecision = "accept" | "edit" | "reject";
export type ReviewReasonCode =
  | "factual_error"
  | "missing_risk_flag"
  | "unsafe_recommendation"
  | "unclear_wording"
  | "wrong_evidence"
  | "other";

export type DraftRequest = {
  raw_text: string;
};

export type SourceSpan = {
  id: string;
  text: string;
  start: number;
  end: number;
};

export type EvidenceBackedItem = {
  text: string;
  evidence_ids: string[];
  confidence: Confidence;
  requires_clinician_review: boolean;
};

export type ClinicalReviewDraft = {
  key_clinical_summary: EvidenceBackedItem[];
  trends: EvidenceBackedItem[];
  risk_flags: EvidenceBackedItem[];
  uncertainties: EvidenceBackedItem[];
  suggested_follow_up_areas: EvidenceBackedItem[];
  safety_note: string;
};

export type ValidationIssue = {
  code: string;
  severity: IssueSeverity;
  message: string;
  section: string | null;
  evidence_ids: string[];
};

export type ValidationResult = {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  issues: ValidationIssue[];
};

export type ResponseMetadata = {
  prompt_version: string;
  model_version: string;
  llm_provider: string;
};

export type DraftDebugInfo = {
  first_pass_payload: unknown;
};

export type DraftResponse = {
  draft: ClinicalReviewDraft | null;
  source_spans: SourceSpan[];
  validation: ValidationResult;
  metadata: ResponseMetadata;
  debug: DraftDebugInfo | null;
};

export type ReviewState = {
  itemKey: string;
  decision: ReviewDecision;
  reasonCodes: ReviewReasonCode[];
  comments?: string;
};

export type DesignReference = {
  label: string;
  authority: string;
  url: string;
};

export type DesignControl = {
  feature_id: string;
  title: string;
  summary: string;
  rationale: string;
  implemented_in: string[];
  references: DesignReference[];
};

export type DesignControlsResponse = {
  controls: DesignControl[];
};
