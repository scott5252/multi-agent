import { Activity } from "lucide-react";

import type { TestRunDetail } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface RunProgressPanelProps {
  run: TestRunDetail | null;
}

export function RunProgressPanel({ run }: RunProgressPanelProps) {
  return (
    <section className="governance-panel testbench-panel" aria-labelledby="run-progress-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Progress</p>
          <h2 id="run-progress-title">Backend-owned status</h2>
        </div>
        <Activity aria-hidden="true" size={20} />
      </div>
      {run ? (
        <article className="governance-card">
          <div className="card-heading">
            <strong>{run.summary.run_id}</strong>
            <Badge tone={toneFor(run.progress.status)}>{run.progress.status}</Badge>
          </div>
          <p>{run.progress.summary}</p>
          <dl className="compact-dl">
            <div>
              <dt>Cases</dt>
              <dd>
                {run.progress.completed_cases}/{run.progress.total_cases}
              </dd>
            </div>
            <div>
              <dt>Refresh</dt>
              <dd>{run.progress.next_poll_seconds}s</dd>
            </div>
            <div>
              <dt>Audit</dt>
              <dd>{run.progress.audit_reference_id}</dd>
            </div>
          </dl>
        </article>
      ) : (
        <p className="safe-note">Launch or open a run to view progress.</p>
      )}
    </section>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (["ready", "passed"].includes(status)) {
    return "success";
  }
  if (["blocked", "denied", "failed", "failed_assertion", "unavailable", "artifact_unavailable", "audit_unavailable", "redaction_unavailable"].includes(status)) {
    return "critical";
  }
  if (["warning", "queued", "running", "stale", "missing"].includes(status)) {
    return "warning";
  }
  return "info";
}
