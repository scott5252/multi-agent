import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { membershipDashboardFixture } from "../../test/membershipTestData";
import { AccessHistoryPanel } from "./AccessHistoryPanel";

describe("AccessHistoryPanel", () => {
  it("renders bounded safe access history", () => {
    render(<AccessHistoryPanel records={membershipDashboardFixture.access_history} />);

    expect(screen.getByText("Open membership workspace")).toBeInTheDocument();
    expect(screen.getByText(/trace-membership-qa034-allow/)).toBeInTheDocument();
  });
});
