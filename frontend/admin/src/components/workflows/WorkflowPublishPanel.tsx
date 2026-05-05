import { Send, ShieldCheck } from "lucide-react";

import type {
  BuilderMutationResult,
  WorkflowPublishReadiness,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface WorkflowPublishPanelProps {
  lastResult: BuilderMutationResult | null;
  onPublish: (readyFixture: boolean, confirmed: boolean) => void;
  publishing: boolean;
  readiness: WorkflowPublishReadiness;
}

export function WorkflowPublishPanel({
  lastResult,
  onPublish,
  publishing,
  readiness,
}: WorkflowPublishPanelProps) {
  const confirmationReady =
    lastResult?.status === "confirmation_required" || readiness.confirmation !== null;
  return (
    <section className="workflow-publish-panel" aria-labelledby="publish-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Publish gate</p>
          <h2 id="publish-title">Evidence and decision</h2>
        </div>
        <Badge tone={toneFor(readiness.decision)}>{readiness.decision}</Badge>
      </div>
      <p>{readiness.summary}</p>
      <div className="publish-evidence-grid">
        {readiness.required_evidence.map((item) => (
          <article key={item.evidence_id}>
            <div className="card-heading">
              <strong>{item.label}</strong>
              <Badge tone={toneFor(item.status)}>{item.status}</Badge>
            </div>
            <p>{item.summary}</p>
            {item.artifact_reference_id ? (
              <small>{item.artifact_reference_id}</small>
            ) : null}
          </article>
        ))}
      </div>
      {readiness.blockers.length > 0 ? (
        <ul className="validation-list">
          {readiness.blockers.map((blocker) => (
            <li key={blocker}>{blocker}</li>
          ))}
        </ul>
      ) : null}
      {readiness.published_bundle_summary ? (
        <p className="published-summary">{readiness.published_bundle_summary}</p>
      ) : null}
      <div className="action-row">
        <Button
          disabled={publishing}
          onClick={() => onPublish(false, false)}
          type="button"
          variant="secondary"
        >
          <ShieldCheck aria-hidden="true" size={16} />
          Check publish gate
        </Button>
        <Button
          disabled={publishing}
          onClick={() => onPublish(true, false)}
          type="button"
          variant="secondary"
        >
          <Send aria-hidden="true" size={16} />
          Prepare publish
        </Button>
        <Button
          disabled={publishing || !confirmationReady}
          onClick={() => onPublish(true, true)}
          type="button"
          variant="primary"
        >
          <Send aria-hidden="true" size={16} />
          Confirm publish
        </Button>
      </div>
      {lastResult ? (
        <section className={`mutation-result ${lastResult.status}`}>
          <p className="eyebrow">Publish result</p>
          <h2>{lastResult.status.replace("_", " ")}</h2>
          <p>{lastResult.summary}</p>
          {lastResult.confirmation ? (
            <div className="confirmation-box">
              <strong>{lastResult.confirmation.title}</strong>
              <p>{lastResult.confirmation.summary}</p>
            </div>
          ) : null}
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
  if (
    status === "blocked" ||
    status === "critical" ||
    status === "validation_error"
  ) {
    return "critical";
  }
  if (status === "warning" || status === "confirmation_required") {
    return "warning";
  }
  return "info";
}
