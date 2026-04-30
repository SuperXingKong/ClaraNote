export const ASSIGNMENT_SAMPLE = `58-year-old female with history of type 2 diabetes and hyperlipidemia.
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
- Some lab values recorded from different clinics`;

export const FHIR_BUNDLE_SAMPLE = JSON.stringify(
  {
    resourceType: "Bundle",
    type: "collection",
    entry: [
      {
        resource: {
          resourceType: "Patient",
          id: "p1",
          gender: "female",
          birthDate: "1968-01-01",
        },
      },
      {
        resource: {
          resourceType: "Condition",
          id: "c1",
          code: { text: "type 2 diabetes" },
        },
      },
      {
        resource: {
          resourceType: "Condition",
          id: "c2",
          code: { text: "hyperlipidemia" },
        },
      },
      {
        resource: {
          resourceType: "Observation",
          id: "o1",
          code: { text: "HbA1c" },
          valueQuantity: { value: 7.8, unit: "%" },
          effectiveDateTime: "2026-01-15",
          performer: [{ display: "Clinic A" }],
        },
      },
      {
        resource: {
          resourceType: "Observation",
          id: "o2",
          code: { text: "HbA1c" },
          valueQuantity: { value: 8.4, unit: "%" },
          effectiveDateTime: "2026-03-10",
          performer: [{ display: "Clinic B" }],
        },
      },
      {
        resource: {
          resourceType: "Observation",
          id: "o3",
          code: { text: "Fasting glucose" },
          valueQuantity: { value: 6.5, unit: "mmol/L" },
          note: [{ text: "date unclear" }],
          performer: [{ display: "Clinic A" }],
        },
      },
      {
        resource: {
          resourceType: "Observation",
          id: "o4",
          code: { text: "Fasting glucose" },
          valueQuantity: { value: 8.9, unit: "mmol/L" },
          note: [{ text: "date unclear" }],
          performer: [{ display: "Clinic B" }],
        },
      },
      {
        resource: {
          resourceType: "Observation",
          id: "o5",
          code: { text: "LDL cholesterol" },
          valueQuantity: { value: 4.2, unit: "mmol/L" },
          performer: [{ display: "Clinic A" }],
        },
      },
      {
        resource: {
          resourceType: "Observation",
          id: "o6",
          code: { text: "Fatigue" },
        },
      },
      {
        resource: {
          resourceType: "Observation",
          id: "o7",
          code: { text: "Occasional blurred vision" },
        },
      },
      {
        resource: {
          resourceType: "MedicationStatement",
          id: "m1",
          status: "active",
          medicationCodeableConcept: { text: "Metformin 500mg" },
          dosage: [{ text: "500mg twice daily" }],
        },
      },
      {
        resource: {
          resourceType: "MedicationStatement",
          id: "m2",
          status: "unknown",
          medicationCodeableConcept: { text: "Atorvastatin 10mg" },
          note: [{ text: "patient unsure if still taking" }],
        },
      },
    ],
  },
  null,
  2,
);
