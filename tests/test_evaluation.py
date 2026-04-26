from clinical_ai.app.evaluation import (
    DEFAULT_GOLDEN_CASES,
    compute_clinician_edit_rate,
    evaluate_golden_cases,
    generate_assignment_report,
)
from clinical_ai.app.pipeline import DraftPipeline
from clinical_ai.app.schemas import ClinicianReviewRecord


def test_golden_case_evaluation_runs_and_reports_metrics():
    result = evaluate_golden_cases(pipeline=DraftPipeline(), cases=DEFAULT_GOLDEN_CASES[:1])

    assert result.metrics.total_cases == 1
    assert result.metrics.evidence_coverage_rate > 0
    assert result.case_results[0].case_id == "assignment_full"


def test_assignment_report_contains_safety_summary():
    result = evaluate_golden_cases(pipeline=DraftPipeline(), cases=DEFAULT_GOLDEN_CASES[:1])
    report = generate_assignment_report(result)

    assert "Safety-first Clinical Summarization Evaluation" in report
    assert "Evidence coverage rate" in report
    assert "Human-in-the-loop" in report


def test_clinician_edit_rate_counts_edit_and_reject():
    records = [
        ClinicianReviewRecord(draft_id="1", decision="accept"),
        ClinicianReviewRecord(draft_id="2", decision="edit"),
        ClinicianReviewRecord(draft_id="3", decision="reject"),
    ]

    assert compute_clinician_edit_rate(records) == 2 / 3

