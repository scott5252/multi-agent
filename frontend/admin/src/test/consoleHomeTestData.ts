import type { ConsoleHomeEnvelope } from "../api/generated/reactAdminApi";

export const consoleHomeFixture: ConsoleHomeEnvelope = {
  page_id: "console-home",
  title: "Console Home",
  description:
    "A scope-aware starting point for workflows, operations, governance, skills, access, usage, and channels.",
  scope: {
    scope_type: "tenant",
    tenant_id: "11111111-1111-1111-1111-111111111111",
    label: "Acme",
  },
  updated_at: "2026-05-08T12:00:00Z",
  metrics: [
    {
      metric_id: "workspace-count",
      label: "Workspaces",
      value: "4",
      summary: "Authorized destinations available in this scope.",
      href: null,
      tone: "success",
    },
    {
      metric_id: "attention-count",
      label: "Needs attention",
      value: "0",
      summary: "Current admin notices for the active scope.",
      href: null,
      tone: "success",
    },
    {
      metric_id: "scope-mode",
      label: "Scope mode",
      value: "Tenant",
      summary: "Actions and data are constrained by the selected scope.",
      href: null,
      tone: "info",
    },
  ],
  attention_items: [
    {
      item_id: "no-active-notices",
      title: "No active notices",
      summary: "No admin notices are active for this scope.",
      href: null,
      tone: "success",
    },
  ],
  quick_actions: [
    {
      action_id: "workflow_onboarding",
      label: "Set up workflow",
      summary:
        "Launch guided setup for a generic workflow from scenario intake through publish and launch.",
      href: "/admin/app/workflows/onboarding?tenant_id=11111111-1111-1111-1111-111111111111",
      group: "Workflows",
    },
    {
      action_id: "workflow_registry",
      label: "Review workflows",
      summary: "Open drafts, validation results, publishing readiness, and sharing.",
      href: "/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111",
      group: "Workflows",
    },
    {
      action_id: "usage_analytics",
      label: "Review usage",
      summary: "Inspect usage, cost attribution, exports, and drilldowns.",
      href: "/admin/app/usage?tenant_id=11111111-1111-1111-1111-111111111111",
      group: "Model And Skill Config",
    },
  ],
  workspaces: [
    {
      workspace_id: "workflow_registry",
      label: "Workflow Registry",
      summary: "Draft, validate, publish, and share workflow versions.",
      href: "/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111",
      group: "Workflows",
      status_label: "Available",
      status_tone: "success",
    },
    {
      workspace_id: "usage_analytics",
      label: "Usage Analytics",
      summary: "Review usage, cost attribution, exports, and trends.",
      href: "/admin/app/usage?tenant_id=11111111-1111-1111-1111-111111111111",
      group: "Model And Skill Config",
      status_label: "Available",
      status_tone: "success",
    },
  ],
  provenance: {
    source_kind: "computed_metadata",
    source_label: "Authorized admin navigation",
    source_detail:
      "Console Home is assembled from the current principal, scope, and route visibility decisions.",
    last_verified_at: null,
  },
};
