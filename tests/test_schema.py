import pytest
from pydantic import ValidationError

from claranote.app.schemas import ClinicalReviewDraft


def test_missing_required_schema_fields_fail():
    with pytest.raises(ValidationError):
        ClinicalReviewDraft.model_validate({"key_clinical_summary": []})


def test_valid_minimal_schema_passes():
    draft = ClinicalReviewDraft.model_validate(
        {
            "key_clinical_summary": [],
            "trends": [],
            "risk_flags": [],
            "uncertainties": [],
            "suggested_follow_up_areas": [],
            "safety_note": "Draft for clinician review only.",
        }
    )

    assert draft.safety_note.startswith("Draft for clinician review")

