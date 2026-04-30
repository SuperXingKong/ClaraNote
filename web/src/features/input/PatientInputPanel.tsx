import { Braces, FileText, Play, RotateCcw, Trash2 } from "lucide-react";

import { Button } from "../../components/ui/Button";
import { ASSIGNMENT_SAMPLE, FHIR_BUNDLE_SAMPLE } from "../../test/fixtures";
import type { SourceSpan } from "../../api/types";
import { SourceSpanList } from "./SourceSpanList";

export type InputMode = "text" | "fhir";

export function PatientInputPanel({
  rawText,
  fhirText,
  inputMode,
  sourceSpans,
  selectedEvidenceId,
  isLoading,
  onRawTextChange,
  onFhirTextChange,
  onInputModeChange,
  onRunDraft,
  onSelectEvidence,
}: {
  rawText: string;
  fhirText: string;
  inputMode: InputMode;
  sourceSpans: SourceSpan[];
  selectedEvidenceId: string | null;
  isLoading: boolean;
  onRawTextChange: (value: string) => void;
  onFhirTextChange: (value: string) => void;
  onInputModeChange: (mode: InputMode) => void;
  onRunDraft: () => void;
  onSelectEvidence: (id: string) => void;
}) {
  const isFhir = inputMode === "fhir";
  const currentValue = isFhir ? fhirText : rawText;
  const handleChange = isFhir ? onFhirTextChange : onRawTextChange;
  const loadSample = () =>
    isFhir ? onFhirTextChange(FHIR_BUNDLE_SAMPLE) : onRawTextChange(ASSIGNMENT_SAMPLE);
  const clear = () => (isFhir ? onFhirTextChange("") : onRawTextChange(""));

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div
        aria-label="Input mode"
        className="flex gap-1 border-b border-clinical-border p-2"
        role="tablist"
      >
        <button
          aria-selected={!isFhir}
          className={`flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium ${
            isFhir
              ? "text-clinical-muted hover:bg-clinical-bg"
              : "bg-clinical-bg text-clinical-text"
          }`}
          onClick={() => onInputModeChange("text")}
          role="tab"
          type="button"
        >
          <FileText aria-hidden="true" size={14} />
          Plain text
        </button>
        <button
          aria-selected={isFhir}
          className={`flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-xs font-medium ${
            isFhir
              ? "bg-clinical-bg text-clinical-text"
              : "text-clinical-muted hover:bg-clinical-bg"
          }`}
          onClick={() => onInputModeChange("fhir")}
          role="tab"
          type="button"
        >
          <Braces aria-hidden="true" size={14} />
          FHIR Bundle
        </button>
      </div>
      <div className="flex flex-wrap gap-2 border-b border-clinical-border p-3">
        <Button
          icon={<FileText aria-hidden="true" size={16} />}
          onClick={loadSample}
        >
          Load sample
        </Button>
        <Button
          icon={<Trash2 aria-hidden="true" size={16} />}
          onClick={clear}
        >
          Clear
        </Button>
        <Button
          className="ml-auto"
          disabled={!currentValue.trim() || isLoading}
          icon={isLoading ? <RotateCcw aria-hidden="true" className="animate-spin" size={16} /> : <Play aria-hidden="true" size={16} />}
          onClick={onRunDraft}
          variant="primary"
        >
          {isLoading ? "Running" : "Run draft"}
        </Button>
      </div>
      <label
        className="px-4 pt-4 text-xs font-semibold uppercase tracking-wide text-clinical-muted"
        htmlFor="patient-summary"
      >
        {isFhir ? "FHIR Bundle JSON" : "Patient summary"}
      </label>
      <textarea
        id="patient-summary"
        className={`mx-4 mt-2 min-h-64 flex-1 resize-none rounded-md border border-clinical-border bg-white p-3 leading-6 outline-none focus:border-blue-600 ${
          isFhir ? "font-mono text-xs" : "text-sm"
        }`}
        onChange={(event) => handleChange(event.target.value)}
        placeholder={
          isFhir
            ? 'Paste a FHIR Bundle JSON or click "Load sample"...'
            : "Paste or load the assignment patient summary..."
        }
        spellCheck={!isFhir}
        value={currentValue}
      />
      <SourceSpanList
        onSelectEvidence={onSelectEvidence}
        selectedEvidenceId={selectedEvidenceId}
        sourceSpans={sourceSpans}
      />
    </div>
  );
}
