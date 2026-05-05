import { useEffect, useState } from "react";

import { fetchUsageExportDetail } from "../../api/client";
import type { UsageReactExportSummary } from "../../api/generated/reactAdminApi";
import { CommonState } from "../states/CommonState";

export function UsageExportDetailPage({ exportUrl }: { exportUrl: string }) {
  const [summary, setSummary] = useState<UsageReactExportSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    fetchUsageExportDetail(exportUrl)
      .then((payload) => {
        if (alive) {
          setSummary(payload);
          setError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setError(caught instanceof Error ? caught.message : "Usage export unavailable");
        }
      });
    return () => {
      alive = false;
    };
  }, [exportUrl]);

  if (error) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: error,
          title: "Usage export unavailable",
          trace_id: null,
        }}
      />
    );
  }

  if (!summary) {
    return (
      <CommonState
        state={{
          action: null,
          state: "loading",
          summary: "Loading safe export evidence.",
          title: "Loading usage export",
          trace_id: null,
        }}
      />
    );
  }

  return (
    <section className="usage-page usage-export-detail-page">
      <div className="patterns-hero usage-hero">
        <p className="eyebrow">Usage export</p>
        <h2>{summary.status}</h2>
        <p>{summary.next_step}</p>
      </div>
      <section className="usage-panel">
        <dl className="usage-export-summary">
          <dt>Scope</dt>
          <dd>{summary.scope_label}</dd>
          <dt>Requester</dt>
          <dd>{summary.requested_by_label}</dd>
          <dt>Rows</dt>
          <dd>{summary.row_count}</dd>
          <dt>Artifact</dt>
          <dd>{summary.artifact_reference ?? "Pending"}</dd>
          <dt>Audit</dt>
          <dd>{summary.audit_reference}</dd>
        </dl>
      </section>
    </section>
  );
}
