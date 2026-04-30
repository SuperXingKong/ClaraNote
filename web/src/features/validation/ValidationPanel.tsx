import { AlertCircle, CheckCircle2, Info } from "lucide-react";

import { Badge } from "../../components/ui/Badge";
import type { ResponseMetadata, ValidationIssue, ValidationResult } from "../../api/types";
import { humanizeIssueCode, humanizeSection, itemKeyFor } from "../../utils/labels";
import { SafetyStatusBadge } from "./SafetyStatusBadge";

export function ValidationPanel({
  validation,
  metadata,
  onSelectItem,
  selectedItemKey,
}: {
  validation: ValidationResult | null;
  metadata: ResponseMetadata | null;
  onSelectItem?: (itemKey: string) => void;
  selectedItemKey?: string | null;
}) {
  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="space-y-3 border-b border-clinical-border p-4">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-sm font-semibold">Safety review</h2>
          <SafetyStatusBadge validation={validation} variant="detailed" />
        </div>
        {metadata && (
          <dl className="grid grid-cols-1 gap-2 text-xs text-clinical-muted">
            <div className="flex justify-between gap-3">
              <dt>Prompt</dt>
              <dd className="font-medium text-clinical-text">{metadata.prompt_version}</dd>
            </div>
            <div className="flex justify-between gap-3">
              <dt>Model</dt>
              <dd className="font-medium text-clinical-text">{metadata.model_version}</dd>
            </div>
            <div className="flex justify-between gap-3">
              <dt>Provider</dt>
              <dd className="font-medium text-clinical-text">{metadata.llm_provider}</dd>
            </div>
          </dl>
        )}
      </div>
      <div className="clinical-scrollbar min-h-0 flex-1 space-y-4 overflow-auto p-4">
        {!validation ? (
          <EmptyState />
        ) : (
          <IssueList
            issues={validation.issues}
            onSelectItem={onSelectItem}
            selectedItemKey={selectedItemKey ?? null}
            warningsWithoutIssue={collectStandaloneWarnings(validation)}
          />
        )}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="rounded-md border border-dashed border-clinical-border p-4 text-sm text-clinical-muted">
      Run a draft to see schema, evidence, ambiguity, omission, and safety validation.
    </div>
  );
}

/**
 * `validation.errors` and `validation.warnings` mirror messages from `validation.issues`,
 * but the safety_note check appends a warning that has no matching issue. Surface only
 * those orphan messages so we don't duplicate the issue list.
 */
function collectStandaloneWarnings(validation: ValidationResult): string[] {
  const issueMessages = new Set(validation.issues.map((issue) => issue.message));
  return validation.warnings.filter((message) => !issueMessages.has(message));
}

function IssueList({
  issues,
  warningsWithoutIssue,
  onSelectItem,
  selectedItemKey,
}: {
  issues: ValidationIssue[];
  warningsWithoutIssue: string[];
  onSelectItem?: (itemKey: string) => void;
  selectedItemKey: string | null;
}) {
  if (issues.length === 0 && warningsWithoutIssue.length === 0) {
    return (
      <div className="rounded-md border border-green-200 bg-status-valid-bg p-3 text-sm text-status-valid">
        <CheckCircle2 aria-hidden="true" className="mr-2 inline" size={16} />
        No issues detected.
      </div>
    );
  }

  return (
    <section>
      <h3 className="mb-2 text-sm font-semibold">
        Detected issues ({issues.length + warningsWithoutIssue.length})
      </h3>
      <div className="space-y-2">
        {issues.map((issue, index) => (
          <IssueCard
            issue={issue}
            isSelected={
              selectedItemKey != null &&
              itemKeyFor(issue.section, issue.item_index) === selectedItemKey
            }
            key={`${issue.code}-${issue.section ?? "global"}-${issue.item_index ?? index}-${index}`}
            onSelectItem={onSelectItem}
          />
        ))}
        {warningsWithoutIssue.map((message, index) => (
          <article
            className="rounded-md border border-clinical-border bg-white p-3 text-sm"
            key={`warning-${index}`}
          >
            <Badge tone="warning">
              <Info aria-hidden="true" size={14} />
              Warning
            </Badge>
            <p className="mt-2 leading-6">{message}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function IssueCard({
  issue,
  isSelected,
  onSelectItem,
}: {
  issue: ValidationIssue;
  isSelected: boolean;
  onSelectItem?: (itemKey: string) => void;
}) {
  const itemKey = itemKeyFor(issue.section, issue.item_index);
  const isClickable = itemKey != null && onSelectItem != null;
  const severityLabel = issue.severity === "error" ? "Error" : "Warning";
  const severityTone = issue.severity === "error" ? "blocked" : "warning";
  const SeverityIcon = issue.severity === "error" ? AlertCircle : Info;

  const handleClick = () => {
    if (isClickable && itemKey) onSelectItem(itemKey);
  };

  return (
    <article
      aria-pressed={isClickable ? isSelected : undefined}
      className={`rounded-md border bg-white p-3 text-sm transition-colors ${
        isSelected ? "border-blue-500 ring-2 ring-blue-300" : "border-clinical-border"
      } ${isClickable ? "cursor-pointer hover:bg-clinical-bg" : ""}`}
      onClick={isClickable ? handleClick : undefined}
      onKeyDown={
        isClickable
          ? (event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                handleClick();
              }
            }
          : undefined
      }
      role={isClickable ? "button" : undefined}
      tabIndex={isClickable ? 0 : undefined}
    >
      <div className="flex flex-wrap gap-2">
        <Badge tone={severityTone}>
          <SeverityIcon aria-hidden="true" size={14} />
          {severityLabel}
        </Badge>
        <Badge tone="neutral">{humanizeIssueCode(issue.code)}</Badge>
        {issue.section && <Badge tone="info">{humanizeSection(issue.section)}</Badge>}
        {issue.evidence_ids.length > 0 && (
          <span className="text-xs text-clinical-muted">
            evidence: {issue.evidence_ids.join(", ")}
          </span>
        )}
      </div>
      <p className="mt-2 leading-6">{issue.message}</p>
      {isClickable && (
        <p className="mt-2 text-xs text-blue-700">Click to highlight the affected item →</p>
      )}
    </article>
  );
}
