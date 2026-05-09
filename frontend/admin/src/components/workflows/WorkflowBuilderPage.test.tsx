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
          json: async () => ({
            profile_options: [],
            prompt_options: [],
            provider_options: [],
            skill_options: [],
            subworkflow_options: [],
            test_suite_options: [],
          }),
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
    expect(screen.getByText("Custom workflow launch checklist")).toBeInTheDocument();
    expect(screen.getByText("Pinned runtime inputs")).toBeInTheDocument();
    expect(screen.getByText("Per-Agent Bindings")).toBeInTheDocument();
    expect(screen.getByText("Required publish evidence")).toBeInTheDocument();
    expect(screen.getByText("Workflow structure")).toBeInTheDocument();
    expect(await screen.findByText("Draft communication")).toBeInTheDocument();
    expect(screen.getByText("Published version communication")).toBeInTheDocument();

    await userEvent.click(
      screen.getByRole("button", { name: /Apply three-agent starter/ }),
    );
    await userEvent.click(screen.getByRole("button", { name: /Save draft/ }));

    await waitFor(() => {
      expect(screen.getByText("audit-workflow-save-qa030")).toBeInTheDocument();
    });
    expect(fetch).toHaveBeenCalledWith(
      "/admin/app/workflows/drafts/00000000-0000-0000-0000-000000000030/save",
      expect.objectContaining({ method: "POST" }),
    );
    const saveCall = vi.mocked(fetch).mock.calls.at(-1);
    const saveBody = JSON.parse(String(saveCall?.[1]?.body));
    expect(saveBody.document.workflow_key).toBe("daily-briefing-workflow");
    expect(saveBody.selected_prompt_ref).toBe("prompt-daily-briefing-v3");
    expect(saveBody.selected_profile_ref).toBe("profile-briefing-safe");
    expect(saveBody.document.prompt_profile_references.length).toBeGreaterThan(0);
    expect(saveBody.document.test_requirements).toHaveLength(1);
    expect(JSON.stringify(saveBody.document)).not.toContain(
      "Classify the request using only authorized workflow context",
    );
    expect(saveBody.document.roles).toHaveLength(3);
    expect(saveBody.document.roles[2].role_key).toBe("synthesis");
    expect(
      saveBody.document.nodes.some(
        (node: { node_type: string }) => node.node_type === "join",
      ),
    ).toBe(true);
    expect(saveBody.client_context.form_version).toBe(
      "workflow-graph-role-builder.v1",
    );
  });

  it("launches deterministic evidence and persists safe requirement state", async () => {
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
          json: async () => ({
            audit_reference_id: "audit-case",
            diagnostics: ["Raw fixture bodies and evaluator prompts were not returned."],
            field_errors: [],
            status: "accepted",
            summary: "Test case saved with structured assertion descriptors.",
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            audit_reference_id: "audit-run",
            diagnostics: [],
            field_errors: [],
            run: {
              assertion_diagnostics: [],
              summary: {
                finished_label: "Now",
                run_id: "run-current-evidence",
                status: "passed",
              },
            },
            status: "accepted",
            summary: "Test run persisted with backend-owned progress evidence.",
          }),
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

    await screen.findByText("Required publish evidence");
    await userEvent.click(screen.getByRole("button", { name: /Add safe case/ }));
    expect(
      await screen.findByText("Test case saved with structured assertion descriptors."),
    ).toBeInTheDocument();
    await userEvent.click(
      screen.getByRole("button", { name: /Launch deterministic run/ }),
    );
    expect(
      await screen.findAllByText(
        "Test run persisted with backend-owned progress evidence.",
      ),
    ).not.toHaveLength(0);
    await userEvent.click(screen.getByRole("button", { name: /Save draft/ }));

    await waitFor(() => {
      const saveCall = vi.mocked(fetch).mock.calls.at(-1);
      const saveBody = JSON.parse(String(saveCall?.[1]?.body));
      expect(saveBody.document.test_requirements[0].latest_result_id).toBe(
        "run-current-evidence",
      );
      expect(saveBody.document.test_requirements[0].latest_result_status).toBe(
        "passed",
      );
      expect(JSON.stringify(saveBody.document)).not.toContain("raw transcript");
    });
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
