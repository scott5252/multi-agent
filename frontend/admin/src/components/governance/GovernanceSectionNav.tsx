import type { GovernanceSection } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface GovernanceSectionNavProps {
  activeSection: string;
  onChange: (sectionId: string) => void;
  sections: GovernanceSection[];
}

export function GovernanceSectionNav({
  activeSection,
  onChange,
  sections,
}: GovernanceSectionNavProps) {
  return (
    <nav aria-label="Governance sections" className="governance-section-nav">
      {sections.map((section) => (
        <button
          aria-current={activeSection === section.section_id ? "page" : undefined}
          key={section.section_id}
          onClick={() => onChange(section.section_id)}
          type="button"
        >
          <span>{section.label}</span>
          <Badge tone={toneFor(section.status)}>{section.status}</Badge>
          <small>{section.summary}</small>
        </button>
      ))}
    </nav>
  );
}

function toneFor(status: string): "info" | "success" | "warning" | "critical" {
  if (status === "ready") {
    return "success";
  }
  if (status === "blocked" || status === "denied" || status === "unavailable") {
    return "critical";
  }
  if (status === "warning" || status === "degraded" || status === "summarized") {
    return "warning";
  }
  return "info";
}
