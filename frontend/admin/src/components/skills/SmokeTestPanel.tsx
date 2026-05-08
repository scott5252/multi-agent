import { RefreshCw } from "lucide-react";

import type {
  SkillLifecycleMutationResult,
  TenantSkillInstallationSummary,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

interface SmokeTestPanelProps {
  installations: TenantSkillInstallationSummary[];
  onRefresh: (url: string, installation: TenantSkillInstallationSummary) => void;
  readinessResult: SkillLifecycleMutationResult | null;
}

export function SmokeTestPanel({
  installations,
  onRefresh,
  readinessResult,
}: SmokeTestPanelProps) {
  return (
    <section className="governance-panel skill-panel" aria-labelledby="smoke-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Smoke tests</p>
          <h2 id="smoke-title">Queued readiness</h2>
        </div>
      </div>
      <div className="governance-card-grid">
        {installations.length === 0 ? (
          <article className="governance-card">
            <strong>No readiness checks</strong>
            <p>No tenant skill installation is available for smoke-test readiness.</p>
          </article>
        ) : null}
        {installations.map((installation) => {
          const refreshAction = installation.authorized_actions.find(
            (action) => action.action_id === "refresh-smoke-tests",
          );
          return (
            <article className="governance-card" key={installation.installation_id}>
              <div className="card-heading">
                <strong>{installation.package_slug}</strong>
                <Badge tone={toneFor(installation.smoke_test_readiness)}>
                  {installation.smoke_test_readiness}
                </Badge>
              </div>
              <p>{installation.audit_reference_id}</p>
              {refreshAction ? (
                <Button
                  onClick={() => onRefresh(refreshAction.href, installation)}
                  type="button"
                  variant="secondary"
                >
                  <RefreshCw aria-hidden="true" size={16} />
                  Refresh readiness
                </Button>
              ) : null}
            </article>
          );
        })}
      </div>
      {readinessResult ? (
        <article className={`mutation-result ${readinessResult.status}`}>
          <p className="eyebrow">Readiness result</p>
          <h3>{readinessResult.status}</h3>
          <p>{readinessResult.summary}</p>
          {readinessResult.smoke_test ? (
            <small>{readinessResult.smoke_test.evidence_reference_id}</small>
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
