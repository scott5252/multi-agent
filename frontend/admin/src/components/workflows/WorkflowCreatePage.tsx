import type { WorkflowCreateEnvelope } from "../../api/generated/reactAdminApi";

interface WorkflowCreatePageProps {
  createState: WorkflowCreateEnvelope;
}

export function WorkflowCreatePage({ createState }: WorkflowCreatePageProps) {
  return (
    <section className="workflow-create-panel" aria-labelledby="workflow-create-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Create</p>
          <h2 id="workflow-create-title">{createState.title}</h2>
        </div>
        <a className="ui-button secondary" href={createState.create_action.href}>
          {createState.create_action.label}
        </a>
      </div>
      <p>{createState.summary}</p>
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
