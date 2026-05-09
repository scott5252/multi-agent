import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import {
  acceptedWorkflowMutation,
  workflowBuilderEnvelope,
} from "../../test/workflowBuilderTestData";
import { WorkflowPublishPanel } from "./WorkflowPublishPanel";

describe("WorkflowPublishPanel", () => {
  it("renders required evidence and publish actions", async () => {
    const onPublish = vi.fn();

    render(
      <WorkflowPublishPanel
        lastResult={{
          ...acceptedWorkflowMutation,
          confirmation: {
            confirm_label: "Publish workflow",
            summary: "This creates an immutable published workflow bundle.",
            title: "Publish workflow",
          },
          status: "confirmation_required",
        }}
        onPublish={onPublish}
        publishing={false}
        readiness={workflowBuilderEnvelope.publish_readiness!}
      />,
    );

    expect(screen.getByText("Evidence and decision")).toBeInTheDocument();
    expect(screen.getByText("artifact-ref-qa030-stale-evidence"))
      .toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /Review evidence setup/ }),
    ).toHaveAttribute("href", "/admin/agent-tests/ui");

    await userEvent.click(
      screen.getByRole("button", { name: /Check publish gate/ }),
    );
    await userEvent.click(screen.getByRole("button", { name: /Prepare publish/ }));
    await userEvent.click(screen.getByRole("button", { name: /Confirm publish/ }));

    expect(onPublish).toHaveBeenNthCalledWith(1, false, false);
    expect(onPublish).toHaveBeenNthCalledWith(2, true, false);
    expect(onPublish).toHaveBeenNthCalledWith(3, true, true);
  });
});
