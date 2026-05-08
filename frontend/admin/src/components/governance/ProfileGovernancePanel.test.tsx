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

    expect(screen.getByText("Governance runtime profile")).toBeInTheDocument();
    expect(
      screen.getAllByText(governanceDashboardFixture.providers[0].provider_id),
    ).toHaveLength(2);

    await userEvent.click(screen.getByRole("button", { name: /Resolve/ }));
    await userEvent.click(screen.getByRole("button", { name: /Save profile/ }));

    expect(onResolve).toHaveBeenCalledWith(
      governanceDashboardFixture.profiles[0].authorized_actions[1].href,
    );
    expect(onSave).toHaveBeenCalledWith(
      governanceDashboardFixture.profiles[0].authorized_actions[0].href,
      governanceDashboardFixture.profiles[0],
    );
  });
});
