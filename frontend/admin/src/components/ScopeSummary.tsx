import type { ReactAdminBootstrap } from "../api/generated/reactAdminApi";

interface ScopeSummaryProps {
  bootstrap: ReactAdminBootstrap;
}

export function ScopeSummary({ bootstrap }: ScopeSummaryProps) {
  const { active_scope, principal } = bootstrap;
  const roleLabel = principal.role_codes.length
    ? principal.role_codes.join(", ")
    : "no roles";
  return (
    <section className="scope-summary" aria-label="Active scope">
      <div>
        <span className="label">Signed in as</span>
        <strong>{principal.display_name ?? principal.principal_id}</strong>
      </div>
      <div>
        <span className="label">Auth mode</span>
        <strong>{principal.auth_mode}</strong>
      </div>
      <div>
        <span className="label">Scope</span>
        <strong>{active_scope.label}</strong>
      </div>
      <div>
        <span className="label">Roles</span>
        <strong>{roleLabel}</strong>
      </div>
    </section>
  );
}
