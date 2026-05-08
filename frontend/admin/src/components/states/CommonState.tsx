import type { ReactAdminShellState } from "../../api/generated/reactAdminApi";

export function CommonState({ state }: { state: ReactAdminShellState }) {
  return (
    <section className={`common-state ${state.state}`} data-state={state.state}>
      <p className="eyebrow">{state.state.replaceAll("_", " ")}</p>
      <h1>{state.title}</h1>
      <p>{state.summary}</p>
      {state.empty_state ? (
        <div className="state-metadata">
          <strong>{state.empty_state.title}</strong>
          <p>{state.empty_state.summary}</p>
          {state.empty_state.setup_hint ? (
            <small>{state.empty_state.setup_hint}</small>
          ) : null}
        </div>
      ) : null}
      {state.provenance ? (
        <dl className="state-provenance">
          <div>
            <dt>Source</dt>
            <dd>{state.provenance.source_label}</dd>
          </div>
          {state.provenance.source_detail ? (
            <div>
              <dt>Evidence</dt>
              <dd>{state.provenance.source_detail}</dd>
            </div>
          ) : null}
        </dl>
      ) : null}
      {state.action?.href ? (
        <a className="primary-link" href={state.action.href}>
          {state.action.label}
        </a>
      ) : null}
      {state.trace_id ? <small>Trace {state.trace_id}</small> : null}
    </section>
  );
}

export function stateByKind(
  states: ReactAdminShellState[],
  kind: ReactAdminShellState["state"],
): ReactAdminShellState {
  return (
    states.find((state) => state.state === kind) ?? {
      state: kind,
      title: "Admin state unavailable",
      summary: "The admin shell could not load this safe state descriptor.",
      action: null,
      trace_id: null,
      provenance: null,
      empty_state: null,
    }
  );
}
