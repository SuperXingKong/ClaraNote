import type { EvidenceBackedItem, ReviewState, ValidationIssue } from "../../api/types";
import { DraftItem } from "./DraftItem";

export function DraftSection({
  draftId,
  title,
  sectionKey,
  items,
  selectedEvidenceId,
  selectedItemKey,
  isUncertainty,
  reviews,
  issuesByItemKey,
  onSelectEvidence,
  onReviewChange,
  onReviewSubmitted,
}: {
  draftId: string;
  title: string;
  sectionKey: string;
  items: EvidenceBackedItem[];
  selectedEvidenceId: string | null;
  selectedItemKey: string | null;
  isUncertainty?: boolean;
  reviews: Record<string, ReviewState>;
  issuesByItemKey: Record<string, ValidationIssue[]>;
  onSelectEvidence: (id: string) => void;
  onReviewChange: (review: ReviewState) => void;
  onReviewSubmitted?: () => void;
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
          {items
            .map((item, index) => ({ item, index }))
            .sort((a, b) => {
              const priority = (entry: { item: EvidenceBackedItem }) =>
                entry.item.requires_clinician_review ? 0 : 1;
              return priority(a) - priority(b);
            })
            .map(({ item, index }) => {
              const itemKey = `${sectionKey}-${index}`;
              return (
                <DraftItem
                  draftId={draftId}
                  isSelected={selectedItemKey === itemKey}
                  isUncertainty={isUncertainty}
                  issues={issuesByItemKey[itemKey]}
                  item={item}
                  itemKey={itemKey}
                  key={itemKey}
                  onReviewChange={onReviewChange}
                  onReviewSubmitted={onReviewSubmitted}
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
