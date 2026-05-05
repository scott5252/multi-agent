import type { MembershipAuditRecord } from "../../api/generated/reactAdminApi";

export function MembershipAuditPanel({
  records,
}: {
  records: MembershipAuditRecord[];
}) {
  return (
    <section className="governance-panel membership-panel" id="audit">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Audit</p>
          <h2>Membership timeline</h2>
        </div>
      </div>
      <div className="timeline-list">
        {records.map((record) => (
          <article className="timeline-row" key={record.audit_reference_id}>
            <span className={`status-dot ${record.outcome}`} />
            <div>
              <strong>{record.action}</strong>
              <p>{record.safe_diff_summary}</p>
              <dl className="compact-dl">
                <div>
                  <dt>Actor</dt>
                  <dd>{record.actor_label}</dd>
                </div>
                <div>
                  <dt>Target</dt>
                  <dd>{record.target_label}</dd>
                </div>
                <div>
                  <dt>Tenant</dt>
                  <dd>{record.tenant_scope_label}</dd>
                </div>
                <div>
                  <dt>Audit</dt>
                  <dd>{record.audit_reference_id}</dd>
                </div>
              </dl>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
