import { KeyRound } from "lucide-react";

import type {
  SkillLifecycleMutationResult,
  TenantSkillInstallationSummary,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface CredentialReadinessPanelProps {
  credentialResult: SkillLifecycleMutationResult | null;
  installations: TenantSkillInstallationSummary[];
  onConfigure: (
    url: string,
    installation: TenantSkillInstallationSummary,
    referenceId: string,
  ) => void;
}

export function CredentialReadinessPanel({
  credentialResult,
  installations,
  onConfigure,
}: CredentialReadinessPanelProps) {
  return (
    <section className="governance-panel skill-panel" aria-labelledby="credentials-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Credentials</p>
          <h2 id="credentials-title">Reference readiness</h2>
        </div>
      </div>
      <div className="governance-card-grid">
        {installations.length === 0 ? (
          <article className="governance-card">
            <strong>No credential readiness records</strong>
            <p>No tenant skill installation has credential metadata yet.</p>
          </article>
        ) : null}
        {installations.map((installation) => {
          const credentialAction = installation.authorized_actions.find(
            (action) => action.action_id === "configure-credentials",
          );
          const selected = installation.credential_options[0];
          return (
            <article className="governance-card" key={installation.installation_id}>
              <div className="card-heading">
                <strong>{installation.package_slug}</strong>
                <Badge tone={toneFor(installation.credential_readiness)}>
                  {installation.credential_readiness}
                </Badge>
              </div>
              {installation.credential_options.map((option) => (
                <section className="skill-subpanel" key={option.reference_id}>
                  <div className="card-heading">
                    <strong>{option.label}</strong>
                    <Badge tone={toneFor(option.readiness)}>{option.readiness}</Badge>
                  </div>
                  <p>{option.policy_reason}</p>
                  <small>{option.fingerprint}</small>
                </section>
              ))}
              {credentialAction && selected ? (
                <Button
                  onClick={() =>
                    onConfigure(
                      credentialAction.href,
                      installation,
                      selected.reference_id,
                    )
                  }
                  type="button"
                  variant="secondary"
                >
                  <KeyRound aria-hidden="true" size={16} />
                  Save reference
                </Button>
              ) : null}
            </article>
          );
        })}
      </div>
      {credentialResult ? (
        <article className={`mutation-result ${credentialResult.status}`}>
          <p className="eyebrow">Credential result</p>
          <h3>{credentialResult.status}</h3>
          <p>{credentialResult.summary}</p>
          {credentialResult.credential ? (
            <small>{credentialResult.credential.fingerprint}</small>
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
