import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  migrationDashboard,
  migrationRollbackPlan,
  migrationRouteGroups,
} from "../../test/migrationHardeningTestData";
import { MigrationHardeningPage } from "./MigrationHardeningPage";

describe("MigrationHardeningPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads dashboard, route matrix, rollback, and refreshes safely", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({ ok: true, json: async () => migrationDashboard })
        .mockResolvedValueOnce({ ok: true, json: async () => migrationRouteGroups })
        .mockResolvedValueOnce({ ok: true, json: async () => migrationRollbackPlan })
        .mockResolvedValueOnce({ ok: true, json: async () => migrationDashboard })
        .mockResolvedValueOnce({ ok: true, json: async () => migrationRouteGroups })
        .mockResolvedValueOnce({ ok: true, json: async () => migrationRollbackPlan }),
    );

    render(
      <MigrationHardeningPage dashboardUrl="/admin/app/migration/bootstrap.json" />,
    );

    await screen.findByRole("heading", { name: "React Admin Migration Hardening" });
    expect(screen.getByText("React admin home")).toBeInTheDocument();
    expect(screen.getByText("Retained fallback")).toBeInTheDocument();
    expect(screen.getByText("Route safety plan")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Refresh" }));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledTimes(6);
    });
    expect(screen.queryByText(/qa037-secret-value|raw prompt/i)).not.toBeInTheDocument();
  });

  it("renders a denied dependency state when loading fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("tenant_scope_denied")));

    render(
      <MigrationHardeningPage dashboardUrl="/admin/app/migration/bootstrap.json" />,
    );

    await screen.findByRole("heading", { name: "Migration hardening unavailable" });
    expect(screen.getByText("tenant_scope_denied")).toBeInTheDocument();
  });
});
