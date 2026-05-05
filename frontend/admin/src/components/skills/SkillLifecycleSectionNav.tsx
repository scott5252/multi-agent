import type { SkillLifecycleSection } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface SkillLifecycleSectionNavProps {
  activeSection: string;
  onChange: (sectionId: string) => void;
  sections: SkillLifecycleSection[];
}

export function SkillLifecycleSectionNav({
  activeSection,
  onChange,
  sections,
}: SkillLifecycleSectionNavProps) {
  return (
    <nav aria-label="Skill lifecycle sections" className="governance-section-nav">
      {sections.map((section) => (
        <button
          aria-current={section.section_id === activeSection ? "page" : undefined}
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
  if (status === "ready" || status === "passed" || status === "published") {
    return "success";
  }
  if (status === "blocked" || status === "denied" || status === "failed") {
    return "critical";
  }
  if (status === "degraded" || status === "warning" || status === "queued") {
    return "warning";
  }
  return "info";
}
