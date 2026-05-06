import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { jinjaInventoryDashboard } from "../../test/migrationHardeningTestData";
import { JinjaInventoryPanel } from "./JinjaInventoryPanel";

describe("JinjaInventoryPanel", () => {
  it("renders grouped deletion readiness without unsafe evidence", () => {
    render(<JinjaInventoryPanel inventory={jinjaInventoryDashboard} />);

    expect(screen.getByRole("heading", { name: "Deletion readiness" })).toBeInTheDocument();
    expect(screen.getByText("Spec 039: Shell Auth")).toBeInTheDocument();
    expect(screen.getByText("app.html")).toBeInTheDocument();
    expect(screen.getAllByText("Blocked").length).toBeGreaterThan(0);
    expect(screen.getByText("Compatibility needed")).toBeInTheDocument();
    expect(screen.getAllByText("scanner-qa038").length).toBeGreaterThan(0);
    expect(
      screen.queryByText(/qa038-secret-value|raw prompt|\/Users\//i),
    ).not.toBeInTheDocument();
  });

  it("renders a scoped empty state", () => {
    render(
      <JinjaInventoryPanel
        inventory={{
          evidence: [],
          groups: [],
          summary: {
            blocked_count: 0,
            direct_link_count: 0,
            generated_at: "2026-05-06T12:00:00Z",
            reviewer_signoff_required: true,
            route_count: 0,
            safe_to_delete_count: 0,
            static_asset_count: 0,
            template_count: 0,
            total_items: 0,
          },
        }}
      />,
    );

    expect(screen.getByText("No inventory rows are visible for this scope.")).toBeInTheDocument();
  });
});
