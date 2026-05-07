import type { WorkflowRegistryEnvelope } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface WorkflowRegistryPageProps {
  registry: WorkflowRegistryEnvelope;
}

export function WorkflowRegistryPage({ registry }: WorkflowRegistryPageProps) {
  return (
    <section className="workflow-registry-panel" aria-labelledby="workflow-registry-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Registry</p>
          <h2 id="workflow-registry-title">{registry.title}</h2>
        </div>
        {registry.create_action ? (
          <a className="ui-button primary" href={registry.create_action.href}>
            {registry.create_action.label}
          </a>
        ) : null}
      </div>
      <p>{registry.summary}</p>
      <div className="workflow-registry-list">
        {registry.items.map((item) => (
          <article className="workflow-registry-item" key={item.href}>
            <div className="card-heading">
              <strong>{item.name}</strong>
              <Badge tone={toneFor(item.status)}>{item.status}</Badge>
            </div>
            <p>{item.required_evidence_summary}</p>
            <small>
              {item.workflow_kind} / {item.owner_label}
              {item.tenant_label ? ` / ${item.tenant_label}` : ""}
            </small>
            <div className="action-row">
              {item.actions.map((action) => (
                <a
                  className={`ui-button ${
                    action.variant === "primary" ? "primary" : "secondary"
                  }`}
                  href={action.href}
                  key={action.action_id}
                >
                  {action.label}
                </a>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (status === "ready" || status === "published") {
    return "success";
  }
  if (status === "blocked" || status === "critical") {
    return "critical";
  }
  if (status === "warning" || status === "stale") {
    return "warning";
  }
  return "info";
}
