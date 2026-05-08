import type {
  LiveDataInventoryDashboard,
  LiveDataInventoryFinding,
  LiveDataInventoryStatus,
  LiveDataRouteTarget,
} from "../../api/generated/reactAdminApi";

const statusLabels: Record<LiveDataInventoryStatus, string> = {
  allowed_computed_metadata: "Computed",
  mapped_legacy: "Mapped",
  new_regression: "Blocking",
  test_only: "Test only",
};

export function LiveDataInventoryPanel({
  inventory,
}: {
  inventory: LiveDataInventoryDashboard | null;
}) {
  if (!inventory) {
    return (
      <section
        className="migration-panel live-data-inventory"
        aria-labelledby="live-data-inventory-title"
      >
        <div className="migration-panel-heading">
          <div>
            <p className="eyebrow">Live-only gate</p>
            <h2 id="live-data-inventory-title">Live-data guardrails</h2>
          </div>
          <span className="migration-count">Unavailable</span>
        </div>
        <p className="migration-empty">Live-data inventory evidence is unavailable for this scope.</p>
      </section>
    );
  }

  const summary = inventory.summary;
  const visibleFindings = inventory.findings.slice(0, 8);
  const visibleTargets = inventory.route_targets.slice(0, 6);

  return (
    <section
      className="migration-panel live-data-inventory"
      aria-labelledby="live-data-inventory-title"
    >
      <div className="migration-panel-heading">
        <div>
          <p className="eyebrow">Live-only gate</p>
          <h2 id="live-data-inventory-title">Live-data guardrails</h2>
        </div>
        <span className={`migration-count live-ci-status ${summary.ci_status}`}>
          {summary.ci_status}
        </span>
      </div>

      <dl className="migration-summary-grid compact" aria-label="Live data inventory counts">
        <Metric label="Findings" value={summary.total_findings} />
        <Metric label="Mapped/deferred" value={summary.mapped_legacy_findings} />
        <Metric label="Blocking" value={summary.blocking_findings} />
        <Metric label="Computed" value={summary.allowed_computed_metadata} />
        <Metric label="Routes" value={summary.route_targets} />
        <Metric label="Empty scans" value={summary.empty_state_scans} />
        <Metric label="Seeded scans" value={summary.seeded_state_scans} />
      </dl>

      <p className="migration-next-step">{summary.next_step}</p>

      {visibleFindings.length ? (
        <div className="migration-table-wrap">
          <table className="admin-table migration-table live-data-table">
            <thead>
              <tr>
                <th scope="col">Gate finding</th>
                <th scope="col">Replacement</th>
                <th scope="col">Marker</th>
                <th scope="col">Evidence</th>
              </tr>
            </thead>
            <tbody>
              {visibleFindings.map((finding) => (
                <FindingRow finding={finding} key={finding.finding_id} />
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="migration-empty">No production live-data gate findings are reachable for this scope.</p>
      )}

      <div className="migration-two-column live-data-supporting">
        <article className="migration-checklist">
          <h3>Route targets</h3>
          <ul className="migration-evidence-list">
            {visibleTargets.map((target) => (
              <li key={target.target_id}>
                <code>
                  {target.method} {target.path}
                </code>
                <small>{routeTargetSummary(target)}</small>
              </li>
            ))}
          </ul>
        </article>
        <article className="migration-checklist">
          <h3>Evidence</h3>
          <ul className="migration-evidence-list">
            {inventory.evidence.map((evidence) => (
              <li key={evidence.evidence_id}>
                {formatEnum(evidence.evidence_type)}: <code>{evidence.evidence_id}</code>
                <small>{evidence.reference}</small>
              </li>
            ))}
          </ul>
        </article>
      </div>
    </section>
  );
}

function FindingRow({ finding }: { finding: LiveDataInventoryFinding }) {
  return (
    <tr>
      <td>
        <strong>{finding.source_path}</strong>
        {finding.route_path ? <small>{finding.route_path}</small> : null}
        <small>{formatEnum(finding.reachability)}</small>
      </td>
      <td>
        <code>{finding.replacement_spec ?? finding.owner_spec ?? "computed metadata"}</code>
        <small>{finding.durable_source}</small>
      </td>
      <td>
        <span className={`jinja-classification live-status ${finding.status}`}>
          {statusLabels[finding.status]}
        </span>
        <small>{formatEnum(finding.marker_kind)}</small>
      </td>
      <td>
        <small>{finding.safe_excerpt}</small>
      </td>
    </tr>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

function formatEnum(value: string): string {
  return value.replaceAll("_", " ");
}

function routeTargetSummary(target: LiveDataRouteTarget): string {
  const states = [
    target.empty_state_required ? "empty" : null,
    target.seeded_state_required ? "seeded" : null,
    target.computed_metadata_only ? "computed" : null,
  ].filter(Boolean);
  return `${target.principal}; ${states.join(", ") || "mutation"} state`;
}
