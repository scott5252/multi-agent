import type { MigrationSweepSummary } from "../../api/generated/reactAdminApi";
import { StatusBadge } from "./RouteDecisionBadges";

export function MigrationSweepPanel({
  redaction,
  tenantIsolation,
}: {
  redaction: MigrationSweepSummary;
  tenantIsolation: MigrationSweepSummary;
}) {
  return (
    <section className="migration-panel" aria-labelledby="migration-sweeps-title">
      <div className="migration-panel-heading">
        <div>
          <p className="eyebrow">Sweeps</p>
          <h2 id="migration-sweeps-title">Redaction and tenant isolation</h2>
        </div>
      </div>
      <div className="migration-sweep-grid">
        <Sweep summary={redaction} title="Redaction sweep" />
        <Sweep summary={tenantIsolation} title="Tenant isolation sweep" />
      </div>
    </section>
  );
}

function Sweep({
  summary,
  title,
}: {
  summary: MigrationSweepSummary;
  title: string;
}) {
  return (
    <article className="migration-sweep">
      <div className="migration-state-top">
        <h3>{title}</h3>
        <StatusBadge status={summary.status} label={summary.status} />
      </div>
      <dl>
        <div>
          <dt>Artifacts</dt>
          <dd>{summary.checked_artifacts}</dd>
        </div>
        <div>
          <dt>Unsafe matches</dt>
          <dd>{summary.unsafe_match_count}</dd>
        </div>
      </dl>
      <p>{summary.safe_summary}</p>
      <code>{summary.evidence_reference}</code>
    </article>
  );
}
