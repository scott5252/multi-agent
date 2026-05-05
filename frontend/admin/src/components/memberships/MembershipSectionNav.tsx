import type { MembershipSection } from "../../api/generated/reactAdminApi";

interface MembershipSectionNavProps {
  activeSection: string;
  onChange: (section: string) => void;
  sections: MembershipSection[];
}

export function MembershipSectionNav({
  activeSection,
  onChange,
  sections,
}: MembershipSectionNavProps) {
  return (
    <nav className="workflow-section-rail membership-section-rail" aria-label="Membership sections">
      {sections.map((section) => (
        <a
          aria-current={activeSection === section.section_id ? "page" : undefined}
          href={`#${section.section_id}`}
          key={section.section_id}
          onClick={() => onChange(section.section_id)}
        >
          <span>{section.label}</span>
          <small>{section.status}</small>
        </a>
      ))}
    </nav>
  );
}
