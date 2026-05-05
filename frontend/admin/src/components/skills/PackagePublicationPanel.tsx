import { CheckCircle2, FileUp, PackageCheck } from "lucide-react";

import type {
  PackagePublicationWorkspace,
  SkillLifecycleMutationResult,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";
import { ValidationFindingsPanel } from "./ValidationFindingsPanel";

interface PackagePublicationPanelProps {
  candidateResult: SkillLifecycleMutationResult | null;
  onPublish: (url: string) => void;
  onSaveCandidate: (url: string) => void;
  onValidate: (url: string, ready: boolean) => void;
  publication: PackagePublicationWorkspace;
  publishResult: SkillLifecycleMutationResult | null;
  validationResult: SkillLifecycleMutationResult | null;
}

export function PackagePublicationPanel({
  candidateResult,
  onPublish,
  onSaveCandidate,
  onValidate,
  publication,
  publishResult,
  validationResult,
}: PackagePublicationPanelProps) {
  const candidate = publication.candidate;
  const saveAction = publication.authorized_actions.find(
    (action) => action.action_id === "candidate-create",
  );
  const validateAction = candidate.authorized_actions.find(
    (action) => action.action_id === "candidate-validate",
  );
  const publishAction = candidate.authorized_actions.find(
    (action) => action.action_id === "candidate-publish",
  );

  return (
    <section className="governance-panel skill-panel" aria-labelledby="publish-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Publish</p>
          <h2 id="publish-title">Package publication</h2>
        </div>
        <Badge tone="success">{publication.publish_readiness}</Badge>
      </div>
      <div className="skill-step-grid">
        {publication.available_steps.map((step) => (
          <article className="skill-step" key={step.step_id}>
            <Badge tone={toneFor(step.status)}>{step.status}</Badge>
            <strong>{step.label}</strong>
            <p>{step.summary}</p>
          </article>
        ))}
      </div>
      <div className="governance-card-grid">
        <article className="governance-card">
          <div className="card-heading">
            <strong>{candidate.package_slug}</strong>
            <Badge tone={toneFor(candidate.validation_status)}>
              {candidate.validation_status}
            </Badge>
          </div>
          <p>{candidate.safe_manifest_summary}</p>
          <dl className="compact-dl">
            <div>
              <dt>Digest</dt>
              <dd>{candidate.manifest_digest}</dd>
            </div>
            <div>
              <dt>Source</dt>
              <dd>{candidate.manifest_source}</dd>
            </div>
            <div>
              <dt>Revision</dt>
              <dd>{candidate.candidate_revision}</dd>
            </div>
          </dl>
          <div className="button-row">
            {saveAction ? (
              <Button onClick={() => onSaveCandidate(saveAction.href)} type="button">
                <FileUp aria-hidden="true" size={16} />
                Save candidate
              </Button>
            ) : null}
            {validateAction ? (
              <Button
                onClick={() => onValidate(validateAction.href, true)}
                type="button"
                variant="secondary"
              >
                <CheckCircle2 aria-hidden="true" size={16} />
                Validate
              </Button>
            ) : null}
            {publishAction ? (
              <Button
                onClick={() => onPublish(publishAction.href)}
                type="button"
                variant="primary"
              >
                <PackageCheck aria-hidden="true" size={16} />
                Publish
              </Button>
            ) : null}
          </div>
        </article>
        <ValidationFindingsPanel
          candidate={candidate}
          validationResult={validationResult}
        />
      </div>
      {candidateResult ? (
        <ResultCard label="Candidate result" result={candidateResult} />
      ) : null}
      {publishResult ? <ResultCard label="Publish result" result={publishResult} /> : null}
    </section>
  );
}

function ResultCard({
  label,
  result,
}: {
  label: string;
  result: SkillLifecycleMutationResult;
}) {
  return (
    <article className={`mutation-result ${result.status}`}>
      <p className="eyebrow">{label}</p>
      <h3>{result.status}</h3>
      <p>{result.summary}</p>
      {result.audit_reference_id ? <small>{result.audit_reference_id}</small> : null}
    </article>
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
