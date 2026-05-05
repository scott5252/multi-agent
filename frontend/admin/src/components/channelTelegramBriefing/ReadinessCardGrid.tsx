import type { ChannelTelegramReadiness } from "../../api/generated/reactAdminApi";

export function ReadinessCardGrid({ readiness }: { readiness: ChannelTelegramReadiness[] }) {
  return (
    <section aria-labelledby="channel-readiness-heading" className="channel-section">
      <div className="section-heading-row">
        <h2 id="channel-readiness-heading">Readiness</h2>
        <span>{readiness.length} scoped summaries</span>
      </div>
      <div className="channel-card-grid">
        {readiness.map((item) => (
          <article className="channel-card" key={item.readiness_id}>
            <div className={`status-pill status-pill--${item.status}`}>{item.status}</div>
            <h3>{item.tenant_label}</h3>
            <dl className="compact-definition-list">
              <div>
                <dt>Telegram</dt>
                <dd>{item.telegram_enabled ? "Enabled" : "Disabled"}</dd>
              </div>
              <div>
                <dt>Webhook</dt>
                <dd>{item.webhook_status}</dd>
              </div>
              <div>
                <dt>Reference</dt>
                <dd>{item.secret_reference_status}</dd>
              </div>
              <div>
                <dt>Identities</dt>
                <dd>{item.linked_identity_count}</dd>
              </div>
              <div>
                <dt>Aliases</dt>
                <dd>{item.alias_count}</dd>
              </div>
            </dl>
            <p>{item.delivery_health_label}</p>
            <small>{item.audit_reference}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
