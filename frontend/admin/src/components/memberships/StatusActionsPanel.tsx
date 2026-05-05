import { Ban, RotateCcw } from "lucide-react";

import type {
  MembershipMutationResult,
  MembershipStatusSummary,
  UserDirectoryEntry,
} from "../../api/generated/reactAdminApi";
import { MembershipMutationResultPanel } from "./MembershipMutationResultPanel";

interface StatusActionsPanelProps {
  directory: UserDirectoryEntry[];
  membershipStatuses: MembershipStatusSummary[];
  mutationResult: MembershipMutationResult | null;
  onMembershipStatus: (url: string) => void;
  onPrincipalStatus: (url: string) => void;
}

export function StatusActionsPanel({
  directory,
  membershipStatuses,
  mutationResult,
  onMembershipStatus,
  onPrincipalStatus,
}: StatusActionsPanelProps) {
  return (
    <section className="governance-panel membership-panel" id="status">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Status</p>
          <h2>Access-changing actions</h2>
        </div>
      </div>
      <div className="membership-list-grid">
        {directory.map((entry) => (
          <article className="governance-card" key={entry.principal_identity_id}>
            <p className="eyebrow">{entry.principal_status}</p>
            <h3>{entry.display_name}</h3>
            <div className="button-row">
              {entry.authorized_actions.map((action) => (
                <button
                  className={action.variant === "danger" ? "danger-button compact-button" : "ghost-button compact-button"}
                  key={action.action_id}
                  onClick={() => onPrincipalStatus(action.href)}
                  type="button"
                >
                  {action.action_id.includes("reactivate") ? (
                    <RotateCcw aria-hidden="true" size={14} />
                  ) : (
                    <Ban aria-hidden="true" size={14} />
                  )}
                  {action.label}
                </button>
              ))}
            </div>
          </article>
        ))}
      </div>
      <div className="membership-list-grid">
        {membershipStatuses.map((status) => (
          <article className="governance-card" key={status.tenant_membership_id}>
            <p className="eyebrow">{status.membership_status}</p>
            <h3>{status.tenant_label}</h3>
            <p>{status.status_reason}</p>
            <div className="button-row">
              {status.authorized_actions.map((action) => (
                <button
                  className="ghost-button compact-button"
                  key={action.action_id}
                  onClick={() => onMembershipStatus(action.href)}
                  type="button"
                >
                  {action.label}
                </button>
              ))}
            </div>
          </article>
        ))}
      </div>
      <MembershipMutationResultPanel result={mutationResult} />
    </section>
  );
}
