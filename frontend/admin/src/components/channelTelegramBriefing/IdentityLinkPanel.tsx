import type {
  LinkTokenResult,
  LinkedTelegramIdentitySummary,
} from "../../api/generated/reactAdminApi";

export function IdentityLinkPanel({
  identities,
  tokenResult,
  onCreateToken,
}: {
  identities: LinkedTelegramIdentitySummary[];
  tokenResult: LinkTokenResult | null;
  onCreateToken: () => void;
}) {
  return (
    <section aria-labelledby="identity-link-heading" className="channel-section">
      <div className="section-heading-row">
        <h2 id="identity-link-heading">Identity Links</h2>
        <button type="button" onClick={onCreateToken}>
          Create Code
        </button>
      </div>
      {tokenResult ? (
        <div className="token-result">
          <strong>{tokenResult.masked_status}</strong>
          {tokenResult.display_mode === "immediate" && tokenResult.token_value ? (
            <code>{tokenResult.token_value}</code>
          ) : null}
          <span>Expires {new Date(tokenResult.expires_at).toLocaleString()}</span>
          <small>{tokenResult.audit_reference}</small>
        </div>
      ) : null}
      <div className="channel-table">
        {identities.map((identity) => (
          <article className="channel-row" key={identity.identity_id}>
            <div>
              <strong>{identity.principal_label}</strong>
              <span>{identity.status}</span>
            </div>
            <div>
              <span>{identity.telegram_label}</span>
              <span>{identity.chat_label}</span>
            </div>
            <small>{identity.audit_reference}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
