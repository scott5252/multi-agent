import type { PolicyHistoryRecord } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

export function PolicyHistoryPanel({
  history,
}: {
  history: PolicyHistoryRecord[];
}) {
  return (
    <section className="governance-panel" aria-labelledby="history-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Policy history</p>
          <h2 id="history-title">Safe changes</h2>
        </div>
      </div>
      <table className="admin-table">
        <thead>
          <tr>
            <th>Domain</th>
            <th>Actor</th>
            <th>Status</th>
            <th>Summary</th>
          </tr>
        </thead>
        <tbody>
          {history.map((record) => (
            <tr key={record.history_id}>
              <td>{record.domain}</td>
              <td>{record.actor_label}</td>
              <td>
                <Badge tone={record.outcome === "ready" ? "success" : "warning"}>
                  {record.outcome}
                </Badge>
              </td>
              <td>{record.safe_diff_summary}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
