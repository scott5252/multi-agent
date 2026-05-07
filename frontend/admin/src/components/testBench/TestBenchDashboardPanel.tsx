import { AlertTriangle, CheckCircle2, Gauge } from "lucide-react";

import type {
  PublishGateEvidence,
  TestBenchSummaryMetric,
} from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface TestBenchDashboardPanelProps {
  gateAlerts: PublishGateEvidence[];
  metrics: TestBenchSummaryMetric[];
}

export function TestBenchDashboardPanel({
  gateAlerts,
  metrics,
}: TestBenchDashboardPanelProps) {
  return (
    <section className="governance-panel testbench-panel" aria-labelledby="testbench-dashboard-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Overview</p>
          <h2 id="testbench-dashboard-title">Release confidence</h2>
        </div>
        <Gauge aria-hidden="true" size={20} />
      </div>
      <div className="testbench-metric-grid">
        {metrics.map((metric) => (
          <article className="governance-card metric-card" key={metric.metric_id}>
            <div className="card-heading">
              <strong>{metric.label}</strong>
              <Badge tone={toneFor(metric.status)}>{metric.status}</Badge>
            </div>
            <p className="metric-value">{metric.value}</p>
            <p>{metric.summary}</p>
          </article>
        ))}
      </div>
      <div className="gate-alert-row" aria-label="Publish gate alerts">
        {gateAlerts.map((gate) => (
          <article className="gate-alert" key={gate.gate_id}>
            {gate.evidence_status === "passed" ? (
              <CheckCircle2 aria-hidden="true" size={18} />
            ) : (
              <AlertTriangle aria-hidden="true" size={18} />
            )}
            <div>
              <strong>{gate.required_suite_label}</strong>
              <p>{gate.reason}</p>
            </div>
            <Badge tone={toneFor(gate.evidence_status)}>{gate.evidence_status}</Badge>
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
