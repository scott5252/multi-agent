import type { WorkflowSharingSummary } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface WorkflowSharingPanelProps {
  sharing: WorkflowSharingSummary;
}

export function WorkflowSharingPanel({ sharing }: WorkflowSharingPanelProps) {
  return (
    <section className="workflow-sharing-panel" aria-labelledby="workflow-sharing-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Sharing</p>
          <h2 id="workflow-sharing-title">Visibility and grants</h2>
        </div>
        <Badge tone={sharing.status === "ready" ? "success" : "warning"}>
          {sharing.status}
        </Badge>
      </div>
      <p>{sharing.summary}</p>
      <small>{sharing.grants_label}</small>
      <div className="action-row">
        {sharing.actions.map((action) => (
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
    </section>
  );
}
