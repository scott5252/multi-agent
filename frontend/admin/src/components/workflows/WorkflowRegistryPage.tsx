import type { WorkflowRegistryEnvelope } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";
import { CommonState } from "../states/CommonState";

interface WorkflowRegistryPageProps {
  registry: WorkflowRegistryEnvelope;
}

export function WorkflowRegistryPage({ registry }: WorkflowRegistryPageProps) {
  const emptyAction = registry.create_action
    ? {
        action_id: registry.create_action.action_id,
        action_metadata: registry.create_action.action_metadata ?? null,
        disabled_reason: registry.create_action.disabled_reason ?? null,
        href: registry.create_action.href,
        label: registry.create_action.label,
        method: "get" as const,
        variant: registry.create_action.variant,
      }
    : null;

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
      <dl className="workflow-draft-facts">
        <div>
          <dt>Sort</dt>
          <dd>{registry.sorting?.active.label ?? registry.filters.sort ?? "Latest"}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{registry.filters.status ?? "all"}</dd>
        </div>
        <div>
          <dt>Rows</dt>
          <dd>{registry.pagination?.total_items ?? registry.items.length}</dd>
        </div>
      </dl>
      {registry.items.length === 0 && registry.empty_state ? (
        <CommonState
          state={{
            action: emptyAction,
            empty_state: registry.empty_state,
            provenance: registry.provenance,
            state: "empty",
            summary: registry.empty_state.summary,
            title: registry.empty_state.title,
            trace_id: null,
          }}
        />
      ) : null}
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
