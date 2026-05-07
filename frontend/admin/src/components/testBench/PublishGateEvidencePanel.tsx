import { ShieldCheck } from "lucide-react";

import type {
  PublishGateEvidence,
  TestBenchMutationResult,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface PublishGateEvidencePanelProps {
  gates: PublishGateEvidence[];
  onRefreshGate: (href: string) => void;
  refreshResult: TestBenchMutationResult | null;
}

export function PublishGateEvidencePanel({
  gates,
  onRefreshGate,
  refreshResult,
}: PublishGateEvidencePanelProps) {
  return (
    <section className="governance-panel testbench-panel" aria-labelledby="gate-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Gates</p>
          <h2 id="gate-title">Publish-gate evidence</h2>
        </div>
        <ShieldCheck aria-hidden="true" size={20} />
      </div>
      <div className="governance-card-grid">
        {gates.map((gate) => {
          const refreshAction = gate.authorized_actions.find(
            (action) => action.action_id === "run-suite",
          );
          return (
            <article className="governance-card gate-card" key={gate.gate_id}>
              <div className="card-heading">
                <strong>{gate.required_suite_label}</strong>
                <Badge tone={toneFor(gate.evidence_status)}>
                  {gate.evidence_status}
                </Badge>
              </div>
              <p>{gate.reason}</p>
              <p>{gate.remediation}</p>
              <small>{gate.target_revision}</small>
              {refreshAction ? (
                <Button
                  onClick={() => onRefreshGate("/admin/app/test-bench/gates/qa033-required-suite/refresh")}
                  type="button"
                  variant="secondary"
                >
                  Refresh evidence
                </Button>
              ) : null}
            </article>
          );
        })}
      </div>
      {refreshResult ? (
        <article className={`mutation-result ${refreshResult.status}`}>
          <p className="eyebrow">Gate result</p>
          <h3>{refreshResult.status}</h3>
          <p>{refreshResult.summary}</p>
        </article>
      ) : null}
    </section>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (["ready", "passed"].includes(status)) {
    return "success";
  }
  if (["blocked", "denied", "failed", "unavailable", "artifact_unavailable", "audit_unavailable", "redaction_unavailable"].includes(status)) {
    return "critical";
  }
  if (["warning", "queued", "running", "stale", "missing"].includes(status)) {
    return "warning";
  }
  return "info";
}
