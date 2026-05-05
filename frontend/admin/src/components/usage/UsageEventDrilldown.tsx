import type { UsageReactEventDrilldown as UsageReactEventDrilldownType } from "../../api/generated/reactAdminApi";
import { UsageAttributionBadges } from "./UsageAttributionBadges";

export function UsageEventDrilldown({
  drilldown,
}: {
  drilldown: UsageReactEventDrilldownType;
}) {
  return (
    <section className="usage-panel usage-drilldown-panel" aria-label="Usage event drilldown">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Drilldown</p>
          <h2>Safe events</h2>
        </div>
        <small>
          {drilldown.rows.length} of {drilldown.total_rows} rows
          {drilldown.truncated ? " · truncated" : ""}
        </small>
      </div>
      <table className="admin-table">
        <thead>
          <tr>
            <th>When</th>
            <th>Tenant</th>
            <th>Provider</th>
            <th>Workflow</th>
            <th>Tokens</th>
            <th>Cost</th>
            <th>Latency</th>
            <th>Evidence</th>
          </tr>
        </thead>
        <tbody>
          {drilldown.rows.map((event) => (
            <tr key={event.event_id}>
              <td>{new Date(event.recorded_at).toLocaleString()}</td>
              <td>{event.tenant_label}</td>
              <td>
                <strong>{event.provider_label}</strong>
                <small>{event.model_label}</small>
              </td>
              <td>
                <strong>{event.workflow_label}</strong>
                <small>{event.agent_label}</small>
              </td>
              <td>{event.total_tokens.toLocaleString()}</td>
              <td>{event.estimated_cost_display}</td>
              <td>{event.latency_ms.toLocaleString()} ms</td>
              <td>
                <UsageAttributionBadges event={event} />
                <small>{event.audit_reference}</small>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
