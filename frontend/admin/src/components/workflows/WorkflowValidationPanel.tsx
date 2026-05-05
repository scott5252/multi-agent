import { CheckCircle2, ShieldAlert } from "lucide-react";

import type {
  BuilderMutationResult,
  WorkflowValidationSummary,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface WorkflowValidationPanelProps {
  lastResult: BuilderMutationResult | null;
  onValidate: (ready: boolean) => void;
  validating: boolean;
  validation: WorkflowValidationSummary;
}

export function WorkflowValidationPanel({
  lastResult,
  onValidate,
  validating,
  validation,
}: WorkflowValidationPanelProps) {
  return (
    <section className="workflow-validation-panel" aria-labelledby="validation-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Validation</p>
          <h2 id="validation-title">Backend-owned findings</h2>
        </div>
        <Badge tone={toneFor(validation.status)}>{validation.status}</Badge>
      </div>
      <p>{validation.summary}</p>
      <small>{validation.generated_at_label}</small>
      <div className="action-row">
        <Button
          disabled={validating}
          onClick={() => onValidate(false)}
          type="button"
          variant="secondary"
        >
          <ShieldAlert aria-hidden="true" size={16} />
          Run validation
        </Button>
        <Button
          disabled={validating}
          onClick={() => onValidate(true)}
          type="button"
          variant="secondary"
        >
          <CheckCircle2 aria-hidden="true" size={16} />
          Mark evidence current
        </Button>
      </div>
      {validation.findings.length > 0 ? (
        <ul className="validation-list">
          {validation.findings.map((finding) => (
            <li key={finding.finding_id}>
              <div className="card-heading">
                <strong>{finding.section}</strong>
                <Badge tone={toneFor(finding.severity)}>{finding.severity}</Badge>
              </div>
              <p>{finding.message}</p>
              <small>{finding.recommended_action}</small>
              {finding.evidence_reference_id ? (
                <small>{finding.evidence_reference_id}</small>
              ) : null}
            </li>
          ))}
        </ul>
      ) : (
        <p className="table-footer">No validation blockers are present.</p>
      )}
      {lastResult ? (
        <section className={`mutation-result ${lastResult.status}`}>
          <p className="eyebrow">Validation result</p>
          <h2>{lastResult.status.replace("_", " ")}</h2>
          <p>{lastResult.summary}</p>
          {lastResult.audit_reference_id ? (
            <small>{lastResult.audit_reference_id}</small>
          ) : null}
        </section>
      ) : null}
    </section>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (status === "ready" || status === "published" || status === "accepted") {
    return "success";
  }
  if (status === "blocked" || status === "critical" || status === "blocking") {
    return "critical";
  }
  if (status === "warning" || status === "stale") {
    return "warning";
  }
  return "info";
}
