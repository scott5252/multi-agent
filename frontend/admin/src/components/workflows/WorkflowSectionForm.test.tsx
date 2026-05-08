import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import {
  acceptedWorkflowMutation,
  workflowBuilderEnvelope,
} from "../../test/workflowBuilderTestData";
import {
  WorkflowSectionForm,
  type WorkflowDraftFormValues,
} from "./WorkflowSectionForm";

describe("WorkflowSectionForm", () => {
  it("renders draft metadata, dirty state, save, and stale controls", async () => {
    const values: WorkflowDraftFormValues = {
      description: workflowBuilderEnvelope.draft!.description,
      join_policy: "wait_for_required_branches",
      name: workflowBuilderEnvelope.draft!.name,
      selected_profile_ref: "profile-briefing-safe",
      selected_prompt_ref: "prompt-daily-briefing-v3",
    };
    const onChange = vi.fn();
    const onSave = vi.fn();
    const onForceStale = vi.fn();

    render(
      <WorkflowSectionForm
        dirty
        draft={workflowBuilderEnvelope.draft!}
        error={null}
        joinPolicies={workflowBuilderEnvelope.draft!.graph.join_policies}
        mutationResult={acceptedWorkflowMutation}
        onChange={onChange}
        onForceStale={onForceStale}
        onSave={onSave}
        saving={false}
        sections={workflowBuilderEnvelope.sections}
        values={values}
      />,
    );

    expect(screen.getByText("Unsaved changes")).toBeInTheDocument();
    expect(screen.getByText("draft-rev-qa030-current")).toBeInTheDocument();
    expect(screen.getByText("audit-workflow-save-qa030")).toBeInTheDocument();

    await userEvent.clear(screen.getByLabelText("Name"));
    await userEvent.type(screen.getByLabelText("Name"), "Updated briefing");
    expect(onChange).toHaveBeenCalled();

    await userEvent.click(screen.getByRole("button", { name: /Save draft/ }));
    expect(onSave).toHaveBeenCalled();

    await userEvent.click(
      screen.getByRole("button", { name: /Simulate stale save/ }),
    );
    expect(onForceStale).toHaveBeenCalled();
  });
});
