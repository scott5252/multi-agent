import type {
  HealthPressurePanel,
  LikelyCauseSummary,
  WorkbenchSummaryCard,
} from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

function toneFor(status: string) {
  if (status === "ready" || status === "available") {
    return "success";
  }
  if (status === "critical" || status === "unavailable" || status === "denied") {
    return "critical";
  }
  if (status === "empty" || status === "not_found") {
    return "neutral";
  }
  return "warning";
}

export function WorkbenchSummaryGrid({
  cards,
  causes,
  panels,
}: {
  cards: WorkbenchSummaryCard[];
  causes: LikelyCauseSummary[];
  panels: HealthPressurePanel[];
}) {
  return (
    <section className="workbench-grid" aria-label="Workbench summaries">
      <div className="summary-card-grid">
        {cards.map((card) => (
          <article className={`workbench-card ${card.status}`} key={card.card_id}>
            <div className="card-heading">
              <strong>{card.label}</strong>
              <Badge tone={toneFor(card.status)}>{card.status}</Badge>
            </div>
            <span className="metric-value">{card.value}</span>
            <p>{card.summary}</p>
            <small>{card.freshness_label}</small>
            {card.href ? <a href={card.href}>Open details</a> : null}
          </article>
        ))}
      </div>
      <div className="likely-causes">
        <h2>Likely causes</h2>
        {causes.length === 0 ? (
          <p>No live warning symptoms match this scope.</p>
        ) : (
          causes.map((cause) => (
            <article key={cause.cause_id}>
              <strong>{cause.affected_subsystem}</strong>
              <p>{cause.symptom}</p>
              <small>{cause.likely_cause_category}</small>
              {cause.href ? <a href={cause.href}>{cause.recommended_next_step}</a> : null}
            </article>
          ))
        )}
      </div>
      <div className="health-panels">
        {panels.map((panel) => (
          <article className="health-panel" key={panel.panel_id}>
            <div className="card-heading">
              <h2>{panel.title}</h2>
              <Badge tone={toneFor(panel.status)}>{panel.status}</Badge>
            </div>
            <dl className="metric-list">
              {[...panel.metrics, ...panel.dependencies].map((metric) => (
                <div key={`${panel.panel_id}-${metric.label}`}>
                  <dt>{metric.label}</dt>
                  <dd>{metric.value}</dd>
                </div>
              ))}
            </dl>
            {panel.partial_reason ? <p>{panel.partial_reason}</p> : null}
            <small>
              {panel.freshness_label}
              {panel.polling_allowed ? " · safe polling available" : ""}
            </small>
          </article>
        ))}
      </div>
    </section>
  );
}
