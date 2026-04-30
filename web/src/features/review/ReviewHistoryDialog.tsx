import * as Dialog from "@radix-ui/react-dialog";
import { useQuery } from "@tanstack/react-query";
import { History, RefreshCw, X } from "lucide-react";

import { fetchReviews } from "../../api/reviewApi";
import type { ReviewDecision } from "../../api/types";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";

const DECISION_TONE: Record<ReviewDecision, "valid" | "warning" | "blocked"> = {
  accept: "valid",
  edit: "warning",
  reject: "blocked",
};

function formatTimestamp(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString();
}

export function ReviewHistoryDialog({
  open,
  onOpenChange,
  refreshKey = 0,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  refreshKey?: number;
}) {
  const { data, isLoading, isFetching, error, refetch } = useQuery({
    queryFn: () => fetchReviews(50),
    queryKey: ["review-history", refreshKey],
    enabled: open,
    staleTime: 0,
  });

  return (
    <Dialog.Root onOpenChange={onOpenChange} open={open}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-slate-950/35" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 flex max-h-[90vh] w-[min(92vw,48rem)] -translate-x-1/2 -translate-y-1/2 flex-col rounded-panel border border-clinical-border bg-white shadow-xl">
          <div className="flex items-start justify-between gap-4 border-b border-clinical-border px-5 py-4">
            <div>
              <Dialog.Title className="flex items-center gap-2 text-base font-semibold">
                <History aria-hidden="true" size={18} /> Review history
              </Dialog.Title>
              <Dialog.Description className="mt-1 text-sm text-clinical-muted">
                Recent clinician decisions. Comments are redacted for direct
                identifiers before storage.
              </Dialog.Description>
            </div>
            <div className="flex items-center gap-2">
              <Button
                aria-label="Refresh review history"
                icon={
                  <RefreshCw
                    aria-hidden="true"
                    className={isFetching ? "animate-spin" : ""}
                    size={14}
                  />
                }
                onClick={() => refetch()}
              >
                Refresh
              </Button>
              <Dialog.Close asChild>
                <Button
                  aria-label="Close review history"
                  icon={<X aria-hidden="true" size={16} />}
                  variant="ghost"
                />
              </Dialog.Close>
            </div>
          </div>
          <div className="clinical-scrollbar min-h-0 flex-1 overflow-auto px-5 py-4">
            {isLoading && (
              <p className="text-sm text-clinical-muted">Loading review history…</p>
            )}
            {error && (
              <p className="rounded-md border border-red-300 bg-status-blocked-bg p-3 text-sm text-status-blocked">
                Failed to load reviews:{" "}
                {error instanceof Error ? error.message : "Unknown error"}
              </p>
            )}
            {data && data.length === 0 && !isLoading && (
              <p className="rounded-md border border-dashed border-clinical-border p-4 text-sm text-clinical-muted">
                No reviews recorded yet. Submitted decisions appear here.
              </p>
            )}
            {data && data.length > 0 && (
              <ul className="space-y-3">
                {data.map((record) => (
                  <li
                    className="rounded-md border border-clinical-border bg-clinical-panel p-3"
                    key={`${record.draft_id}-${record.item_key}-${record.created_at}`}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <Badge tone={DECISION_TONE[record.decision]}>
                          {record.decision}
                        </Badge>
                        <code className="rounded bg-clinical-bg px-1.5 py-0.5 text-xs">
                          {record.item_key}
                        </code>
                      </div>
                      <span className="text-xs text-clinical-muted">
                        {formatTimestamp(record.created_at)}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-clinical-muted">
                      <span className="font-semibold uppercase tracking-wide">
                        draft:
                      </span>{" "}
                      <span className="font-mono">{record.draft_id}</span>
                    </p>
                    {record.reason_codes.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {record.reason_codes.map((code) => (
                          <Badge key={code} tone="warning">
                            {code.replace(/_/g, " ")}
                          </Badge>
                        ))}
                      </div>
                    )}
                    {record.comments && (
                      <p className="mt-2 text-sm leading-6">{record.comments}</p>
                    )}
                    {record.edited_text && (
                      <pre className="mt-2 whitespace-pre-wrap rounded bg-clinical-bg p-2 text-xs">
                        {record.edited_text}
                      </pre>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
