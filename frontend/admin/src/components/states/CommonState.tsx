import type { ReactAdminShellState } from "../../api/generated/reactAdminApi";

export function CommonState({ state }: { state: ReactAdminShellState }) {
  return (
    <section className={`common-state ${state.state}`} data-state={state.state}>
      <p className="eyebrow">{state.state.replaceAll("_", " ")}</p>
      <h1>{state.title}</h1>
      <p>{state.summary}</p>
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
    }
  );
}
