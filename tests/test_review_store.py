from fastapi.testclient import TestClient

from clinical_ai.app import api
from clinical_ai.app.main import create_app
from clinical_ai.app.review_store import JsonlReviewStore
from clinical_ai.app.schemas import ReviewSubmissionRequest


def test_review_store_redacts_and_lists_records(tmp_path):
    store = JsonlReviewStore(tmp_path / "reviews.jsonl")
    record = store.add(
        ReviewSubmissionRequest(
            draft_id="draft-1",
            item_key="summary-0",
            decision="edit",
            reason_codes=["wrong_evidence"],
            comments="contact user@example.com and key sk-testsecret1234567890",
        )
    )

    assert record.comments is not None
    assert "user@example.com" not in record.comments
    assert "sk-testsecret" not in record.comments
    assert len(store.list()) == 1


def test_review_api_persists_records(tmp_path, monkeypatch):
    monkeypatch.setattr(api, "review_store", JsonlReviewStore(tmp_path / "reviews.jsonl"))
    client = TestClient(create_app())

    response = client.post(
        "/v1/reviews",
        json={
            "draft_id": "draft-1",
            "item_key": "risk-0",
            "decision": "reject",
            "reason_codes": ["unsafe_recommendation"],
            "comments": "unsafe wording",
        },
    )

    assert response.status_code == 200
    assert response.json()["review"]["decision"] == "reject"

    list_response = client.get("/v1/reviews")
    assert list_response.status_code == 200
    assert len(list_response.json()["reviews"]) == 1
