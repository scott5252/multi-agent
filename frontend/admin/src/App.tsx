import { useEffect, useState } from "react";

import { fetchBootstrap } from "./api/client";
import { ChannelTelegramBriefingPage } from "./components/channelTelegramBriefing/ChannelTelegramBriefingPage";
import { GovernancePage } from "./components/governance/GovernancePage";
import { ConsoleHomePage } from "./components/home/ConsoleHomePage";
import { MembershipPage } from "./components/memberships/MembershipPage";
import { MigrationHardeningPage } from "./components/migrationHardening/MigrationHardeningPage";
import { SavedFilterManagementPage } from "./components/savedFilters/SavedFilterManagementPage";
import { AdminShell } from "./components/shell/AdminShell";
import { SkillLifecyclePage } from "./components/skills/SkillLifecyclePage";
import { StatePanel } from "./components/StatePanel";
import { TestBenchPage } from "./components/testBench/TestBenchPage";
import { UsageExportDetailPage } from "./components/usage/UsageExportDetailPage";
import { UsagePage } from "./components/usage/UsagePage";
import { UserRunPage } from "./components/userRuns/UserRunPage";
import { WorkbenchPage } from "./components/workbench/WorkbenchPage";
import { WorkflowBuilderPage } from "./components/workflows/WorkflowBuilderPage";
import { currentDisabledRoute, disabledRouteFallbacks } from "./routes";
import type { ReactAdminBootstrap } from "./api/generated/reactAdminApi";

interface AppProps {
  bootstrapUrl?: string;
}

function workflowQueryString(): string {
  const params = new URLSearchParams(window.location.search);
  const draftMatch = window.location.pathname.match(
    /^\/admin\/app\/workflows\/drafts\/([^/]+)/,
  );
  if (draftMatch?.[1]) {
    params.set("workflow_draft_id", draftMatch[1]);
  }
  const query = params.toString();
  return query ? `?${query}` : "";
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
          setError(caught instanceof Error ? caught.message : "Admin unavailable");
        }
      });
    return () => {
      alive = false;
    };
  }, [bootstrapUrl]);

  if (error) {
    return (
      <StatePanel
        title="Admin unavailable"
        summary={error}
        actionHref="/auth/local-login?redirect_to=/admin/app"
        actionLabel="Open local login"
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
        title="Admin route unavailable"
        summary="This admin area still opens in the existing authorized console."
        actionHref={disabledRouteFallbacks[disabledRoute]}
        actionLabel="Open existing page"
      />
    );
  }

  if (window.location.pathname === "/admin/app") {
    return (
      <AdminShell bootstrap={bootstrap}>
        <ConsoleHomePage homeUrl={`/admin/app/home.json${window.location.search}`} />
      </AdminShell>
    );
  }

  if (window.location.pathname === "/admin/app/migration") {
    return (
      <AdminShell bootstrap={bootstrap}>
        <MigrationHardeningPage
          dashboardUrl={`/admin/app/migration/bootstrap.json${window.location.search}`}
        />
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

  if (window.location.pathname.startsWith("/admin/app/workflows")) {
    const workflowQuery = workflowQueryString();
    return (
      <AdminShell bootstrap={bootstrap}>
        <WorkflowBuilderPage
          builderUrl={`/admin/app/workflows/builder.json${workflowQuery}`}
          lookupsUrl={`/admin/app/workflows/lookups.json${workflowQuery}`}
        />
      </AdminShell>
    );
  }

  if (window.location.pathname.startsWith("/admin/app/governance")) {
    return (
      <AdminShell bootstrap={bootstrap}>
        <GovernancePage
          governanceUrl={`/admin/app/governance/bootstrap.json${window.location.search}`}
        />
      </AdminShell>
    );
  }

  if (window.location.pathname.startsWith("/admin/app/skills")) {
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

  if (window.location.pathname.startsWith("/admin/app/saved-filters/")) {
    const adminArea = window.location.pathname.split("/").at(-1) ?? "workflows";
    return (
      <AdminShell bootstrap={bootstrap}>
        <SavedFilterManagementPage
          savedFiltersUrl={`/admin/filters/${adminArea}.json${window.location.search}`}
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

  if (window.location.pathname.startsWith("/admin/app/channels/runs")) {
    const pathParts = window.location.pathname.split("/");
    const runId =
      window.location.pathname === "/admin/app/channels/runs"
        ? null
        : (pathParts.at(-1) ?? null);
    return (
      <AdminShell bootstrap={bootstrap}>
        <UserRunPage runId={runId} search={window.location.search} />
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
