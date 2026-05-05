import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import {
  governanceDashboardFixture,
  governanceMutationFixture,
} from "../../test/governanceTestData";
import { ProfileGovernancePanel } from "./ProfileGovernancePanel";

describe("ProfileGovernancePanel", () => {
  it("renders profile bindings and read-only resolver actions", async () => {
    const onResolve = vi.fn();
    const onSave = vi.fn();

    render(
      <ProfileGovernancePanel
        mutationResult={governanceMutationFixture}
        onResolve={onResolve}
        onSave={onSave}
        profiles={governanceDashboardFixture.profiles}
        resolution={governanceDashboardFixture.profile_resolution}
      />,
    );

    expect(screen.getByText("Briefing runtime profile")).toBeInTheDocument();
    expect(screen.getByText("openai-primary through ModelGateway")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Resolve/ }));
    await userEvent.click(screen.getByRole("button", { name: /Save profile/ }));

    expect(onResolve).toHaveBeenCalledWith(
      "/admin/app/governance/profiles/briefing-runtime/resolve",
    );
    expect(onSave).toHaveBeenCalledWith(
      "/admin/app/governance/profiles/briefing-runtime/save",
      governanceDashboardFixture.profiles[0],
    );
  });
});
