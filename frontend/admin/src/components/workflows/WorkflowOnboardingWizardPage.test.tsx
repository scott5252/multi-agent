import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  acceptedWorkflowMutation,
  workflowBuilderEnvelope,
  workflowReferenceCatalog,
} from "../../test/workflowBuilderTestData";
import { WorkflowOnboardingWizardPage } from "./WorkflowOnboardingWizardPage";

describe("WorkflowOnboardingWizardPage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders a fixed-frame wizard and saves evidence through the existing draft API", async () => {
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
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => workflowBuilderEnvelope,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => workflowReferenceCatalog,
        }),
    );

    render(
      <WorkflowOnboardingWizardPage
        builderUrl="/admin/app/workflows/builder.json"
        lookupsUrl="/admin/app/workflows/lookups.json"
      />,
    );

    expect(await screen.findByRole("heading", { name: "Set up workflow" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /Evidence/ }));
    await userEvent.click(screen.getByRole("button", { name: /Attach evidence/ }));
    await userEvent.click(screen.getByRole("button", { name: /Save evidence/ }));

    await waitFor(() => {
      expect(screen.getByText("Draft saved as a new explicit revision.")).toBeInTheDocument();
    });
    const saveCall = vi.mocked(fetch).mock.calls.find((call) =>
      String(call[0]).includes("/save"),
    );
    const saveBody = JSON.parse(String(saveCall?.[1]?.body));
    expect(saveBody.client_context.form_version).toBe(
      "workflow-onboarding-wizard.v1",
    );
    expect(saveBody.document.test_requirements[0].requirement_key).toBe(
      "onboarding-required-evidence",
    );
    expect(JSON.stringify(saveBody.document)).not.toContain("raw transcript");
  });

  it("creates a generic blueprint from clean-tenant scenario intake", async () => {
    const emptyBuilder = {
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
    };
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => emptyBuilder,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => workflowReferenceCatalog,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            ...acceptedWorkflowMutation,
            next_action: {
              action_id: "workflow-open-created-draft",
              href: "/admin/app/workflows/drafts/00000000-0000-0000-0000-000000000030",
              label: "Open draft",
              method: "get",
              variant: "primary",
            },
            summary: "Workflow draft created through durable registry state.",
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => workflowBuilderEnvelope,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => workflowReferenceCatalog,
        }),
    );

    render(
      <WorkflowOnboardingWizardPage
        builderUrl="/admin/app/workflows/builder.json"
        lookupsUrl="/admin/app/workflows/lookups.json"
      />,
    );

    expect(await screen.findByRole("heading", { name: "Scenario intake" })).toBeInTheDocument();
    await userEvent.clear(screen.getByLabelText("Workflow name"));
    await userEvent.type(screen.getByLabelText("Workflow name"), "Supplier Risk Intake");
    await userEvent.click(screen.getByRole("button", { name: /Create durable draft/ }));

    await waitFor(() => {
      expect(
        screen.getByText("Workflow draft created through durable registry state."),
      ).toBeInTheDocument();
    });
    const createCall = vi.mocked(fetch).mock.calls.find(
      (call) => String(call[0]) === emptyBuilder.create_state.create_action.href,
    );
    const createBody = JSON.parse(String(createCall?.[1]?.body));
    expect(createBody.slug).toBe("supplier-risk-intake");
    expect(createBody.document.roles).toHaveLength(3);
    expect(createBody.document.contracts[0].contract_key).toBe("scenario-request");
    expect(JSON.stringify(createBody.document)).not.toContain("Daily Intelligence Briefing");
    expect(JSON.stringify(createBody.document)).not.toContain("Design Reviewer Council");
  });
});
