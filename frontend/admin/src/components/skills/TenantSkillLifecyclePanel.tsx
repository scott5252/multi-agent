import { Download, PackagePlus } from "lucide-react";

import type {
  SkillLifecycleMutationResult,
  TenantSkillDiscovery,
  TenantSkillInstallationSummary,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface TenantSkillLifecyclePanelProps {
  discovery: TenantSkillDiscovery | null;
  installResult: SkillLifecycleMutationResult | null;
  installations: TenantSkillInstallationSummary[];
  onInstall: (url: string, installation: TenantSkillInstallationSummary) => void;
}

export function TenantSkillLifecyclePanel({
  discovery,
  installResult,
  installations,
  onInstall,
}: TenantSkillLifecyclePanelProps) {
  return (
    <section className="governance-panel skill-panel" aria-labelledby="tenant-skills-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Discover</p>
          <h2 id="tenant-skills-title">Granted tenant skills</h2>
        </div>
        <Badge tone="info">{discovery?.grants.length ?? 0} grants</Badge>
      </div>
      <div className="governance-card-grid">
        {discovery?.available_versions.map((version) => (
          <article className="governance-card" key={version.version_id}>
            <div className="card-heading">
              <strong>{version.package_slug}</strong>
              <Badge tone={toneFor(version.lifecycle_status)}>
                {version.lifecycle_status}
              </Badge>
            </div>
            <p>{version.safe_manifest_summary}</p>
            <dl className="compact-dl">
              <div>
                <dt>Version</dt>
                <dd>{version.version_label}</dd>
              </div>
              <div>
                <dt>Digest</dt>
                <dd>{version.manifest_digest}</dd>
              </div>
            </dl>
          </article>
        ))}
        {installations.map((installation) => {
          const installAction = installation.authorized_actions.find(
            (action) => action.action_id === "install-package",
          );
          return (
            <article className="governance-card" key={installation.installation_id}>
              <div className="card-heading">
                <strong>{installation.package_slug}</strong>
                <Badge tone={toneFor(installation.installation_status)}>
                  {installation.installation_status}
                </Badge>
              </div>
              <p>{installation.findings.join(" ")}</p>
              <dl className="compact-dl">
                <div>
                  <dt>Installed</dt>
                  <dd>{installation.installed_version}</dd>
                </div>
                <div>
                  <dt>Binding</dt>
                  <dd>{installation.binding_readiness}</dd>
                </div>
                <div>
                  <dt>Upgrade</dt>
                  <dd>{installation.upgrade_path ?? "Current"}</dd>
                </div>
              </dl>
              {installAction ? (
                <Button
                  onClick={() => onInstall(installAction.href, installation)}
                  type="button"
                  variant="primary"
                >
                  <PackagePlus aria-hidden="true" size={16} />
                  Install
                </Button>
              ) : (
                <p className="safe-note">
                  <Download aria-hidden="true" size={16} />
                  No tenant install action is available.
                </p>
              )}
            </article>
          );
        })}
      </div>
      {installResult ? (
        <article className={`mutation-result ${installResult.status}`}>
          <p className="eyebrow">Install result</p>
          <h3>{installResult.status}</h3>
          <p>{installResult.summary}</p>
          {installResult.audit_reference_id ? (
            <small>{installResult.audit_reference_id}</small>
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
