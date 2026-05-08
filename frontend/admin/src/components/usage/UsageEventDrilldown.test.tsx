import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { usageDrilldown } from "../../test/usageTestData";
import { UsageEventDrilldown } from "./UsageEventDrilldown";

describe("UsageEventDrilldown", () => {
  it("renders bounded safe event evidence", () => {
    render(<UsageEventDrilldown drilldown={usageDrilldown} />);

    expect(screen.getByText("Safe events")).toBeInTheDocument();
    expect(screen.getByText("Daily briefing workflow")).toBeInTheDocument();
    expect(screen.getByText("audit-usage-qa056-0001")).toBeInTheDocument();
    expect(screen.queryByText(/raw completion|authorization header/i)).not.toBeInTheDocument();
  });
});
