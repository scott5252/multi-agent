import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import {
  migrationDashboard,
  migrationRollbackPlan,
} from "../../test/migrationHardeningTestData";
import { MigrationParityMatrix } from "./MigrationParityMatrix";
import { RollbackPlanPanel } from "./RollbackPlanPanel";
import { RouteDecisionBadge } from "./RouteDecisionBadges";

describe("rollback and route decisions", () => {
  it("renders rollback steps, verification, owner, and audit evidence", () => {
    render(<RollbackPlanPanel plan={migrationRollbackPlan} />);

    expect(screen.getByRole("heading", { name: "Route safety plan" })).toBeInTheDocument();
    expect(screen.getByText("Release rollback")).toBeInTheDocument();
    expect(screen.getByText("Platform operations")).toBeInTheDocument();
    expect(screen.getByText("Redeploy the previous reviewed release if rollback is required.")).toBeInTheDocument();
    expect(screen.getByText("audit-qa047-rollback-plan")).toBeInTheDocument();
  });

  it("labels every migration decision without exposing unsafe evidence", () => {
    render(
      <>
        <RouteDecisionBadge decision="redirect" />
        <RouteDecisionBadge decision="alias" />
        <RouteDecisionBadge decision="retained_fallback" />
        <RouteDecisionBadge decision="retirement_candidate" />
        <RouteDecisionBadge decision="blocked" />
        <MigrationParityMatrix groups={migrationDashboard.route_groups} />
      </>,
    );

    expect(screen.getAllByText("Redirect").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Alias").length).toBeGreaterThan(0);
    expect(screen.getByText("Retained fallback")).toBeInTheDocument();
    expect(screen.getByText("Retirement candidate")).toBeInTheDocument();
    expect(screen.getByText("Blocked")).toBeInTheDocument();
    expect(screen.getAllByText("Retirement evidence complete").length).toBeGreaterThan(0);
    expect(screen.queryByText(/qa037-secret-value|authorization header/i)).not.toBeInTheDocument();
  });
});
