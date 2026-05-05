import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  testBenchDashboardFixture,
  testBenchMutationFixture,
  testBenchRunDetailFixture,
} from "../../test/testBenchTestData";
import { TestBenchPage } from "./TestBenchPage";

describe("TestBenchPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads safe test bench data and saves a suite", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => testBenchDashboardFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => testBenchRunDetailFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            ...testBenchMutationFixture,
            audit_reference_id: "audit-test-suite-save-qa033",
            summary: "Test suite saved with current target revision binding.",
          }),
        }),
    );

    render(<TestBenchPage testBenchUrl="/admin/app/test-bench/bootstrap.json" />);

    await screen.findByRole("heading", { name: "Test Bench" });
    expect(screen.getAllByText("Daily briefing release gate").length).toBeGreaterThan(0);
    expect(screen.getByText("Blocked side-effect assertion failed")).toBeInTheDocument();
    expect(screen.queryByText(/qa033-secret-value/)).not.toBeInTheDocument();
    expect(screen.queryByText(/raw prompt/)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Save suite/ }));

    await waitFor(() => {
      expect(screen.getByText("audit-test-suite-save-qa033")).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith(
      "/admin/app/test-bench/suites",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
