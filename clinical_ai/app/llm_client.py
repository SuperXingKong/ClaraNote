from __future__ import annotations

from typing import Any, Protocol

from clinical_ai.app.schemas import SourceSpan


class LLMClient(Protocol):
    def generate(self, prompt: str, source_spans: list[SourceSpan]) -> dict[str, Any]:
        """Generate a draft payload that can be parsed as ClinicalReviewDraft."""


class MockLLMClient:
    """Deterministic MVP client for tests and local demos without an API key."""

    def generate(self, prompt: str, source_spans: list[SourceSpan]) -> dict[str, Any]:
        del prompt

        def ids_containing(*needles: str) -> list[str]:
            lowered_needles = [needle.lower() for needle in needles]
            matches = [
                span.id
                for span in source_spans
                if any(needle in span.text.lower() for needle in lowered_needles)
            ]
            return matches or [source_spans[0].id]

        history_ids = ids_containing("58-year-old", "type 2 diabetes", "hyperlipidemia")
        hba1c_ids = ids_containing("hba1c", "7.8", "8.4")
        glucose_ids = ids_containing("fasting glucose", "unclear which is most recent")
        ldl_ids = ids_containing("ldl", "4.2")
        metformin_ids = ids_containing("metformin")
        atorvastatin_ids = ids_containing("atorvastatin", "unsure")
        symptom_ids = ids_containing("fatigue", "blurred vision")
        adherence_ids = ids_containing("adherence unclear", "patient unsure")
        clinic_ids = ids_containing("different clinics")
        diet_ids = ids_containing("improving diet")

        return {
            "key_clinical_summary": [
                {
                    "text": "58-year-old female with history of type 2 diabetes and hyperlipidemia.",
                    "evidence_ids": history_ids,
                    "confidence": "high",
                    "requires_clinician_review": True,
                },
                {
                    "text": "Recent labs include HbA1c 7.8% in January and 8.4% in March, fasting glucose values 6.5 and 8.9 mmol/L with unclear recency, and LDL 4.2 mmol/L.",
                    "evidence_ids": sorted(set(hba1c_ids + glucose_ids + ldl_ids)),
                    "confidence": "high",
                    "requires_clinician_review": True,
                },
                {
                    "text": "Reported medications include metformin 500 mg twice daily and atorvastatin 10 mg, with uncertainty about whether atorvastatin is still being taken.",
                    "evidence_ids": sorted(set(metformin_ids + atorvastatin_ids)),
                    "confidence": "high",
                    "requires_clinician_review": True,
                },
                {
                    "text": "Symptoms reported include fatigue and occasional blurred vision.",
                    "evidence_ids": symptom_ids,
                    "confidence": "high",
                    "requires_clinician_review": True,
                },
            ],
            "trends": [
                {
                    "text": "HbA1c increased from 7.8% in January to 8.4% in March, suggesting worsening glycemic control for clinician review.",
                    "evidence_ids": hba1c_ids,
                    "confidence": "high",
                    "requires_clinician_review": True,
                }
            ],
            "risk_flags": [
                {
                    "text": "HbA1c 8.4% and symptoms of fatigue and occasional blurred vision may warrant review of glycemic control.",
                    "evidence_ids": sorted(set(hba1c_ids + symptom_ids)),
                    "confidence": "medium",
                    "requires_clinician_review": True,
                },
                {
                    "text": "LDL 4.2 mmol/L is a cardiovascular risk flag in a patient with diabetes and hyperlipidemia.",
                    "evidence_ids": sorted(set(ldl_ids + history_ids)),
                    "confidence": "medium",
                    "requires_clinician_review": True,
                },
                {
                    "text": "Medication adherence is unclear, including uncertainty about current atorvastatin use.",
                    "evidence_ids": sorted(set(adherence_ids + atorvastatin_ids)),
                    "confidence": "high",
                    "requires_clinician_review": True,
                },
            ],
            "uncertainties": [
                {
                    "text": "The fasting glucose values have unclear recency, so no fasting glucose trend should be inferred.",
                    "evidence_ids": glucose_ids,
                    "confidence": "high",
                    "requires_clinician_review": True,
                },
                {
                    "text": "The patient is unsure whether she is still taking atorvastatin.",
                    "evidence_ids": atorvastatin_ids,
                    "confidence": "high",
                    "requires_clinician_review": True,
                },
                {
                    "text": "Overall medication adherence is unclear.",
                    "evidence_ids": adherence_ids,
                    "confidence": "high",
                    "requires_clinician_review": True,
                },
                {
                    "text": "Some lab values were recorded from different clinics, so source reconciliation may be needed.",
                    "evidence_ids": clinic_ids,
                    "confidence": "high",
                    "requires_clinician_review": True,
                },
            ],
            "suggested_follow_up_areas": [
                {
                    "text": "Confirm current medication adherence, including metformin use and whether atorvastatin is still being taken.",
                    "evidence_ids": sorted(set(metformin_ids + atorvastatin_ids + adherence_ids)),
                    "confidence": "medium",
                    "requires_clinician_review": True,
                },
                {
                    "text": "Clarify the dates and sources of fasting glucose results before interpreting trend.",
                    "evidence_ids": sorted(set(glucose_ids + clinic_ids)),
                    "confidence": "high",
                    "requires_clinician_review": True,
                },
                {
                    "text": "Review glycemic control in light of HbA1c trend, reported symptoms, and recent diet changes.",
                    "evidence_ids": sorted(set(hba1c_ids + symptom_ids + diet_ids)),
                    "confidence": "medium",
                    "requires_clinician_review": True,
                },
                {
                    "text": "Review lipid and cardiovascular risk context given LDL 4.2 mmol/L and diabetes history.",
                    "evidence_ids": sorted(set(ldl_ids + history_ids)),
                    "confidence": "medium",
                    "requires_clinician_review": True,
                },
            ],
            "safety_note": "Draft for clinician review only. This output does not diagnose, prescribe, or replace clinical judgment.",
        }

