import { useMutation } from "@tanstack/react-query";
import {
  AlertCircle,
  History,
  PanelRightClose,
  PanelRightOpen,
  ShieldCheck,
} from "lucide-react";
import { useMemo, useState } from "react";

import { createDraft } from "../../api/draftApi";
import { createFhirDraft } from "../../api/fhirDraftApi";
import type { DraftResponse, ReviewState, ValidationIssue } from "../../api/types";
import { Badge } from "../../components/ui/Badge";
import { Panel } from "../../components/ui/Panel";
import { itemKeyFor } from "../../utils/labels";
import { DesignControlsDialog } from "../design-controls/DesignControlsDialog";
import { PatientInputPanel, type InputMode } from "../input/PatientInputPanel";
import { ValidationPanel } from "../validation/ValidationPanel";
import { SafetyStatusBadge } from "../validation/SafetyStatusBadge";
import { DraftSection } from "./DraftSection";
import { Button } from "../../components/ui/Button";
import { EvaluationReportView } from "../evaluation/EvaluationReportView";
import { ReviewHistoryDialog } from "../review/ReviewHistoryDialog";

export function DraftWorkspace() {
  const [rawText, setRawText] = useState("");
  const [fhirText, setFhirText] = useState("");
  const [inputMode, setInputMode] = useState<InputMode>("text");
  const [draftResponse, setDraftResponse] = useState<DraftResponse | null>(null);
  const [draftError, setDraftError] = useState<string | null>(null);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [selectedItemKey, setSelectedItemKey] = useState<string | null>(null);
  const [reviews, setReviews] = useState<Record<string, ReviewState>>({});
  const [showRightPanel, setShowRightPanel] = useState(true);
  const [designControlsOpen, setDesignControlsOpen] = useState(false);
  const [reviewHistoryOpen, setReviewHistoryOpen] = useState(false);
  const [reviewHistoryRefreshKey, setReviewHistoryRefreshKey] = useState(0);

  const onMutationSuccess = (response: DraftResponse) => {
    setDraftResponse(response);
    setDraftError(null);
    setSelectedEvidenceId(response.source_spans[0]?.id ?? null);
    setSelectedItemKey(null);
    setReviews({});
  };

  const draftMutation = useMutation({
    mutationFn: createDraft,
    onSuccess: onMutationSuccess,
    onError: (error) =>
      setDraftError(error instanceof Error ? error.message : "Draft request failed"),
  });

  const fhirMutation = useMutation({
    mutationFn: createFhirDraft,
    onSuccess: onMutationSuccess,
    onError: (error) =>
      setDraftError(error instanceof Error ? error.message : "FHIR draft request failed"),
  });

  const isLoading = draftMutation.isPending || fhirMutation.isPending;
  const draft = draftResponse?.draft ?? null;
  const sourceSpans = draftResponse?.source_spans ?? [];
  const validation = draftResponse?.validation ?? null;
  const metadata = draftResponse?.metadata ?? null;
  const draftId = metadata?.draft_id ?? "pending-draft";
  const reviewCount = useMemo(() => Object.keys(reviews).length, [reviews]);

  const issuesByItemKey = useMemo(
    () => groupIssuesByItem(validation?.issues ?? []),
    [validation],
  );

  function runDraft() {
    if (inputMode === "fhir") {
      let parsed: Record<string, unknown>;
      try {
        parsed = JSON.parse(fhirText) as Record<string, unknown>;
      } catch (error) {
        setDraftError(
          error instanceof Error
            ? `FHIR Bundle JSON is invalid: ${error.message}`
            : "FHIR Bundle JSON is invalid",
        );
        return;
      }
      fhirMutation.mutate({ bundle: parsed });
    } else {
      draftMutation.mutate({ raw_text: rawText });
    }
  }

  function updateReview(review: ReviewState) {
    setReviews((current) => ({ ...current, [review.itemKey]: review }));
  }

  function handleReviewSubmitted() {
    setReviewHistoryRefreshKey((value) => value + 1);
  }

  return (
    <main className="min-h-screen bg-clinical-bg text-clinical-text">
      <header className="sticky top-0 z-20 border-b border-clinical-border bg-white/95 px-4 py-3 backdrop-blur">
        <div className="mx-auto flex max-w-[96rem] flex-wrap items-center gap-3">
          <div className="min-w-0 flex-1">
            <p className="text-xs font-semibold uppercase tracking-wide text-clinical-muted">
              Safety-first clinical summarization
            </p>
            <h1 className="text-lg font-semibold">Clinical Review Draft Workspace</h1>
          </div>
          <SafetyStatusBadge validation={validation} />
          {reviewCount > 0 && <Badge tone="info">{reviewCount} reviewed</Badge>}
          <Button
            icon={<ShieldCheck aria-hidden="true" size={16} />}
            onClick={() => setDesignControlsOpen(true)}
          >
            Design controls
          </Button>
          <Button
            icon={<History aria-hidden="true" size={16} />}
            onClick={() => setReviewHistoryOpen(true)}
          >
            Review history
          </Button>
          <Button
            className="lg:hidden"
            icon={
              showRightPanel ? (
                <PanelRightClose aria-hidden="true" size={16} />
              ) : (
                <PanelRightOpen aria-hidden="true" size={16} />
              )
            }
            onClick={() => setShowRightPanel((value) => !value)}
          >
            Safety panel
          </Button>
        </div>
      </header>
      <div className="mx-auto grid max-w-[96rem] gap-4 px-4 py-4 lg:grid-cols-[minmax(20rem,0.95fr)_minmax(28rem,1.35fr)_minmax(20rem,0.95fr)]">
        <Panel className="min-h-[38rem] lg:h-[calc(100vh-6rem)]" title="Patient input">
          <PatientInputPanel
            fhirText={fhirText}
            inputMode={inputMode}
            isLoading={isLoading}
            onFhirTextChange={setFhirText}
            onInputModeChange={setInputMode}
            onRawTextChange={setRawText}
            onRunDraft={runDraft}
            onSelectEvidence={setSelectedEvidenceId}
            rawText={rawText}
            selectedEvidenceId={selectedEvidenceId}
            sourceSpans={sourceSpans}
          />
        </Panel>

        <Panel
          className="min-h-[38rem] lg:h-[calc(100vh-6rem)]"
          title="Clinical review draft"
        >
          <div className="clinical-scrollbar h-full min-h-0 space-y-6 overflow-auto p-4">
            {draftError && (
              <div className="rounded-md border border-red-300 bg-status-blocked-bg p-3 text-sm text-status-blocked">
                <AlertCircle aria-hidden="true" className="mr-2 inline" size={16} />
                {draftError}
              </div>
            )}
            {!draft ? (
              <div className="rounded-md border border-dashed border-clinical-border p-4 text-sm text-clinical-muted">
                Load the assignment sample or paste text, then run a draft to review
                structured output.
              </div>
            ) : (
              <>
                <DraftSection
                  draftId={draftId}
                  issuesByItemKey={issuesByItemKey}
                  items={draft.key_clinical_summary}
                  onReviewChange={updateReview}
                  onReviewSubmitted={handleReviewSubmitted}
                  onSelectEvidence={setSelectedEvidenceId}
                  reviews={reviews}
                  sectionKey="summary"
                  selectedEvidenceId={selectedEvidenceId}
                  selectedItemKey={selectedItemKey}
                  title="Key clinical summary"
                />
                <DraftSection
                  draftId={draftId}
                  issuesByItemKey={issuesByItemKey}
                  items={draft.trends}
                  onReviewChange={updateReview}
                  onReviewSubmitted={handleReviewSubmitted}
                  onSelectEvidence={setSelectedEvidenceId}
                  reviews={reviews}
                  sectionKey="trends"
                  selectedEvidenceId={selectedEvidenceId}
                  selectedItemKey={selectedItemKey}
                  title="Trends"
                />
                <DraftSection
                  draftId={draftId}
                  issuesByItemKey={issuesByItemKey}
                  items={draft.risk_flags}
                  onReviewChange={updateReview}
                  onReviewSubmitted={handleReviewSubmitted}
                  onSelectEvidence={setSelectedEvidenceId}
                  reviews={reviews}
                  sectionKey="risk"
                  selectedEvidenceId={selectedEvidenceId}
                  selectedItemKey={selectedItemKey}
                  title="Risk flags"
                />
                <DraftSection
                  draftId={draftId}
                  isUncertainty
                  issuesByItemKey={issuesByItemKey}
                  items={draft.uncertainties}
                  onReviewChange={updateReview}
                  onReviewSubmitted={handleReviewSubmitted}
                  onSelectEvidence={setSelectedEvidenceId}
                  reviews={reviews}
                  sectionKey="uncertainties"
                  selectedEvidenceId={selectedEvidenceId}
                  selectedItemKey={selectedItemKey}
                  title="Uncertainties and data quality"
                />
                <DraftSection
                  draftId={draftId}
                  issuesByItemKey={issuesByItemKey}
                  items={draft.suggested_follow_up_areas}
                  onReviewChange={updateReview}
                  onReviewSubmitted={handleReviewSubmitted}
                  onSelectEvidence={setSelectedEvidenceId}
                  reviews={reviews}
                  sectionKey="follow-up"
                  selectedEvidenceId={selectedEvidenceId}
                  selectedItemKey={selectedItemKey}
                  title="Suggested follow-up areas"
                />
                <section className="rounded-md border border-clinical-border bg-white p-3 text-sm">
                  <h3 className="font-semibold">Safety note</h3>
                  <p className="mt-2 leading-6 text-clinical-muted">
                    {draft.safety_note}
                  </p>
                </section>
              </>
            )}
          </div>
        </Panel>

        <Panel
          className={`min-h-[30rem] lg:h-[calc(100vh-6rem)] ${showRightPanel ? "block" : "hidden lg:block"}`}
          title="Evidence and validation"
        >
          <ValidationPanel
            metadata={metadata}
            onSelectItem={setSelectedItemKey}
            selectedItemKey={selectedItemKey}
            validation={validation}
          />
          <div className="border-t border-clinical-border p-4">
            <EvaluationReportView />
          </div>
        </Panel>
      </div>

      <DesignControlsDialog
        onOpenChange={setDesignControlsOpen}
        open={designControlsOpen}
      />
      <ReviewHistoryDialog
        onOpenChange={setReviewHistoryOpen}
        open={reviewHistoryOpen}
        refreshKey={reviewHistoryRefreshKey}
      />
    </main>
  );
}

function groupIssuesByItem(issues: ValidationIssue[]): Record<string, ValidationIssue[]> {
  const grouped: Record<string, ValidationIssue[]> = {};
  for (const issue of issues) {
    const key = itemKeyFor(issue.section, issue.item_index);
    if (!key) continue;
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(issue);
  }
  return grouped;
}
