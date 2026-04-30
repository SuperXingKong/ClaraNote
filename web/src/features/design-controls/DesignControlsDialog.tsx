import * as Dialog from "@radix-ui/react-dialog";
import { useQuery } from "@tanstack/react-query";
import { ExternalLink, ShieldCheck, X } from "lucide-react";

import { fetchDesignControls } from "../../api/designControlsApi";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";

export function DesignControlsDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const { data, isLoading, error } = useQuery({
    queryFn: fetchDesignControls,
    queryKey: ["design-controls"],
    enabled: open,
    staleTime: 5 * 60 * 1000,
  });

  return (
    <Dialog.Root onOpenChange={onOpenChange} open={open}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-slate-950/35" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 flex max-h-[90vh] w-[min(92vw,52rem)] -translate-x-1/2 -translate-y-1/2 flex-col rounded-panel border border-clinical-border bg-white shadow-xl">
          <div className="flex items-start justify-between gap-4 border-b border-clinical-border px-5 py-4">
            <div>
              <Dialog.Title className="flex items-center gap-2 text-base font-semibold">
                <ShieldCheck aria-hidden="true" size={18} /> Safety design controls
              </Dialog.Title>
              <Dialog.Description className="mt-1 text-sm text-clinical-muted">
                Each control maps a safety feature to authoritative references (FDA, WHO,
                HL7, NIST, HHS, W3C, CHAI).
              </Dialog.Description>
            </div>
            <Dialog.Close asChild>
              <Button
                aria-label="Close design controls"
                icon={<X aria-hidden="true" size={16} />}
                variant="ghost"
              />
            </Dialog.Close>
          </div>
          <div className="clinical-scrollbar min-h-0 flex-1 overflow-auto px-5 py-4">
            {isLoading && (
              <p className="text-sm text-clinical-muted">Loading design controls…</p>
            )}
            {error && (
              <p className="rounded-md border border-red-300 bg-status-blocked-bg p-3 text-sm text-status-blocked">
                Failed to load design controls:{" "}
                {error instanceof Error ? error.message : "Unknown error"}
              </p>
            )}
            {data && (
              <ul className="space-y-4">
                {data.controls.map((control) => (
                  <li
                    className="rounded-md border border-clinical-border bg-clinical-panel p-4"
                    key={control.feature_id}
                  >
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <h3 className="text-sm font-semibold">{control.title}</h3>
                      <Badge tone="info">{control.feature_id}</Badge>
                    </div>
                    <p className="mt-2 text-sm leading-6">{control.summary}</p>
                    <p className="mt-2 text-xs leading-5 text-clinical-muted">
                      <span className="font-semibold uppercase tracking-wide">
                        Rationale:
                      </span>{" "}
                      {control.rationale}
                    </p>
                    {control.implemented_in.length > 0 && (
                      <p className="mt-2 text-xs text-clinical-muted">
                        <span className="font-semibold uppercase tracking-wide">
                          Implemented in:
                        </span>{" "}
                        <span className="font-mono">
                          {control.implemented_in.join(", ")}
                        </span>
                      </p>
                    )}
                    {control.references.length > 0 && (
                      <ul className="mt-3 space-y-1">
                        {control.references.map((reference) => (
                          <li className="text-xs" key={reference.url}>
                            <a
                              className="inline-flex items-center gap-1 text-blue-700 hover:underline"
                              href={reference.url}
                              rel="noreferrer"
                              target="_blank"
                            >
                              {reference.authority}: {reference.label}
                              <ExternalLink aria-hidden="true" size={12} />
                            </a>
                          </li>
                        ))}
                      </ul>
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
