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
    expect(screen.getByText("React admin primary routing flag")).toBeInTheDocument();
    expect(screen.getByText("Platform operations")).toBeInTheDocument();
    expect(screen.getByText("Set React admin primary routing flag to fallback mode.")).toBeInTheDocument();
    expect(screen.getByText("audit-qa037-rollback-plan")).toBeInTheDocument();
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

    expect(screen.getByText("Redirect")).toBeInTheDocument();
    expect(screen.getAllByText("Alias").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Retained fallback").length).toBeGreaterThan(0);
    expect(screen.getByText("Retirement candidate")).toBeInTheDocument();
    expect(screen.getByText("Blocked")).toBeInTheDocument();
    expect(screen.getAllByText("Retirement evidence complete").length).toBeGreaterThan(0);
    expect(screen.queryByText(/qa037-secret-value|authorization header/i)).not.toBeInTheDocument();
  });
});
