import { Target } from "lucide-react";

import type {
  AssertionDefinition,
  TargetRevisionBinding,
  TestBenchFormMetadata,
} from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface AssertionAndTargetPanelProps {
  metadata: TestBenchFormMetadata;
  targetBinding: TargetRevisionBinding;
}

export function AssertionAndTargetPanel({
  metadata,
  targetBinding,
}: AssertionAndTargetPanelProps) {
  return (
    <section className="governance-panel testbench-panel" aria-labelledby="assertion-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Contracts</p>
          <h2 id="assertion-title">Targets and assertions</h2>
        </div>
        <Target aria-hidden="true" size={20} />
      </div>
      <div className="governance-review-grid">
        <article className="governance-card">
          <div className="card-heading">
            <strong>{targetBinding.target_label}</strong>
            <Badge tone={toneFor(targetBinding.revision_status)}>
              {targetBinding.revision_status}
            </Badge>
          </div>
          <p>{targetBinding.remediation}</p>
          <dl className="compact-dl">
            <div>
              <dt>Selected</dt>
              <dd>{targetBinding.selected_revision}</dd>
            </div>
            <div>
              <dt>Current</dt>
              <dd>{targetBinding.current_revision}</dd>
            </div>
          </dl>
        </article>
        <article className="governance-card">
          <strong>Authorized targets</strong>
          <ul className="evidence-list">
            {metadata.target_options.map((target) => (
              <li key={target.target_id}>
                {target.label}: {target.safe_summary}
              </li>
            ))}
          </ul>
        </article>
      </div>
      <div className="assertion-list">
        {metadata.assertion_templates.map((assertion) => (
          <AssertionCard assertion={assertion} key={assertion.assertion_id} />
        ))}
      </div>
    </section>
  );
}

function AssertionCard({ assertion }: { assertion: AssertionDefinition }) {
  return (
    <article className="governance-card assertion-card">
      <div className="card-heading">
        <strong>{assertion.label}</strong>
        <Badge tone={toneFor(assertion.validation_status)}>
          {assertion.validation_status}
        </Badge>
      </div>
      <dl className="compact-dl">
        <div>
          <dt>Path</dt>
          <dd>{assertion.path_summary}</dd>
        </div>
        <div>
          <dt>Comparator</dt>
          <dd>{assertion.comparator}</dd>
        </div>
        <div>
          <dt>Expected</dt>
          <dd>{assertion.expected_summary}</dd>
        </div>
      </dl>
    </article>
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
