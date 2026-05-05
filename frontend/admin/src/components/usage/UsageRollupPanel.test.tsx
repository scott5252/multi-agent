import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { usageDashboard } from "../../test/usageTestData";
import { UsageRollupPanel } from "./UsageRollupPanel";

describe("UsageRollupPanel", () => {
  it("renders bounded safe rows and opens drilldowns", async () => {
    const onDrilldown = vi.fn();

    render(<UsageRollupPanel onDrilldown={onDrilldown} rollup={usageDashboard.rollup} />);

    expect(screen.getByText("OpenAI")).toBeInTheDocument();
    expect(screen.getByText("Grouped by provider.")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "View" }));
    expect(onDrilldown).toHaveBeenCalledWith(
      "/admin/app/usage/events.json?group_by=provider&rollup_key=OpenAI",
    );
  });
});
