import { Badge } from "../../components/ui/Badge";
import type { SourceSpan } from "../../api/types";
import { cn } from "../../utils/cn";

export function SourceSpanList({
  sourceSpans,
  selectedEvidenceId,
  onSelectEvidence,
}: {
  sourceSpans: SourceSpan[];
  selectedEvidenceId: string | null;
  onSelectEvidence: (id: string) => void;
}) {
  return (
    <div className="mt-4 border-t border-clinical-border">
      <div className="flex items-center justify-between px-4 py-3">
        <h3 className="text-sm font-semibold">Source spans</h3>
        <Badge tone={sourceSpans.length ? "info" : "neutral"}>{sourceSpans.length} spans</Badge>
      </div>
      <div className="clinical-scrollbar max-h-72 space-y-2 overflow-auto px-4 pb-4">
        {sourceSpans.length === 0 ? (
          <p className="rounded-md border border-dashed border-clinical-border p-3 text-sm text-clinical-muted">
            Source spans appear after a draft run.
          </p>
        ) : (
          sourceSpans.map((span) => (
            <button
              className={cn(
                "w-full rounded-md border p-3 text-left text-sm transition",
                selectedEvidenceId === span.id
                  ? "border-evidence-border bg-evidence-bg"
                  : "border-clinical-border bg-white hover:bg-slate-50",
              )}
              key={span.id}
              onClick={() => onSelectEvidence(span.id)}
            >
              <span className="mb-1 block text-xs font-semibold text-blue-800">{span.id}</span>
              <span>{span.text}</span>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
