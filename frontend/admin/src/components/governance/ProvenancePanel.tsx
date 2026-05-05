import type { RunProvenanceSummary } from "../../api/generated/reactAdminApi";

export function ProvenancePanel({
  provenance,
}: {
  provenance: RunProvenanceSummary[];
}) {
  return (
    <section className="governance-panel" aria-labelledby="provenance-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Provenance</p>
          <h2 id="provenance-title">Run evidence</h2>
        </div>
      </div>
      <div className="governance-card-grid">
        {provenance.map((run) => (
          <article className="governance-card" key={run.run_id}>
            <div className="card-heading">
              <strong>{run.workflow_label}</strong>
              <small>{run.started_at_label}</small>
            </div>
            <dl className="compact-dl">
              <div>
                <dt>Provider</dt>
                <dd>{run.provider_evidence}</dd>
              </div>
              <div>
                <dt>Prompt</dt>
                <dd>{run.prompt_evidence}</dd>
              </div>
              <div>
                <dt>Profile</dt>
                <dd>{run.profile_evidence}</dd>
              </div>
              <div>
                <dt>Credential</dt>
                <dd>{run.credential_reference_evidence}</dd>
              </div>
            </dl>
            <small>{run.audit_reference_id}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
