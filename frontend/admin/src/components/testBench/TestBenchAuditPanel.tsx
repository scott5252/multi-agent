import { History } from "lucide-react";

import type { TestBenchAuditRecord } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface TestBenchAuditPanelProps {
  auditTimeline: TestBenchAuditRecord[];
}

export function TestBenchAuditPanel({ auditTimeline }: TestBenchAuditPanelProps) {
  return (
    <section className="governance-panel testbench-panel" aria-labelledby="audit-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Governance</p>
          <h2 id="audit-title">Audit timeline</h2>
        </div>
        <History aria-hidden="true" size={20} />
      </div>
      <div className="timeline-list">
        {auditTimeline.map((record) => (
          <article className="governance-card timeline-card" key={record.record_id}>
            <div className="card-heading">
              <strong>{record.action}</strong>
              <Badge tone={toneFor(record.outcome)}>{record.outcome}</Badge>
            </div>
            <p>{record.safe_diff_summary}</p>
            <dl className="compact-dl">
              <div>
                <dt>Actor</dt>
                <dd>{record.actor_label}</dd>
              </div>
              <div>
                <dt>Scope</dt>
                <dd>{record.tenant_scope_label}</dd>
              </div>
              <div>
                <dt>Audit</dt>
                <dd>{record.audit_reference_id}</dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    </section>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (["ready", "passed"].includes(status)) {
    return "success";
  }
  if (["blocked", "denied", "failed", "unavailable", "artifact_unavailable", "audit_unavailable", "redaction_unavailable"].includes(status)) {
    return "critical";
  }
  if (["warning", "queued", "running", "stale", "missing"].includes(status)) {
    return "warning";
  }
  return "info";
}
