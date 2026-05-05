import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { membershipDashboardFixture } from "../../test/membershipTestData";
import { MembershipAuditPanel } from "./MembershipAuditPanel";

describe("MembershipAuditPanel", () => {
  it("renders safe membership audit evidence", () => {
    render(<MembershipAuditPanel records={membershipDashboardFixture.audit_timeline} />);

    expect(screen.getByText("invitation_replayed")).toBeInTheDocument();
    expect(
      screen.getByText("Original invitation returned without duplicate row."),
    ).toBeInTheDocument();
  });
});
