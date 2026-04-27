import { BarChart3 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { Badge } from "../../components/ui/Badge";
import { getEvaluationReport } from "../../api/evaluationApi";

export function EvaluationReportView() {
  const { data, error, isLoading } = useQuery({
    queryKey: ["evaluation-report"],
    queryFn: getEvaluationReport,
    staleTime: 60_000,
  });
  const metrics = data?.result.metrics;

  return (
    <section className="rounded-md border border-clinical-border bg-white p-3 text-sm">
      <div className="flex items-center gap-2">
        <Badge tone="info">
          <BarChart3 aria-hidden="true" size={14} />
          Evaluation
        </Badge>
        <span className="font-medium">Backend report</span>
      </div>
      {isLoading && <p className="mt-2 text-clinical-muted">Loading evaluation metrics...</p>}
      {error && (
        <p className="mt-2 leading-6 text-clinical-muted">
          Run <code>python -m clinical_ai.app.evaluate</code> for the golden-case safety report,
          or start the backend to load this card.
        </p>
      )}
      {metrics && (
        <dl aria-label="Evaluation metrics" className="mt-3 grid grid-cols-2 gap-2 text-xs">
          <Metric label="Cases" value={`${metrics.valid_cases}/${metrics.total_cases}`} />
          <Metric label="Evidence" value={`${Math.round(metrics.evidence_coverage_rate * 100)}%`} />
          <Metric label="Hallucination" value={metrics.hallucination_issue_count.toString()} />
          <Metric label="Omission" value={metrics.omission_issue_count.toString()} />
          <Metric label="Unsafe" value={metrics.unsafe_directive_count.toString()} />
          <Metric label="Ambiguity" value={metrics.ambiguity_failure_count.toString()} />
        </dl>
      )}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-clinical-border p-2">
      <dt className="text-clinical-muted">{label}</dt>
      <dd className="mt-1 text-sm font-semibold text-clinical-text">{value}</dd>
    </div>
  );
}
