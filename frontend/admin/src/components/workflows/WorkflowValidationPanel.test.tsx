import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import {
  acceptedWorkflowMutation,
  workflowBuilderEnvelope,
} from "../../test/workflowBuilderTestData";
import { WorkflowValidationPanel } from "./WorkflowValidationPanel";

describe("WorkflowValidationPanel", () => {
  it("renders validation findings and calls blocked and ready actions", async () => {
    const onValidate = vi.fn();

    render(
      <WorkflowValidationPanel
        lastResult={acceptedWorkflowMutation}
        onValidate={onValidate}
        validating={false}
        validation={workflowBuilderEnvelope.validation!}
      />,
    );

    expect(screen.getByText("Backend-owned findings")).toBeInTheDocument();
    expect(screen.getByText("Required Daily briefing test evidence is stale."))
      .toBeInTheDocument();
    expect(screen.getByText("audit-workflow-save-qa030")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Run validation/ }));
    await userEvent.click(
      screen.getByRole("button", { name: /Mark evidence current/ }),
    );

    expect(onValidate).toHaveBeenNthCalledWith(1, false);
    expect(onValidate).toHaveBeenNthCalledWith(2, true);
  });
});
