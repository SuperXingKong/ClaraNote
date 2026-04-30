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

function countByPredicate(
  issues: ValidationIssue[],
  predicate: (issue: ValidationIssue) => boolean,
): number {
  return issues.filter(predicate).length;
}

function summarize(validation: ValidationResult) {
  return {
    hallucination: countByPredicate(validation.issues, (i) => HALLUCINATION_CODES.has(i.code)),
    omission: countByPredicate(validation.issues, (i) => i.code === "omission"),
    unsafe: countByPredicate(validation.issues, (i) => i.code === "unsupported_recommendation"),
    ambiguity: countByPredicate(validation.issues, (i) => i.code === "incorrect_temporality"),
  };
}

export function SafetyStatusBadge({
  validation,
  variant = "compact",
}: {
  validation: ValidationResult | null;
  variant?: "compact" | "detailed";
}) {
  if (!validation) {
    return <Badge tone="neutral">Not run</Badge>;
  }

  if (validation.is_valid) {
    return (
      <Badge tone="valid">
        <CheckCircle2 aria-hidden="true" size={14} />
        Valid
      </Badge>
    );
  }

  const counts = summarize(validation);
  const totalCategoryIssues =
    counts.hallucination + counts.omission + counts.unsafe + counts.ambiguity;

  if (variant === "compact") {
    return (
      <Badge tone="blocked">
        <ShieldAlert aria-hidden="true" size={14} />
        Needs review{totalCategoryIssues > 0 ? ` · ${totalCategoryIssues}` : ""}
      </Badge>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      <Badge tone="blocked">
        <ShieldAlert aria-hidden="true" size={14} />
        Needs review
      </Badge>
      {counts.hallucination > 0 && (
        <Badge tone="blocked">Hallucination {counts.hallucination}</Badge>
      )}
      {counts.unsafe > 0 && <Badge tone="blocked">Unsafe {counts.unsafe}</Badge>}
      {counts.omission > 0 && <Badge tone="warning">Omission {counts.omission}</Badge>}
      {counts.ambiguity > 0 && (
        <Badge tone="warning">
          <AlertTriangle aria-hidden="true" size={14} />
          Ambiguity {counts.ambiguity}
        </Badge>
      )}
      {totalCategoryIssues === 0 && (
        <Badge tone="warning">{validation.issues.length} other issue{validation.issues.length === 1 ? "" : "s"}</Badge>
      )}
    </div>
  );
}
