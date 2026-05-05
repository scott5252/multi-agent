import { Download } from "lucide-react";

import type { UsageReactExportSummary } from "../../api/generated/reactAdminApi";

interface UsageExportPanelProps {
  exports: UsageReactExportSummary[];
  exportResult: UsageReactExportSummary | null;
  onExport: () => void;
}

export function UsageExportPanel({
  exports,
  exportResult,
  onExport,
}: UsageExportPanelProps) {
  const current = exportResult ?? exports[0] ?? null;

  return (
    <section className="usage-panel usage-export-panel" aria-label="Usage export">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Export</p>
          <h2>Audited CSV evidence</h2>
        </div>
        <button className="primary-button" onClick={onExport} type="button">
          <Download aria-hidden="true" size={18} />
          Create export
        </button>
      </div>
      {current ? (
        <dl className="usage-export-summary">
          <dt>Status</dt>
          <dd>{current.status}</dd>
          <dt>Rows</dt>
          <dd>{current.row_count}</dd>
          <dt>Artifact</dt>
          <dd>{current.artifact_reference ?? current.next_step}</dd>
          <dt>Audit</dt>
          <dd>{current.audit_reference}</dd>
          <dt>Checksum</dt>
          <dd>{current.checksum_prefix ?? "Pending"}</dd>
        </dl>
      ) : (
        <p>No export evidence has been requested for this filter snapshot.</p>
      )}
    </section>
  );
}
