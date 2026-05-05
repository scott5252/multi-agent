import type { MembershipMutationResult } from "../../api/generated/reactAdminApi";

export function MembershipMutationResultPanel({
  result,
}: {
  result: MembershipMutationResult | null;
}) {
  if (!result) {
    return null;
  }
  return (
    <section className={`mutation-result membership-result ${result.status}`} aria-live="polite">
      <p className="eyebrow">{result.status}</p>
      <h3>{result.summary}</h3>
      <dl className="compact-dl">
        <div>
          <dt>Audit</dt>
          <dd>{result.audit_reference_id}</dd>
        </div>
        <div>
          <dt>Effect</dt>
          <dd>{result.next_request_effect}</dd>
        </div>
        {result.invitation ? (
          <div>
            <dt>Invite</dt>
            <dd>{result.invitation.masked_email}</dd>
          </div>
        ) : null}
        {result.role_grant ? (
          <div>
            <dt>Role</dt>
            <dd>{result.role_grant.role_label}</dd>
          </div>
        ) : null}
      </dl>
      {result.confirmation ? (
        <p className="guardrail-copy">{result.confirmation.summary}</p>
      ) : null}
      {result.stale_conflict ? (
        <p className="safe-error">{result.stale_conflict.message}</p>
      ) : null}
      {result.field_errors.length ? (
        <ul className="evidence-list">
          {result.field_errors.map((error) => (
            <li key={`${error.field}-${error.code}`}>{error.message}</li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
