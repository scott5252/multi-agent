import type { SafePromptPreview } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

export function SafePromptPreviewPanel({
  preview,
}: {
  preview: SafePromptPreview;
}) {
  return (
    <section className="safe-preview-panel" aria-label="Safe prompt preview">
      <div className="card-heading">
        <strong>{preview.fixture_label}</strong>
        <Badge tone={preview.status === "ready" ? "success" : "warning"}>
          {preview.status}
        </Badge>
      </div>
      <p>{preview.safe_output}</p>
      <ul>
        {preview.redaction_findings.map((finding) => (
          <li key={finding}>{finding}</li>
        ))}
      </ul>
      <small>{preview.audit_reference_id}</small>
    </section>
  );
}
