import { describe, expect, it, vi } from "vitest";

import {
  buildClientRequestId,
  buildIdempotencyKey,
  generatedActionMetadata,
  generatedRevisionMarker,
} from "./adminActionMetadata";

describe("adminActionMetadata", () => {
  it("generates safe idempotency and request identifiers without QA fixtures", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue(
      "11111111-2222-4333-8444-555555555555",
    );

    expect(buildClientRequestId("Workflow Save")).toBe(
      "workflow-save-11111111-2222-4333-8444-555555555555",
    );
    expect(buildIdempotencyKey("workflow-save")).toBe(
      "idem-workflow-save-11111111-2222-4333-8444-555555555555",
    );
    expect(generatedActionMetadata("usage-export")).toEqual({
      idempotencyKey:
        "idem-usage-export-11111111-2222-4333-8444-555555555555",
      requestId: "req-usage-export-11111111-2222-4333-8444-555555555555",
    });
    expect(generatedRevisionMarker("fallback")).toBe(
      "rev-fallback-11111111-2222-4333-8444-555555555555",
    );
  });
});
