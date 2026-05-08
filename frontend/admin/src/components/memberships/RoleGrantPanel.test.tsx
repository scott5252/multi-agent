import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { membershipDashboardFixture } from "../../test/membershipTestData";
import { RoleGrantPanel } from "./RoleGrantPanel";

describe("RoleGrantPanel", () => {
  it("submits backend-owned role choices and revoke actions", async () => {
    const grant = vi.fn();
    const revoke = vi.fn();

    render(
      <RoleGrantPanel
        directory={membershipDashboardFixture.directory}
        form={membershipDashboardFixture.role_grant_form}
        grants={membershipDashboardFixture.directory[0].role_summaries}
        mutationResult={null}
        onGrant={grant}
        onRevoke={revoke}
      />,
    );

    await userEvent.click(screen.getByRole("button", { name: /Grant/ }));
    expect(grant).toHaveBeenCalledWith(
      "/admin/app/memberships/role-grants",
      expect.objectContaining({
        role_code: "tenant_admin",
        scope_type: "tenant",
      }),
    );

    await userEvent.click(screen.getByRole("button", { name: /Revoke/ }));
    expect(revoke).toHaveBeenCalledWith(
      "/admin/app/memberships/role-grants/grant-qa034-acme-maya/revoke",
      null,
    );
  });
});
