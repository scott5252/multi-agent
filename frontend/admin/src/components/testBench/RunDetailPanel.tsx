import { XCircle } from "lucide-react";

import type { TestRunDetail } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface RunDetailPanelProps {
  run: TestRunDetail | null;
}

export function RunDetailPanel({ run }: RunDetailPanelProps) {
  return (
    <section className="governance-panel testbench-panel" aria-labelledby="run-detail-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Results</p>
          <h2 id="run-detail-title">Pass/fail diagnostics</h2>
        </div>
        <XCircle aria-hidden="true" size={20} />
      </div>
      {run ? (
        <>
          <article className="governance-card">
            <div className="card-heading">
              <strong>{run.summary.run_id}</strong>
              <Badge tone={toneFor(run.summary.status)}>{run.summary.status}</Badge>
            </div>
            <p>{run.redaction_summary}</p>
            <dl className="compact-dl">
              <div>
                <dt>Target revision</dt>
                <dd>{run.summary.target_revision}</dd>
              </div>
              <div>
                <dt>Safe mode</dt>
                <dd>{run.summary.safe_mode}</dd>
              </div>
              <div>
                <dt>Audit</dt>
                <dd>{run.audit_reference_id}</dd>
              </div>
            </dl>
          </article>
          <div className="governance-card-grid">
            {run.assertion_diagnostics.map((finding) => (
              <article className="governance-card diagnostic-card" key={finding.finding_id}>
                <div className="card-heading">
                  <strong>{finding.label}</strong>
                  <Badge tone={toneFor(finding.category)}>{finding.category}</Badge>
                </div>
                <p>{finding.remediation}</p>
                <dl className="compact-dl">
                  <div>
                    <dt>Path</dt>
                    <dd>{finding.path_summary}</dd>
                  </div>
                  <div>
                    <dt>Expected</dt>
                    <dd>{finding.expected_summary}</dd>
                  </div>
                  <div>
                    <dt>Actual</dt>
                    <dd>{finding.actual_summary}</dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        </>
      ) : (
        <p className="safe-note">Open a deterministic run to review diagnostics.</p>
      )}
    </section>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (["ready", "passed"].includes(status)) {
    return "success";
  }
  if (
    ["blocked", "denied", "failed", "failed_assertion", "contract_failure", "unavailable", "artifact_unavailable", "audit_unavailable", "redaction_unavailable"].includes(
      status,
    )
  ) {
    return "critical";
  }
  if (["warning", "queued", "running", "stale", "missing"].includes(status)) {
    return "warning";
  }
  return "info";
}
