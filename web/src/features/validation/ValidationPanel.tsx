import { AlertCircle, CheckCircle2, Info } from "lucide-react";

import { Badge } from "../../components/ui/Badge";
import type { ResponseMetadata, ValidationResult } from "../../api/types";
import { SafetyStatusBadge } from "./SafetyStatusBadge";

export function ValidationPanel({
  validation,
  metadata,
}: {
  validation: ValidationResult | null;
  metadata: ResponseMetadata | null;
}) {
  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="space-y-3 border-b border-clinical-border p-4">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-sm font-semibold">Safety review</h2>
          <SafetyStatusBadge validation={validation} />
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
          <>
            <MessageList icon="error" messages={validation.errors} title="Errors" tone="blocked" />
            <MessageList icon="warning" messages={validation.warnings} title="Warnings" tone="warning" />
            <IssueList validation={validation} />
          </>
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

function MessageList({
  title,
  messages,
  tone,
  icon,
}: {
  title: string;
  messages: string[];
  tone: "blocked" | "warning";
  icon: "error" | "warning";
}) {
  if (messages.length === 0) return null;
  const Icon = icon === "error" ? AlertCircle : Info;

  return (
    <section>
      <h3 className="mb-2 text-sm font-semibold">{title}</h3>
      <div className="space-y-2">
        {messages.map((message, index) => (
          <div className="rounded-md border border-clinical-border bg-white p-3 text-sm" key={`${title}-${index}`}>
            <Badge tone={tone}>
              <Icon aria-hidden="true" size={14} />
              {tone === "blocked" ? "Blocked" : "Review"}
            </Badge>
            <p className="mt-2 leading-6">{message}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function IssueList({ validation }: { validation: ValidationResult }) {
  if (validation.issues.length === 0) {
    return (
      <div className="rounded-md border border-green-200 bg-status-valid-bg p-3 text-sm text-status-valid">
        <CheckCircle2 aria-hidden="true" className="mr-2 inline" size={16} />
        No structured issues returned.
      </div>
    );
  }

  return (
    <section>
      <h3 className="mb-2 text-sm font-semibold">Structured issues</h3>
      <div className="space-y-2">
        {validation.issues.map((issue, index) => (
          <article className="rounded-md border border-clinical-border bg-white p-3 text-sm" key={`${issue.code}-${index}`}>
            <div className="flex flex-wrap gap-2">
              <Badge tone={issue.severity === "error" ? "blocked" : "warning"}>{issue.severity}</Badge>
              <Badge tone="neutral">{issue.code}</Badge>
              {issue.section && <Badge tone="info">{issue.section}</Badge>}
            </div>
            <p className="mt-2 leading-6">{issue.message}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
