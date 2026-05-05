import { PlugZap } from "lucide-react";

import type {
  ConnectorReadinessSummary,
  SkillLifecycleMutationResult,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface ConnectorReadinessPanelProps {
  connectors: ConnectorReadinessSummary[];
  diagnosticResult: SkillLifecycleMutationResult | null;
  onDiagnostic: (url: string) => void;
}

export function ConnectorReadinessPanel({
  connectors,
  diagnosticResult,
  onDiagnostic,
}: ConnectorReadinessPanelProps) {
  return (
    <section className="governance-panel skill-panel" aria-labelledby="connectors-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Readiness</p>
          <h2 id="connectors-title">Connector readiness</h2>
        </div>
        <Badge tone="info">{connectors.length} connectors</Badge>
      </div>
      <div className="connector-grid">
        {connectors.map((connector) => {
          const diagnosticAction = connector.authorized_actions[0];
          return (
            <article className="governance-card" key={connector.connector_id}>
              <div className="card-heading">
                <strong>{connector.connector_label}</strong>
                <Badge tone={toneFor(connector.readiness)}>
                  {connector.readiness}
                </Badge>
              </div>
              <p>{connector.last_safe_summary}</p>
              <dl className="compact-dl">
                <div>
                  <dt>Credential</dt>
                  <dd>{connector.credential_status}</dd>
                </div>
                <div>
                  <dt>Policy</dt>
                  <dd>{connector.policy_status}</dd>
                </div>
                <div>
                  <dt>Smoke</dt>
                  <dd>{connector.smoke_test_status}</dd>
                </div>
              </dl>
              <small>{connector.evidence_reference_id}</small>
              {diagnosticAction ? (
                <Button
                  onClick={() => onDiagnostic(diagnosticAction.href)}
                  type="button"
                  variant="secondary"
                >
                  <PlugZap aria-hidden="true" size={16} />
                  Run diagnostic
                </Button>
              ) : null}
            </article>
          );
        })}
      </div>
      {diagnosticResult ? (
        <article className={`mutation-result ${diagnosticResult.status}`}>
          <p className="eyebrow">Diagnostic result</p>
          <h3>{diagnosticResult.status}</h3>
          <p>{diagnosticResult.summary}</p>
          {diagnosticResult.diagnostic ? (
            <small>{diagnosticResult.diagnostic.audit_reference_id}</small>
          ) : null}
        </article>
      ) : null}
    </section>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (["ready", "passed", "published"].includes(status)) {
    return "success";
  }
  if (["blocked", "denied", "failed", "unavailable"].includes(status)) {
    return "critical";
  }
  if (["degraded", "warning", "queued", "stale"].includes(status)) {
    return "warning";
  }
  return "info";
}
