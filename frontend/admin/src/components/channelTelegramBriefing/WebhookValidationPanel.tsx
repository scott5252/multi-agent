import type {
  ChannelMutationResult,
  TelegramTenantConfiguration,
  WebhookDiagnosticSummary,
} from "../../api/generated/reactAdminApi";

export function WebhookValidationPanel({
  configs,
  diagnostics,
  result,
  onValidate,
}: {
  configs: TelegramTenantConfiguration[];
  diagnostics: WebhookDiagnosticSummary[];
  result: ChannelMutationResult | null;
  onValidate: (config: TelegramTenantConfiguration) => void;
}) {
  return (
    <section aria-labelledby="webhook-validation-heading" className="channel-section">
      <div className="section-heading-row">
        <h2 id="webhook-validation-heading">Webhook Validation</h2>
        <span>Mock-safe local evidence</span>
      </div>
      <div className="channel-card-grid channel-card-grid--compact">
        {diagnostics.map((diagnostic) => (
          <article className="channel-card" key={diagnostic.diagnostic_id}>
            <div className={`status-pill status-pill--${diagnostic.status}`}>
              {diagnostic.status}
            </div>
            <h3>{diagnostic.safe_update_summary}</h3>
            <p>Receipts: {diagnostic.receipt_count}</p>
            <p>{diagnostic.next_step}</p>
            <small>{diagnostic.audit_reference}</small>
          </article>
        ))}
      </div>
      <div className="button-row">
        {configs.map((config) => (
          <button key={config.tenant_label} type="button" onClick={() => onValidate(config)}>
            Validate {config.tenant_label}
          </button>
        ))}
      </div>
      {result ? <p className="mutation-note">{result.summary}</p> : null}
    </section>
  );
}
