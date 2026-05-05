import { Link } from "lucide-react";
import { useState } from "react";

import type { MembershipMutationResult } from "../../api/generated/reactAdminApi";
import { MembershipMutationResultPanel } from "./MembershipMutationResultPanel";

interface PrincipalLinkPanelProps {
  mutationResult: MembershipMutationResult | null;
  onLink: (url: string, payload: {
    display_name: string;
    email: string | null;
    external_subject: string;
    idempotency_key: string;
    overwrite_confirmed: boolean;
    principal_identity_id: string | null;
  }) => void;
}

export function PrincipalLinkPanel({ mutationResult, onLink }: PrincipalLinkPanelProps) {
  const [overwriteConfirmed, setOverwriteConfirmed] = useState(false);
  return (
    <section className="governance-panel membership-panel" aria-label="Principal linking">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Principal</p>
          <h2>Link identity</h2>
        </div>
        <button
          className="secondary-button icon-button"
          onClick={() =>
            onLink("/admin/app/memberships/principals/link", {
              display_name: "Linked Reviewer",
              email: "linked.reviewer@example.test",
              external_subject: overwriteConfirmed
                ? "auth0-safe-existing-subject-7788"
                : "auth0-safe-subject-7788",
              idempotency_key: "principal-link-ui-qa034",
              overwrite_confirmed: overwriteConfirmed,
              principal_identity_id: null,
            })
          }
          type="button"
        >
          <Link aria-hidden="true" size={16} />
          Link
        </button>
      </div>
      <label className="toggle-row">
        <input
          checked={overwriteConfirmed}
          onChange={(event) => setOverwriteConfirmed(event.target.checked)}
          type="checkbox"
        />
        <span>Confirm overwrite when backend reports a conflict</span>
      </label>
      <MembershipMutationResultPanel result={mutationResult} />
    </section>
  );
}
