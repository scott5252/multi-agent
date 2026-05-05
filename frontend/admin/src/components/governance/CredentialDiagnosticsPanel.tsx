import type { ProviderCredentialReference } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

export function CredentialDiagnosticsPanel({
  credential,
}: {
  credential: ProviderCredentialReference;
}) {
  return (
    <div className="credential-diagnostics">
      <div className="card-heading">
        <strong>{credential.label}</strong>
        <Badge tone={credential.readiness === "ready" ? "success" : "warning"}>
          {credential.readiness}
        </Badge>
      </div>
      <dl>
        <div>
          <dt>Source</dt>
          <dd>{credential.source_type}</dd>
        </div>
        <div>
          <dt>Fingerprint</dt>
          <dd>{credential.fingerprint ?? "not available"}</dd>
        </div>
        <div>
          <dt>Resolution</dt>
          <dd>{credential.last_resolution_status}</dd>
        </div>
      </dl>
      <p>{credential.policy_reason}</p>
      <small>{credential.remediation}</small>
    </div>
  );
}
