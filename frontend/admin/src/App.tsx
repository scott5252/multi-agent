import { useEffect, useState } from "react";

import { fetchBootstrap } from "./api/client";
import { PatternsPage } from "./components/patterns/PatternsPage";
import { ChannelTelegramBriefingPage } from "./components/channelTelegramBriefing/ChannelTelegramBriefingPage";
import { RunStatusSummaryPage } from "./components/channelTelegramBriefing/RunStatusSummaryPage";
import { GovernancePage } from "./components/governance/GovernancePage";
import { MembershipPage } from "./components/memberships/MembershipPage";
import { MigrationHardeningPage } from "./components/migrationHardening/MigrationHardeningPage";
import { AdminShell } from "./components/shell/AdminShell";
import { SkillLifecyclePage } from "./components/skills/SkillLifecyclePage";
import { StatePanel } from "./components/StatePanel";
import { TestBenchPage } from "./components/testBench/TestBenchPage";
import { UsageExportDetailPage } from "./components/usage/UsageExportDetailPage";
import { UsagePage } from "./components/usage/UsagePage";
import { WorkbenchPage } from "./components/workbench/WorkbenchPage";
import { WorkflowBuilderPage } from "./components/workflows/WorkflowBuilderPage";
import { currentDisabledRoute, disabledRouteFallbacks } from "./routes";
import type { ReactAdminBootstrap } from "./api/generated/reactAdminApi";

interface AppProps {
  bootstrapUrl?: string;
}

export function App({ bootstrapUrl = "/admin/app/bootstrap.json" }: AppProps) {
  const [bootstrap, setBootstrap] = useState<ReactAdminBootstrap | null>(null);
  const [error, setError] = useState<string | null>(null);
  const disabledRoute = currentDisabledRoute(window.location.pathname);

  useEffect(() => {
    let alive = true;
    fetchBootstrap(bootstrapUrl)
      .then((payload) => {
        if (alive) {
          setBootstrap(payload);
          setError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setError(caught instanceof Error ? caught.message : "React admin unavailable");
        }
      });
    return () => {
      alive = false;
    };
  }, [bootstrapUrl]);

  if (error) {
    return (
      <StatePanel
        title="React admin unavailable"
        summary={error}
        actionHref="/admin"
        actionLabel="Open existing admin console"
      />
    );
  }

  if (!bootstrap) {
    return (
      <StatePanel
        title="Loading admin shell"
        summary="Checking your signed-in principal and active scope."
      />
    );
  }

  if (disabledRoute) {
    return (
      <StatePanel
        title="React route not migrated"
        summary="This admin area still opens in the existing authorized console."
        actionHref={disabledRouteFallbacks[disabledRoute]}
        actionLabel="Open existing page"
      />
    );
  }

  if (
    window.location.pathname === "/admin/app" ||
    window.location.pathname === "/admin/app/migration"
  ) {
    return (
      <AdminShell bootstrap={bootstrap}>
        <MigrationHardeningPage
          dashboardUrl={`/admin/app/migration/bootstrap.json${window.location.search}`}
        />
      </AdminShell>
    );
  }

  if (window.location.pathname === "/admin/app/patterns") {
    return (
      <AdminShell bootstrap={bootstrap}>
        <PatternsPage patternsUrl={`/admin/app/patterns.json${window.location.search}`} />
      </AdminShell>
    );
  }

  if (window.location.pathname === "/admin/app/operations") {
    return (
      <AdminShell bootstrap={bootstrap}>
        <WorkbenchPage workbenchUrl={`/admin/app/operations.json${window.location.search}`} />
      </AdminShell>
    );
  }

  if (window.location.pathname === "/admin/app/workflows") {
    return (
      <AdminShell bootstrap={bootstrap}>
        <WorkflowBuilderPage
          builderUrl={`/admin/app/workflows/builder.json${window.location.search}`}
          lookupsUrl={`/admin/app/workflows/lookups.json${window.location.search}`}
        />
      </AdminShell>
    );
  }

  if (window.location.pathname === "/admin/app/governance") {
    return (
      <AdminShell bootstrap={bootstrap}>
        <GovernancePage
          governanceUrl={`/admin/app/governance/bootstrap.json${window.location.search}`}
        />
      </AdminShell>
    );
  }

  if (window.location.pathname === "/admin/app/skills") {
    return (
      <AdminShell bootstrap={bootstrap}>
        <SkillLifecyclePage
          skillsUrl={`/admin/app/skills/bootstrap.json${window.location.search}`}
        />
      </AdminShell>
    );
  }

  if (window.location.pathname === "/admin/app/test-bench") {
    return (
      <AdminShell bootstrap={bootstrap}>
        <TestBenchPage
          testBenchUrl={`/admin/app/test-bench/bootstrap.json${window.location.search}`}
        />
      </AdminShell>
    );
  }

  if (window.location.pathname === "/admin/app/memberships") {
    return (
      <AdminShell bootstrap={bootstrap}>
        <MembershipPage
          membershipsUrl={`/admin/app/memberships/bootstrap.json${window.location.search}`}
        />
      </AdminShell>
    );
  }

  if (window.location.pathname.startsWith("/admin/app/usage/exports/")) {
    const exportId = window.location.pathname.split("/").at(-1) ?? "";
    return (
      <AdminShell bootstrap={bootstrap}>
        <UsageExportDetailPage
          exportUrl={`/admin/app/usage/exports/${exportId}.json${window.location.search}`}
        />
      </AdminShell>
    );
  }

  if (window.location.pathname === "/admin/app/usage") {
    return (
      <AdminShell bootstrap={bootstrap}>
        <UsagePage usageUrl={`/admin/app/usage/bootstrap.json${window.location.search}`} />
      </AdminShell>
    );
  }

  if (window.location.pathname.startsWith("/admin/app/channels/runs/")) {
    const runId = window.location.pathname.split("/").at(-1) ?? "";
    return (
      <AdminShell bootstrap={bootstrap}>
        <RunStatusSummaryPage
          runStatusUrl={`/admin/app/channels/runs/${runId}/status.json${window.location.search}`}
        />
      </AdminShell>
    );
  }

  if (window.location.pathname === "/admin/app/channels") {
    return (
      <AdminShell bootstrap={bootstrap}>
        <ChannelTelegramBriefingPage
          channelsUrl={`/admin/app/channels/bootstrap.json${window.location.search}`}
        />
      </AdminShell>
    );
  }

  return <AdminShell bootstrap={bootstrap} />;
}
