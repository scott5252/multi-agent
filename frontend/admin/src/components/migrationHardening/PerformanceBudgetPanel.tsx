import type { MigrationPerformanceBudget } from "../../api/generated/reactAdminApi";
import { StatusBadge } from "./RouteDecisionBadges";

export function PerformanceBudgetPanel({
  budget,
}: {
  budget: MigrationPerformanceBudget;
}) {
  return (
    <section className="migration-panel" aria-labelledby="migration-performance-title">
      <div className="migration-panel-heading">
        <div>
          <p className="eyebrow">Performance</p>
          <h2 id="migration-performance-title">Budget evidence</h2>
        </div>
        <StatusBadge status={budget.status} label={budget.status} />
      </div>
      <dl className="migration-definition-grid compact">
        <div>
          <dt>Bootstrap limit</dt>
          <dd>{budget.route_bootstrap_ms_limit} ms</dd>
        </div>
        <div>
          <dt>Interactive limit</dt>
          <dd>{budget.primary_interactive_ms_limit} ms</dd>
        </div>
        <div>
          <dt>Compressed asset limit</dt>
          <dd>{budget.compressed_asset_kb_limit} KB</dd>
        </div>
      </dl>
      <div className="migration-budget-rows">
        {budget.measurements.map((measurement) => (
          <div className="migration-budget-row" key={measurement.measurement_id}>
            <div>
              <strong>{measurement.label}</strong>
              <small>{measurement.evidence_reference}</small>
            </div>
            <span>
              {measurement.value} {measurement.unit} / {measurement.limit} {measurement.unit}
            </span>
            <StatusBadge status={measurement.status} label={measurement.status} />
          </div>
        ))}
      </div>
      {budget.mitigation ? <p className="migration-muted">{budget.mitigation}</p> : null}
    </section>
  );
}
