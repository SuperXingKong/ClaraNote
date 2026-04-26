from __future__ import annotations

import argparse

from clinical_ai.app.config import DEFAULT_OPENAI_MODEL, get_settings
from clinical_ai.app.openai_client import OpenAIClinicalReviewClient


def main() -> int:
    parser = argparse.ArgumentParser(description="Test the configured OpenAI API key.")
    parser.add_argument(
        "--model",
        default=None,
        help=f"Model to test. Defaults to OPENAI_MODEL or {DEFAULT_OPENAI_MODEL}.",
    )
    args = parser.parse_args()

    settings = get_settings()
    model = args.model or settings.openai_model
    client = OpenAIClinicalReviewClient(
        api_key=settings.openai_api_key,
        model=model,
        timeout_seconds=settings.openai_timeout_seconds,
    )
    result = client.test_api_key()
    print(result.model_dump_json(indent=2))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

