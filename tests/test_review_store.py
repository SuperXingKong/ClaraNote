from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from clinical_ai.app import api
from clinical_ai.app.main import create_app
from clinical_ai.app.review_store import JsonlReviewStore
from clinical_ai.app.schemas import ClinicianReviewRecord, ReviewSubmissionRequest


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


def test_review_store_purges_records_outside_retention_window(tmp_path):
    path = tmp_path / "reviews.jsonl"
    now = datetime(2026, 4, 27, tzinfo=UTC)
    old_record = ClinicianReviewRecord(
        draft_id="old",
        item_key="summary-0",
        decision="accept",
        created_at=now - timedelta(days=31),
    )
    current_record = ClinicianReviewRecord(
        draft_id="current",
        item_key="summary-1",
        decision="accept",
        created_at=now - timedelta(days=2),
    )
    path.write_text(old_record.model_dump_json() + "\n" + current_record.model_dump_json() + "\n", encoding="utf-8")
    store = JsonlReviewStore(path, retention_days=30)

    removed_count = store.purge_expired(now=now)

    assert removed_count == 1
    retained_records = JsonlReviewStore(path, retention_days=None).list()
    assert [record.draft_id for record in retained_records] == ["current"]


def test_review_store_can_disable_retention_for_tests(tmp_path):
    path = tmp_path / "reviews.jsonl"
    old_record = ClinicianReviewRecord(
        draft_id="old",
        item_key="summary-0",
        decision="accept",
        created_at=datetime(2020, 1, 1, tzinfo=UTC),
    )
    path.write_text(old_record.model_dump_json() + "\n", encoding="utf-8")
    store = JsonlReviewStore(path, retention_days=None)

    assert store.purge_expired() == 0
    assert len(store.list()) == 1
