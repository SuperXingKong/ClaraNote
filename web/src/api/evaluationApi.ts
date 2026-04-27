import { getJson } from "./client";
import type { EvaluationReportResponse } from "./types";

export function getEvaluationReport(): Promise<EvaluationReportResponse> {
  return getJson<EvaluationReportResponse>("/v1/evaluation");
}
