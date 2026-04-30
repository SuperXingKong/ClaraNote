from fastapi.testclient import TestClient

from clinical_ai.app.main import create_app


def test_healthz_reports_status_and_provider():
    client = TestClient(create_app())

    response = client.get("/healthz")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["llm_provider"] == "openai"
    assert isinstance(payload["openai_key_configured"], bool)
