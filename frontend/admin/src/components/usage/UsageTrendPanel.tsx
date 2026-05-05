import type { UsageReactTrendPoint } from "../../api/generated/reactAdminApi";

export function UsageTrendPanel({ trend }: { trend: UsageReactTrendPoint[] }) {
  const maxTokens = Math.max(
    1,
    ...trend.map((point) => point.confirmed_tokens + point.estimated_tokens),
  );

  return (
    <section className="usage-panel usage-trend-panel" aria-label="Usage trend">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Trend</p>
          <h2>Daily usage</h2>
        </div>
      </div>
      <div className="usage-trend-chart" role="img" aria-label="Daily token trend">
        {trend.map((point) => {
          const confirmed = Math.max(3, (point.confirmed_tokens / maxTokens) * 100);
          const estimated = Math.max(3, (point.estimated_tokens / maxTokens) * 100);
          return (
            <div className="usage-trend-bar" key={point.bucket_start}>
              <div className="usage-trend-stack">
                <span
                  className="usage-trend-confirmed"
                  style={{ height: `${confirmed}%` }}
                />
                <span
                  className="usage-trend-estimated"
                  style={{ height: `${estimated}%` }}
                />
              </div>
              <small>{point.label}</small>
            </div>
          );
        })}
      </div>
      <table className="admin-table usage-trend-table">
        <thead>
          <tr>
            <th>Day</th>
            <th>Confirmed</th>
            <th>Estimated</th>
            <th>Cost</th>
            <th>Latency</th>
          </tr>
        </thead>
        <tbody>
          {trend.map((point) => (
            <tr key={`row-${point.bucket_start}`}>
              <td>{point.label}</td>
              <td>{point.confirmed_tokens.toLocaleString()}</td>
              <td>{point.estimated_tokens.toLocaleString()}</td>
              <td>{point.estimated_cost_display}</td>
              <td>{point.average_latency_ms.toLocaleString()} ms</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
