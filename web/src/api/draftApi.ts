import { postJson } from "./client";
import type { DraftRequest, DraftResponse } from "./types";

export function createDraft(request: DraftRequest): Promise<DraftResponse> {
  return postJson<DraftRequest, DraftResponse>("/v1/drafts", request);
}
