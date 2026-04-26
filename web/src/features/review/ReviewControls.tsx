import { Check, Edit3, Flag, ShieldAlert, XCircle } from "lucide-react";
import { useState } from "react";

import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import type { ReviewDecision, ReviewReasonCode, ReviewState } from "../../api/types";
import { ReviewReasonDialog } from "./ReviewReasonDialog";

export function ReviewControls({
  itemKey,
  review,
  onReviewChange,
}: {
  itemKey: string;
  review?: ReviewState;
  onReviewChange: (review: ReviewState) => void;
}) {
  const [dialogDecision, setDialogDecision] = useState<ReviewDecision | null>(null);

  function saveDecision(
    decision: ReviewDecision,
    reasonCodes: ReviewReasonCode[] = [],
    comments = "",
  ) {
    onReviewChange({ itemKey, decision, reasonCodes, comments });
  }

  return (
    <div className="mt-3 flex flex-wrap items-center gap-2">
      {review && (
        <Badge tone={review.decision === "accept" ? "valid" : review.decision === "reject" ? "blocked" : "warning"}>
          {review.decision}
        </Badge>
      )}
      <Button
        className="min-h-8 px-2 text-xs"
        icon={<Check aria-hidden="true" size={14} />}
        onClick={() => saveDecision("accept")}
      >
        Accept
      </Button>
      <Button
        className="min-h-8 px-2 text-xs"
        icon={<Edit3 aria-hidden="true" size={14} />}
        onClick={() => setDialogDecision("edit")}
      >
        Edit
      </Button>
      <Button
        className="min-h-8 px-2 text-xs"
        icon={<XCircle aria-hidden="true" size={14} />}
        onClick={() => setDialogDecision("reject")}
      >
        Reject
      </Button>
      <Button
        className="min-h-8 px-2 text-xs"
        icon={<Flag aria-hidden="true" size={14} />}
        onClick={() => saveDecision("edit", ["wrong_evidence"])}
      >
        Wrong evidence
      </Button>
      <Button
        className="min-h-8 px-2 text-xs"
        icon={<ShieldAlert aria-hidden="true" size={14} />}
        onClick={() => saveDecision("edit", ["missing_risk_flag"])}
      >
        Missing risk
      </Button>
      {dialogDecision && (
        <ReviewReasonDialog
          decision={dialogDecision}
          onOpenChange={(open) => {
            if (!open) setDialogDecision(null);
          }}
          onSave={(reasonCodes, comments) => saveDecision(dialogDecision, reasonCodes, comments)}
          open={dialogDecision !== null}
        />
      )}
    </div>
  );
}
