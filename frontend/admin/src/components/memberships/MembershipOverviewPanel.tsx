import type {
  MembershipSummaryCard,
  ReactAdminScope,
  ReactAdminScopeOption,
} from "../../api/generated/reactAdminApi";

interface MembershipOverviewPanelProps {
  cards: MembershipSummaryCard[];
  scope: ReactAdminScope;
  scopes: ReactAdminScopeOption[];
}

export function MembershipOverviewPanel({
  cards,
  scope,
  scopes,
}: MembershipOverviewPanelProps) {
  return (
    <section className="governance-panel membership-panel" id="overview">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Overview</p>
          <h2>{scope.label}</h2>
        </div>
        <div className="scope-switcher" aria-label="Membership scope">
          {scopes.map((option) => (
            <a
              aria-current={option.selected ? "page" : undefined}
              className={option.selected ? "scope-chip active" : "scope-chip"}
              href={option.href.replace("/admin/app", "/admin/app/memberships").split("?")[0] === "/admin/app/memberships"
                ? option.href
                : option.scope.tenant_id
                  ? `/admin/app/memberships?tenant_id=${option.scope.tenant_id}`
                  : "/admin/app/memberships"}
              key={`${option.scope.scope_type}-${option.scope.tenant_id ?? "platform"}`}
            >
              {option.label}
            </a>
          ))}
        </div>
      </div>
      <div className="testbench-metric-grid membership-metric-grid">
        {cards.map((card) => (
          <article className="governance-card" key={card.card_id}>
            <p className="eyebrow">{card.status}</p>
            <h3>{card.value}</h3>
            <strong>{card.label}</strong>
            <p>{card.summary}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
