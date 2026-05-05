import { Activity, ClipboardCheck } from "lucide-react";

import type {
  BindingEligibilityPreview,
  SkillExecutionDiagnosticSummary,
  SkillLifecycleMutationResult,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface BindingAndDiagnosticsPanelProps {
  bindingResult: SkillLifecycleMutationResult | null;
  diagnostics: SkillExecutionDiagnosticSummary[];
  onDiagnostic: () => void;
  onPreview: () => void;
  preview: BindingEligibilityPreview;
}

export function BindingAndDiagnosticsPanel({
  bindingResult,
  diagnostics,
  onDiagnostic,
  onPreview,
  preview,
}: BindingAndDiagnosticsPanelProps) {
  const activePreview = bindingResult?.binding_preview ?? preview;
  return (
    <section className="governance-panel skill-panel" aria-labelledby="binding-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Binding</p>
          <h2 id="binding-title">Eligibility and diagnostics</h2>
        </div>
        <div className="button-row">
          <Button onClick={onPreview} type="button" variant="primary">
            <ClipboardCheck aria-hidden="true" size={16} />
            Preview binding
          </Button>
          <Button onClick={onDiagnostic} type="button" variant="secondary">
            <Activity aria-hidden="true" size={16} />
            Run diagnostic
          </Button>
        </div>
      </div>
      <div className="governance-review-grid">
        <article className="governance-card">
          <div className="card-heading">
            <strong>{activePreview.selected_context}</strong>
            <Badge tone="success">read only</Badge>
          </div>
          <ul className="evidence-list">
            {activePreview.policy_reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
          <dl className="compact-dl">
            <div>
              <dt>Eligible</dt>
              <dd>{activePreview.eligible_tools.length}</dd>
            </div>
            <div>
              <dt>Blocked</dt>
              <dd>{activePreview.blocked_tools.length}</dd>
            </div>
          </dl>
          <div className="skill-tool-columns">
            <div>
              <strong>Eligible tools</strong>
              <ul>
                {activePreview.eligible_tools.map((tool) => (
                  <li key={tool}>{tool}</li>
                ))}
              </ul>
            </div>
            <div>
              <strong>Blocked tools</strong>
              <ul>
                {activePreview.blocked_tools.map((tool) => (
                  <li key={tool}>{tool}</li>
                ))}
              </ul>
            </div>
          </div>
          {activePreview.missing_requirements.length ? (
            <ul className="evidence-list">
              {activePreview.missing_requirements.map((requirement) => (
                <li key={requirement}>{requirement}</li>
              ))}
            </ul>
          ) : null}
          <p className="safe-note">{activePreview.remediation}</p>
          <small>{activePreview.audit_reference_id}</small>
        </article>
        <article className="governance-card">
          <div className="card-heading">
            <strong>Gateway diagnostics</strong>
            <Badge tone="info">{diagnostics.length}</Badge>
          </div>
          {diagnostics.map((diagnostic) => (
            <section className="skill-subpanel" key={diagnostic.diagnostic_id}>
              <div className="card-heading">
                <strong>{diagnostic.tool_name}</strong>
                <Badge tone={toneFor(diagnostic.connector_readiness)}>
                  {diagnostic.connector_readiness}
                </Badge>
              </div>
              <p>{diagnostic.safe_attempt_summary}</p>
              <small>{diagnostic.redaction_summary}</small>
            </section>
          ))}
        </article>
      </div>
      {bindingResult ? (
        <article className={`mutation-result ${bindingResult.status}`}>
          <p className="eyebrow">Binding result</p>
          <h3>{bindingResult.status}</h3>
          <p>{bindingResult.summary}</p>
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
