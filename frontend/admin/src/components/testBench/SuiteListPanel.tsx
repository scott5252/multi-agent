import { FolderOpen } from "lucide-react";

import type { TestSuiteSummary } from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface SuiteListPanelProps {
  onOpenSuite: (href: string) => void;
  suites: TestSuiteSummary[];
}

export function SuiteListPanel({ onOpenSuite, suites }: SuiteListPanelProps) {
  return (
    <section className="governance-panel testbench-panel" aria-labelledby="suite-list-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Suites</p>
          <h2 id="suite-list-title">Reusable suites</h2>
        </div>
        <FolderOpen aria-hidden="true" size={20} />
      </div>
      {suites.length === 0 ? (
        <p className="safe-note">No suites are available for the active scope.</p>
      ) : (
        <div className="governance-card-grid">
          {suites.map((suite) => {
            const openAction = suite.authorized_actions.find(
              (action) => action.action_id === "open-suite",
            );
            return (
              <article className="governance-card" key={suite.suite_id}>
                <div className="card-heading">
                  <strong>{suite.suite_name}</strong>
                  <Badge tone={toneFor(suite.publish_gate_status)}>
                    {suite.publish_gate_status}
                  </Badge>
                </div>
                <p>{suite.target_label}</p>
                <dl className="compact-dl">
                  <div>
                    <dt>Cases</dt>
                    <dd>{suite.case_count}</dd>
                  </div>
                  <div>
                    <dt>Threshold</dt>
                    <dd>{Math.round(suite.pass_threshold * 100)}%</dd>
                  </div>
                  <div>
                    <dt>Revision</dt>
                    <dd>{suite.target_revision}</dd>
                  </div>
                </dl>
                {openAction ? (
                  <Button
                    onClick={() => onOpenSuite(openAction.href)}
                    type="button"
                    variant="secondary"
                  >
                    Open suite
                  </Button>
                ) : null}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (["ready", "passed"].includes(status)) {
    return "success";
  }
  if (["blocked", "denied", "failed", "unavailable"].includes(status)) {
    return "critical";
  }
  if (["warning", "queued", "running", "stale", "missing"].includes(status)) {
    return "warning";
  }
  return "info";
}
