import { UserPlus } from "lucide-react";
import { useState } from "react";

import type {
  InvitationFormMetadata,
  InvitationSummary,
  MembershipMutationResult,
} from "../../api/generated/reactAdminApi";
import { MembershipMutationResultPanel } from "./MembershipMutationResultPanel";

interface InvitationPanelProps {
  form: InvitationFormMetadata;
  invitations: InvitationSummary[];
  mutationResult: MembershipMutationResult | null;
  onInvite: (url: string, payload: {
    tenant_id: string | null;
    email: string;
    requested_roles: string[];
    idempotency_key: string;
  }) => void;
}

export function InvitationPanel({
  form,
  invitations,
  mutationResult,
  onInvite,
}: InvitationPanelProps) {
  const [tenantId, setTenantId] = useState(form.default_tenant_id);
  const [roleCode, setRoleCode] = useState(form.role_choices[0]?.role_code ?? "tenant_user");
  const [email, setEmail] = useState("invite.replay@example.test");

  return (
    <section className="governance-panel membership-panel" id="invitations">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Invitations</p>
          <h2>Invite users</h2>
        </div>
        <button
          className="primary-button icon-button"
          onClick={() =>
            onInvite("/admin/app/memberships/invitations", {
              email,
              idempotency_key: email.includes("replay")
                ? "invite-ui-qa034-replay"
                : "invite-ui-qa034-create",
              requested_roles: [roleCode],
              tenant_id: tenantId,
            })
          }
          type="button"
        >
          <UserPlus aria-hidden="true" size={16} />
          Invite
        </button>
      </div>
      <div className="membership-form-grid">
        <label>
          <span className="field-label">Email</span>
          <input value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        {form.tenant_options.length > 1 ? (
          <label>
            <span className="field-label">Tenant</span>
            <select value={tenantId ?? ""} onChange={(event) => setTenantId(event.target.value || null)}>
              {form.tenant_options.map((option) => (
                <option key={option.option_id} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        ) : null}
        <label>
          <span className="field-label">Role</span>
          <select value={roleCode} onChange={(event) => setRoleCode(event.target.value)}>
            {form.role_choices.map((choice) => (
              <option disabled={!choice.eligible} key={choice.role_code} value={choice.role_code}>
                {choice.role_label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <p className="guardrail-copy">{form.idempotency_hint}</p>
      <div className="membership-list-grid">
        {invitations.map((invitation) => (
          <article className="governance-card" key={invitation.invitation_id}>
            <p className="eyebrow">{invitation.status}</p>
            <h3>{invitation.masked_email}</h3>
            <p>{invitation.tenant_label}</p>
            <p>{invitation.next_request_effect}</p>
            <small>{invitation.audit_reference_id}</small>
          </article>
        ))}
      </div>
      <MembershipMutationResultPanel result={mutationResult} />
    </section>
  );
}
