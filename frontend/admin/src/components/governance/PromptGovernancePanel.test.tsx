import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import {
  governanceDashboardFixture,
  governanceMutationFixture,
} from "../../test/governanceTestData";
import { PromptGovernancePanel } from "./PromptGovernancePanel";

describe("PromptGovernancePanel", () => {
  it("renders prompt history and fixture-safe preview controls", async () => {
    const onPreview = vi.fn();
    const onSave = vi.fn();

    render(
      <PromptGovernancePanel
        mutationResult={governanceMutationFixture}
        onPreview={onPreview}
        onSave={onSave}
        preview={governanceDashboardFixture.prompt_preview}
        prompts={governanceDashboardFixture.prompts}
      />,
    );

    expect(screen.getByText("Daily briefing prompt")).toBeInTheDocument();
    expect(screen.getByText("Daily briefing preview uses safe fixture summaries.")).toBeInTheDocument();
    expect(screen.queryByText(/raw prompt/i)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Preview unsafe fixture/ }));
    await userEvent.click(screen.getByRole("button", { name: /Save summary/ }));

    expect(onPreview).toHaveBeenCalledWith(
      "/admin/app/governance/prompts/daily-briefing/preview",
      true,
    );
    expect(onSave).toHaveBeenCalledWith(
      "/admin/app/governance/prompts/daily-briefing/save",
    );
  });
});
