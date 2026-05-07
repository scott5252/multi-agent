import { FileText } from "lucide-react";

import type { TestRunDetail } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface TraceAndArtifactPanelProps {
  run: TestRunDetail | null;
}

export function TraceAndArtifactPanel({ run }: TraceAndArtifactPanelProps) {
  return (
    <section className="governance-panel testbench-panel" aria-labelledby="trace-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Evidence</p>
          <h2 id="trace-title">Traces and artifacts</h2>
        </div>
        <FileText aria-hidden="true" size={20} />
      </div>
      {run ? (
        <>
          <div className="trace-list">
            {run.trace_steps.map((step) => (
              <article className="governance-card" key={step.step_id}>
                <div className="card-heading">
                  <strong>{step.step_label}</strong>
                  <Badge tone={toneFor(step.status)}>{step.status}</Badge>
                </div>
                <p>{step.safe_transcript_excerpt}</p>
                <small>{step.gateway_decision}</small>
                {step.blocked_side_effects.length ? (
                  <ul className="evidence-list">
                    {step.blocked_side_effects.map((effect) => (
                      <li key={effect}>{effect}</li>
                    ))}
                  </ul>
                ) : null}
              </article>
            ))}
          </div>
          <div className="governance-card-grid">
            {run.artifacts.map((artifact) => (
              <article className="governance-card" key={artifact.artifact_reference_id}>
                <div className="card-heading">
                  <strong>{artifact.label}</strong>
                  <Badge tone={toneFor(artifact.access_status)}>
                    {artifact.access_status}
                  </Badge>
                </div>
                <p>{artifact.safe_summary}</p>
                <dl className="compact-dl">
                  <div>
                    <dt>Checksum</dt>
                    <dd>{artifact.checksum}</dd>
                  </div>
                  <div>
                    <dt>Size</dt>
                    <dd>{artifact.size_label}</dd>
                  </div>
                  <div>
                    <dt>Retention</dt>
                    <dd>{artifact.retention_state}</dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        </>
      ) : (
        <p className="safe-note">Artifact payloads are not rendered inline.</p>
      )}
    </section>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (["ready", "passed"].includes(status)) {
    return "success";
  }
  if (["blocked", "denied", "failed", "failed_assertion", "unavailable", "artifact_unavailable", "audit_unavailable", "redaction_unavailable"].includes(status)) {
    return "critical";
  }
  if (["warning", "queued", "running", "stale", "missing"].includes(status)) {
    return "warning";
  }
  return "info";
}
