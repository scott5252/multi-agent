import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  acceptedWorkflowMutation,
  workflowBuilderEnvelope,
  workflowReferenceCatalog,
} from "../../test/workflowBuilderTestData";
import { WorkflowBuilderPage } from "./WorkflowBuilderPage";

vi.mock("@xyflow/react", () => ({
  Background: () => <div data-testid="graph-background" />,
  Controls: () => <div data-testid="graph-controls" />,
  ReactFlow: ({ children }: { children: ReactNode }) => (
    <div data-testid="react-flow">{children}</div>
  ),
}));

describe("WorkflowBuilderPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads builder data and saves through backend-owned actions", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => workflowBuilderEnvelope,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => workflowReferenceCatalog,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => acceptedWorkflowMutation,
        }),
    );

    render(
      <WorkflowBuilderPage
        builderUrl="/admin/app/workflows/builder.json"
        lookupsUrl="/admin/app/workflows/lookups.json"
      />,
    );

    await screen.findByText("Workflow builder");
    expect(screen.getByText("Pinned runtime inputs")).toBeInTheDocument();
    expect(screen.getByText("Runtime structure")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Save draft/ }));

    await waitFor(() => {
      expect(screen.getByText("audit-workflow-save-qa030")).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith(
      "/admin/app/workflows/drafts/00000000-0000-0000-0000-000000000030/save",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
