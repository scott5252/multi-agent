import type { WorkflowJsonInspector as WorkflowJsonInspectorData } from "../../api/generated/reactAdminApi";

export function WorkflowJsonInspector({
  inspector,
}: {
  inspector: WorkflowJsonInspectorData;
}) {
  return (
    <section className="workflow-json-panel" aria-labelledby="json-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">JSON</p>
          <h2 id="json-title">Read-only preview</h2>
        </div>
      </div>
      <p>{inspector.summary}</p>
      <p className="table-footer">{inspector.redaction_summary}</p>
      <dl className="json-preview-list">
        {Object.entries(inspector.safe_document_preview).map(([key, value]) => (
          <div key={key}>
            <dt>{key}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
      {inspector.artifact_reference_id ? (
        <small>{inspector.artifact_reference_id}</small>
      ) : null}
    </section>
  );
}
