import { BarChart3 } from "lucide-react";

import { Badge } from "../../components/ui/Badge";

export function EvaluationReportView() {
  return (
    <section className="rounded-md border border-clinical-border bg-white p-3 text-sm">
      <div className="flex items-center gap-2">
        <Badge tone="info">
          <BarChart3 aria-hidden="true" size={14} />
          Evaluation
        </Badge>
        <span className="font-medium">Backend report</span>
      </div>
      <p className="mt-2 leading-6 text-clinical-muted">
        Run <code>python -m clinical_ai.app.evaluate</code> for the golden-case safety report.
        A future API endpoint can render that report here.
      </p>
    </section>
  );
}
