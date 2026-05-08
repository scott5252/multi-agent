import type {
  BuilderMutationResult,
  WorkflowCreateEnvelope,
} from "../../api/generated/reactAdminApi";

interface WorkflowCreatePageProps {
  createState: WorkflowCreateEnvelope;
  creating?: boolean;
  mutationResult?: BuilderMutationResult | null;
  onCreate?: () => void;
}

export function WorkflowCreatePage({
  createState,
  creating = false,
  mutationResult = null,
  onCreate,
}: WorkflowCreatePageProps) {
  return (
    <section className="workflow-create-panel" aria-labelledby="workflow-create-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Create</p>
          <h2 id="workflow-create-title">{createState.title}</h2>
        </div>
        {onCreate ? (
          <button
            className="ui-button secondary"
            disabled={creating || !createState.create_action.enabled}
            onClick={onCreate}
            type="button"
          >
            {creating ? "Creating draft" : createState.create_action.label}
          </button>
        ) : (
          <a className="ui-button secondary" href={createState.create_action.href}>
            {createState.create_action.label}
          </a>
        )}
      </div>
      <p>{createState.summary}</p>
      {mutationResult ? (
        <div className={`mutation-result ${mutationResult.status}`}>
          <strong>{mutationResult.toast?.title ?? "Workflow action"}</strong>
          <p>{mutationResult.summary}</p>
          {mutationResult.audit_reference_id ? (
            <small>{mutationResult.audit_reference_id}</small>
          ) : null}
          {mutationResult.next_action?.href ? (
            <a className="primary-link" href={mutationResult.next_action.href}>
              {mutationResult.next_action.label}
            </a>
          ) : null}
        </div>
      ) : null}
      <div className="workflow-template-list">
        {createState.templates.map((template) => (
          <article className="workflow-template-card" key={template.template_id}>
            <strong>{template.label}</strong>
            <p>{template.summary}</p>
            <small>{template.workflow_kind}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
