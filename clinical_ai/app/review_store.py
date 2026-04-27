from __future__ import annotations

import json
from pathlib import Path

from clinical_ai.app.privacy import redact_text
from clinical_ai.app.schemas import ClinicianReviewRecord, ReviewSubmissionRequest


DEFAULT_REVIEW_LOG_PATH = Path(".data/reviews.jsonl")


class JsonlReviewStore:
    def __init__(self, path: Path | str = DEFAULT_REVIEW_LOG_PATH) -> None:
        self.path = Path(path)

    def add(self, request: ReviewSubmissionRequest) -> ClinicianReviewRecord:
        record = ClinicianReviewRecord(
            draft_id=request.draft_id,
            item_key=request.item_key,
            decision=request.decision,
            reason_codes=request.reason_codes,
            edited_text=redact_text(request.edited_text),
            comments=redact_text(request.comments),
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(record.model_dump_json() + "\n")
        return record

    def list(self, limit: int = 100) -> list[ClinicianReviewRecord]:
        if not self.path.exists():
            return []

        rows: list[ClinicianReviewRecord] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped:
                    continue
                rows.append(ClinicianReviewRecord.model_validate(json.loads(stripped)))

        if limit <= 0:
            return []
        return rows[-limit:]
