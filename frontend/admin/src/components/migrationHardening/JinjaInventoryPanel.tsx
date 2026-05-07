import type {
  JinjaInventoryClassification,
  JinjaInventoryDashboard,
  JinjaInventoryItem,
} from "../../api/generated/reactAdminApi";

const classificationLabels: Record<JinjaInventoryClassification, string> = {
  blocked_with_reason: "Blocked",
  non_jinja_compatibility_needed: "Compatibility needed",
  react_parity_missing: "Parity missing",
  react_parity_proven: "Parity proven",
  redirectable: "Redirectable",
  safe_to_delete: "Safe to delete",
};

export function JinjaInventoryPanel({
  inventory,
}: {
  inventory: JinjaInventoryDashboard;
}) {
  const summary = inventory.summary;
  return (
    <section
      className="migration-panel jinja-inventory"
      aria-labelledby="jinja-inventory-title"
    >
      <div className="migration-panel-heading">
        <div>
          <p className="eyebrow">Decommission inventory</p>
          <h2 id="jinja-inventory-title">React-only readiness</h2>
        </div>
        <span className="migration-count">{summary.total_items} items</span>
      </div>

      <dl className="migration-summary-grid compact" aria-label="Decommission inventory counts">
        <Metric label="Templates removed" value={summary.template_count} />
        <Metric label="Routes" value={summary.route_count} />
        <Metric label="Assets removed" value={summary.static_asset_count} />
        <Metric label="Direct links" value={summary.direct_link_count} />
        <Metric label="Blocked" value={summary.blocked_count} />
        <Metric label="Safe" value={summary.safe_to_delete_count} />
      </dl>

      <div className="jinja-inventory-groups">
        {inventory.groups.length ? (
          inventory.groups.map((group) => (
            <article className="jinja-inventory-group" key={group.group_id}>
              <header>
                <div>
                  <h3>{group.label}</h3>
                  <small>Removal spec {group.planned_removal_spec}</small>
                </div>
                <small>
                  {group.blocked_count} blocked / {group.safe_to_delete_count} safe
                </small>
              </header>
              <div className="migration-table-wrap">
                <table className="admin-table migration-table jinja-table">
                  <thead>
                    <tr>
                      <th scope="col">Surface</th>
                      <th scope="col">Replacement</th>
                      <th scope="col">Readiness</th>
                      <th scope="col">Evidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {group.items.slice(0, 10).map((item) => (
                      <InventoryRow item={item} key={item.item_id} />
                    ))}
                  </tbody>
                </table>
              </div>
            </article>
          ))
        ) : (
          <p className="migration-empty">No server-rendered inventory rows remain for this scope.</p>
        )}
      </div>

      <ul className="migration-evidence-list">
        {inventory.evidence.map((evidence) => (
          <li key={evidence.evidence_id}>
            {evidence.evidence_type.replaceAll("_", " ")}: <code>{evidence.evidence_id}</code>
            {evidence.reference ? <small>{evidence.reference}</small> : null}
          </li>
        ))}
      </ul>
    </section>
  );
}

function InventoryRow({ item }: { item: JinjaInventoryItem }) {
  return (
    <tr>
      <td>
        <strong>{item.label}</strong>
        <small>{item.item_type.replaceAll("_", " ")}</small>
        {item.source_path ? <small>{item.source_path}</small> : null}
      </td>
      <td>
        <code>{item.react_path ?? item.legacy_route ?? "Compatibility response"}</code>
        <small>{item.redirect_preserves.join(", ") || item.owner_category}</small>
      </td>
      <td>
        <span className={`jinja-classification ${item.classification}`}>
          {classificationLabels[item.classification]}
        </span>
        <small>{item.notes}</small>
      </td>
      <td>
        <ul className="migration-evidence-list">
          {item.evidence_refs.map((evidence) => (
            <li key={evidence}>{evidence}</li>
          ))}
          {item.blocker_refs.map((blocker) => (
            <li key={blocker}>{blocker}</li>
          ))}
        </ul>
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
