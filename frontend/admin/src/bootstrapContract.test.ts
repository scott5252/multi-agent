import { describe, expect, it } from "vitest";

import {
  assertMutationResult,
  assertReactAdminBootstrap,
  assertReactAdminCommandSearch,
  REACT_ADMIN_SCHEMA_HASH,
} from "./api/generated/reactAdminApi";
import { validationResultFixture } from "./test/patternsTestData";
import { bootstrapFixture } from "./test/shellTestData";

describe("generated React admin contract", () => {
  it("accepts the minimal safe bootstrap shape", () => {
    expect(assertReactAdminBootstrap(bootstrapFixture).principal.principal_id).toBe(
      "tenant-admin-acme",
    );
    expect(REACT_ADMIN_SCHEMA_HASH).toHaveLength(64);
  });

  it("rejects payloads without a safe principal", () => {
    expect(() => assertReactAdminBootstrap({ navigation: [] })).toThrow(
      /safe principal/,
    );
  });

  it("accepts safe command search results", () => {
    const payload = {
      query: "workflow",
      results: bootstrapFixture.shell.command_results,
    };

    expect(assertReactAdminCommandSearch(payload).results[0].label).toBe(
      "Workflow Registry",
    );
  });

  it("accepts safe mutation results", () => {
    expect(assertMutationResult(validationResultFixture).status).toBe(
      "validation_error",
    );
  });
});
