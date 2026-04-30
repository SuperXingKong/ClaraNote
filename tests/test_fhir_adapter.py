import os

import pytest
from fastapi.testclient import TestClient

from clinical_ai.app.fhir_adapter import fhir_bundle_to_text
from clinical_ai.app.main import create_app


def assignment_fhir_bundle():
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-1",
                    "gender": "female",
                    "birthDate": "1967-06-15",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "condition-diabetes",
                    "code": {"text": "type 2 diabetes"},
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "condition-hyperlipidemia",
                    "code": {"text": "hyperlipidemia"},
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "hba1c-jan",
                    "code": {"text": "HbA1c"},
                    "effectiveDateTime": "2026-01-15",
                    "valueQuantity": {"value": 7.8, "unit": "%"},
                    "performer": [{"display": "North Clinic"}],
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "hba1c-mar",
                    "code": {"text": "HbA1c"},
                    "effectiveDateTime": "2026-03-15",
                    "valueQuantity": {"value": 8.4, "unit": "%"},
                    "performer": [{"display": "South Clinic"}],
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "glucose-a",
                    "code": {"text": "Fasting glucose"},
                    "valueQuantity": {"value": 6.5, "unit": "mmol/L"},
                    "note": [{"text": "unclear which is most recent"}],
                    "performer": [{"display": "North Clinic"}],
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "glucose-b",
                    "code": {"text": "Fasting glucose"},
                    "valueQuantity": {"value": 8.9, "unit": "mmol/L"},
                    "note": [{"text": "unclear which is most recent"}],
                    "performer": [{"display": "South Clinic"}],
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "ldl",
                    "code": {"text": "LDL"},
                    "valueQuantity": {"value": 4.2, "unit": "mmol/L"},
                    "performer": [{"display": "South Clinic"}],
                }
            },
            {
                "resource": {
                    "resourceType": "MedicationStatement",
                    "id": "metformin",
                    "status": "active",
                    "medicationCodeableConcept": {"text": "Metformin"},
                    "dosage": [{"text": "500mg twice daily"}],
                }
            },
            {
                "resource": {
                    "resourceType": "MedicationStatement",
                    "id": "atorvastatin",
                    "status": "unknown",
                    "medicationCodeableConcept": {"text": "Atorvastatin"},
                    "dosage": [{"text": "10mg"}],
                    "note": [{"text": "patient unsure if still taking"}],
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "fatigue",
                    "code": {"text": "Fatigue"},
                    "valueBoolean": True,
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "blurred-vision",
                    "code": {"text": "Occasional blurred vision"},
                    "valueBoolean": True,
                }
            },
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "diet",
                    "code": {"text": "Diet"},
                    "note": [{"text": "Patient reports improving diet recently"}],
                }
            },
        ],
    }


def test_fhir_bundle_to_text_preserves_assignment_evidence():
    text = fhir_bundle_to_text(assignment_fhir_bundle())

    assert "58-year-old female with history of type 2 diabetes and hyperlipidemia" in text
    assert "HbA1c: 7.8% (Jan), 8.4% (Mar)" in text
    assert "Fasting glucose: 6.5 mmol/L, 8.9 mmol/L (unclear which is most recent)" in text
    assert "LDL: 4.2 mmol/L" in text
    assert "Atorvastatin 10mg (patient unsure if still taking)" in text
    assert "Some lab values recorded from different clinics" in text


def test_fhir_draft_endpoint_runs_existing_safety_pipeline():
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set — skipping live-LLM endpoint test")

    client = TestClient(create_app())

    response = client.post("/v1/drafts/fhir", json={"bundle": assignment_fhir_bundle()})

    assert response.status_code == 200
    payload = response.json()
    assert payload["draft"] is not None, payload["validation"]["errors"]
    output_text = str(payload["draft"]).lower()
    # Real-LLM phrasing varies; assert on clinical content, not exact wording.
    assert "hba1c" in output_text and ("8.4" in output_text or "increase" in output_text)
    assert "ldl" in output_text and "4.2" in output_text
    assert "clinic" in output_text or "source" in output_text


def test_fhir_draft_endpoint_rejects_non_bundle_input():
    client = TestClient(create_app())

    response = client.post("/v1/drafts/fhir", json={"bundle": {"resourceType": "Patient"}})

    assert response.status_code == 400
    assert "Expected a FHIR Bundle" in response.json()["detail"]
