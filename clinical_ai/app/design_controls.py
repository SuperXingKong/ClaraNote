from __future__ import annotations

from clinical_ai.app.schemas import DesignControl, DesignReference, DesignControlsResponse


FDA_CDS = DesignReference(
    label="Clinical Decision Support Software Guidance, January 2026",
    authority="FDA",
    url="https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software",
)
FDA_GMLP = DesignReference(
    label="Good Machine Learning Practice for Medical Device Development",
    authority="FDA",
    url="https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles",
)
WHO_LMM = DesignReference(
    label="Ethics and governance guidance for large multi-modal models, 2024",
    authority="WHO",
    url="https://www.who.int/news/item/18-01-2024-who-releases-ai-ethics-and-governance-guidance-for-large-multi-modal-models",
)
CHAI_RAIG = DesignReference(
    label="Responsible AI Guide",
    authority="Coalition for Health AI",
    url="https://www.chai.org/workgroup/responsible-ai/responsible-ai-guide-raig-and-raig-executive-summary",
)
CREOLA = DesignReference(
    label="CREOLA clinical summarisation hallucination and omission framework",
    authority="npj Digital Medicine",
    url="https://www.nature.com/articles/s41746-025-01670-7",
)
WCAG_22 = DesignReference(
    label="WCAG 2.2 as ISO/IEC 40500:2025",
    authority="W3C",
    url="https://www.w3.org/press-releases/2025/wcag22-iso-pas/",
)


DESIGN_CONTROLS = [
    DesignControl(
        feature_id="clinician_review_draft",
        title="Clinician-review draft boundary",
        summary="The system frames outputs as review drafts, not autonomous diagnosis or treatment.",
        rationale=(
            "The assignment asks for clinician-readable output. FDA CDS guidance emphasizes that "
            "healthcare professionals must be able to independently review the basis of recommendations."
        ),
        implemented_in=[
            "clinical_ai/app/prompt.py",
            "clinical_ai/app/schemas.py",
            "web/src/features/draft/DraftWorkspace.tsx",
        ],
        references=[FDA_CDS, WHO_LMM],
    ),
    DesignControl(
        feature_id="evidence_mapping",
        title="Evidence mapping for every clinical claim",
        summary="Each draft item carries source-span IDs so reviewers can trace claims to input text.",
        rationale=(
            "Traceable evidence supports independent review and reduces unsupported-claim risk in "
            "clinical summarisation."
        ),
        implemented_in=[
            "clinical_ai/app/pipeline.py",
            "clinical_ai/app/validators.py",
            "web/src/features/draft/EvidenceBadge.tsx",
        ],
        references=[FDA_CDS, CREOLA, CHAI_RAIG],
    ),
    DesignControl(
        feature_id="uncertainty_handling",
        title="Explicit uncertainty and data-quality handling",
        summary="Ambiguous or conflicting data are surfaced as uncertainties rather than inferred away.",
        rationale=(
            "WHO notes risks from false, inaccurate, biased, or incomplete LMM statements. CREOLA "
            "supports structured prompts and unknown handling to reduce clinical summarisation errors."
        ),
        implemented_in=[
            "clinical_ai/app/prompt.py",
            "clinical_ai/app/validators.py",
            "web/src/features/draft/DraftSection.tsx",
        ],
        references=[WHO_LMM, CREOLA],
    ),
    DesignControl(
        feature_id="second_pass_safety_review",
        title="Second-pass deterministic safety review",
        summary="Generated drafts are checked for unsafe directives, temporality errors, evidence gaps, and omissions.",
        rationale=(
            "CREOLA describes clinical safety assessment for hallucinations and omissions. CHAI emphasizes "
            "safety, reliability, transparency, and accountability across the health AI lifecycle."
        ),
        implemented_in=[
            "clinical_ai/app/safety_reviewer.py",
            "clinical_ai/app/validators.py",
            "web/src/features/validation/ValidationPanel.tsx",
        ],
        references=[CREOLA, CHAI_RAIG],
    ),
    DesignControl(
        feature_id="human_review_controls",
        title="Human-in-the-loop review controls",
        summary="Reviewers can accept, edit, reject, mark wrong evidence, and mark missing risk, with backend audit records.",
        rationale=(
            "WHO recommends stakeholder engagement and oversight across development and deployment. "
            "The UI and API record human review decisions to reduce automation-bias risk and support accountability."
        ),
        implemented_in=[
            "clinical_ai/app/schemas.py",
            "clinical_ai/app/review_store.py",
            "clinical_ai/app/api.py",
            "web/src/features/review/ReviewControls.tsx",
            "web/src/features/review/ReviewReasonDialog.tsx",
        ],
        references=[WHO_LMM, CHAI_RAIG],
    ),
    DesignControl(
        feature_id="accessible_review_ui",
        title="Accessible safety review UI",
        summary="The UI uses text plus icons and accessible controls for review, validation, and evidence interactions.",
        rationale=(
            "Clinical safety controls must be usable by reviewers. WCAG 2.2 provides the current web "
            "accessibility baseline and is approved as ISO/IEC 40500:2025."
        ),
        implemented_in=[
            "web/src/components/ui/Button.tsx",
            "web/src/features/validation/SafetyStatusBadge.tsx",
            "web/tests/a11y.spec.ts",
        ],
        references=[WCAG_22],
    ),
    DesignControl(
        feature_id="evaluation_reporting",
        title="Golden-case evaluation reporting",
        summary="The backend exposes lifecycle evaluation metrics and a markdown report for the safety-first summarisation workflow.",
        rationale=(
            "FDA GMLP emphasizes total product lifecycle thinking for AI/ML systems. CHAI and CREOLA "
            "support explicit testing, monitoring, and reporting of safety-relevant failure modes."
        ),
        implemented_in=[
            "clinical_ai/app/evaluation.py",
            "clinical_ai/app/api.py",
            "web/src/features/evaluation/EvaluationReportView.tsx",
        ],
        references=[FDA_GMLP, CHAI_RAIG, CREOLA],
    ),
]


def get_design_controls() -> DesignControlsResponse:
    return DesignControlsResponse(controls=DESIGN_CONTROLS)
