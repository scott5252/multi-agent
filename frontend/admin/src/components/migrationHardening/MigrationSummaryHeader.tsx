import { RefreshCw } from "lucide-react";

import type { AdminMigrationHardeningDashboard } from "../../api/generated/reactAdminApi";
import { Button } from "../primitives";
import { StatusBadge } from "./RouteDecisionBadges";

export function MigrationSummaryHeader({
  dashboard,
  onRefresh,
}: {
  dashboard: AdminMigrationHardeningDashboard;
  onRefresh: () => void;
}) {
  const summary = dashboard.summary;
  return (
    <section className="migration-hero" aria-labelledby="migration-title">
      <div>
        <p className="eyebrow">{dashboard.scope.label}</p>
        <h1 id="migration-title">{dashboard.title}</h1>
        <p>{dashboard.description}</p>
      </div>
      <div className="migration-hero-side">
        <StatusBadge status={summary.overall_status} label={summary.overall_status} />
        <Button className="icon-text-button" onClick={onRefresh} type="button">
          <RefreshCw aria-hidden="true" size={16} />
          Refresh
        </Button>
        <small>Updated {formatDateTime(dashboard.updated_at)}</small>
      </div>
      <dl className="migration-summary-grid" aria-label="Migration route counts">
        <Metric label="Destinations" value={summary.total_destinations} />
        <Metric label="React primary" value={summary.react_primary_count} />
        <Metric label="Redirects" value={summary.redirect_count} />
        <Metric label="Fallbacks" value={summary.retained_fallback_count} />
        <Metric label="Retirement ready" value={summary.retirement_candidate_count} />
        <Metric label="Blocked" value={summary.blocked_count} />
      </dl>
      <p className="migration-next-step">{summary.next_step}</p>
    </section>
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

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
