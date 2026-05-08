import type { SupportOverrideSummary } from "../../api/generated/reactAdminApi";

export function SupportOverridePanel({
  overrides,
}: {
  overrides: SupportOverrideSummary[];
}) {
  return (
    <section className="governance-panel membership-panel" id="support">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Support overrides</p>
          <h2>Temporary access evidence</h2>
        </div>
      </div>
      <div className="membership-list-grid">
        {overrides.length === 0 ? (
          <article className="governance-card">
            <p className="eyebrow">unavailable</p>
            <h3>No support overrides</h3>
            <p>No persisted support override records exist for this scope.</p>
          </article>
        ) : null}
        {overrides.map((override) => (
          <article className="governance-card" key={override.support_override_id}>
            <p className="eyebrow">{override.status}</p>
            <h3>{override.tenant_label}</h3>
            <p>{override.safe_summary}</p>
            <dl className="compact-dl">
              <div>
                <dt>Requester</dt>
                <dd>{override.requester_label}</dd>
              </div>
              <div>
                <dt>Approver</dt>
                <dd>{override.approver_label ?? "Not recorded"}</dd>
              </div>
              <div>
                <dt>Expires</dt>
                <dd>{override.expires_label}</dd>
              </div>
              <div>
                <dt>Audit</dt>
                <dd>{override.audit_reference_id}</dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    </section>
  );
}
