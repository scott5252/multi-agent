import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { governanceDashboardFixture } from "../../test/governanceTestData";
import { ProviderGovernancePanel } from "./ProviderGovernancePanel";

describe("ProviderGovernancePanel", () => {
  it("shows safe credential diagnostics and platform probe action", async () => {
    const onProbe = vi.fn();

    render(
      <ProviderGovernancePanel
        onProbe={onProbe}
        probeResult={null}
        probing={false}
        providers={governanceDashboardFixture.providers}
      />,
    );

    expect(screen.getByText("OpenAI production reference")).toBeInTheDocument();
    expect(screen.getByText("fp_qa031_openai")).toBeInTheDocument();
    expect(screen.getByText("ModelGateway-only execution is enforced.")).toBeInTheDocument();
    expect(screen.queryByText(/resolved credential/i)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Run probe/ }));

    expect(onProbe).toHaveBeenCalledWith(
      "/admin/app/governance/providers/openai-primary/probe",
    );
  });
});
