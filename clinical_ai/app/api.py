from __future__ import annotations

from fastapi import APIRouter

from clinical_ai.app.pipeline import DraftPipeline
from clinical_ai.app.schemas import DraftRequest, DraftResponse


router = APIRouter()
pipeline = DraftPipeline()


@router.post("/v1/drafts", response_model=DraftResponse)
async def create_draft(request: DraftRequest) -> DraftResponse:
    return pipeline.process(raw_text=request.raw_text)

