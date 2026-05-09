import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";
import { channelDashboard } from "./test/channelTelegramBriefingTestData";
import { consoleHomeFixture } from "./test/consoleHomeTestData";
import { governanceDashboardFixture } from "./test/governanceTestData";
import { membershipDashboardFixture } from "./test/membershipTestData";
import {
  jinjaInventoryDashboard,
  liveDataInventoryDashboard,
  migrationDashboard,
  migrationRollbackPlan,
  migrationRouteGroups,
} from "./test/migrationHardeningTestData";
import { bootstrapFixture } from "./test/shellTestData";
import { skillLifecycleDashboardFixture } from "./test/skillLifecycleTestData";
import { usageDashboard } from "./test/usageTestData";
import { workbenchEnvelopeFixture } from "./test/workbenchTestData";
import {
  workflowBuilderEnvelope,
  workflowReferenceCatalog,
} from "./test/workflowBuilderTestData";

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => bootstrapFixture,
      }),
    );
    window.history.pushState({}, "", "/admin/app");
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders a product-facing Console Home without development traces", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => bootstrapFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => consoleHomeFixture,
        }),
    );

    render(<App />);

    expect(screen.getByText("Loading admin shell")).toBeInTheDocument();
    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "Start here" }),
      ).toBeInTheDocument();
    });

    expect(screen.getAllByText("Multi-Agent Admin").length).toBeGreaterThan(0);
    expect(screen.getByLabelText("Signed-in user")).toHaveTextContent("Tenant Admin");
    expect(screen.getByLabelText("System health")).toHaveTextContent("Ready");
    expect(screen.getByLabelText("Admin scope")).toHaveTextContent("Acme");
    expect(screen.getByRole("link", { name: "Log off" })).toHaveAttribute(
      "href",
      "/auth/local-logout?redirect_to=/auth/local-login",
    );
    expect(
      screen.getByRole("link", { name: "Workflow Registry" }),
    ).toHaveAttribute(
      "href",
      "/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111",
    );
    expect(screen.getByRole("link", { name: /Review workflows/ })).toHaveAttribute(
      "href",
      "/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111",
    );
    expect(screen.getByText("Current notices")).toBeInTheDocument();
    expect(screen.queryByText(/Spec Kit/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/migration/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Jinja/i)).not.toBeInTheDocument();
  });

  it("keeps migration evidence isolated on the migration route", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => bootstrapFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => migrationDashboard,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => migrationRouteGroups,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => migrationRollbackPlan,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => jinjaInventoryDashboard,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => liveDataInventoryDashboard,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => migrationDashboard.transitional_label_gate,
        }),
    );
    window.history.pushState({}, "", "/admin/app/migration");

    render(<App />);

    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "Admin browser UI" }),
      ).toBeInTheDocument();
    });

    expect(screen.getByText("Route safety plan")).toBeInTheDocument();
  });

  it("renders the channel workspace route inside the shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => bootstrapFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => channelDashboard,
        }),
    );
    window.history.pushState({}, "", "/admin/app/channels");

    render(<App />);

    await waitFor(() => {
      expect(
        screen.getByRole("heading", {
          name: "Channel, Telegram, and Briefing Preferences",
        }),
      ).toBeInTheDocument();
    });
    expect(screen.getAllByText("Morning briefing")[0]).toBeInTheDocument();
  });

  it("renders the user-facing run route inside the shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => bootstrapFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            artifact_availability: "none",
            latest_timeline_cursor: "1",
            permitted_actions: ["cancel"],
            progress_summary: "Run accepted through channel facade.",
            result_availability: "unavailable",
            run_id: "00000000-0000-0000-0000-000000000046",
            state: "queued",
            subscribed: true,
            terminal_outcome: "none",
            trace_id: "trace-app-qa046",
            waiting_prompt: null,
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            items: [
              {
                event_id: "33333333-3333-3333-3333-333333333046",
                event_type: "run_queued",
                occurred_at: "2026-05-07T12:00:00Z",
                sequence: 1,
                severity: "info",
                state: "queued",
                summary: "Run accepted through channel facade.",
                trace_id: "trace-app-qa046",
              },
            ],
            next_cursor: null,
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            availability: "unavailable",
            run_id: "00000000-0000-0000-0000-000000000046",
            state: "queued",
            structured_result: null,
            summary: null,
            trace_id: "trace-app-qa046",
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            items: [],
            run_id: "00000000-0000-0000-0000-000000000046",
          }),
        }),
    );
    window.history.pushState(
      {},
      "",
      "/admin/app/channels/runs/00000000-0000-0000-0000-000000000046",
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Run workspace" })).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(
        screen.getAllByText("Run accepted through channel facade.").length,
      ).toBeGreaterThan(0);
    });
  });

  it("renders the usage analytics route inside the shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => bootstrapFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => usageDashboard,
        }),
    );
    window.history.pushState({}, "", "/admin/app/usage");

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Usage and Cost Analytics")).toBeInTheDocument();
    });
    expect(screen.getByText("Total tokens")).toBeInTheDocument();
  });

  it("renders the membership route inside the shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => bootstrapFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => membershipDashboardFixture,
        }),
    );
    window.history.pushState({}, "", "/admin/app/memberships");

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Membership Administration")).toBeInTheDocument();
    });
    expect(screen.getAllByText("Maya Chen").length).toBeGreaterThan(0);
  });

  it("renders the skill lifecycle route inside the shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => bootstrapFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => skillLifecycleDashboardFixture,
        }),
    );
    window.history.pushState({}, "", "/admin/app/skills");

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Skill lifecycle")).toBeInTheDocument();
    });
    expect(screen.getByText("Package publication")).toBeInTheDocument();
    expect(screen.getByText("Connector readiness")).toBeInTheDocument();
  });

  it("renders skill lifecycle subroutes inside the shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => bootstrapFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => skillLifecycleDashboardFixture,
        }),
    );
    window.history.pushState({}, "", "/admin/app/skills/diagnostics");

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Skill lifecycle")).toBeInTheDocument();
    });
    expect(screen.getByText("Connector readiness")).toBeInTheDocument();
  });

  it("renders the governance route inside the shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => bootstrapFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => governanceDashboardFixture,
        }),
    );
    window.history.pushState({}, "", "/admin/app/governance");

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Setup and health")).toBeInTheDocument();
    });
    expect(screen.getByText("Read-only policy preview")).toBeInTheDocument();
  });

  it("renders governance subroutes inside the shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => bootstrapFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => governanceDashboardFixture,
        }),
    );
    window.history.pushState({}, "", "/admin/app/governance/providers");

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Setup and health")).toBeInTheDocument();
    });
    expect(screen.getByText("Read-only policy preview")).toBeInTheDocument();
  });

  it("does not render the retired sample patterns route in the shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => bootstrapFixture,
      }),
    );
    window.history.pushState({}, "", "/admin/app/patterns");

    render(<App />);

    await waitFor(() => {
      expect(screen.getAllByText("Multi-Agent Admin").length).toBeGreaterThan(0);
    });
    expect(screen.queryByText("Forms and data patterns")).not.toBeInTheDocument();
    expect(screen.queryByText("Workflow readiness review")).not.toBeInTheDocument();
  });

  it("renders the operations workbench route inside the shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => bootstrapFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => workbenchEnvelopeFixture,
        }),
    );
    window.history.pushState({}, "", "/admin/app/operations");

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Operations workbench")).toBeInTheDocument();
    });
    expect(
      screen.getByText("Workflow run 11111111 from live audit evidence"),
    ).toBeInTheDocument();
  });

  it("renders the workflow builder route inside the shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => bootstrapFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => workflowBuilderEnvelope,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => workflowReferenceCatalog,
        }),
    );
    window.history.pushState({}, "", "/admin/app/workflows");

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Workflow builder")).toBeInTheDocument();
    });
    expect(screen.getByText("Workflow structure")).toBeInTheDocument();
    expect(screen.getByText("Evidence and decision")).toBeInTheDocument();
  });

  it("shows a safe unavailable state when bootstrap fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 403,
        json: async () => ({ detail: "insufficient_role" }),
      }),
    );

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Admin unavailable")).toBeInTheDocument();
    });
    expect(screen.getByText("insufficient_role")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open local login" })).toHaveAttribute(
      "href",
      "/auth/local-login?redirect_to=/admin/app",
    );
  });
});
