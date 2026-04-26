import type { EvidenceBackedItem, ReviewState } from "../../api/types";
import { DraftItem } from "./DraftItem";

export function DraftSection({
  title,
  sectionKey,
  items,
  selectedEvidenceId,
  isUncertainty,
  reviews,
  onSelectEvidence,
  onReviewChange,
}: {
  title: string;
  sectionKey: string;
  items: EvidenceBackedItem[];
  selectedEvidenceId: string | null;
  isUncertainty?: boolean;
  reviews: Record<string, ReviewState>;
  onSelectEvidence: (id: string) => void;
  onReviewChange: (review: ReviewState) => void;
}) {
  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold">{title}</h3>
        <span className="text-xs text-clinical-muted">{items.length} items</span>
      </div>
      {items.length === 0 ? (
        <p className="rounded-md border border-dashed border-clinical-border p-3 text-sm text-clinical-muted">
          No items returned.
        </p>
      ) : (
        <div className="space-y-3">
          {items.map((item, index) => {
            const itemKey = `${sectionKey}-${index}`;
            return (
              <DraftItem
                isUncertainty={isUncertainty}
                item={item}
                itemKey={itemKey}
                key={itemKey}
                onReviewChange={onReviewChange}
                onSelectEvidence={onSelectEvidence}
                review={reviews[itemKey]}
                selectedEvidenceId={selectedEvidenceId}
              />
            );
          })}
        </div>
      )}
    </section>
  );
}
