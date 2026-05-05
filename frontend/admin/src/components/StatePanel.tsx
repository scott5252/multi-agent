interface StatePanelProps {
  title: string;
  summary: string;
  actionHref?: string;
  actionLabel?: string;
}

export function StatePanel({
  title,
  summary,
  actionHref,
  actionLabel,
}: StatePanelProps) {
  return (
    <main className="app-frame state-frame">
      <section className="state-panel" aria-live="polite">
        <p className="eyebrow">Admin</p>
        <h1>{title}</h1>
        <p>{summary}</p>
        {actionHref && actionLabel ? (
          <a className="primary-link" href={actionHref}>
            {actionLabel}
          </a>
        ) : null}
      </section>
    </main>
  );
}
