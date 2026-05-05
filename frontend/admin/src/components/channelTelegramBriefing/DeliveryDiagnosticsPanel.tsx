import type {
  DeliveryAttemptSummary,
  WebhookDiagnosticSummary,
} from "../../api/generated/reactAdminApi";

export function DeliveryDiagnosticsPanel({
  attempts,
  receipts,
  onOpenRun,
}: {
  attempts: DeliveryAttemptSummary[];
  receipts: WebhookDiagnosticSummary[];
  onOpenRun: (href: string) => void;
}) {
  return (
    <section aria-labelledby="delivery-diagnostics-heading" className="channel-section">
      <div className="section-heading-row">
        <h2 id="delivery-diagnostics-heading">Delivery Diagnostics</h2>
        <span>{attempts.length} bounded attempts</span>
      </div>
      <div className="channel-table">
        {attempts.map((attempt) => (
          <article className="channel-row" key={attempt.attempt_id}>
            <div>
              <strong>{attempt.alias_label}</strong>
              <span>{attempt.tenant_label}</span>
            </div>
            <div>
              <span>{attempt.status}</span>
              <span>{attempt.retry_category}</span>
            </div>
            <div>
              <span>{attempt.bot_api_boundary_status}</span>
              <span>{attempt.safe_error_summary}</span>
            </div>
            {attempt.run_status_href ? (
              <button type="button" onClick={() => onOpenRun(attempt.run_status_href ?? "")}>
                Open Run Status
              </button>
            ) : null}
          </article>
        ))}
      </div>
      <div className="receipt-strip">
        {receipts.map((receipt) => (
          <span key={receipt.diagnostic_id}>
            {receipt.status}: {receipt.receipt_count} receipts
          </span>
        ))}
      </div>
    </section>
  );
}
