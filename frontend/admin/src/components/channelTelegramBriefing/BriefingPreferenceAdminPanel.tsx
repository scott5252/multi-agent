import type { BriefingPreferenceProfile } from "../../api/generated/reactAdminApi";

export function BriefingPreferenceAdminPanel({
  summaries,
  evidence,
  onImport,
  onExport,
}: {
  summaries: BriefingPreferenceProfile[];
  evidence: string[];
  onImport: () => void;
  onExport: () => void;
}) {
  return (
    <section aria-labelledby="briefing-admin-heading" className="channel-section">
      <div className="section-heading-row">
        <h2 id="briefing-admin-heading">Admin Summaries</h2>
        <div className="button-row button-row--inline">
          <button type="button" onClick={onImport}>
            Import
          </button>
          <button type="button" onClick={onExport}>
            Export
          </button>
        </div>
      </div>
      <div className="channel-card-grid channel-card-grid--compact">
        {summaries.map((summary) => (
          <article className="channel-card" key={summary.profile_id}>
            <h3>{summary.principal_label}</h3>
            <p>{summary.news_topics_summary}</p>
            <p>{summary.vip_sender_summary}</p>
            <p>{summary.default_account_summary}</p>
            <small>{summary.audit_reference}</small>
          </article>
        ))}
      </div>
      <div className="receipt-strip">
        {evidence.map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>
    </section>
  );
}
