import { act, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { validationResultFixture } from "../test/patternsTestData";
import { errorsByField, useAdminMutation } from "./useAdminMutation";

describe("useAdminMutation", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("maps field errors by backend field key", () => {
    expect(errorsByField(validationResultFixture.field_errors)).toEqual({
      sample_name: validationResultFixture.field_errors[0],
    });
  });

  it("submits admin actions and exposes mutation results", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => validationResultFixture,
      }),
    );
    const { result } = renderHook(() =>
      useAdminMutation("/admin/app/admin-actions/test"),
    );

    await act(async () => {
      await result.current.submit({
        confirmed: false,
        idempotency_key: "key-1",
        sample_name: "",
      });
    });

    expect(result.current.result?.status).toBe("validation_error");
    expect(result.current.fieldErrors.sample_name.message).toBe("Enter a sample name.");
  });
});
