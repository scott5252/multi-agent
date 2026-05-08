import type {
  ReactAdminEmptyStateMetadata,
  ReactAdminPageProvenance,
} from "../api/generated/reactAdminApi";

interface StatePanelProps {
  title: string;
  summary: string;
  actionHref?: string;
  actionLabel?: string;
  provenance?: ReactAdminPageProvenance | null;
  emptyState?: ReactAdminEmptyStateMetadata | null;
}

export function StatePanel({
  title,
  summary,
  actionHref,
  actionLabel,
  provenance,
  emptyState,
}: StatePanelProps) {
  return (
    <main className="app-frame state-frame">
      <section className="state-panel" aria-live="polite">
        <p className="eyebrow">Admin</p>
        <h1>{title}</h1>
        <p>{summary}</p>
        {emptyState ? (
          <div className="state-metadata">
            <strong>{emptyState.title}</strong>
            <p>{emptyState.summary}</p>
            {emptyState.setup_hint ? <small>{emptyState.setup_hint}</small> : null}
          </div>
        ) : null}
        {provenance ? (
          <dl className="state-provenance">
            <div>
              <dt>Source</dt>
              <dd>{provenance.source_label}</dd>
            </div>
            {provenance.source_detail ? (
              <div>
                <dt>Evidence</dt>
                <dd>{provenance.source_detail}</dd>
              </div>
            ) : null}
          </dl>
        ) : null}
        {actionHref && actionLabel ? (
          <a className="primary-link" href={actionHref}>
            {actionLabel}
          </a>
        ) : null}
      </section>
    </main>
  );
}
