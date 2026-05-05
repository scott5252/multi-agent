import type { ChannelTelegramBriefingDashboard } from "../../api/generated/reactAdminApi";

export function ChannelReadinessHeader({
  dashboard,
  onRefresh,
}: {
  dashboard: ChannelTelegramBriefingDashboard;
  onRefresh: () => void;
}) {
  const readyCount = dashboard.readiness.filter((item) => item.status === "ready").length;
  return (
    <header className="channel-header">
      <div>
        <p className="eyebrow">Active scope: {dashboard.scope.label}</p>
        <h1>{dashboard.title}</h1>
        <p>{dashboard.description}</p>
      </div>
      <div className="channel-header__meta">
        <strong>
          {readyCount}/{dashboard.readiness.length} ready
        </strong>
        <span>Updated {new Date(dashboard.updated_at).toLocaleString()}</span>
        <button type="button" onClick={onRefresh}>
          Refresh
        </button>
      </div>
    </header>
  );
}
