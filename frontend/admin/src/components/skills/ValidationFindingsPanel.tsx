import { AlertTriangle, CheckCircle2 } from "lucide-react";

import type {
  SkillLifecycleMutationResult,
  SkillPackageCandidate,
} from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface ValidationFindingsPanelProps {
  candidate: SkillPackageCandidate;
  validationResult: SkillLifecycleMutationResult | null;
}

export function ValidationFindingsPanel({
  candidate,
  validationResult,
}: ValidationFindingsPanelProps) {
  const findings = candidate.validation_findings;
  return (
    <section className="skill-subpanel" aria-labelledby="validation-title">
      <div className="card-heading">
        <h3 id="validation-title">Validation findings</h3>
        <Badge tone={findings.length ? "warning" : "success"}>
          {candidate.validation_status}
        </Badge>
      </div>
      <p>{candidate.safe_documentation_summary}</p>
      {findings.length ? (
        <ul className="evidence-list">
          {findings.map((finding) => (
            <li key={`${finding.field}-${finding.code}`}>
              <AlertTriangle aria-hidden="true" size={16} />
              <span>{finding.message}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="guardrail-copy">
          <CheckCircle2 aria-hidden="true" size={16} />
          No blocking findings in the current safe candidate summary.
        </p>
      )}
      {validationResult ? (
        <article className={`mutation-result ${validationResult.status}`}>
          <strong>{validationResult.status}</strong>
          <p>{validationResult.summary}</p>
          {validationResult.audit_reference_id ? (
            <small>{validationResult.audit_reference_id}</small>
          ) : null}
        </article>
      ) : null}
    </section>
  );
}
