import type { UsageReactProblem } from "../../api/generated/reactAdminApi";

export function UsageStatePanel({ states }: { states: UsageReactProblem[] }) {
  if (!states.length) {
    return null;
  }

  return (
    <section className="usage-state-list" aria-label="Usage states">
      {states.map((state) => (
        <article className={`usage-state usage-state-${state.reason}`} key={state.reason}>
          <h3>{state.title}</h3>
          <p>{state.detail}</p>
          <small>{state.next_action}</small>
          {state.audit_reference ? <code>{state.audit_reference}</code> : null}
        </article>
      ))}
    </section>
  );
}
