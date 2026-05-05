import type { WorkflowRevisionSummary } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

export function WorkflowRevisionPanel({
  revisions,
}: {
  revisions: WorkflowRevisionSummary[];
}) {
  return (
    <section className="workflow-revision-panel" aria-labelledby="revision-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Revisions</p>
          <h2 id="revision-title">Immutable draft history</h2>
        </div>
      </div>
      <ol className="revision-list">
        {revisions.map((revision) => (
          <li key={revision.revision}>
            <div className="card-heading">
              <strong>{revision.created_at_label}</strong>
              {revision.current ? <Badge tone="success">current</Badge> : null}
            </div>
            <p>{revision.summary}</p>
            <small>
              {revision.actor_label} / {revision.change_category}
            </small>
            <small>{revision.audit_reference_id}</small>
          </li>
        ))}
      </ol>
    </section>
  );
}
