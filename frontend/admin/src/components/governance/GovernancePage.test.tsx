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
            audit_reference_id: "provider-test:aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            probe: {
              audit_reference_id: "provider-test:aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
              breaker_state: "closed",
              credential_resolution_status: "safe reference selected",
              failure_category: null,
              latency_bucket: "under 300 ms",
              probe_id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
              provider_id: governanceDashboardFixture.providers[0].provider_id,
              redaction_summary: "Attempt evidence is summarized.",
              retry_state: "no retry needed",
              status: "ready",
              summary: "Local safe probe completed.",
            },
          }),
        }),
    );

    render(<GovernancePage governanceUrl="/admin/app/governance/bootstrap.json" />);

    await screen.findByRole("heading", { name: "Governance" });
    expect(screen.getByText("ModelGateway-only execution is enforced.")).toBeInTheDocument();
    expect(screen.queryByText(/raw prompt/i)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Run probe/ }));

    await waitFor(() => {
      expect(
        screen.getByText("provider-test:aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
      ).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith(
      governanceDashboardFixture.providers[0].authorized_actions[0].href,
      expect.objectContaining({ method: "POST" }),
    );
  });
});
