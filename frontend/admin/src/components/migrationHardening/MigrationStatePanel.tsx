import type { MigrationProblem } from "../../api/generated/reactAdminApi";
import { StatusBadge } from "./RouteDecisionBadges";

export function MigrationStatePanel({ states }: { states: MigrationProblem[] }) {
  if (!states.length) {
    return null;
  }
  return (
    <section className="migration-panel migration-state-panel" aria-labelledby="migration-state-title">
      <div className="migration-panel-heading">
        <div>
          <p className="eyebrow">Review states</p>
          <h2 id="migration-state-title">Migration guidance</h2>
        </div>
      </div>
      <div className="migration-state-grid">
        {states.map((state) => (
          <article className="migration-state" key={`${state.reason}-${state.title}`}>
            <div className="migration-state-top">
              <h3>{state.title}</h3>
              <StatusBadge status={state.severity} label={state.severity} />
            </div>
            <p>{state.detail}</p>
            <small>{state.next_action}</small>
            {state.audit_reference ? <code>{state.audit_reference}</code> : null}
          </article>
        ))}
      </div>
    </section>
  );
}
