import { ShieldPlus, Trash2 } from "lucide-react";
import { useState } from "react";

import type {
  MembershipMutationResult,
  RoleGrantFormMetadata,
  RoleGrantSummary,
  UserDirectoryEntry,
} from "../../api/generated/reactAdminApi";
import { MembershipMutationResultPanel } from "./MembershipMutationResultPanel";

interface RoleGrantPanelProps {
  directory: UserDirectoryEntry[];
  form: RoleGrantFormMetadata;
  grants: RoleGrantSummary[];
  mutationResult: MembershipMutationResult | null;
  onGrant: (url: string, payload: {
    confirmed: boolean;
    idempotency_key: string;
    principal_identity_id: string;
    role_code: string;
    scope_type: "platform" | "tenant";
    tenant_id: string | null;
  }) => void;
  onRevoke: (url: string) => void;
}

export function RoleGrantPanel({
  directory,
  form,
  grants,
  mutationResult,
  onGrant,
  onRevoke,
}: RoleGrantPanelProps) {
  const [principalId, setPrincipalId] = useState(
    directory[0]?.principal_identity_id ?? "",
  );
  const [roleCode, setRoleCode] = useState(form.role_choices[0]?.role_code ?? "tenant_user");
  const role = form.role_choices.find((choice) => choice.role_code === roleCode) ?? form.role_choices[0];

  return (
    <section className="governance-panel membership-panel" id="roles">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Role grants</p>
          <h2>Assign roles</h2>
        </div>
        <button
          className="secondary-button icon-button"
          onClick={() =>
            onGrant("/admin/app/memberships/role-grants", {
              confirmed: true,
              idempotency_key: "role-grant-ui-qa034",
              principal_identity_id: principalId,
              role_code: role?.role_code ?? "tenant_user",
              scope_type: role?.scope_type ?? "tenant",
              tenant_id: role?.tenant_id ?? null,
            })
          }
          type="button"
        >
          <ShieldPlus aria-hidden="true" size={16} />
          Grant
        </button>
      </div>
      <div className="membership-form-grid">
        <label>
          <span className="field-label">User</span>
          <select value={principalId} onChange={(event) => setPrincipalId(event.target.value)}>
            {directory.map((entry) => (
              <option key={entry.principal_identity_id} value={entry.principal_identity_id}>
                {entry.display_name}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span className="field-label">Role</span>
          <select value={roleCode} onChange={(event) => setRoleCode(event.target.value)}>
            {form.role_choices.map((choice) => (
              <option disabled={!choice.eligible} key={`${choice.scope_type}-${choice.role_code}`} value={choice.role_code}>
                {choice.role_label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <p className="guardrail-copy">{form.confirmation_copy}</p>
      <div className="membership-list-grid">
        {grants.map((grant) => (
          <article className="governance-card" key={grant.role_grant_id}>
            <p className="eyebrow">{grant.grant_status}</p>
            <h3>{grant.role_label}</h3>
            <p>{grant.principal_label}</p>
            <p>{grant.tenant_label ?? "Platform"}</p>
            <small>{grant.next_request_effect}</small>
            <button
              className="ghost-button compact-button"
              onClick={() => onRevoke(grant.authorized_actions[0]?.href ?? `/admin/app/memberships/role-grants/${grant.role_grant_id}/revoke`)}
              type="button"
            >
              <Trash2 aria-hidden="true" size={14} />
              Revoke
            </button>
          </article>
        ))}
      </div>
      <MembershipMutationResultPanel result={mutationResult} />
    </section>
  );
}
