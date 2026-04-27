from __future__ import annotations

from fastapi import APIRouter

from clinical_ai.app.design_controls import get_design_controls
from clinical_ai.app.pipeline import DraftPipeline
from clinical_ai.app.review_store import JsonlReviewStore
from clinical_ai.app.schemas import (
    DesignControlsResponse,
    DraftRequest,
    DraftResponse,
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


@router.get("/v1/design-controls", response_model=DesignControlsResponse)
async def read_design_controls() -> DesignControlsResponse:
    return get_design_controls()


@router.post("/v1/reviews", response_model=ReviewSubmissionResponse)
async def create_review(request: ReviewSubmissionRequest) -> ReviewSubmissionResponse:
    return ReviewSubmissionResponse(review=review_store.add(request))


@router.get("/v1/reviews", response_model=ReviewListResponse)
async def list_reviews(limit: int = 100) -> ReviewListResponse:
    return ReviewListResponse(reviews=review_store.list(limit=limit))
