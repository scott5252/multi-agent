import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { skillLifecycleDashboardFixture } from "../../test/skillLifecycleTestData";
import { SkillLifecycleAuditPanel } from "./SkillLifecycleAuditPanel";

describe("SkillLifecycleAuditPanel", () => {
  it("renders safe audit timeline records", () => {
    render(
      <SkillLifecycleAuditPanel
        auditTimeline={skillLifecycleDashboardFixture.audit_timeline}
      />,
    );

    expect(screen.getByText("Lifecycle timeline")).toBeInTheDocument();
    expect(screen.getByText("configured_credentials")).toBeInTheDocument();
    expect(screen.getByText(/Credential reference fingerprint changed/)).toBeInTheDocument();
    expect(screen.getByText(/audit-credential-configured-qa032/)).toBeInTheDocument();
    expect(screen.queryByText(/qa032-secret-value/)).not.toBeInTheDocument();
    expect(screen.queryByText(/raw manifest/i)).not.toBeInTheDocument();
  });
});
