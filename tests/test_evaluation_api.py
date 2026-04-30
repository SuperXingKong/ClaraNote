from fastapi.testclient import TestClient

from claranote.app.main import create_app


def test_evaluation_api_returns_metrics_and_report():
    client = TestClient(create_app())

    response = client.get("/v1/evaluation")

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"]["metrics"]["total_cases"] >= 1
    assert "Safety-first Clinical Summarization Evaluation" in payload["report_markdown"]
