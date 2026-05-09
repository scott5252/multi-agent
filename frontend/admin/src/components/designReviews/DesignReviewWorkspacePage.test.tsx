import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DesignReviewWorkspacePage } from "./DesignReviewWorkspacePage";

const tenantId = "11111111-1111-1111-1111-111111111111";
const sessionId = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa";
const roundId = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb";
const workflowId = "cccccccc-cccc-4ccc-8ccc-cccccccccccc";
const draftId = "dddd1111-dddd-4ddd-8ddd-dddd11111111";

function action(actionId: string, label: string, href: string, enabled = true) {
  return {
    action_id: actionId,
    action_metadata: null,
    action_token: null,
    confirmation: null,
    disabled_reason: enabled ? null : "Select a session with an authorized workflow.",
    enabled,
    href,
    label,
    method: actionId === "refresh" ? "get" : "post",
    requires_confirmation: false,
    requires_idempotency_key: actionId !== "refresh",
    variant: "primary",
  };
}

function readyTemplateSetup() {
  return {
    agent_test_suite_id: "11112222-3333-4444-8888-555566667777",
    deterministic_run_id: "22222222-3333-4444-8888-555566667777",
    display_name: "Design Reviewer Council",
    evidence_modes: ["deterministic", "model backed safe"],
    install_action: action(
      "install-template",
      "Install council template",
      "/admin/design-reviews/templates/council/install",
    ),
    latest_run_id: "22222222-3333-4444-8888-555566667777",
    model_safe_run_id: "33333333-3333-4444-8888-555566667777",
    publish_gate_status: "ready",
    ready_to_publish: true,
    required_evidence_status: "passing",
    safe_summary: "Council template has current required evidence.",
    status: "ready",
    template_key: "design-reviewer-council",
    workflow_draft_id: draftId,
    workflow_draft_revision_id: "dddd2222-dddd-4ddd-8ddd-dddd22222222",
    workflow_key: "design-reviewer-council",
    workflow_lineage_id: "dddd3333-dddd-4ddd-8ddd-dddd33333333",
  };
}

function notInstalledTemplateSetup() {
  return {
    ...readyTemplateSetup(),
    agent_test_suite_id: null,
    deterministic_run_id: null,
    display_name: null,
    evidence_modes: [],
    latest_run_id: null,
    model_safe_run_id: null,
    publish_gate_status: "not_evaluated",
    ready_to_publish: false,
    required_evidence_status: "missing",
    safe_summary: "Council template is not installed for this tenant.",
    status: "not_installed",
    workflow_draft_id: null,
    workflow_draft_revision_id: null,
    workflow_key: null,
    workflow_lineage_id: null,
  };
}

function liveEnvelope() {
  return {
    actions: {
      create_session: action("create-session", "Create session", "/admin/design-reviews/sessions"),
      launch_round: action(
        "launch-round",
        "Launch round",
        `/admin/design-reviews/sessions/${sessionId}/coordinator/launch-round`,
      ),
      manual_decision: null,
      refresh: action("refresh", "Refresh", `/admin/app/design-reviews/bootstrap.json?tenant_id=${tenantId}`),
    },
    active_scope: { label: "Acme", scope_type: "tenant", tenant_id: tenantId },
    description: "Live council sessions, round decisions, manual actions, and handoff references.",
    empty_state: null,
    provenance: {
      last_verified_at: null,
      source_detail: "Sessions, revisions, rounds, decisions, and handoffs are loaded from durable records.",
      source_kind: "live_repository",
      source_label: "Design review records",
    },
    quorum_policies: [
      {
        approval_count: 4,
        label: "Four of five, no blockers",
        policy_key: "four_of_five_no_blockers",
        reviewer_count: 5,
        summary: "At least four approved verdicts and zero blockers.",
      },
    ],
    selected_session: {
      coordinator: {
        latest_round: {
          design_review_round_id: roundId,
          design_review_session_id: sessionId,
          design_revision_id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
          quorum_count: 4,
          reviewer_count: 5,
          round_number: 1,
          status: "completed",
          workflow_run_id: "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
        },
        manual_resolution_required: false,
        next_action: "handoff",
      },
      handoff: {
        approved_revision_id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
        artifact_id: null,
        design_development_handoff_id: "ffffffff-ffff-4fff-8fff-ffffffffffff",
        output_digest: "sha256-handoff",
        safe_summary: "Approved implementation reference.",
        state: { kind: "ready", summary: "Development handoff loaded." },
        status: "ready",
      },
      manual_decisions: [],
      revisions: [
        {
          artifact_id: null,
          author_role_key: "requester",
          design_revision_id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
          payload_digest: "sha256-revision",
          previous_revision_id: null,
          revision_number: 1,
          safe_summary: "Checkout flow clarity pass.",
        },
      ],
      rounds: [
        {
          assignments: [],
          quorum_decision: {
            approval_count: 4,
            blocking_issue_count: 0,
            design_quorum_decision_id: "99999999-9999-4999-8999-999999999999",
            next_action: "handoff",
            policy_version: "four_of_five_no_blockers:v1",
            safe_rationale: "Council approved without blockers.",
            state: { kind: "ready", summary: "Quorum decision loaded." },
            status: "passed",
          },
          round: {
            design_review_round_id: roundId,
            design_review_session_id: sessionId,
            design_revision_id: "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
            quorum_count: 4,
            reviewer_count: 5,
            round_number: 1,
            status: "completed",
            workflow_run_id: "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
          },
          verdicts: [
            {
              artifact_id: null,
              blocking_issue_count: 0,
              design_reviewer_verdict_id: "12121212-1212-4212-8212-121212121212",
              output_digest: "sha256-reviewer",
              reviewer_key: "reviewer-0",
              safe_feedback_summary: "Clear layout and accessible labels.",
              score: 5,
              usage_summary: {},
              verdict: "approved",
            },
          ],
        },
      ],
      session: {
        active_revision_number: 1,
        current_revision: null,
        design_review_session_id: sessionId,
        owner_principal_id: "tenant-admin-acme",
        quorum_policy_key: "four_of_five_no_blockers",
        request_summary: "Checkout flow review",
        status: "approved",
        tenant_id: tenantId,
        workflow_version_bundle_id: workflowId,
      },
    },
    sessions: [
      {
        active_revision_number: 1,
        current_revision: null,
        design_review_session_id: sessionId,
        owner_principal_id: "tenant-admin-acme",
        quorum_policy_key: "four_of_five_no_blockers",
        request_summary: "Checkout flow review",
        status: "approved",
        tenant_id: tenantId,
        workflow_version_bundle_id: workflowId,
      },
    ],
    state: {
      action: null,
      empty_state: null,
      provenance: null,
      state: "partial_data",
      summary: "Live design review sessions and council decisions loaded.",
      title: "Design reviews loaded",
      trace_id: null,
    },
    summary_cards: [
      { card_id: "total", label: "Sessions", summary: "Live sessions in this tenant scope.", tone: "neutral", value: "1" },
      { card_id: "approved", label: "Approved", summary: "Sessions with a development handoff.", tone: "success", value: "1" },
      { card_id: "template", label: "Template", summary: "Council template has current required evidence.", tone: "success", value: "ready" },
    ],
    template_setup: readyTemplateSetup(),
    title: "Design reviews",
    workflow_options: [
      {
        display_version: "v1",
        label: "qa063-design-review-council v1",
        status: "published",
        tenant_id: tenantId,
        workflow_key: "qa063-design-review-council",
        workflow_version_bundle_id: workflowId,
      },
    ],
  };
}

function emptyEnvelope() {
  return {
    ...liveEnvelope(),
    selected_session: null,
    sessions: [],
    state: {
      action: null,
      empty_state: null,
      provenance: null,
      state: "empty",
      summary: "No live design review sessions exist for this tenant.",
      title: "No design reviews",
      trace_id: null,
    },
    summary_cards: [
      { card_id: "total", label: "Sessions", summary: "Live sessions in this tenant scope.", tone: "neutral", value: "0" },
      { card_id: "template", label: "Template", summary: "Council template is not installed for this tenant.", tone: "neutral", value: "not installed" },
    ],
    template_setup: notInstalledTemplateSetup(),
  };
}

describe("DesignReviewWorkspacePage", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders live session, verdict, quorum, and handoff state", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => liveEnvelope(),
      }),
    );

    render(<DesignReviewWorkspacePage workspaceUrl="/admin/app/design-reviews/bootstrap.json" />);

    await screen.findByRole("heading", { name: "Checkout flow review" });
    expect(
      screen.getAllByText("Council template has current required evidence.").length,
    ).toBeGreaterThan(0);
    expect(screen.getByText(/model backed safe/)).toBeInTheDocument();
    expect(screen.getByText("Clear layout and accessible labels.")).toBeInTheDocument();
    expect(screen.getByText("Approved implementation reference.")).toBeInTheDocument();
    expect(screen.getByText("passed")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open runtime graph" })).toHaveAttribute(
      "href",
      `/admin/app/operations?tenant_id=${tenantId}&run_id=eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee&panel=runtime-graph#runtime-run-graph`,
    );
    expect(screen.queryByText(/raw prompt/i)).not.toBeInTheDocument();
  });

  it("selects a published workflow from setup handoff query links", async () => {
    const customWorkflowId = "99999999-9999-4999-8999-999999999999";
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          ...liveEnvelope(),
          workflow_options: [
            ...liveEnvelope().workflow_options,
            {
              display_version: "v2",
              label: "custom-launch-workflow v2",
              status: "published",
              tenant_id: tenantId,
              workflow_key: "custom-launch-workflow",
              workflow_version_bundle_id: customWorkflowId,
            },
          ],
        }),
      }),
    );

    render(
      <DesignReviewWorkspacePage
        workspaceUrl={`/admin/app/design-reviews/bootstrap.json?workflow_version_bundle_id=${customWorkflowId}`}
      />,
    );

    await screen.findByRole("heading", { name: "Checkout flow review" });
    expect(screen.getAllByLabelText("Workflow")[0]).toHaveValue(customWorkflowId);
  });

  it("shows truthful empty state without sample records", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => emptyEnvelope(),
      }),
    );

    render(<DesignReviewWorkspacePage workspaceUrl="/admin/app/design-reviews/bootstrap.json" />);

    await screen.findByText("No live sessions exist for this tenant.");
    expect(screen.queryByText("Checkout flow review")).not.toBeInTheDocument();
  });

  it("creates sessions through backend action links", async () => {
    const fetchSpy = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => emptyEnvelope(),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ design_review_session_id: sessionId }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => liveEnvelope(),
      });
    vi.stubGlobal("fetch", fetchSpy);

    render(<DesignReviewWorkspacePage workspaceUrl="/admin/app/design-reviews/bootstrap.json" />);

    await screen.findByText("No live sessions exist for this tenant.");
    await userEvent.type(screen.getByLabelText("Request summary"), "Review checkout flow");
    await userEvent.click(screen.getByRole("button", { name: "Create session" }));

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith(
        "/admin/design-reviews/sessions",
        expect.objectContaining({ method: "POST" }),
      );
    });
  });

  it("installs the council template through backend action links", async () => {
    const fetchSpy = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => emptyEnvelope(),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          ready_to_publish: true,
          workflow_draft_id: draftId,
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => liveEnvelope(),
      });
    vi.stubGlobal("fetch", fetchSpy);

    render(<DesignReviewWorkspacePage workspaceUrl="/admin/app/design-reviews/bootstrap.json" />);

    await waitFor(() => {
      expect(
        screen.getAllByText("Council template is not installed for this tenant.")
          .length,
      ).toBeGreaterThan(0);
    });
    await userEvent.click(screen.getByRole("button", { name: "Install template" }));

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith(
        "/admin/design-reviews/templates/council/install",
        expect.objectContaining({ method: "POST" }),
      );
    });
    const [, request] = fetchSpy.mock.calls[1];
    expect(JSON.parse(String(request.body))).toMatchObject({
      safe_mode: "both",
      template_key: "design-reviewer-council",
      tenant_id: tenantId,
    });
  });
});
