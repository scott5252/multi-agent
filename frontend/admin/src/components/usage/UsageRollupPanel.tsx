import type {
  UsageReactGroupBy,
  UsageReactRollupSection,
} from "../../api/generated/reactAdminApi";
import { UsageAttributionBadges } from "./UsageAttributionBadges";

interface UsageRollupPanelProps {
  rollup: UsageReactRollupSection;
  onDrilldown: (href: string) => void;
}

export function UsageRollupPanel({ rollup, onDrilldown }: UsageRollupPanelProps) {
  return (
    <section className="usage-panel usage-rollup-panel" aria-label="Usage rollups">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Rollups</p>
          <h2>{groupLabel(rollup.group_by)}</h2>
        </div>
        <small>
          {rollup.rows.length} of {rollup.total_rows} rows
        </small>
      </div>
      <table className="admin-table">
        <thead>
          <tr>
            <th>Group</th>
            <th>Events</th>
            <th>Tokens</th>
            <th>Cost</th>
            <th>Latency</th>
            <th>Status</th>
            <th>Attribution</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          {rollup.rows.map((row) => (
            <tr key={row.row_id}>
              <td>
                <strong>{row.safe_label}</strong>
                <small>{row.safe_summary}</small>
              </td>
              <td>{row.event_count}</td>
              <td>{row.total_tokens.toLocaleString()}</td>
              <td>{row.estimated_cost_display}</td>
              <td>{row.average_latency_ms.toLocaleString()} ms</td>
              <td>
                <span className={`usage-status usage-status-${row.confidence_status}`}>
                  {row.confidence_status}
                </span>
              </td>
              <td>
                <UsageAttributionBadges row={row} />
              </td>
              <td>
                <button type="button" onClick={() => onDrilldown(row.drilldown_href)}>
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function groupLabel(group: UsageReactGroupBy): string {
  return group
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
