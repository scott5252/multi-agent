import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  skillLifecycleDashboardFixture,
  skillLifecycleMutationFixture,
} from "../../test/skillLifecycleTestData";
import { SkillLifecyclePage } from "./SkillLifecyclePage";

describe("SkillLifecyclePage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads safe lifecycle data and submits an explicit candidate action", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => skillLifecycleDashboardFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            ...skillLifecycleMutationFixture,
            audit_reference_id: "audit-skill-candidate-live",
            summary: "Package candidate saved with safe manifest summary.",
          }),
        }),
    );

    render(<SkillLifecyclePage skillsUrl="/admin/app/skills/bootstrap.json" />);

    await screen.findByRole("heading", { name: "Skill lifecycle" });
    expect(screen.getByText("Package publication")).toBeInTheDocument();
    expect(screen.getByText("Credential reference fingerprint changed.")).toBeInTheDocument();
    expect(screen.getByText("Eligibility and diagnostics")).toBeInTheDocument();
    expect(screen.queryByText("Legacy route redirects")).not.toBeInTheDocument();
    expect(screen.queryByText("/admin/skill-registry/ui/packages")).not.toBeInTheDocument();
    expect(screen.queryByText("/admin/app/skills/diagnostics")).not.toBeInTheDocument();
    expect(screen.queryByText(/live-secret-value/)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Save candidate/ }));

    await waitFor(() => {
      expect(screen.getByText("audit-skill-candidate-live")).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith(
      "/admin/app/skills/packages/candidates",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
