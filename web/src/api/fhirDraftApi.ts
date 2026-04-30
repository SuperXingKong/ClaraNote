import { postJson } from "./client";
import type { DraftResponse, FhirDraftRequest } from "./types";

export function createFhirDraft(request: FhirDraftRequest): Promise<DraftResponse> {
  return postJson<FhirDraftRequest, DraftResponse>("/v1/drafts/fhir", request);
}
