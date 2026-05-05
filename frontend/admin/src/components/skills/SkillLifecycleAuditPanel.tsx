import { History } from "lucide-react";

import type { SkillLifecycleAuditRecord } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface SkillLifecycleAuditPanelProps {
  auditTimeline: SkillLifecycleAuditRecord[];
}

export function SkillLifecycleAuditPanel({
  auditTimeline,
}: SkillLifecycleAuditPanelProps) {
  return (
    <section className="governance-panel skill-panel" aria-labelledby="audit-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Audit</p>
          <h2 id="audit-title">Lifecycle timeline</h2>
        </div>
        <Badge tone="info">{auditTimeline.length} records</Badge>
      </div>
      <div className="timeline-list">
        {auditTimeline.map((record) => (
          <article className="timeline-row" key={record.record_id}>
            <History aria-hidden="true" size={18} />
            <div>
              <div className="card-heading">
                <strong>{record.action}</strong>
                <Badge tone={toneFor(record.outcome)}>{record.outcome}</Badge>
              </div>
              <p>{record.safe_diff_summary}</p>
              <small>
                {record.tenant_scope_label} · {record.audit_reference_id}
              </small>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (["ready", "passed", "published"].includes(status)) {
    return "success";
  }
  if (["blocked", "denied", "failed", "unavailable", "withdrawn"].includes(status)) {
    return "critical";
  }
  if (["degraded", "warning", "queued", "quarantined", "stale"].includes(status)) {
    return "warning";
  }
  return "info";
}
