from clinical_ai.app.pipeline import split_source_spans

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


def test_assignment_source_spans_are_section_sized_and_informative():
    spans = split_source_spans(ASSIGNMENT_SUMMARY)

    assert len(spans) == 5
    assert spans[0].text == "58-year-old female with history of type 2 diabetes and hyperlipidemia."
    assert spans[1].text.startswith("Latest labs")
    assert "HbA1c" in spans[1].text
    assert "Fasting glucose" in spans[1].text
    assert "LDL" in spans[1].text
    assert spans[2].text.startswith("Medications:")
    assert "Metformin" in spans[2].text
    assert "Atorvastatin" in spans[2].text
    assert spans[3].text.startswith("Symptoms:")
    assert "Fatigue" in spans[3].text
    assert spans[4].text.startswith("Notes:")
    assert "different clinics" in spans[4].text


def test_heading_only_lines_are_not_standalone_source_spans():
    spans = split_source_spans("Labs:\n- LDL: 4.2 mmol/L\nNotes:\n")

    assert [span.text for span in spans] == ["Labs:\nLDL: 4.2 mmol/L"]


def test_single_paragraph_falls_back_to_sentence_spans():
    spans = split_source_spans("Patient has diabetes. LDL is 4.2 mmol/L.")

    assert [span.text for span in spans] == ["Patient has diabetes.", "LDL is 4.2 mmol/L."]
