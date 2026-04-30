from types import SimpleNamespace

from claranote.app.config import DEFAULT_OPENAI_MODEL
from claranote.app.openai_client import OpenAIClinicalReviewClient


class FakeResponses:
    def __init__(self, output_text="ok"):
        self.output_text = output_text
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=self.output_text)


class FakeOpenAIClient:
    def __init__(self, responses):
        self.responses = responses


def test_openai_key_test_uses_default_model():
    responses = FakeResponses()
    client = OpenAIClinicalReviewClient(
        api_key="sk-test-key",
        client=FakeOpenAIClient(responses),
    )

    result = client.test_api_key()

    assert result.ok
    assert result.model == DEFAULT_OPENAI_MODEL
    assert responses.calls[0]["model"] == DEFAULT_OPENAI_MODEL
    assert responses.calls[0]["max_output_tokens"] == 16


def test_openai_key_test_reports_missing_key_without_calling_sdk():
    client = OpenAIClinicalReviewClient(api_key=None)

    result = client.test_api_key()

    assert not result.ok
    assert result.model == DEFAULT_OPENAI_MODEL
    assert "OPENAI_API_KEY is not set" in result.message


def test_openai_key_test_redacts_api_key_from_errors():
    class BrokenResponses:
        def create(self, **kwargs):
            raise RuntimeError("bad key sk-secret-1234567890")

    client = OpenAIClinicalReviewClient(
        api_key="sk-secret-1234567890",
        client=FakeOpenAIClient(BrokenResponses()),
    )

    result = client.test_api_key()

    assert not result.ok
    assert "sk-secret" not in result.message
    assert "[REDACTED_OPENAI_API_KEY]" in result.message

