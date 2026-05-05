import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { workflowReferenceCatalog } from "../../test/workflowBuilderTestData";
import { WorkflowReferencePicker } from "./WorkflowReferencePicker";

describe("WorkflowReferencePicker", () => {
  it("renders reference groups and emits prompt/profile changes", async () => {
    const onPromptChange = vi.fn();
    const onProfileChange = vi.fn();

    render(
      <WorkflowReferencePicker
        catalog={workflowReferenceCatalog}
        onProfileChange={onProfileChange}
        onPromptChange={onPromptChange}
        selectedProfileRef="profile-briefing-safe"
        selectedPromptRef="prompt-daily-briefing-v3"
      />,
    );

    expect(screen.getByText("Pinned runtime inputs")).toBeInTheDocument();
    expect(screen.getByText("Weather connector skill")).toBeInTheDocument();
    expect(screen.getByText("Daily briefing required suite")).toBeInTheDocument();

    await userEvent.selectOptions(
      screen.getByLabelText("Prompt"),
      "prompt-daily-briefing-v3",
    );
    await userEvent.selectOptions(
      screen.getByLabelText("Runtime profile"),
      "profile-briefing-safe",
    );

    expect(onPromptChange).toHaveBeenCalledWith("prompt-daily-briefing-v3");
    expect(onProfileChange).toHaveBeenCalledWith("profile-briefing-safe");
  });
});
