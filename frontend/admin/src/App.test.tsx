import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";
import { channelDashboard } from "./test/channelTelegramBriefingTestData";
import { governanceDashboardFixture } from "./test/governanceTestData";
import { membershipDashboardFixture } from "./test/membershipTestData";
import {
  migrationDashboard,
  migrationRollbackPlan,
  migrationRouteGroups,
} from "./test/migrationHardeningTestData";
import { patternsEnvelopeFixture } from "./test/patternsTestData";
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

  it("renders safe principal scope and Jinja fallback links", async () => {
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
        }),
    );

    render(<App />);

    expect(screen.getByText("Loading admin shell")).toBeInTheDocument();
    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "React Admin Migration Hardening" }),
      ).toBeInTheDocument();
    });

    expect(screen.getAllByText("Multi-Agent Admin").length).toBeGreaterThan(0);
    expect(screen.getByLabelText("Admin scope")).toHaveTextContent("Acme");
    expect(
      screen.getByRole("link", { name: "Workflow Registry react" }),
    ).toHaveAttribute(
      "href",
      "/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111",
    );
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

  it("renders the sample data and form patterns route inside the shell", async () => {
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
          json: async () => patternsEnvelopeFixture,
        }),
    );
    window.history.pushState({}, "", "/admin/app/patterns");

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("Forms and data patterns")).toBeInTheDocument();
    });
    expect(screen.getByText("Workflow readiness review")).toBeInTheDocument();
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
    expect(screen.getByText("Daily briefing graph run")).toBeInTheDocument();
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
    expect(screen.getByText("Runtime structure")).toBeInTheDocument();
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
      expect(screen.getByText("React admin unavailable")).toBeInTheDocument();
    });
    expect(screen.getByText("insufficient_role")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open existing admin console" }))
      .toHaveAttribute("href", "/admin");
  });
});
