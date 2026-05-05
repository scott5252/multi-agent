import type { UsageReactDashboard, UsageReactGroupBy } from "../../api/generated/reactAdminApi";
import { UsageGroupSelector } from "./UsageGroupSelector";

interface UsageFilterBarProps {
  dashboard: UsageReactDashboard;
  onGroupChange: (value: UsageReactGroupBy) => void;
}

export function UsageFilterBar({ dashboard, onGroupChange }: UsageFilterBarProps) {
  const selectedTenant =
    dashboard.filters.tenant_options.find((option) => option.selected)?.label ??
    dashboard.scope.label;
  const selectedProvider =
    dashboard.filters.provider_options.find((option) => option.selected)?.label ?? "All";
  const selectedModel =
    dashboard.filters.model_options.find((option) => option.selected)?.label ?? "All";

  return (
    <section className="usage-filter-bar" aria-label="Usage filters">
      <UsageGroupSelector
        onChange={onGroupChange}
        options={dashboard.filters.group_by_options}
        value={dashboard.filters.selected_group_by}
      />
      <div className="usage-filter-chip">
        <span>Tenant</span>
        <strong>{selectedTenant}</strong>
      </div>
      <div className="usage-filter-chip">
        <span>Provider</span>
        <strong>{selectedProvider}</strong>
      </div>
      <div className="usage-filter-chip">
        <span>Model</span>
        <strong>{selectedModel}</strong>
      </div>
    </section>
  );
}
