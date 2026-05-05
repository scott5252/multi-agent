import type { RunDebugEnvelope } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

export function WorkbenchTimeline({ runDebug }: { runDebug: RunDebugEnvelope }) {
  return (
    <section className="workbench-panel timeline-panel" aria-label="Run debug timeline">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Run debug</p>
          <h2>{runDebug.safe_title}</h2>
        </div>
        <Badge tone={runDebug.run_status === "ready" ? "success" : "warning"}>
          {runDebug.run_status}
        </Badge>
      </div>
      <ol className="timeline-list">
        {runDebug.timeline.map((event) => (
          <li key={event.event_id}>
            <span>{event.occurred_at_label}</span>
            <strong>{event.summary}</strong>
            <small>{event.category}</small>
          </li>
        ))}
      </ol>
      <div className="branch-grid">
        {runDebug.branches.map((branch) => (
          <article key={branch.branch_id}>
            <strong>{branch.label}</strong>
            <p>{branch.summary}</p>
            {branch.join_decision ? <small>{branch.join_decision}</small> : null}
          </article>
        ))}
      </div>
      <div className="diagnostic-grid">
        {runDebug.gateway_attempts.map((attempt) => (
          <article key={attempt.attempt_id}>
            <strong>{attempt.provider_label}</strong>
            <p>{attempt.safe_summary}</p>
            <small>{attempt.credential_diagnostic_category}</small>
          </article>
        ))}
        {runDebug.tool_calls.map((tool) => (
          <article key={tool.tool_call_id}>
            <strong>{tool.tool_label}</strong>
            <p>{tool.safe_summary}</p>
            <small>{tool.policy_outcome}</small>
          </article>
        ))}
        {runDebug.deliveries.map((delivery) => (
          <article key={delivery.delivery_id}>
            <strong>{delivery.alias_label}</strong>
            <p>{delivery.safe_summary}</p>
            <small>{delivery.failure_category}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
