import { useEffect, useState } from "react";

import {
  fetchMigrationHardeningDashboard,
  fetchJinjaInventoryDashboard,
  fetchMigrationRollbackPlan,
  fetchMigrationRouteGroups,
} from "../../api/client";
import type {
  AdminMigrationHardeningDashboard,
  JinjaInventoryDashboard,
  MigrationRollbackPlan,
  MigrationRouteGroup,
} from "../../api/generated/reactAdminApi";
import { CommonState } from "../states/CommonState";
import { AccessibilityAuditPanel } from "./AccessibilityAuditPanel";
import { JinjaInventoryPanel } from "./JinjaInventoryPanel";
import { MigrationParityMatrix } from "./MigrationParityMatrix";
import { MigrationStatePanel } from "./MigrationStatePanel";
import { MigrationSummaryHeader } from "./MigrationSummaryHeader";
import { MigrationSweepPanel } from "./MigrationSweepPanel";
import { PerformanceBudgetPanel } from "./PerformanceBudgetPanel";
import { RollbackPlanPanel } from "./RollbackPlanPanel";

export function MigrationHardeningPage({
  dashboardUrl,
  inventoryUrl = withSearch("/admin/app/migration/jinja-inventory.json"),
  rollbackUrl = withSearch("/admin/app/migration/rollback.json"),
  routesUrl = withSearch("/admin/app/migration/routes.json"),
}: {
  dashboardUrl: string;
  inventoryUrl?: string;
  rollbackUrl?: string;
  routesUrl?: string;
}) {
  const [dashboard, setDashboard] =
    useState<AdminMigrationHardeningDashboard | null>(null);
  const [inventory, setInventory] = useState<JinjaInventoryDashboard | null>(null);
  const [routeGroups, setRouteGroups] = useState<MigrationRouteGroup[] | null>(null);
  const [rollbackPlan, setRollbackPlan] = useState<MigrationRollbackPlan | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    loadDashboard({
      dashboardUrl,
      inventoryUrl,
      rollbackUrl,
      routesUrl,
    })
      .then((payload) => {
        if (alive) {
          setDashboard(payload.dashboard);
          setInventory(payload.inventory);
          setRouteGroups(payload.routeGroups);
          setRollbackPlan(payload.rollbackPlan);
          setLoadError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setLoadError(
            caught instanceof Error ? caught.message : "Migration hardening unavailable",
          );
        }
      });
    return () => {
      alive = false;
    };
  }, [dashboardUrl, inventoryUrl, rollbackUrl, routesUrl]);

  async function refresh() {
    const payload = await loadDashboard({
      dashboardUrl,
      inventoryUrl,
      rollbackUrl,
      routesUrl,
    });
    setDashboard(payload.dashboard);
    setInventory(payload.inventory);
    setRouteGroups(payload.routeGroups);
    setRollbackPlan(payload.rollbackPlan);
    setLoadError(null);
  }

  if (loadError && !dashboard) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: loadError,
          title: "Migration hardening unavailable",
          trace_id: null,
        }}
      />
    );
  }

  if (!dashboard) {
    return (
      <CommonState
        state={{
          action: null,
          state: "loading",
          summary: "Loading route parity, rollback, budget, and evidence summaries.",
          title: "Loading migration hardening",
          trace_id: null,
        }}
      />
    );
  }

  const visibleGroups = routeGroups ?? dashboard.route_groups;
  const visibleInventory = inventory ?? dashboard.jinja_inventory;
  const visibleRollback = rollbackPlan ?? dashboard.rollback_plan;

  return (
    <div className="migration-page">
      <MigrationSummaryHeader dashboard={dashboard} onRefresh={() => void refresh()} />
      {loadError ? <p className="safe-error">{loadError}</p> : null}
      <MigrationStatePanel states={dashboard.states} />
      <MigrationParityMatrix groups={visibleGroups} />
      <JinjaInventoryPanel inventory={visibleInventory} />
      <div className="migration-evidence-grid">
        <RollbackPlanPanel plan={visibleRollback} />
        <PerformanceBudgetPanel budget={dashboard.performance_budget} />
        <AccessibilityAuditPanel audit={dashboard.accessibility_audit} />
        <MigrationSweepPanel
          redaction={dashboard.redaction_sweep}
          tenantIsolation={dashboard.tenant_isolation_sweep}
        />
      </div>
    </div>
  );
}

async function loadDashboard({
  dashboardUrl,
  inventoryUrl,
  rollbackUrl,
  routesUrl,
}: {
  dashboardUrl: string;
  inventoryUrl: string;
  rollbackUrl: string;
  routesUrl: string;
}) {
  const [dashboard, routeGroups, rollbackPlan, inventory] = await Promise.all([
    fetchMigrationHardeningDashboard(dashboardUrl),
    fetchMigrationRouteGroups(routesUrl),
    fetchMigrationRollbackPlan(rollbackUrl),
    fetchJinjaInventoryDashboard(inventoryUrl).catch(() => null),
  ]);
  return { dashboard, inventory, rollbackPlan, routeGroups };
}

function withSearch(url: string): string {
  if (!window.location.search || url.includes("?")) {
    return url;
  }
  return `${url}${window.location.search}`;
}
