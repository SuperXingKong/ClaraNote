from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from claranote.app.privacy import redact_text
from claranote.app.schemas import ClinicianReviewRecord, ReviewSubmissionRequest

DEFAULT_REVIEW_LOG_PATH = Path(".data/reviews.jsonl")
DEFAULT_REVIEW_RETENTION_DAYS = 30


class JsonlReviewStore:
    def __init__(
        self,
        path: Path | str = DEFAULT_REVIEW_LOG_PATH,
        retention_days: int | None = DEFAULT_REVIEW_RETENTION_DAYS,
    ) -> None:
        self.path = Path(path)
        self.retention_days = retention_days

    def add(self, request: ReviewSubmissionRequest) -> ClinicianReviewRecord:
        self.purge_expired()
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
        self.purge_expired()
        rows = self._read_all()

        if limit <= 0:
            return []
        return rows[-limit:]

    def purge_expired(self, now: datetime | None = None) -> int:
        if self.retention_days is None or not self.path.exists():
            return 0

        current_time = now or datetime.now(UTC)
        cutoff = current_time - timedelta(days=self.retention_days)
        rows = self._read_all()
        retained = [record for record in rows if record.created_at >= cutoff]
        removed_count = len(rows) - len(retained)

        if removed_count:
            self._write_all(retained)

        return removed_count

    def _read_all(self) -> list[ClinicianReviewRecord]:
        if not self.path.exists():
            return []

        rows: list[ClinicianReviewRecord] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped:
                    continue
                rows.append(ClinicianReviewRecord.model_validate(json.loads(stripped)))
        return rows

    def _write_all(self, rows: list[ClinicianReviewRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(row.model_dump_json() + "\n")
