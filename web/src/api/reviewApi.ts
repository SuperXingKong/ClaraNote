import { getJson, postJson } from "./client";
import type {
  ClinicianReviewRecord,
  ReviewSubmissionRequest,
  ReviewSubmissionResponse,
} from "./types";

export function submitReview(
  request: ReviewSubmissionRequest,
): Promise<ReviewSubmissionResponse> {
  return postJson<ReviewSubmissionRequest, ReviewSubmissionResponse>("/v1/reviews", request);
}

type ReviewListResponse = {
  reviews: ClinicianReviewRecord[];
};

export async function fetchReviews(limit = 25): Promise<ClinicianReviewRecord[]> {
  const response = await getJson<ReviewListResponse>(`/v1/reviews?limit=${limit}`);
  return response.reviews;
}
