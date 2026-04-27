from __future__ import annotations

from fastapi import APIRouter, HTTPException

from clinical_ai.app.design_controls import get_design_controls
from clinical_ai.app.evaluation import (
    EvaluationReportResponse,
    evaluate_golden_cases,
    generate_assignment_report,
)
from clinical_ai.app.fhir_adapter import fhir_bundle_to_text
from clinical_ai.app.pipeline import DraftPipeline
from clinical_ai.app.review_store import JsonlReviewStore
from clinical_ai.app.schemas import (
    DesignControlsResponse,
    DraftRequest,
    DraftResponse,
    FhirDraftRequest,
    ReviewListResponse,
    ReviewSubmissionRequest,
    ReviewSubmissionResponse,
)


router = APIRouter()
pipeline = DraftPipeline()
review_store = JsonlReviewStore()


@router.post("/v1/drafts", response_model=DraftResponse)
async def create_draft(request: DraftRequest) -> DraftResponse:
    return pipeline.process(raw_text=request.raw_text)


@router.post("/v1/drafts/fhir", response_model=DraftResponse)
async def create_fhir_draft(request: FhirDraftRequest) -> DraftResponse:
    try:
        raw_text = fhir_bundle_to_text(request.bundle)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return pipeline.process(raw_text=raw_text)


@router.get("/v1/design-controls", response_model=DesignControlsResponse)
async def read_design_controls() -> DesignControlsResponse:
    return get_design_controls()


@router.post("/v1/reviews", response_model=ReviewSubmissionResponse)
async def create_review(request: ReviewSubmissionRequest) -> ReviewSubmissionResponse:
    return ReviewSubmissionResponse(review=review_store.add(request))


@router.get("/v1/reviews", response_model=ReviewListResponse)
async def list_reviews(limit: int = 100) -> ReviewListResponse:
    return ReviewListResponse(reviews=review_store.list(limit=limit))


@router.get("/v1/evaluation", response_model=EvaluationReportResponse)
async def read_evaluation_report() -> EvaluationReportResponse:
    result = evaluate_golden_cases()
    return EvaluationReportResponse(
        result=result,
        report_markdown=generate_assignment_report(result),
    )
