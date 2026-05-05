import type {
  MembershipDirectoryFilters,
  UserDirectoryEntry,
} from "../../api/generated/reactAdminApi";
import { MaskedIdentityCell } from "./MaskedIdentityCell";

interface UserDirectoryPanelProps {
  directory: UserDirectoryEntry[];
  filters: MembershipDirectoryFilters;
  onOpenDetail: (entry: UserDirectoryEntry) => void;
}

export function UserDirectoryPanel({
  directory,
  filters,
  onOpenDetail,
}: UserDirectoryPanelProps) {
  return (
    <section className="governance-panel membership-panel" id="directory">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Directory</p>
          <h2>Users</h2>
        </div>
      </div>
      <div className="membership-filter-row" aria-label="Directory filters">
        <FilterGroup label="Tenant" values={filters.tenant_options.map((item) => item.label)} />
        <FilterGroup label="Role" values={filters.role_options.map((item) => item.label)} />
        <FilterGroup label="Status" values={filters.status_options.map((item) => item.label)} />
        <FilterGroup
          label="Decision"
          values={filters.access_decision_options.map((item) => item.label)}
        />
      </div>
      {directory.length ? (
        <div className="membership-directory-table" role="table" aria-label="Membership directory">
          <div className="membership-directory-head" role="row">
            <span role="columnheader">User</span>
            <span role="columnheader">Tenants</span>
            <span role="columnheader">Roles</span>
            <span role="columnheader">Access</span>
          </div>
          {directory.map((entry) => (
            <div className="membership-directory-row" role="row" key={entry.principal_identity_id}>
              <div role="cell">
                <MaskedIdentityCell entry={entry} onOpenDetail={onOpenDetail} />
              </div>
              <div role="cell">
                {entry.tenant_memberships.map((membership) => (
                  <span className="status-pill" key={membership.tenant_membership_id}>
                    {membership.tenant_label} {membership.membership_status}
                  </span>
                ))}
              </div>
              <div role="cell">
                {entry.role_summaries.map((grant) => (
                  <span className="status-pill" key={grant.role_grant_id}>
                    {grant.role_label}
                  </span>
                ))}
              </div>
              <div role="cell">
                <p>{entry.last_access_summary}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="safe-empty">No users match the active filters.</p>
      )}
    </section>
  );
}

function FilterGroup({ label, values }: { label: string; values: string[] }) {
  return (
    <div className="membership-filter-group">
      <span className="field-label">{label}</span>
      <div className="button-row">
        {values.map((value) => (
          <span className="status-pill" key={value}>
            {value}
          </span>
        ))}
      </div>
    </div>
  );
}
