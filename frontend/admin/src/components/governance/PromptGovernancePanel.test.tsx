import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import {
  governanceDashboardFixture,
  governanceMutationFixture,
} from "../../test/governanceTestData";
import { PromptGovernancePanel } from "./PromptGovernancePanel";

describe("PromptGovernancePanel", () => {
  it("renders prompt history and safe preview controls", async () => {
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

    expect(screen.getByText("Governance prompt")).toBeInTheDocument();
    expect(screen.getByText("Prompt preview is summarized before rendering.")).toBeInTheDocument();
    expect(screen.queryByText(/raw prompt/i)).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Preview redaction check/ }));
    await userEvent.click(screen.getByRole("button", { name: /Save summary/ }));

    expect(onPreview).toHaveBeenCalledWith(
      governanceDashboardFixture.prompts[0].authorized_actions[1].href,
      true,
    );
    expect(onSave).toHaveBeenCalledWith(
      governanceDashboardFixture.prompts[0].authorized_actions[0].href,
      governanceDashboardFixture.prompts[0],
    );
  });
});
