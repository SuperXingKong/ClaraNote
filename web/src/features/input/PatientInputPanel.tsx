import { FileText, Play, RotateCcw, Trash2 } from "lucide-react";

import { Button } from "../../components/ui/Button";
import { ASSIGNMENT_SAMPLE } from "../../test/fixtures";
import type { SourceSpan } from "../../api/types";
import { SourceSpanList } from "./SourceSpanList";

export function PatientInputPanel({
  rawText,
  sourceSpans,
  selectedEvidenceId,
  isLoading,
  onRawTextChange,
  onRunDraft,
  onSelectEvidence,
}: {
  rawText: string;
  sourceSpans: SourceSpan[];
  selectedEvidenceId: string | null;
  isLoading: boolean;
  onRawTextChange: (value: string) => void;
  onRunDraft: () => void;
  onSelectEvidence: (id: string) => void;
}) {
  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex flex-wrap gap-2 border-b border-clinical-border p-3">
        <Button
          icon={<FileText aria-hidden="true" size={16} />}
          onClick={() => onRawTextChange(ASSIGNMENT_SAMPLE)}
        >
          Load sample
        </Button>
        <Button
          icon={<Trash2 aria-hidden="true" size={16} />}
          onClick={() => onRawTextChange("")}
        >
          Clear
        </Button>
        <Button
          className="ml-auto"
          disabled={!rawText.trim() || isLoading}
          icon={isLoading ? <RotateCcw aria-hidden="true" className="animate-spin" size={16} /> : <Play aria-hidden="true" size={16} />}
          onClick={onRunDraft}
          variant="primary"
        >
          {isLoading ? "Running" : "Run draft"}
        </Button>
      </div>
      <label className="px-4 pt-4 text-xs font-semibold uppercase tracking-wide text-clinical-muted" htmlFor="patient-summary">
        Patient summary
      </label>
      <textarea
        id="patient-summary"
        className="mx-4 mt-2 min-h-64 flex-1 resize-none rounded-md border border-clinical-border bg-white p-3 text-sm leading-6 outline-none focus:border-blue-600"
        onChange={(event) => onRawTextChange(event.target.value)}
        placeholder="Paste or load the assignment patient summary..."
        value={rawText}
      />
      <SourceSpanList
        onSelectEvidence={onSelectEvidence}
        selectedEvidenceId={selectedEvidenceId}
        sourceSpans={sourceSpans}
      />
    </div>
  );
}
