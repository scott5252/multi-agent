import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  governanceDashboardFixture,
  governanceMutationFixture,
} from "../../test/governanceTestData";
import { GovernancePage } from "./GovernancePage";

describe("GovernancePage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads safe governance data and runs an explicit provider probe", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => governanceDashboardFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            ...governanceMutationFixture,
            audit_reference_id: "audit-governance-probe-qa031-openai-primary",
            probe: {
              audit_reference_id: "audit-governance-probe-qa031-openai-primary",
              breaker_state: "closed",
              credential_resolution_status: "safe reference selected",
              failure_category: null,
              latency_bucket: "under 300 ms",
              probe_id: "probe-qa031-openai-primary",
              provider_id: "openai-primary",
              redaction_summary: "Attempt evidence is summarized.",
              retry_state: "no retry needed",
              status: "ready",
              summary: "Explicit mocked probe completed.",
            },
          }),
        }),
    );

    render(<GovernancePage governanceUrl="/admin/app/governance/bootstrap.json" />);

    await screen.findByRole("heading", { name: "Governance" });
    expect(screen.getByText("ModelGateway-only execution is enforced.")).toBeInTheDocument();
    expect(screen.queryByText(/qa031-secret-value/)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Run probe/ }));

    await waitFor(() => {
      expect(
        screen.getByText("audit-governance-probe-qa031-openai-primary"),
      ).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith(
      "/admin/app/governance/providers/openai-primary/probe",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
