import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  membershipDashboardFixture,
  membershipMutationFixture,
} from "../../test/membershipTestData";
import { MembershipPage } from "./MembershipPage";

describe("MembershipPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads safe membership data and replays an invite", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => membershipDashboardFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => membershipMutationFixture,
        }),
    );

    render(<MembershipPage membershipsUrl="/admin/app/memberships/bootstrap.json" />);

    await screen.findByRole("heading", { name: "Membership Administration" });
    expect(screen.getAllByText("Maya Chen").length).toBeGreaterThan(0);
    expect(screen.getByText("m***@example.test")).toBeInTheDocument();
    expect(screen.queryByText(/qa034-secret-value/)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Invite/ }));

    await waitFor(() => {
      expect(
        screen.getByText("Invitation replayed with original audit evidence."),
      ).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith(
      "/admin/app/memberships/invitations",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
