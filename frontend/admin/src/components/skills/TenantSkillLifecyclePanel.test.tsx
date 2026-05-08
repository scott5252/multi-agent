import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { skillLifecycleDashboardFixture } from "../../test/skillLifecycleTestData";
import { TenantSkillLifecyclePanel } from "./TenantSkillLifecyclePanel";

describe("TenantSkillLifecyclePanel", () => {
  it("shows granted tenant installation state and install action", async () => {
    const onInstall = vi.fn();
    const [installation] = skillLifecycleDashboardFixture.installations;

    render(
      <TenantSkillLifecyclePanel
        discovery={skillLifecycleDashboardFixture.tenant_discovery}
        installResult={null}
        installations={skillLifecycleDashboardFixture.installations}
        onInstall={onInstall}
      />,
    );

    expect(screen.getByText("Granted tenant skills")).toBeInTheDocument();
    expect(screen.getByText("calendar-assistant")).toBeInTheDocument();
    expect(screen.getByText("1.5.0 available after smoke evidence refresh")).toBeInTheDocument();
    expect(screen.queryByText("Globex")).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Install/ }));

    expect(onInstall).toHaveBeenCalledWith(
      "/admin/app/skills/installations/install-live-calendar/install",
      installation,
    );
  });
});
