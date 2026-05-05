import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { usageDashboard } from "../../test/usageTestData";
import { UsageTrendPanel } from "./UsageTrendPanel";

describe("UsageTrendPanel", () => {
  it("renders accessible trend bars and fallback table", () => {
    render(<UsageTrendPanel trend={usageDashboard.trend} />);

    expect(screen.getByRole("img", { name: "Daily token trend" })).toBeInTheDocument();
    expect(screen.getAllByText("May 5").length).toBeGreaterThan(0);
    expect(screen.getByText("$0.0437")).toBeInTheDocument();
  });
});
