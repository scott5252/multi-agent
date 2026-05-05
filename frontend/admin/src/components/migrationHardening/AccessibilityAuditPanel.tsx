import type { MigrationAccessibilityAudit } from "../../api/generated/reactAdminApi";
import { StatusBadge } from "./RouteDecisionBadges";

export function AccessibilityAuditPanel({
  audit,
}: {
  audit: MigrationAccessibilityAudit;
}) {
  const rows = [
    ["Keyboard", audit.keyboard_status],
    ["Focus", audit.focus_status],
    ["Landmarks", audit.landmark_status],
    ["Labels", audit.label_status],
    ["Contrast states", audit.contrast_state_status],
    ["Text overlap", audit.text_overlap_status],
  ] as const;
  return (
    <section className="migration-panel" aria-labelledby="migration-accessibility-title">
      <div className="migration-panel-heading">
        <div>
          <p className="eyebrow">Accessibility</p>
          <h2 id="migration-accessibility-title">Audit coverage</h2>
        </div>
        <StatusBadge status={audit.status} label={audit.status} />
      </div>
      <div className="migration-audit-grid">
        {rows.map(([label, status]) => (
          <div className="migration-audit-row" key={label}>
            <span>{label}</span>
            <StatusBadge status={status} label={status} />
          </div>
        ))}
      </div>
      <div className="migration-chip-list" aria-label="Viewport coverage">
        {audit.viewport_coverage.map((viewport) => (
          <span key={viewport}>{viewport}</span>
        ))}
      </div>
      <ul className="migration-evidence-list">
        {audit.evidence_references.map((evidence) => (
          <li key={evidence}>{evidence}</li>
        ))}
      </ul>
    </section>
  );
}
