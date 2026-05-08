import { Route } from "lucide-react";

import type {
  GovernanceMutationResult,
  RoutingPreviewResult,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface RoutingPreviewPanelProps {
  lastResult: GovernanceMutationResult | null;
  onPreview: () => void;
  preview: RoutingPreviewResult | null;
}

export function RoutingPreviewPanel({
  lastResult,
  onPreview,
  preview,
}: RoutingPreviewPanelProps) {
  const activePreview = lastResult?.routing_preview ?? preview;
  if (!activePreview) {
    return (
      <section className="governance-panel" aria-labelledby="routing-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Routing</p>
            <h2 id="routing-title">Read-only policy preview</h2>
          </div>
          <Badge tone="warning">unavailable</Badge>
        </div>
        <p>No live routing or policy records are available for this scope.</p>
      </section>
    );
  }
  return (
    <section className="governance-panel" aria-labelledby="routing-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Routing</p>
          <h2 id="routing-title">Read-only policy preview</h2>
        </div>
        <Badge tone="success">{activePreview.status}</Badge>
      </div>
      <p>{activePreview.model_decision}</p>
      <div className="routing-grid">
        <article>
          <strong>Provider decision</strong>
          <p>{activePreview.provider_decision}</p>
        </article>
        <article>
          <strong>Skill decision</strong>
          <p>{activePreview.skill_decision}</p>
        </article>
        <article>
          <strong>Guardrail</strong>
          <p>{activePreview.direct_call_guardrail}</p>
        </article>
      </div>
      <ul>
        {activePreview.policy_reasons.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>
      <Button onClick={onPreview} type="button" variant="primary">
        <Route aria-hidden="true" size={16} />
        Preview routing
      </Button>
      {lastResult ? (
        <small>{lastResult.audit_reference_id ?? activePreview.audit_reference_id}</small>
      ) : null}
    </section>
  );
}
