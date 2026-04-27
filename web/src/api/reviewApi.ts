import { postJson } from "./client";
import type { ReviewSubmissionRequest, ReviewSubmissionResponse } from "./types";

export function submitReview(
  request: ReviewSubmissionRequest,
): Promise<ReviewSubmissionResponse> {
  return postJson<ReviewSubmissionRequest, ReviewSubmissionResponse>("/v1/reviews", request);
}
