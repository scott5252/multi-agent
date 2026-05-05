import type {
  ChannelMutationResult,
  TelegramTenantConfiguration,
} from "../../api/generated/reactAdminApi";

export function TelegramConfigPanel({
  configs,
  result,
  onSave,
}: {
  configs: TelegramTenantConfiguration[];
  result: ChannelMutationResult | null;
  onSave: (config: TelegramTenantConfiguration) => void;
}) {
  return (
    <section aria-labelledby="telegram-config-heading" className="channel-section">
      <div className="section-heading-row">
        <h2 id="telegram-config-heading">Telegram Configuration</h2>
        <span>Backend-owned settings</span>
      </div>
      <div className="channel-table">
        {configs.map((config) => (
          <article className="channel-row" key={config.tenant_label}>
            <div>
              <strong>{config.tenant_label}</strong>
              <p>{config.enabled ? "Enabled" : "Disabled"}</p>
            </div>
            <div>
              <span>{config.bot_token_reference_label}</span>
              <span>{config.webhook_signing_reference_label}</span>
            </div>
            <div>
              <span>Revision {config.revision}</span>
              <span>{config.audit_reference}</span>
            </div>
            <button type="button" onClick={() => onSave(config)}>
              Save
            </button>
          </article>
        ))}
      </div>
      {result ? <p className="mutation-note">{result.summary}</p> : null}
    </section>
  );
}
