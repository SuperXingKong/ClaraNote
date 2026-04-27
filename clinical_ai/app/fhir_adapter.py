from __future__ import annotations

from datetime import date, datetime
from typing import Any


def fhir_bundle_to_text(bundle: dict[str, Any]) -> str:
    """Normalize a small FHIR Bundle into source text for the existing pipeline."""
    resources = _bundle_resources(bundle)
    patient = next((resource for resource in resources if resource.get("resourceType") == "Patient"), None)
    conditions = [resource for resource in resources if resource.get("resourceType") == "Condition"]
    observations = [resource for resource in resources if resource.get("resourceType") == "Observation"]
    medications = [resource for resource in resources if resource.get("resourceType") == "MedicationStatement"]

    lines: list[str] = []
    patient_line = _patient_history_line(patient, conditions)
    if patient_line:
        lines.append(patient_line)

    lab_lines, lab_sources = _lab_lines(observations)
    if lab_lines:
        lines.append("Latest labs from FHIR Observations:")
        lines.extend(lab_lines)

    medication_lines, adherence_uncertain = _medication_lines(medications)
    if medication_lines:
        lines.append("Medications from FHIR MedicationStatement resources:")
        lines.extend(medication_lines)

    symptom_lines = _symptom_lines(observations)
    if symptom_lines:
        lines.append("Symptoms from FHIR Observations:")
        lines.extend(symptom_lines)

    note_lines = _note_lines(observations, medications, lab_sources, adherence_uncertain)
    if note_lines:
        lines.append("Notes:")
        lines.extend(note_lines)

    if not lines:
        raise ValueError("FHIR Bundle does not contain supported Patient, Condition, Observation, or MedicationStatement resources.")

    return "\n".join(lines)


def _bundle_resources(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    if bundle.get("resourceType") != "Bundle":
        raise ValueError("Expected a FHIR Bundle resource.")

    entries = bundle.get("entry")
    if not isinstance(entries, list):
        raise ValueError("FHIR Bundle.entry must be a list.")

    resources: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        resource = entry.get("resource")
        if isinstance(resource, dict):
            resources.append(resource)
    return resources


def _patient_history_line(patient: dict[str, Any] | None, conditions: list[dict[str, Any]]) -> str | None:
    descriptors: list[str] = []
    if patient:
        age = _patient_age(patient)
        gender = patient.get("gender")
        if age is not None and isinstance(gender, str):
            descriptors.append(f"{age}-year-old {gender}")
        elif isinstance(gender, str):
            descriptors.append(gender)

    condition_names = [_display_concept(condition.get("code")) for condition in conditions]
    condition_names = [name for name in condition_names if name]
    if not descriptors and not condition_names:
        return None

    prefix = " ".join(descriptors) if descriptors else "Patient"
    if condition_names:
        return f"{prefix} with history of {_join_clinical_list(condition_names)}."
    return f"{prefix}."


def _lab_lines(observations: list[dict[str, Any]]) -> tuple[list[str], set[str]]:
    grouped: dict[str, list[dict[str, Any]]] = {"hba1c": [], "fasting_glucose": [], "ldl": []}
    lab_sources: set[str] = set()

    for observation in observations:
        category = _lab_category(observation)
        if category is None:
            continue
        grouped[category].append(observation)
        lab_sources.update(_source_displays(observation))

    lines: list[str] = []
    if grouped["hba1c"]:
        lines.append(f"HbA1c: {_format_observation_values(grouped['hba1c'])} {_resource_refs(grouped['hba1c'])}")
    if grouped["fasting_glucose"]:
        suffix = ""
        notes = " ".join(_notes(observation) for observation in grouped["fasting_glucose"]).lower()
        has_missing_date = any(not _effective_date(observation) for observation in grouped["fasting_glucose"])
        if "unclear" in notes or "unknown" in notes or has_missing_date:
            suffix = " (unclear which is most recent)"
        lines.append(
            f"Fasting glucose: {_format_observation_values(grouped['fasting_glucose'])}{suffix} "
            f"{_resource_refs(grouped['fasting_glucose'])}"
        )
    if grouped["ldl"]:
        lines.append(f"LDL: {_format_observation_values(grouped['ldl'])} {_resource_refs(grouped['ldl'])}")

    return lines, lab_sources


def _medication_lines(medications: list[dict[str, Any]]) -> tuple[list[str], bool]:
    lines: list[str] = []
    adherence_uncertain = False
    for medication in medications:
        name = _display_concept(medication.get("medicationCodeableConcept")) or _display_reference(
            medication.get("medicationReference")
        )
        if not name:
            continue
        dosage = _first_dosage_text(medication)
        status = str(medication.get("status", "")).lower()
        notes = _notes(medication)
        uncertainty = ""
        if status in {"unknown", "on-hold", "not-taken"} or "unsure" in notes.lower() or "unclear" in notes.lower():
            uncertainty = " (patient unsure if still taking)"
            adherence_uncertain = True
        detail = f"{name} {dosage}".strip()
        lines.append(f"{detail}{uncertainty} {_resource_refs([medication])}")
    return lines, adherence_uncertain


def _symptom_lines(observations: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for observation in observations:
        label = _display_concept(observation.get("code"))
        if not label:
            continue
        lowered = label.lower()
        if "fatigue" in lowered or "blurred vision" in lowered or "vision" in lowered:
            lines.append(f"{label} {_resource_refs([observation])}")
    return lines


def _note_lines(
    observations: list[dict[str, Any]],
    medications: list[dict[str, Any]],
    lab_sources: set[str],
    adherence_uncertain: bool,
) -> list[str]:
    lines: list[str] = []
    for observation in observations:
        label = _display_concept(observation.get("code")).lower()
        note = _notes(observation)
        lowered = f"{label} {note}".lower()
        if "diet" in lowered and ("improving" in lowered or "improved" in lowered):
            lines.append(f"Patient reports improving diet recently {_resource_refs([observation])}")

    if adherence_uncertain or any("unclear" in _notes(medication).lower() for medication in medications):
        lines.append("Adherence unclear")

    if len(lab_sources) > 1:
        lines.append(f"Some lab values recorded from different clinics: {_join_clinical_list(sorted(lab_sources))}")

    return lines


def _lab_category(observation: dict[str, Any]) -> str | None:
    concept = observation.get("code")
    label = _display_concept(concept).lower()
    codes = {_coding.get("code", "").lower() for _coding in _codings(concept)}
    if "hba1c" in label or "hemoglobin a1c" in label or "4548-4" in codes:
        return "hba1c"
    if "fasting glucose" in label or "1558-6" in codes:
        return "fasting_glucose"
    if "ldl" in label or "13457-7" in codes:
        return "ldl"
    return None


def _format_observation_values(observations: list[dict[str, Any]]) -> str:
    ordered = sorted(observations, key=lambda observation: _effective_date(observation) or date.max)
    return ", ".join(_format_observation_value(observation) for observation in ordered)


def _format_observation_value(observation: dict[str, Any]) -> str:
    value = _quantity_value(observation.get("valueQuantity"))
    effective = _effective_date(observation)
    if effective is not None:
        return f"{value} ({effective.strftime('%b')})"
    return value


def _quantity_value(quantity: Any) -> str:
    if not isinstance(quantity, dict):
        return "value not supplied"
    value = quantity.get("value")
    unit = quantity.get("unit") or quantity.get("code") or ""
    if isinstance(value, float) and value.is_integer():
        value_text = str(int(value))
    else:
        value_text = str(value)
    if unit == "%":
        return f"{value_text}%"
    return f"{value_text} {unit}".strip()


def _patient_age(patient: dict[str, Any]) -> int | None:
    birth_date = patient.get("birthDate")
    if not isinstance(birth_date, str):
        return None
    try:
        born = date.fromisoformat(birth_date)
    except ValueError:
        return None
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def _effective_date(resource: dict[str, Any]) -> date | None:
    raw = resource.get("effectiveDateTime") or resource.get("effectiveInstant") or resource.get("issued")
    if not isinstance(raw, str):
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None


def _display_concept(concept: Any) -> str:
    if not isinstance(concept, dict):
        return ""
    text = concept.get("text")
    if isinstance(text, str) and text.strip():
        return text.strip()
    for coding in _codings(concept):
        display = coding.get("display") or coding.get("code")
        if isinstance(display, str) and display.strip():
            return display.strip()
    return ""


def _codings(concept: Any) -> list[dict[str, Any]]:
    if not isinstance(concept, dict):
        return []
    coding = concept.get("coding")
    return [item for item in coding if isinstance(item, dict)] if isinstance(coding, list) else []


def _display_reference(reference: Any) -> str:
    if not isinstance(reference, dict):
        return ""
    display = reference.get("display") or reference.get("reference")
    return display.strip() if isinstance(display, str) else ""


def _first_dosage_text(medication: dict[str, Any]) -> str:
    dosage = medication.get("dosage")
    if not isinstance(dosage, list):
        return ""
    for item in dosage:
        if isinstance(item, dict) and isinstance(item.get("text"), str):
            return item["text"].strip()
    return ""


def _notes(resource: dict[str, Any]) -> str:
    notes = resource.get("note")
    if not isinstance(notes, list):
        return ""
    return " ".join(note.get("text", "") for note in notes if isinstance(note, dict)).strip()


def _source_displays(resource: dict[str, Any]) -> set[str]:
    sources: set[str] = set()
    meta = resource.get("meta")
    if isinstance(meta, dict) and isinstance(meta.get("source"), str):
        sources.add(meta["source"])
    performer = resource.get("performer")
    if isinstance(performer, list):
        for item in performer:
            display = _display_reference(item)
            if display:
                sources.add(display)
    return sources


def _resource_refs(resources: list[dict[str, Any]]) -> str:
    refs = []
    for resource in resources:
        resource_type = resource.get("resourceType", "Resource")
        resource_id = resource.get("id")
        refs.append(f"{resource_type}/{resource_id}" if resource_id else str(resource_type))
    return f"[FHIR: {', '.join(refs)}]"


def _join_clinical_list(items: list[str]) -> str:
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + f" and {items[-1]}"
