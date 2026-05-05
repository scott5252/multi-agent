import { useEffect, useState } from "react";

import { fetchChannelRunStatus } from "../../api/client";
import type { RunStatusSummary } from "../../api/generated/reactAdminApi";
import { CommonState } from "../states/CommonState";

export function RunStatusSummaryPage({ runStatusUrl }: { runStatusUrl: string }) {
  const [summary, setSummary] = useState<RunStatusSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    fetchChannelRunStatus(runStatusUrl)
      .then((payload) => {
        if (alive) {
          setSummary(payload);
          setError(null);
        }
      })
      .catch((caught: unknown) => {
        if (alive) {
          setError(caught instanceof Error ? caught.message : "Run status unavailable");
        }
      });
    return () => {
      alive = false;
    };
  }, [runStatusUrl]);

  if (error && !summary) {
    return (
      <CommonState
        state={{
          action: null,
          state: "dependency_unavailable",
          summary: error,
          title: "Run status unavailable",
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
          summary: "Loading safe run status.",
          title: "Loading run status",
          trace_id: null,
        }}
      />
    );
  }
  return (
    <section className="channel-page channel-page--run">
      <h1>{summary.workflow_label}</h1>
      <div className={`status-pill status-pill--${summary.status}`}>{summary.status}</div>
      <p>{summary.next_step}</p>
      <dl className="preference-grid">
        <div>
          <dt>Requested by</dt>
          <dd>{summary.requested_by_label}</dd>
        </div>
        <div>
          <dt>Audit</dt>
          <dd>{summary.audit_reference}</dd>
        </div>
        <div>
          <dt>Artifacts</dt>
          <dd>{summary.artifact_references.join(", ")}</dd>
        </div>
      </dl>
    </section>
  );
}
