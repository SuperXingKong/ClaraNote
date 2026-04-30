ASSIGNMENT_SUMMARY = """
58-year-old female with history of type 2 diabetes and hyperlipidemia.
Latest labs (last 2-3 months):
- HbA1c: 7.8% (Jan), 8.4% (March)
- Fasting glucose: 6.5 mmol/L, 8.9 mmol/L (unclear which is most recent)
- LDL: 4.2 mmol/L
Medications:
- Metformin 500mg twice daily
- Atorvastatin 10mg (patient unsure if still taking)
Symptoms:
- Fatigue
- Occasional blurred vision
Notes:
- Patient reports improving diet recently
- Adherence unclear
- Some lab values recorded from different clinics
"""


def test_assignment_case_contains_expected_clinical_review_elements(openai_pipeline):
    response = openai_pipeline.process(ASSIGNMENT_SUMMARY)

    assert response.draft is not None, response.validation.errors
    output_text = response.draft.model_dump_json().lower()

    # Real-LLM outputs vary in wording; assert on the *clinical content*, not
    # specific phrasing. The deterministic safety reviewer is exercised
    # separately in tests/test_safety_first_validators.py and tests/test_evidence.py.
    assert "hba1c" in output_text
    assert "8.4" in output_text
    assert "ldl" in output_text and "4.2" in output_text
    assert "atorvastatin" in output_text
    assert "unsure" in output_text or "unclear" in output_text or "uncertain" in output_text
    assert "fasting glucose" in output_text
    assert "different clinics" in output_text or "multi" in output_text
