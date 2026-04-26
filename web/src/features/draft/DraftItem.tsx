import { AlertTriangle, CheckCircle2 } from "lucide-react";

import { Badge } from "../../components/ui/Badge";
import type { EvidenceBackedItem, ReviewState } from "../../api/types";
import { EvidenceBadge } from "./EvidenceBadge";
import { ReviewControls } from "../review/ReviewControls";

export function DraftItem({
  item,
  itemKey,
  isUncertainty,
  selectedEvidenceId,
  review,
  onSelectEvidence,
  onReviewChange,
}: {
  item: EvidenceBackedItem;
  itemKey: string;
  isUncertainty?: boolean;
  selectedEvidenceId: string | null;
  review?: ReviewState;
  onSelectEvidence: (id: string) => void;
  onReviewChange: (review: ReviewState) => void;
}) {
  return (
    <article className="rounded-md border border-clinical-border bg-white p-3">
      <div className="flex flex-wrap gap-2">
        <Badge tone={isUncertainty ? "warning" : "neutral"}>
          {isUncertainty ? <AlertTriangle aria-hidden="true" size={13} /> : <CheckCircle2 aria-hidden="true" size={13} />}
          {isUncertainty ? "Uncertainty" : item.confidence}
        </Badge>
        {item.requires_clinician_review && <Badge tone="info">Clinician review</Badge>}
      </div>
      <p className="mt-2 text-sm leading-6">{item.text}</p>
      <div className="mt-3 flex flex-wrap gap-2" aria-label="Evidence IDs">
        {item.evidence_ids.length > 0 ? (
          item.evidence_ids.map((evidenceId) => (
            <EvidenceBadge
              evidenceId={evidenceId}
              isSelected={selectedEvidenceId === evidenceId}
              key={evidenceId}
              onSelect={onSelectEvidence}
            />
          ))
        ) : (
          <Badge tone="blocked">Missing evidence</Badge>
        )}
      </div>
      <ReviewControls itemKey={itemKey} onReviewChange={onReviewChange} review={review} />
    </article>
  );
}
