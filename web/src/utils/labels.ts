// Maps backend section names (snake_case) to UI section keys used in DraftSection.
// Keep in sync with sectionKey props in DraftWorkspace.tsx.
const SECTION_TO_UI_KEY: Record<string, string> = {
  key_clinical_summary: "summary",
  trends: "trends",
  risk_flags: "risk",
  uncertainties: "uncertainties",
  suggested_follow_up_areas: "follow-up",
};

const SECTION_LABELS: Record<string, string> = {
  key_clinical_summary: "Key clinical summary",
  trends: "Trends",
  risk_flags: "Risk flags",
  uncertainties: "Uncertainties",
  suggested_follow_up_areas: "Suggested follow-up",
};

const ISSUE_CODE_LABELS: Record<string, string> = {
  unsupported_claim: "Unsupported claim",
  unsupported_condition: "Unsupported condition",
  unsupported_medication: "Unsupported medication",
  unsupported_lab_trend: "Unsupported lab trend",
  unsupported_symptom: "Unsupported symptom",
  unsupported_recommendation: "Unsafe recommendation",
  incorrect_temporality: "Incorrect temporality",
  omission: "Omission",
  privacy_direct_identifier: "Privacy: direct identifier",
};

/** Stable item id used to link a validation issue to a draft item. */
export function itemKeyFor(section: string | null, itemIndex: number | null): string | null {
  if (!section || itemIndex == null) return null;
  const sectionKey = SECTION_TO_UI_KEY[section];
  return sectionKey ? `${sectionKey}-${itemIndex}` : null;
}

export function humanizeSection(section: string | null | undefined): string {
  if (!section) return "";
  return SECTION_LABELS[section] ?? toSentenceCase(section);
}

export function humanizeIssueCode(code: string): string {
  return ISSUE_CODE_LABELS[code] ?? toSentenceCase(code);
}

function toSentenceCase(value: string): string {
  const cleaned = value.replace(/_/g, " ").trim();
  if (!cleaned) return "";
  return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
}
