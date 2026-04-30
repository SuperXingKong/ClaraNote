import { AlertCircle, AlertTriangle, CheckCircle2, Info } from "lucide-react";
import { useEffect, useRef } from "react";

import { Badge } from "../../components/ui/Badge";
import type { EvidenceBackedItem, ReviewState, ValidationIssue } from "../../api/types";
import { humanizeIssueCode } from "../../utils/labels";
import { EvidenceBadge } from "./EvidenceBadge";
import { ReviewControls } from "../review/ReviewControls";

export function DraftItem({
  draftId,
  item,
  itemKey,
  isUncertainty,
  selectedEvidenceId,
  isSelected,
  issues,
  review,
  onSelectEvidence,
  onReviewChange,
  onReviewSubmitted,
}: {
  draftId: string;
  item: EvidenceBackedItem;
  itemKey: string;
  isUncertainty?: boolean;
  selectedEvidenceId: string | null;
  isSelected?: boolean;
  issues?: ValidationIssue[];
  review?: ReviewState;
  onSelectEvidence: (id: string) => void;
  onReviewChange: (review: ReviewState) => void;
  onReviewSubmitted?: () => void;
}) {
  const articleRef = useRef<HTMLElement | null>(null);
  const itemIssues = issues ?? [];
  const errorCount = itemIssues.filter((issue) => issue.severity === "error").length;
  const warningCount = itemIssues.length - errorCount;

  useEffect(() => {
    if (isSelected && articleRef.current) {
      articleRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [isSelected]);

  const evidenceBadges =
    item.evidence_ids.length > 0 ? (
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
    );

  if (!item.requires_clinician_review && itemIssues.length === 0) {
    return (
      <details
        className={`rounded-md border bg-slate-50 px-3 py-2 text-sm transition-colors ${
          isSelected ? "border-blue-500 ring-2 ring-blue-300" : "border-clinical-border"
        }`}
        open={isSelected}
      >
        <summary className="flex cursor-pointer flex-wrap items-center gap-2">
          <Badge tone="neutral">Routine</Badge>
          <span className="flex-1 text-clinical-muted">{item.text}</span>
          <span className="flex flex-wrap gap-1">{evidenceBadges}</span>
        </summary>
        <div className="mt-3">
          <ReviewControls
            draftId={draftId}
            itemKey={itemKey}
            onReviewChange={onReviewChange}
            onReviewSubmitted={onReviewSubmitted}
            review={review}
          />
        </div>
      </details>
    );
  }

  return (
    <article
      className={`rounded-md border bg-white p-3 transition-colors ${
        isSelected
          ? "border-blue-500 ring-2 ring-blue-300"
          : errorCount > 0
            ? "border-red-300"
            : warningCount > 0
              ? "border-amber-300"
              : "border-clinical-border"
      }`}
      ref={articleRef}
    >
      <div className="flex flex-wrap items-center gap-2">
        <Badge tone={isUncertainty ? "warning" : "neutral"}>
          {isUncertainty ? (
            <AlertTriangle aria-hidden="true" size={13} />
          ) : (
            <CheckCircle2 aria-hidden="true" size={13} />
          )}
          {isUncertainty ? "Uncertainty" : item.confidence}
        </Badge>
        {item.requires_clinician_review && <Badge tone="info">Clinician review</Badge>}
        {errorCount > 0 && (
          <Badge tone="blocked">
            <AlertCircle aria-hidden="true" size={13} />
            {errorCount} error{errorCount === 1 ? "" : "s"}
          </Badge>
        )}
        {warningCount > 0 && (
          <Badge tone="warning">
            <Info aria-hidden="true" size={13} />
            {warningCount} warning{warningCount === 1 ? "" : "s"}
          </Badge>
        )}
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
      {itemIssues.length > 0 && (
        <ul className="mt-3 space-y-1.5 border-t border-clinical-border pt-2 text-xs">
          {itemIssues.map((issue, index) => {
            const Icon = issue.severity === "error" ? AlertCircle : Info;
            const tone = issue.severity === "error" ? "text-status-blocked" : "text-amber-700";
            return (
              <li className={`flex gap-1.5 ${tone}`} key={`${issue.code}-${index}`}>
                <Icon aria-hidden="true" className="mt-0.5 shrink-0" size={12} />
                <span>
                  <span className="font-semibold">{humanizeIssueCode(issue.code)}:</span>{" "}
                  {issue.message}
                </span>
              </li>
            );
          })}
        </ul>
      )}
      <ReviewControls
        draftId={draftId}
        itemKey={itemKey}
        onReviewChange={onReviewChange}
        onReviewSubmitted={onReviewSubmitted}
        review={review}
      />
    </article>
  );
}
