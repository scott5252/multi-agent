import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { skillLifecycleDashboardFixture } from "../../test/skillLifecycleTestData";
import { CredentialReadinessPanel } from "./CredentialReadinessPanel";

describe("CredentialReadinessPanel", () => {
  it("renders credential fingerprints and saves authorized references only", async () => {
    const onConfigure = vi.fn();
    const [installation] = skillLifecycleDashboardFixture.installations;

    render(
      <CredentialReadinessPanel
        credentialResult={null}
        installations={skillLifecycleDashboardFixture.installations}
        onConfigure={onConfigure}
      />,
    );

    expect(screen.getByText("Reference readiness")).toBeInTheDocument();
    expect(screen.getByText("Acme briefing connector reference")).toBeInTheDocument();
    expect(screen.getByText("fp_live_calendar")).toBeInTheDocument();
    expect(screen.queryByText(/resolved credential/i)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Save reference/ }));

    expect(onConfigure).toHaveBeenCalledWith(
      "/admin/app/skills/installations/install-live-calendar/credentials",
      installation,
      "cred-ref-acme-briefing",
    );
  });
});
