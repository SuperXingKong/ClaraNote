import { useMutation } from "@tanstack/react-query";
import { AlertCircle, PanelRightClose, PanelRightOpen } from "lucide-react";
import { useMemo, useState } from "react";

import { createDraft } from "../../api/draftApi";
import type { DraftResponse, ReviewState } from "../../api/types";
import { Badge } from "../../components/ui/Badge";
import { Panel } from "../../components/ui/Panel";
import { PatientInputPanel } from "../input/PatientInputPanel";
import { ValidationPanel } from "../validation/ValidationPanel";
import { SafetyStatusBadge } from "../validation/SafetyStatusBadge";
import { DraftSection } from "./DraftSection";
import { Button } from "../../components/ui/Button";
import { EvaluationReportView } from "../evaluation/EvaluationReportView";

export function DraftWorkspace() {
  const [rawText, setRawText] = useState("");
  const [draftResponse, setDraftResponse] = useState<DraftResponse | null>(null);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [reviews, setReviews] = useState<Record<string, ReviewState>>({});
  const [showRightPanel, setShowRightPanel] = useState(true);

  const draftMutation = useMutation({
    mutationFn: createDraft,
    onSuccess: (response) => {
      setDraftResponse(response);
      setSelectedEvidenceId(response.source_spans[0]?.id ?? null);
      setReviews({});
    },
  });

  const draft = draftResponse?.draft ?? null;
  const sourceSpans = draftResponse?.source_spans ?? [];
  const validation = draftResponse?.validation ?? null;
  const metadata = draftResponse?.metadata ?? null;
  const reviewCount = useMemo(() => Object.keys(reviews).length, [reviews]);

  function runDraft() {
    draftMutation.mutate({ raw_text: rawText });
  }

  function updateReview(review: ReviewState) {
    setReviews((current) => ({ ...current, [review.itemKey]: review }));
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
          <Badge tone="info">{reviewCount} reviewed</Badge>
          <Button
            className="lg:hidden"
            icon={showRightPanel ? <PanelRightClose aria-hidden="true" size={16} /> : <PanelRightOpen aria-hidden="true" size={16} />}
            onClick={() => setShowRightPanel((value) => !value)}
          >
            Safety panel
          </Button>
        </div>
      </header>
      <div className="mx-auto grid max-w-[96rem] gap-4 px-4 py-4 lg:grid-cols-[minmax(20rem,0.95fr)_minmax(28rem,1.35fr)_minmax(20rem,0.95fr)]">
        <Panel className="min-h-[38rem] lg:h-[calc(100vh-6rem)]" title="Patient input">
          <PatientInputPanel
            isLoading={draftMutation.isPending}
            onRawTextChange={setRawText}
            onRunDraft={runDraft}
            onSelectEvidence={setSelectedEvidenceId}
            rawText={rawText}
            selectedEvidenceId={selectedEvidenceId}
            sourceSpans={sourceSpans}
          />
        </Panel>

        <Panel className="min-h-[38rem] lg:h-[calc(100vh-6rem)]" title="Clinical review draft">
          <div className="clinical-scrollbar h-full min-h-0 space-y-6 overflow-auto p-4">
            {draftMutation.error && (
              <div className="rounded-md border border-red-300 bg-status-blocked-bg p-3 text-sm text-status-blocked">
                <AlertCircle aria-hidden="true" className="mr-2 inline" size={16} />
                {draftMutation.error instanceof Error ? draftMutation.error.message : "Draft request failed"}
              </div>
            )}
            {!draft ? (
              <div className="rounded-md border border-dashed border-clinical-border p-4 text-sm text-clinical-muted">
                Load the assignment sample or paste text, then run a draft to review structured output.
              </div>
            ) : (
              <>
                <DraftSection
                  items={draft.key_clinical_summary}
                  onReviewChange={updateReview}
                  onSelectEvidence={setSelectedEvidenceId}
                  reviews={reviews}
                  sectionKey="summary"
                  selectedEvidenceId={selectedEvidenceId}
                  title="Key clinical summary"
                />
                <DraftSection
                  items={draft.trends}
                  onReviewChange={updateReview}
                  onSelectEvidence={setSelectedEvidenceId}
                  reviews={reviews}
                  sectionKey="trends"
                  selectedEvidenceId={selectedEvidenceId}
                  title="Trends"
                />
                <DraftSection
                  items={draft.risk_flags}
                  onReviewChange={updateReview}
                  onSelectEvidence={setSelectedEvidenceId}
                  reviews={reviews}
                  sectionKey="risk"
                  selectedEvidenceId={selectedEvidenceId}
                  title="Risk flags"
                />
                <DraftSection
                  isUncertainty
                  items={draft.uncertainties}
                  onReviewChange={updateReview}
                  onSelectEvidence={setSelectedEvidenceId}
                  reviews={reviews}
                  sectionKey="uncertainties"
                  selectedEvidenceId={selectedEvidenceId}
                  title="Uncertainties and data quality"
                />
                <DraftSection
                  items={draft.suggested_follow_up_areas}
                  onReviewChange={updateReview}
                  onSelectEvidence={setSelectedEvidenceId}
                  reviews={reviews}
                  sectionKey="follow-up"
                  selectedEvidenceId={selectedEvidenceId}
                  title="Suggested follow-up areas"
                />
                <section className="rounded-md border border-clinical-border bg-white p-3 text-sm">
                  <h3 className="font-semibold">Safety note</h3>
                  <p className="mt-2 leading-6 text-clinical-muted">{draft.safety_note}</p>
                </section>
              </>
            )}
          </div>
        </Panel>

        <Panel
          className={`min-h-[30rem] lg:h-[calc(100vh-6rem)] ${showRightPanel ? "block" : "hidden lg:block"}`}
          title="Evidence and validation"
        >
          <ValidationPanel metadata={metadata} validation={validation} />
          <div className="border-t border-clinical-border p-4">
            <EvaluationReportView />
          </div>
        </Panel>
      </div>
    </main>
  );
}
