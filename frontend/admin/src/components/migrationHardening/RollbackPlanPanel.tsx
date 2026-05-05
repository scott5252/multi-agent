import { ShieldCheck } from "lucide-react";

import type { MigrationRollbackPlan } from "../../api/generated/reactAdminApi";
import { StatusBadge } from "./RouteDecisionBadges";

export function RollbackPlanPanel({ plan }: { plan: MigrationRollbackPlan }) {
  return (
    <section className="migration-panel" aria-labelledby="migration-rollback-title">
      <div className="migration-panel-heading">
        <div>
          <p className="eyebrow">Rollback</p>
          <h2 id="migration-rollback-title">Route safety plan</h2>
        </div>
        <StatusBadge status={plan.status} label={plan.status} />
      </div>
      <dl className="migration-definition-grid">
        <div>
          <dt>Flag</dt>
          <dd>{plan.feature_flag_label}</dd>
        </div>
        <div>
          <dt>Assets</dt>
          <dd>{plan.asset_version_label}</dd>
        </div>
        <div>
          <dt>Owner</dt>
          <dd>{plan.owner_label}</dd>
        </div>
        <div>
          <dt>Reviewed</dt>
          <dd>{formatDateTime(plan.last_reviewed_at)}</dd>
        </div>
      </dl>
      <div className="migration-two-column">
        <Checklist title="Steps" items={plan.steps} />
        <Checklist title="Verification" items={plan.verification_steps} />
      </div>
      <p className="migration-audit-ref">
        <ShieldCheck aria-hidden="true" size={16} />
        {plan.audit_reference}
      </p>
    </section>
  );
}

function Checklist({ items, title }: { items: string[]; title: string }) {
  return (
    <div className="migration-checklist">
      <h3>{title}</h3>
      <ol>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ol>
    </div>
  );
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
