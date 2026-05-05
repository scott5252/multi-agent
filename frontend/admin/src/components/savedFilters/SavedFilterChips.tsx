import { Filter } from "lucide-react";

import type { ReactAdminSavedFilterChip } from "../../api/generated/reactAdminApi";

export function SavedFilterChips({
  filters,
}: {
  filters: ReactAdminSavedFilterChip[];
}) {
  if (filters.length === 0) {
    return (
      <section className="saved-filters empty" aria-label="Saved filters">
        <Filter aria-hidden="true" size={18} />
        <div>
          <h2>Saved filters</h2>
          <p>Saved filters from existing admin pages will appear here when available.</p>
        </div>
      </section>
    );
  }
  return (
    <section className="saved-filters" aria-label="Saved filters">
      <h2>Saved filters</h2>
      <div className="chip-row">
        {filters.map((filter) => (
          <a className="filter-chip" href={filter.href} key={filter.filter_id}>
            <span>{filter.label}</span>
            <small>{filter.admin_area}</small>
          </a>
        ))}
      </div>
    </section>
  );
}
