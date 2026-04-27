from fastapi.testclient import TestClient

from clinical_ai.app.design_controls import get_design_controls
from clinical_ai.app.main import create_app


def test_design_controls_include_authoritative_references():
    response = get_design_controls()

    assert len(response.controls) >= 5
    for control in response.controls:
        assert control.references, control.feature_id
        for reference in control.references:
            assert reference.authority
            assert reference.url.startswith("https://")


def test_design_controls_api_returns_controls():
    client = TestClient(create_app())

    response = client.get("/v1/design-controls")

    assert response.status_code == 200
    payload = response.json()
    assert payload["controls"]
    assert payload["controls"][0]["references"]
