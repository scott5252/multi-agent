import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { migrationDashboard } from "../../test/migrationHardeningTestData";
import { AccessibilityAuditPanel } from "./AccessibilityAuditPanel";
import { MigrationSweepPanel } from "./MigrationSweepPanel";
import { PerformanceBudgetPanel } from "./PerformanceBudgetPanel";

describe("migration evidence panels", () => {
  it("renders performance measurements and mitigation", () => {
    render(<PerformanceBudgetPanel budget={migrationDashboard.performance_budget} />);

    expect(screen.getByRole("heading", { name: "Budget evidence" })).toBeInTheDocument();
    expect(screen.getByText("React admin home bootstrap")).toBeInTheDocument();
    expect(screen.getByText("214 ms / 500 ms")).toBeInTheDocument();
    expect(screen.getByText("perf-qa037-home-bootstrap")).toBeInTheDocument();
  });

  it("renders accessibility status rows and viewport evidence", () => {
    render(<AccessibilityAuditPanel audit={migrationDashboard.accessibility_audit} />);

    expect(screen.getByRole("heading", { name: "Audit coverage" })).toBeInTheDocument();
    expect(screen.getByText("Keyboard")).toBeInTheDocument();
    expect(screen.getByText("desktop 1440x900")).toBeInTheDocument();
    expect(screen.getByText("qa037-keyboard-checklist")).toBeInTheDocument();
  });

  it("renders redaction and tenant isolation sweep summaries", () => {
    render(
      <MigrationSweepPanel
        redaction={migrationDashboard.redaction_sweep}
        tenantIsolation={migrationDashboard.tenant_isolation_sweep}
      />,
    );

    expect(screen.getByRole("heading", { name: "Redaction and tenant isolation" })).toBeInTheDocument();
    expect(screen.getByText("Redaction sweep")).toBeInTheDocument();
    expect(screen.getByText("Tenant isolation sweep")).toBeInTheDocument();
    expect(screen.getByText("redaction-scan-qa037")).toBeInTheDocument();
    expect(screen.getByText("tenant-isolation-qa037")).toBeInTheDocument();
    expect(screen.queryByText(/raw completion|memory content/i)).not.toBeInTheDocument();
  });
});
