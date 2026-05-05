import type { ProfileResolutionPreview } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

export function ProfileResolutionPanel({
  resolution,
}: {
  resolution: ProfileResolutionPreview;
}) {
  return (
    <section className="resolution-panel" aria-label="Profile resolution preview">
      <div className="card-heading">
        <strong>Resolution preview</strong>
        <Badge tone={resolution.status === "ready" ? "success" : "warning"}>
          {resolution.status}
        </Badge>
      </div>
      <dl className="compact-dl">
        <div>
          <dt>Model</dt>
          <dd>{resolution.model_route}</dd>
        </div>
        <div>
          <dt>Provider</dt>
          <dd>{resolution.provider_route}</dd>
        </div>
        <div>
          <dt>Prompt</dt>
          <dd>{resolution.prompt_route}</dd>
        </div>
      </dl>
      <ul>
        {resolution.policy_reasons.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>
      <small>{resolution.audit_reference_id}</small>
    </section>
  );
}
