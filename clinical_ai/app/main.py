from __future__ import annotations

from fastapi import FastAPI

from clinical_ai.app.api import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Clinical Review Draft Generator",
        version="0.1.0",
        description="MVP backend for evidence-linked clinician-review drafts.",
    )
    app.include_router(router)
    return app


app = create_app()

