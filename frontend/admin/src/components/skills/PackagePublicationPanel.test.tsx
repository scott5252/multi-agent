import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { skillLifecycleDashboardFixture } from "../../test/skillLifecycleTestData";
import { PackagePublicationPanel } from "./PackagePublicationPanel";

describe("PackagePublicationPanel", () => {
  it("renders safe candidate metadata and calls backend-owned actions", async () => {
    const onSaveCandidate = vi.fn();
    const onValidate = vi.fn();
    const onPublish = vi.fn();
    const publication = skillLifecycleDashboardFixture.platform_publication;

    if (!publication) {
      throw new Error("expected platform publication fixture");
    }

    render(
      <PackagePublicationPanel
        candidateResult={null}
        onPublish={onPublish}
        onSaveCandidate={onSaveCandidate}
        onValidate={onValidate}
        publication={publication}
        publishResult={null}
        validationResult={null}
      />,
    );

    expect(screen.getByText("Package publication")).toBeInTheDocument();
    expect(screen.getByText("sha256:qa032dailybriefing")).toBeInTheDocument();
    expect(screen.queryByText(/qa032-secret-value/)).not.toBeInTheDocument();
    expect(screen.queryByText(/raw manifest/i)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Save candidate/ }));
    await userEvent.click(screen.getByRole("button", { name: /Validate/ }));
    await userEvent.click(screen.getByRole("button", { name: /Publish/ }));

    expect(onSaveCandidate).toHaveBeenCalledWith("/admin/app/skills/packages/candidates");
    expect(onValidate).toHaveBeenCalledWith(
      "/admin/app/skills/packages/candidates/qa032-candidate/validate",
      true,
    );
    expect(onPublish).toHaveBeenCalledWith(
      "/admin/app/skills/packages/candidates/qa032-candidate/publish",
    );
  });
});
