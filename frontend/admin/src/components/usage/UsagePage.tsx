import { useEffect, useState } from "react";

import {
  createUsageExport,
  fetchUsageDashboard,
  fetchUsageEvents,
} from "../../api/client";
import type {
  UsageReactDashboard,
  UsageReactEventDrilldown,
  UsageReactExportSummary,
  UsageReactGroupBy,
} from "../../api/generated/reactAdminApi";
import { buildIdempotencyKey } from "../../utils/adminActionMetadata";
import { CommonState } from "../states/CommonState";
import { UsageEventDrilldown } from "./UsageEventDrilldown";
import { UsageExportPanel } from "./UsageExportPanel";
import { UsageFilterBar } from "./UsageFilterBar";
import { UsageHeader } from "./UsageHeader";
import { UsageRollupPanel } from "./UsageRollupPanel";
import { UsageStatePanel } from "./UsageStatePanel";
import { UsageSummaryCards } from "./UsageSummaryCards";
import { UsageTrendPanel } from "./UsageTrendPanel";

export function UsagePage({ usageUrl }: { usageUrl: string }) {
  const [dashboard, setDashboard] = useState<UsageReactDashboard | null>(null);
  const [drilldown, setDrilldown] = useState<UsageReactEventDrilldown | null>(null);
  const [exportResult, setExportResult] = useState<UsageReactExportSummary | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    fetchUsageDashboard(usageUrl)
      .then((payload) => {
        if (alive) {
          setDashboard(payload);
          setDrilldown(payload.drilldown);
          setExportResult(payload.exports[0] ?? null);
          setLoadError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setLoadError(caught instanceof Error ? caught.message : "Usage unavailable");
        }
      });
    return () => {
      alive = false;
    };
  }, [usageUrl]);

  async function refresh(nextUrl = usageUrl) {
    const payload = await fetchUsageDashboard(nextUrl);
    setDashboard(payload);
    setDrilldown(payload.drilldown);
    setLoadError(null);
  }

  async function changeGroup(groupBy: UsageReactGroupBy) {
    const nextUrl = setQueryParam(usageUrl, "group_by", groupBy);
    await refresh(nextUrl);
  }

  async function loadDrilldown(href: string) {
    const url = new URL(href, window.location.origin);
    const source = new URL(usageUrl, window.location.origin);
    for (const [key, value] of source.searchParams) {
      if (!url.searchParams.has(key)) {
        url.searchParams.set(key, value);
      }
    }
    setDrilldown(await fetchUsageEvents(url.toString()));
  }

  async function requestExport() {
    if (!dashboard) {
      return;
    }
    const filterSnapshot: Record<string, string> = {
      end: dashboard.filters.selected_range.end,
      group_by: dashboard.filters.selected_group_by,
      range: dashboard.filters.selected_range.label,
      start: dashboard.filters.selected_range.start,
    };
    const tenant = dashboard.filters.tenant_options.find((option) => option.selected);
    if (tenant) {
      filterSnapshot.tenant_id = tenant.value;
    }
    setExportResult(
      await createUsageExport(withSearch("/admin/app/usage/exports"), {
        filters: filterSnapshot,
        idempotency_key: buildIdempotencyKey("usage-export"),
        requested_group_by: dashboard.filters.selected_group_by,
      }),
    );
  }

  if (loadError && !dashboard) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: loadError,
          title: "Usage analytics unavailable",
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
          summary: "Loading usage summaries, rollups, drilldowns, and exports.",
          title: "Loading usage analytics",
          trace_id: null,
        }}
      />
    );
  }

  return (
    <div className="usage-page">
      <UsageHeader
        dashboard={dashboard}
        onExport={() => void requestExport()}
        onRefresh={() => void refresh()}
      />
      {loadError ? <p className="safe-error">{loadError}</p> : null}
      <UsageFilterBar dashboard={dashboard} onGroupChange={(value) => void changeGroup(value)} />
      <UsageStatePanel states={dashboard.states} />
      <UsageSummaryCards cards={dashboard.summary_cards} />
      <UsageTrendPanel trend={dashboard.trend} />
      <UsageRollupPanel rollup={dashboard.rollup} onDrilldown={(href) => void loadDrilldown(href)} />
      <UsageEventDrilldown drilldown={drilldown ?? dashboard.drilldown} />
      <UsageExportPanel
        exportResult={exportResult}
        exports={dashboard.exports}
        onExport={() => void requestExport()}
      />
    </div>
  );
}

function setQueryParam(url: string, key: string, value: string): string {
  const next = new URL(url, window.location.origin);
  next.searchParams.set(key, value);
  return next.toString();
}

function withSearch(url: string): string {
  if (!window.location.search || url.includes("?")) {
    return url;
  }
  return `${url}${window.location.search}`;
}
