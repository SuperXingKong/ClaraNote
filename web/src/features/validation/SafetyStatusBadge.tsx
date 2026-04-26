import { AlertTriangle, CheckCircle2, ShieldAlert } from "lucide-react";

import { Badge } from "../../components/ui/Badge";
import type { ValidationIssue, ValidationResult } from "../../api/types";

const HALLUCINATION_CODES = new Set([
  "unsupported_condition",
  "unsupported_medication",
  "unsupported_lab_trend",
  "unsupported_symptom",
  "unsupported_recommendation",
  "unsupported_claim",
]);

export function SafetyStatusBadge({ validation }: { validation: ValidationResult | null }) {
  if (!validation) {
    return <Badge tone="neutral">Not run</Badge>;
  }

  const hallucinationCount = countIssues(validation.issues, (issue) =>
    HALLUCINATION_CODES.has(issue.code),
  );
  const omissionCount = countIssues(validation.issues, (issue) => issue.code === "omission");
  const unsafeCount = countIssues(validation.issues, (issue) => issue.code === "unsupported_recommendation");
  const ambiguityCount = countIssues(validation.issues, (issue) => issue.code === "incorrect_temporality");

  if (validation.is_valid) {
    return (
      <Badge tone="valid">
        <CheckCircle2 aria-hidden="true" size={14} />
        Valid
      </Badge>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      <Badge tone="blocked">
        <ShieldAlert aria-hidden="true" size={14} />
        Needs review
      </Badge>
      <Badge tone={hallucinationCount ? "blocked" : "neutral"}>Hallucination {hallucinationCount}</Badge>
      <Badge tone={omissionCount ? "warning" : "neutral"}>Omission {omissionCount}</Badge>
      <Badge tone={unsafeCount ? "blocked" : "neutral"}>Unsafe {unsafeCount}</Badge>
      <Badge tone={ambiguityCount ? "warning" : "neutral"}>
        <AlertTriangle aria-hidden="true" size={14} />
        Ambiguity {ambiguityCount}
      </Badge>
    </div>
  );
}

function countIssues(issues: ValidationIssue[], predicate: (issue: ValidationIssue) => boolean) {
  return issues.filter(predicate).length;
}
