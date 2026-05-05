import type { TestBenchSection } from "../../api/generated/reactAdminApi";
import { Badge } from "../primitives";

interface TestBenchSectionNavProps {
  activeSection: string;
  onChange: (sectionId: string) => void;
  sections: TestBenchSection[];
}

export function TestBenchSectionNav({
  activeSection,
  onChange,
  sections,
}: TestBenchSectionNavProps) {
  return (
    <nav className="governance-section-nav" aria-label="Test bench sections">
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
  if (["ready", "passed"].includes(status)) {
    return "success";
  }
  if (["blocked", "denied", "failed", "unavailable"].includes(status)) {
    return "critical";
  }
  if (["warning", "queued", "running", "stale", "missing"].includes(status)) {
    return "warning";
  }
  return "info";
}
