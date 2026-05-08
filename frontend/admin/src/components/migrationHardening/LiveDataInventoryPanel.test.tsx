import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { liveDataInventoryDashboard } from "../../test/migrationHardeningTestData";
import { LiveDataInventoryPanel } from "./LiveDataInventoryPanel";

describe("LiveDataInventoryPanel", () => {
  it("renders live-only gate findings without unsafe evidence", () => {
    render(<LiveDataInventoryPanel inventory={liveDataInventoryDashboard} />);

    expect(screen.getByRole("heading", { name: "Live-data guardrails" })).toBeInTheDocument();
    expect(screen.getByText("Live-only gate")).toBeInTheDocument();
    expect(screen.getByText("src/multi_agent_platform/api/routers/admin_react.py")).toBeInTheDocument();
    expect(screen.getByText("027")).toBeInTheDocument();
    expect(screen.getAllByText("Computed").length).toBeGreaterThan(0);
    expect(screen.getByText("qa058-live-only-source-scan")).toBeInTheDocument();
    expect(screen.getByText("Route targets")).toBeInTheDocument();
    expect(screen.getByText("Empty scans")).toBeInTheDocument();
    expect(screen.queryByText(/raw prompt|\/Users\//i)).not.toBeInTheDocument();
  });

  it("renders unavailable inventory as a scoped empty state", () => {
    render(<LiveDataInventoryPanel inventory={null} />);

    expect(screen.getByText("Unavailable")).toBeInTheDocument();
    expect(
      screen.getByText("Live-data inventory evidence is unavailable for this scope."),
    ).toBeInTheDocument();
  });
});
