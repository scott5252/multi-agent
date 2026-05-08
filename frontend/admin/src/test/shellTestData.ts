import type { ReactAdminBootstrap } from "../api/generated/reactAdminApi";

export const bootstrapFixture: ReactAdminBootstrap = {
  principal: {
    principal_id: "tenant-admin-acme",
    display_name: "Tenant Admin",
    role_codes: ["tenant_admin"],
    auth_mode: "local_principal",
    trace_id: "trace-ui",
  },
  active_scope: {
    scope_type: "tenant",
    tenant_id: "11111111-1111-1111-1111-111111111111",
    label: "Acme",
  },
  available_scopes: [
    {
      scope: {
        scope_type: "tenant",
        tenant_id: "11111111-1111-1111-1111-111111111111",
        label: "Acme",
      },
      label: "Acme",
      href: "/admin/app?tenant_id=11111111-1111-1111-1111-111111111111",
      selected: true,
    },
  ],
  navigation: [
    {
      label: "Workflows",
      items: [
        {
          item_id: "workflow_registry",
          label: "Workflow Registry",
          group: "Workflows",
          href: "/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111",
          route_surface_key: "GET:/admin/app/workflows",
          required_scope: "either",
          admin_area: "workflows",
          preserve_tenant_scope: true,
          active: false,
          fallback_kind: "react",
        },
      ],
    },
  ],
  feature_flags: {
    react_admin_enabled: true,
    react_domain_routes: {},
    source: "settings",
  },
  version: {
    app_name: "multi-agent-platform",
    app_version: "0.1.0",
    api_version: "qa030",
    commit_sha: "test",
    build_time: "2026-05-04T00:00:00+00:00",
  },
  asset_manifest: {
    available: true,
    base_path: "/admin/static/react",
    entrypoints: [],
    stylesheets: [],
    version: "abc123",
    unavailable_reason: null,
  },
  action_tokens: {
    csrf_token: null,
    issued_at: null,
  },
  system_health: {
    status: "ready",
    label: "Ready",
    summary: "All required platform dependencies are reporting ready.",
    checked_at: "2026-05-08T12:00:00Z",
    dependencies: [
      {
        name: "config",
        required: true,
        status: "ready",
      },
      {
        name: "postgres",
        required: true,
        status: "ready",
      },
    ],
  },
  shell: {
    product_name: "Multi-Agent Admin",
    active_area: "home",
    breadcrumbs: [
      { label: "Admin", href: "/admin", active: false },
      { label: "Admin", href: "/admin/app", active: true },
    ],
    page_actions: [
      {
        action_id: "log-off",
        label: "Log off",
        href: "/auth/local-logout?redirect_to=/auth/local-login",
        method: "get",
        variant: "secondary",
        disabled_reason: null,
      },
    ],
    saved_filters: [],
    notifications: [],
    states: [
      {
        state: "loading",
        title: "Loading admin workspace",
        summary: "Checking your signed-in principal and active scope.",
        action: null,
        trace_id: null,
      },
      {
        state: "partial_data",
        title: "Partial data",
        summary: "Some optional summaries are unavailable.",
        action: null,
        trace_id: null,
      },
    ],
    command_results: [
      {
        result_id: "workflow_registry",
        label: "Workflow Registry",
        description: "Open Workflows",
        group: "Workflows",
        href: "/admin/app/workflows?tenant_id=11111111-1111-1111-1111-111111111111",
        required_scope: "either",
        fallback_kind: "react",
      },
    ],
    design_token_version: "qa030",
    search_url: "/admin/app/search.json?tenant_id=11111111-1111-1111-1111-111111111111",
  },
};
