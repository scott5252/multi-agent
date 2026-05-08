import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { membershipDashboardFixture } from "../../test/membershipTestData";
import { SupportOverridePanel } from "./SupportOverridePanel";

describe("SupportOverridePanel", () => {
  it("renders persisted support override evidence", () => {
    render(
      <SupportOverridePanel
        overrides={membershipDashboardFixture.support_overrides}
      />,
    );

    expect(screen.getByText("Temporary access evidence")).toBeInTheDocument();
    expect(
      screen.getByText("Support override evidence is persisted and scoped."),
    ).toBeInTheDocument();
    expect(screen.queryByText(/raw|token|secret/i)).not.toBeInTheDocument();
  });
});
