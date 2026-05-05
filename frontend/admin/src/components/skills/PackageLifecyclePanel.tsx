import { Ban, ShieldCheck } from "lucide-react";

import type {
  SkillLifecycleMutationResult,
  SkillPackageVersionSummary,
  TenantSkillGrantSummary,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface PackageLifecyclePanelProps {
  grantResult: SkillLifecycleMutationResult | null;
  onLifecycleAction: (url: string) => void;
  onUpdateGrant: (url: string, grant: TenantSkillGrantSummary) => void;
  versions: SkillPackageVersionSummary[];
}

export function PackageLifecyclePanel({
  grantResult,
  onLifecycleAction,
  onUpdateGrant,
  versions,
}: PackageLifecyclePanelProps) {
  return (
    <section className="governance-panel skill-panel" aria-labelledby="versions-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Versions</p>
          <h2 id="versions-title">Immutable package versions</h2>
        </div>
        <Badge tone="info">{versions.length} visible</Badge>
      </div>
      <div className="governance-card-grid">
        {versions.map((version) => {
          const grant = version.tenant_grant_summary[0];
          const grantAction = version.authorized_actions.find(
            (action) => action.action_id === "package-grant",
          );
          const quarantineAction = version.authorized_actions.find(
            (action) => action.action_id === "package-quarantine",
          );
          const withdrawAction = version.authorized_actions.find(
            (action) => action.action_id === "package-withdraw",
          );
          return (
            <article className="governance-card" key={version.version_id}>
              <div className="card-heading">
                <strong>{version.version_label}</strong>
                <Badge tone={toneFor(version.lifecycle_status)}>
                  {version.lifecycle_status}
                </Badge>
              </div>
              <p>{version.safe_manifest_summary}</p>
              <dl className="compact-dl">
                <div>
                  <dt>Validation</dt>
                  <dd>{version.validation_evidence_ref}</dd>
                </div>
                <div>
                  <dt>Smoke evidence</dt>
                  <dd>{version.smoke_evidence_ref}</dd>
                </div>
              </dl>
              {grant ? (
                <section className="skill-subpanel">
                  <div className="card-heading">
                    <strong>{grant.tenant_label}</strong>
                    <Badge tone={toneFor(grant.grant_status)}>
                      {grant.grant_status}
                    </Badge>
                  </div>
                  <p>{grant.restrictions.join(" ")}</p>
                  {grantAction ? (
                    <Button
                      onClick={() => onUpdateGrant(grantAction.href, grant)}
                      type="button"
                      variant="secondary"
                    >
                      <ShieldCheck aria-hidden="true" size={16} />
                      Update grant
                    </Button>
                  ) : null}
                </section>
              ) : null}
              <div className="button-row">
                {quarantineAction ? (
                  <Button
                    onClick={() => onLifecycleAction(quarantineAction.href)}
                    type="button"
                    variant="danger"
                  >
                    <Ban aria-hidden="true" size={16} />
                    Quarantine
                  </Button>
                ) : null}
                {withdrawAction ? (
                  <Button
                    onClick={() => onLifecycleAction(withdrawAction.href)}
                    type="button"
                    variant="danger"
                  >
                    Withdraw
                  </Button>
                ) : null}
              </div>
            </article>
          );
        })}
      </div>
      {grantResult ? (
        <article className={`mutation-result ${grantResult.status}`}>
          <p className="eyebrow">Lifecycle result</p>
          <h3>{grantResult.status}</h3>
          <p>{grantResult.summary}</p>
          {grantResult.audit_reference_id ? (
            <small>{grantResult.audit_reference_id}</small>
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
  if (["blocked", "denied", "failed", "unavailable", "withdrawn"].includes(status)) {
    return "critical";
  }
  if (["degraded", "warning", "queued", "quarantined", "stale"].includes(status)) {
    return "warning";
  }
  return "info";
}
