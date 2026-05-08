import type { ReliabilityRecoverySummary } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

export function WorkbenchReliabilityPanel({
  reliability,
}: {
  reliability: ReliabilityRecoverySummary;
}) {
  const items = [
    ...reliability.breakers,
    ...reliability.retries,
    ...reliability.dead_letters,
    ...reliability.confirmations,
  ];
  return (
    <section className="workbench-panel reliability-panel" aria-label="Reliability recovery">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Reliability</p>
          <h2>Recovery posture</h2>
        </div>
      </div>
      <div className="recovery-list">
        {items.length === 0 ? (
          <p>No live recovery records match this scope.</p>
        ) : (
          items.map((item) => (
            <article key={item.item_id}>
              <div className="card-heading">
                <strong>{item.label}</strong>
                <Badge tone={item.status === "ready" || item.status === "empty" ? "success" : "warning"}>
                  {item.status}
                </Badge>
              </div>
              <p>{item.summary}</p>
              {item.confirmation ? <small>{item.confirmation}</small> : null}
              {item.href ? <a href={item.href}>Open recovery page</a> : null}
            </article>
          ))
        )}
      </div>
      {reliability.partial_reason ? <p>{reliability.partial_reason}</p> : null}
    </section>
  );
}
