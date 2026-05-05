import type { ChannelProblem } from "../../api/generated/reactAdminApi";

export function ChannelStatePanel({ states }: { states: ChannelProblem[] }) {
  if (states.length === 0) {
    return null;
  }
  return (
    <section aria-labelledby="channel-states-heading" className="channel-section">
      <h2 id="channel-states-heading">States</h2>
      <div className="channel-state-list">
        {states.map((state) => (
          <article key={`${state.reason}-${state.audit_reference}`} className="state-inline">
            <strong>{state.title}</strong>
            <span>{state.detail}</span>
            <small>{state.next_action}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
