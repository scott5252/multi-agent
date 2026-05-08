import type {
  TransitionalLabelFinding,
  TransitionalLabelGate,
} from "../../api/generated/reactAdminApi";

const classificationLabels: Record<string, string> = {
  allowed_implementation_reference: "Implementation",
  blocking_transitional_label: "Blocking",
  historical_reference: "Historical",
  internal_generated_identifier: "Internal",
  technical_qa_context: "Technical",
};

export function TransitionalLabelGatePanel({
  gate,
}: {
  gate: TransitionalLabelGate | null;
}) {
  if (!gate) {
    return (
      <section
        className="migration-panel transitional-label-gate"
        aria-labelledby="transitional-label-gate-title"
      >
        <div className="migration-panel-heading">
          <div>
            <p className="eyebrow">Admin terminology</p>
            <h2 id="transitional-label-gate-title">Transitional label gate</h2>
          </div>
          <span className="migration-count">Unavailable</span>
        </div>
        <p className="migration-empty">Admin terminology gate evidence is unavailable for this scope.</p>
      </section>
    );
  }

  const summary = gate.summary;
  const visibleFindings = gate.findings.slice(0, 8);

  return (
    <section
      className="migration-panel transitional-label-gate"
      aria-labelledby="transitional-label-gate-title"
    >
      <div className="migration-panel-heading">
        <div>
          <p className="eyebrow">Admin terminology</p>
          <h2 id="transitional-label-gate-title">Transitional label gate</h2>
        </div>
        <span className={`migration-count live-ci-status ${summary.ci_status}`}>
          {summary.ci_status}
        </span>
      </div>

      <dl className="migration-summary-grid compact" aria-label="Transitional label counts">
        <Metric label="Blocked" value={summary.blocked_count} />
        <Metric label="Allowed" value={summary.allowed_reference_count} />
        <Metric label="Surfaces" value={summary.surfaces_scanned} />
        <Metric label="Routes" value={summary.routes_scanned} />
        <Metric label="Screenshots" value={summary.screenshots_checked} />
      </dl>

      <p className="migration-next-step">{summary.next_step}</p>

      {visibleFindings.length ? (
        <div className="migration-table-wrap">
          <table className="admin-table migration-table live-data-table">
            <thead>
              <tr>
                <th scope="col">Finding</th>
                <th scope="col">Classification</th>
                <th scope="col">Rationale</th>
                <th scope="col">Owner</th>
              </tr>
            </thead>
            <tbody>
              {visibleFindings.map((finding) => (
                <FindingRow finding={finding} key={finding.finding_id} />
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="migration-empty">No transitional admin label findings are reachable for this scope.</p>
      )}

      <article className="migration-checklist">
        <h3>Evidence</h3>
        <ul className="migration-evidence-list">
          {gate.evidence.map((evidence) => (
            <li key={evidence.evidence_id}>
              {formatEnum(evidence.evidence_type)}: <code>{evidence.evidence_id}</code>
              <small>{evidence.reference}</small>
            </li>
          ))}
        </ul>
      </article>
    </section>
  );
}

function FindingRow({ finding }: { finding: TransitionalLabelFinding }) {
  return (
    <tr>
      <td>
        <strong>{finding.surface_id}</strong>
        <small>{finding.matched_text}</small>
      </td>
      <td>
        <span className={`jinja-classification live-status ${finding.severity}`}>
          {classificationLabels[finding.classification] ?? formatEnum(finding.classification)}
        </span>
        <small>{formatEnum(finding.severity)}</small>
      </td>
      <td>
        <small>{finding.rationale}</small>
        {finding.remediation ? <small>{finding.remediation}</small> : null}
      </td>
      <td>
        <small>{finding.owner}</small>
      </td>
    </tr>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

function formatEnum(value: string): string {
  return value.replaceAll("_", " ");
}
