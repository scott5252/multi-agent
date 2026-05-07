import type { TestRunSummary } from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface RunListPanelProps {
  onOpenRun: (href: string) => void;
  runs: TestRunSummary[];
}

export function RunListPanel({ onOpenRun, runs }: RunListPanelProps) {
  return (
    <section className="governance-panel testbench-panel" aria-labelledby="run-list-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">History</p>
          <h2 id="run-list-title">Recent runs</h2>
        </div>
      </div>
      <div className="governance-card-grid">
        {runs.map((run) => {
          const openAction = run.authorized_actions.find(
            (action) => action.action_id === "open-run",
          );
          return (
            <article className="governance-card" key={run.run_id}>
              <div className="card-heading">
                <strong>{run.suite_name}</strong>
                <Badge tone={toneFor(run.status)}>{run.status}</Badge>
              </div>
              <p>{run.safe_mode}</p>
              <dl className="compact-dl">
                <div>
                  <dt>Pass rate</dt>
                  <dd>{Math.round(run.pass_rate * 100)}%</dd>
                </div>
                <div>
                  <dt>Usage</dt>
                  <dd>{run.usage_summary}</dd>
                </div>
                <div>
                  <dt>Latency</dt>
                  <dd>{run.latency_summary}</dd>
                </div>
              </dl>
              {openAction ? (
                <Button
                  onClick={() => onOpenRun(openAction.href)}
                  type="button"
                  variant="secondary"
                >
                  Open run
                </Button>
              ) : null}
            </article>
          );
        })}
      </div>
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
