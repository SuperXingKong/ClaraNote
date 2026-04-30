import { getJson } from "./client";
import type { DesignControlsResponse } from "./types";

export function fetchDesignControls(): Promise<DesignControlsResponse> {
  return getJson<DesignControlsResponse>("/v1/design-controls");
}
