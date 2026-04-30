from __future__ import annotations

from fastapi import APIRouter, HTTPException

from clinical_ai.app.config import Settings, get_settings
from clinical_ai.app.design_controls import get_design_controls
from clinical_ai.app.evaluation import (
    EvaluationReportResponse,
    evaluate_golden_cases,
    generate_assignment_report,
)
from clinical_ai.app.fhir_adapter import fhir_bundle_to_text
from clinical_ai.app.llm_client import MockLLMClient
from clinical_ai.app.openai_client import OpenAIClinicalReviewClient
from clinical_ai.app.pipeline import DraftPipeline
from clinical_ai.app.review_store import JsonlReviewStore
from clinical_ai.app.schemas import (
    DesignControlsResponse,
    DraftRequest,
    DraftResponse,
    FhirDraftRequest,
    HealthResponse,
    ReviewListResponse,
    ReviewSubmissionRequest,
    ReviewSubmissionResponse,
)

router = APIRouter()
def create_llm_client(settings: Settings):
    if settings.llm_provider == "openai":
        return OpenAIClinicalReviewClient(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            timeout_seconds=settings.openai_timeout_seconds,
        )
    return MockLLMClient()


pipeline = DraftPipeline(llm_client=create_llm_client(get_settings()))
review_store = JsonlReviewStore()


@router.get("/healthz", response_model=HealthResponse)
async def healthz() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", llm_provider=settings.llm_provider)


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
