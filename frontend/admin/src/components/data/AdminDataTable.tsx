import { Download } from "lucide-react";

import type {
  ExportSnapshot,
  FilterProfile,
  PaginationState,
  SampleRecord,
  SortingState,
} from "../../api/generated/reactAdminApi";
import { Badge, Button } from "../primitives";

export function AdminDataTable({
  exportSnapshot,
  filters,
  onExport,
  pagination,
  records,
  sorting,
}: {
  exportSnapshot: ExportSnapshot;
  filters: FilterProfile;
  onExport: () => void;
  pagination: PaginationState;
  records: SampleRecord[];
  sorting: SortingState;
}) {
  return (
    <section className="data-patterns" aria-label="Data patterns">
      <header className="section-heading">
        <div>
          <p className="eyebrow">Tables</p>
          <h2>Sample records</h2>
        </div>
        <Button onClick={onExport} type="button" variant="secondary">
          <Download aria-hidden="true" size={16} />
          Export preview
        </Button>
      </header>
      <div className="filter-bar" aria-label="Allowed filters">
        {filters.criteria.map((criterion) => (
          <div className="filter-options" key={criterion.key}>
            <strong>{criterion.label}</strong>
            {criterion.options.map((option) => (
              <a href={`?${criterion.key}=${option.value}`} key={option.value}>
                {option.label}
              </a>
            ))}
          </div>
        ))}
        {filters.active_chips.map((chip) => (
          <a className="filter-chip" href={chip.href} key={chip.key}>
            <span>{chip.label}</span>
            <small>Clear</small>
          </a>
        ))}
      </div>
      <table className="admin-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Scope</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          {records.map((record) => (
            <tr key={record.record_id}>
              <td>{record.name}</td>
              <td>
                <Badge tone={record.status === "ready" ? "success" : "warning"}>
                  {record.status.replace("_", " ")}
                </Badge>
              </td>
              <td>{record.owner_scope}</td>
              <td>{record.updated_label}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <footer className="table-footer">
        <span>
          Showing {records.length} of {pagination.total_items ?? records.length}
        </span>
        <span>Sorted by {sorting.active.label}</span>
      </footer>
      <section className="export-status" aria-label="Export status">
        <strong>Export status</strong>
        <p>{exportSnapshot.summary}</p>
        <small>{exportSnapshot.artifact_reference_id}</small>
      </section>
    </section>
  );
}
