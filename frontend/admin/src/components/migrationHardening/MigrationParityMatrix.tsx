import type { MigrationRouteGroup } from "../../api/generated/reactAdminApi";
import { RouteDecisionBadge, StatusBadge } from "./RouteDecisionBadges";

export function MigrationParityMatrix({
  groups,
}: {
  groups: MigrationRouteGroup[];
}) {
  return (
    <section className="migration-panel migration-parity" aria-labelledby="migration-parity-title">
      <div className="migration-panel-heading">
        <div>
          <p className="eyebrow">Route parity</p>
          <h2 id="migration-parity-title">React and legacy destinations</h2>
        </div>
      </div>
      <div className="migration-route-groups">
        {groups.map((group) => (
          <article className="migration-route-group" key={group.group_id}>
            <header>
              <div>
                <h3>{group.label}</h3>
                <p>Specs {group.spec_refs.join(", ")}</p>
              </div>
              <StatusBadge status={group.group_status} label={group.group_status} />
            </header>
            {group.entries.length ? (
              <div className="migration-table-wrap">
                <table className="admin-table migration-table">
                  <thead>
                    <tr>
                      <th scope="col">Area</th>
                      <th scope="col">React path</th>
                      <th scope="col">Legacy path</th>
                      <th scope="col">Decision</th>
                      <th scope="col">Evidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {group.entries.map((entry) => (
                      <tr key={entry.entry_id}>
                        <td>
                          <strong>{entry.admin_area}</strong>
                          <small>{entry.scope_requirement.replaceAll("_", " ")}</small>
                          <small>{entry.auth_modes.join(" + ")}</small>
                        </td>
                        <td>
                          <code>{entry.react_route ?? "Retained fallback"}</code>
                          <small>{entry.redirect_preserves.join(", ")}</small>
                        </td>
                        <td>
                          <code>{entry.legacy_route ?? "None"}</code>
                          {entry.fallback_notice ? <small>{entry.fallback_notice}</small> : null}
                        </td>
                        <td>
                          <RouteDecisionBadge decision={entry.decision} />
                          <small>
                            {entry.retirement_allowed
                              ? "Retirement evidence complete"
                              : "Keep fallback reviewed"}
                          </small>
                        </td>
                        <td>
                          <ul className="migration-evidence-list">
                            {entry.parity_evidence.map((evidence) => (
                              <li key={evidence}>{evidence}</li>
                            ))}
                            <li>{entry.audit_reference}</li>
                          </ul>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="migration-empty">No route rows are visible for this scope.</p>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
