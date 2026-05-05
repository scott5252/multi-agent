import { Download, RefreshCw } from "lucide-react";

import type { UsageReactDashboard } from "../../api/generated/reactAdminApi";

interface UsageHeaderProps {
  dashboard: UsageReactDashboard;
  onExport: () => void;
  onRefresh: () => void;
}

export function UsageHeader({ dashboard, onExport, onRefresh }: UsageHeaderProps) {
  return (
    <section className="patterns-hero usage-hero">
      <div>
        <p className="eyebrow">Usage</p>
        <h2>{dashboard.title}</h2>
        <p>{dashboard.description}</p>
        <small>
          {dashboard.scope.label} · {dashboard.filters.selected_range.label} · Updated{" "}
          {new Date(dashboard.updated_at).toLocaleString()}
        </small>
      </div>
      <div className="usage-hero-actions">
        <button className="icon-button" onClick={onRefresh} title="Refresh usage dashboard" type="button">
          <RefreshCw aria-hidden="true" size={18} />
        </button>
        <button className="primary-button" onClick={onExport} type="button">
          <Download aria-hidden="true" size={18} />
          Export CSV
        </button>
      </div>
    </section>
  );
}
