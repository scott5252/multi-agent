import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  acceptedWorkflowMutation,
  agentGraphFixture,
  publishedAgentGraphFixture,
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
          json: async () => agentGraphFixture,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => publishedAgentGraphFixture,
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
    expect(await screen.findByText("Draft communication")).toBeInTheDocument();
    expect(screen.getByText("Published version communication")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /Save draft/ }));

    await waitFor(() => {
      expect(screen.getByText("audit-workflow-save-qa030")).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith(
      "/admin/app/workflows/drafts/00000000-0000-0000-0000-000000000030/save",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("renders truthful empty state metadata when no workflow draft exists", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            ...workflowBuilderEnvelope,
            actions: [],
            draft: null,
            empty_state: {
              reason: "no_records",
              setup_hint: "Create a workflow draft to populate this page.",
              summary: "The active scope has no durable workflow draft.",
              title: "No active workflow draft",
            },
            json_inspector: null,
            publish_readiness: null,
            registry: {
              ...workflowBuilderEnvelope.registry,
              empty_state: {
                reason: "no_records",
                setup_hint: "Create a workflow draft to populate the registry.",
                summary: "The active scope has no durable workflow records.",
                title: "No workflows found",
              },
              items: [],
              pagination: {
                ...workflowBuilderEnvelope.registry.pagination!,
                total_items: 0,
              },
            },
            sharing: null,
            state: null,
            validation: null,
            version_detail: null,
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => workflowReferenceCatalog,
        }),
    );

    render(
      <WorkflowBuilderPage
        builderUrl="/admin/app/workflows/builder.json"
        lookupsUrl="/admin/app/workflows/lookups.json"
      />,
    );

    expect(await screen.findAllByText("No active workflow draft")).toHaveLength(2);
    expect(screen.getAllByText("No workflows found")).toHaveLength(2);
    expect(
      screen.getAllByText("The active scope has no durable workflow records."),
    ).toHaveLength(2);
    expect(
      screen.queryByRole("button", { name: /Save draft/ }),
    ).not.toBeInTheDocument();
  });
});
