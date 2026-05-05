import { Activity, ShieldCheck } from "lucide-react";

import type {
  GovernanceMutationResult,
  ProviderGovernanceSummary,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";
import { CredentialDiagnosticsPanel } from "./CredentialDiagnosticsPanel";

interface ProviderGovernancePanelProps {
  onProbe: (probeUrl: string) => void;
  probeResult: GovernanceMutationResult | null;
  probing: boolean;
  providers: ProviderGovernanceSummary[];
}

export function ProviderGovernancePanel({
  onProbe,
  probeResult,
  probing,
  providers,
}: ProviderGovernancePanelProps) {
  return (
    <section className="governance-panel" aria-labelledby="providers-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Providers</p>
          <h2 id="providers-title">Setup and health</h2>
        </div>
        <Badge tone="info">{providers.length} visible</Badge>
      </div>
      <div className="governance-card-grid">
        {providers.map((provider) => {
          const probeAction = provider.authorized_actions.find((action) =>
            action.action_id.startsWith("provider-probe"),
          );
          return (
            <article className="governance-card" key={provider.provider_id}>
              <div className="card-heading">
                <strong>{provider.display_name}</strong>
                <Badge tone={toneFor(provider.status)}>{provider.status}</Badge>
              </div>
              <p>{provider.health.summary}</p>
              <dl className="compact-dl">
                <div>
                  <dt>Type</dt>
                  <dd>{provider.provider_type}</dd>
                </div>
                <div>
                  <dt>Models</dt>
                  <dd>{provider.model_count}</dd>
                </div>
                <div>
                  <dt>Breaker</dt>
                  <dd>{provider.health.breaker_state}</dd>
                </div>
              </dl>
              <CredentialDiagnosticsPanel
                credential={provider.credential_reference}
              />
              <p className="guardrail-copy">
                <ShieldCheck aria-hidden="true" size={16} />
                {provider.direct_call_guardrail}
              </p>
              <small>{provider.local_no_auth_status}</small>
              {probeAction ? (
                <Button
                  disabled={probing}
                  onClick={() => onProbe(probeAction.href)}
                  type="button"
                  variant="primary"
                >
                  <Activity aria-hidden="true" size={16} />
                  Run probe
                </Button>
              ) : (
                <p className="safe-note">Provider mutation is platform-admin only.</p>
              )}
            </article>
          );
        })}
      </div>
      {probeResult?.probe ? (
        <section className="mutation-result accepted">
          <p className="eyebrow">Probe result</p>
          <h2>{probeResult.probe.status}</h2>
          <p>{probeResult.probe.summary}</p>
          <small>{probeResult.probe.audit_reference_id}</small>
        </section>
      ) : null}
    </section>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (status === "ready") {
    return "success";
  }
  if (status === "blocked" || status === "denied" || status === "unavailable") {
    return "critical";
  }
  if (status === "degraded" || status === "warning") {
    return "warning";
  }
  return "info";
}
