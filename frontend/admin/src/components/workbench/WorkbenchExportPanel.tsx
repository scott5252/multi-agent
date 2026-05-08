import { Download } from "lucide-react";

import type { WorkbenchExportSnapshot } from "../../api/generated/reactAdminApi";
import { Button } from "../primitives";

export function WorkbenchExportPanel({
  exportSnapshot,
  onExport,
}: {
  exportSnapshot: WorkbenchExportSnapshot;
  onExport: () => void;
}) {
  return (
    <section className="workbench-panel export-panel" aria-label="Workbench export">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Export</p>
          <h2>Safe evidence package</h2>
        </div>
        <Button onClick={onExport} type="button" variant="secondary">
          <Download aria-hidden="true" size={16} />
          Export evidence
        </Button>
      </div>
      <p>{exportSnapshot.summary}</p>
      <dl className="export-facts">
        <div>
          <dt>Artifact</dt>
          <dd>{exportSnapshot.artifact_reference_id ?? exportSnapshot.status}</dd>
        </div>
        <div>
          <dt>Rows</dt>
          <dd>{exportSnapshot.row_count}</dd>
        </div>
        <div>
          <dt>Redaction</dt>
          <dd>{exportSnapshot.redaction_summary}</dd>
        </div>
      </dl>
    </section>
  );
}
