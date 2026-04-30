"""Shared pytest fixtures.

Per project policy, every test that exercises the LLM pipeline calls the real
OpenAI API. Tests that only exercise the validators with hand-built drafts do
not need this fixture.

If `OPENAI_API_KEY` is not present in the environment, pipeline-using tests
are skipped (rather than failing) so contributors can still run validator-only
tests offline. CI must provide the key as a secret for the full suite to run.
"""

from __future__ import annotations

import os

import pytest

from claranote.app.config import get_settings
from claranote.app.openai_client import OpenAIClinicalReviewClient
from claranote.app.pipeline import DraftPipeline


def _real_openai_client() -> OpenAIClinicalReviewClient:
    settings = get_settings()
    return OpenAIClinicalReviewClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        timeout_seconds=settings.openai_timeout_seconds,
    )


@pytest.fixture(scope="session")
def openai_client() -> OpenAIClinicalReviewClient:
    """Real OpenAI client; pipeline-using tests must request this fixture.

    Skips the test when `OPENAI_API_KEY` is not configured rather than calling
    the API with a missing key (which would 401 noisily).
    """
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set — skipping tests that hit the live LLM")
    return _real_openai_client()


@pytest.fixture(scope="session")
def openai_pipeline(openai_client: OpenAIClinicalReviewClient) -> DraftPipeline:
    """`DraftPipeline` wired to the real OpenAI client."""
    return DraftPipeline(llm_client=openai_client)
