import type { AccessHistoryRecord } from "../../api/generated/reactAdminApi";

export function AccessHistoryPanel({
  records,
}: {
  records: AccessHistoryRecord[];
}) {
  return (
    <section className="governance-panel membership-panel" id="history">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Access history</p>
          <h2>Recent decisions</h2>
        </div>
      </div>
      <div className="history-list">
        {records.map((record) => (
          <article className="timeline-row" key={record.access_history_id}>
            <span className={`status-dot ${record.decision}`} />
            <div>
              <strong>{record.requested_action}</strong>
              <p>{record.principal_label} in {record.tenant_label}</p>
              <p>{record.role_source_summary}</p>
              <small>{record.reason_category} · {record.trace_id}</small>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
