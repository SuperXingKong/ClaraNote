from clinical_ai.app.api import create_llm_client
from clinical_ai.app.config import Settings
from clinical_ai.app.llm_client import MockLLMClient
from clinical_ai.app.openai_client import OpenAIClinicalReviewClient


def test_create_llm_client_defaults_to_mock_provider():
    client = create_llm_client(Settings(openai_api_key=None))

    assert isinstance(client, MockLLMClient)


def test_create_llm_client_uses_openai_when_configured():
    client = create_llm_client(
        Settings(
            openai_api_key="sk-test-key",
            llm_provider="openai",
            openai_model="gpt-5.4",
        )
    )

    assert isinstance(client, OpenAIClinicalReviewClient)
    assert client.provider_name == "openai"
    assert client.model_name == "gpt-5.4"
