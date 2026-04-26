import * as Dialog from "@radix-ui/react-dialog";
import { X } from "lucide-react";
import { useState } from "react";

import { Button } from "../../components/ui/Button";
import type { ReviewDecision, ReviewReasonCode } from "../../api/types";

const REASON_OPTIONS: Array<{ code: ReviewReasonCode; label: string }> = [
  { code: "factual_error", label: "Factual error" },
  { code: "missing_risk_flag", label: "Missing risk flag" },
  { code: "unsafe_recommendation", label: "Unsafe recommendation" },
  { code: "unclear_wording", label: "Unclear wording" },
  { code: "wrong_evidence", label: "Wrong evidence" },
  { code: "other", label: "Other" },
];

export function ReviewReasonDialog({
  decision,
  open,
  onOpenChange,
  onSave,
}: {
  decision: ReviewDecision;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (reasonCodes: ReviewReasonCode[], comments: string) => void;
}) {
  const [reasonCodes, setReasonCodes] = useState<ReviewReasonCode[]>([]);
  const [comments, setComments] = useState("");

  function toggleReason(code: ReviewReasonCode) {
    setReasonCodes((current) =>
      current.includes(code) ? current.filter((item) => item !== code) : [...current, code],
    );
  }

  function save() {
    onSave(reasonCodes, comments);
    setReasonCodes([]);
    setComments("");
  }

  return (
    <Dialog.Root onOpenChange={onOpenChange} open={open}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-slate-950/35" />
        <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[min(92vw,32rem)] -translate-x-1/2 -translate-y-1/2 rounded-panel border border-clinical-border bg-white p-5 shadow-xl">
          <div className="flex items-start justify-between gap-4">
            <div>
              <Dialog.Title className="text-base font-semibold capitalize">
                {decision} draft item
              </Dialog.Title>
              <Dialog.Description className="mt-1 text-sm text-clinical-muted">
                Capture the review reason. This is frontend-only state in the MVP.
              </Dialog.Description>
            </div>
            <Dialog.Close asChild>
              <Button aria-label="Close review dialog" icon={<X aria-hidden="true" size={16} />} variant="ghost" />
            </Dialog.Close>
          </div>
          <fieldset className="mt-4 space-y-2">
            <legend className="text-sm font-semibold">Reason codes</legend>
            <div className="grid gap-2 sm:grid-cols-2">
              {REASON_OPTIONS.map((option) => (
                <label
                  className="flex items-center gap-2 rounded-md border border-clinical-border px-3 py-2 text-sm"
                  key={option.code}
                >
                  <input
                    checked={reasonCodes.includes(option.code)}
                    onChange={() => toggleReason(option.code)}
                    type="checkbox"
                  />
                  {option.label}
                </label>
              ))}
            </div>
          </fieldset>
          <label className="mt-4 block text-sm font-semibold" htmlFor="review-comments">
            Comments
          </label>
          <textarea
            className="mt-2 min-h-24 w-full resize-y rounded-md border border-clinical-border p-3 text-sm"
            id="review-comments"
            onChange={(event) => setComments(event.target.value)}
            placeholder="Optional reviewer note..."
            value={comments}
          />
          <div className="mt-4 flex justify-end gap-2">
            <Dialog.Close asChild>
              <Button>Cancel</Button>
            </Dialog.Close>
            <Dialog.Close asChild>
              <Button onClick={save} variant={decision === "reject" ? "danger" : "primary"}>
                Save review
              </Button>
            </Dialog.Close>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
