# Contract: Admin Console Shell UI

**Feature**: Admin Console Shell
**Date**: 2026-04-27

## Purpose

Define how server-rendered admin pages plug into the shared shell while
preserving existing route identities, authorization, tenant scope, safe states,
and accessibility.

## Shell Context Contract

Every shell-wrapped template receives:

- `shell`: `AdminShellContext`
- `page`: page-specific view model when applicable
- `principal`: `PrincipalContext`

`AdminShellContext` fields:

- `title`: page title
- `active_scope`: `AdminScope`
- `available_scopes`: list of `AdminScopeOption`
- `navigation_groups`: list of `NavigationGroup`
- `breadcrumbs`: list of `BreadcrumbItem`
- `page_actions`: list of `PageAction`
- `messages`: list of `FlashMessage`
- `common_state`: nullable `CommonState`
- `saved_filters`: list of `SavedFilterSummary`
- `filter_restore_outcome`: nullable safe outcome summary
- `trace_id`: request trace id

## Navigation Item Metadata

Every navigation item is defined in Python with:

- `item_id`
- `label`
- `group`
- `href`
- `route_surface_key`
- `required_scope`: `platform`, `tenant`, or `either`
- `admin_area`
- `preserve_tenant_scope`
- `active_matchers`
- `order`
- `filter_profile`

Templates render the filtered navigation groups only. They do not make access
decisions.

## Route Contract

| Route | Method | Purpose | Scope |
|-------|--------|---------|-------|
| `/admin` | GET | Shell landing page | platform or tenant |
| `/admin/scope` | GET | Validate/switch scope and redirect | platform or tenant |
| `/admin/filters/{admin_area}` | GET | List saved filters for active scope | platform or tenant |
| `/admin/filters/{admin_area}` | POST | Save/update validated filter | platform or tenant |
| `/admin/filters/{admin_area}/{filter_id}/restore` | GET | Restore validated filter and redirect | platform or tenant |
| `/admin/filters/{admin_area}/{filter_id}` | DELETE/POST | Delete saved filter | platform or tenant |
| `/admin/workflows/ui` | GET | Workflow registry page | platform or tenant |
| `/admin/workflows/drafts/{workflow_draft_id}/editor` | GET | Workflow draft editor | platform or tenant |
| `/admin/workflows/versions/{workflow_version_bundle_id}/detail` | GET | Workflow version detail | platform or tenant |
| `/admin/config/ui` | GET | Model-skill routing/config page | tenant |
| `/admin/config/ui/history` | GET | Model-skill configuration history | tenant |
| `/admin/config/ui/runs/{workflow_run_id}/provenance` | GET | Model-skill run provenance | tenant |
| `/admin/runs` | GET | Run inspection search | platform or tenant |
| `/admin/runs/{workflow_run_id}` | GET | Run detail | platform or tenant |
| `/admin/runs/{workflow_run_id}/replay` | GET | Run replay | platform or tenant |
| `/admin/reliability/ui/` | GET | Reliability dashboard | platform or tenant |
| `/admin/reliability/ui/breakers` | GET | Circuit breakers | platform or tenant |
| `/admin/reliability/ui/dead-letters` | GET | Dead letters | platform or tenant |

Tenant-scoped links and forms include `tenant_id=<uuid>`. Platform-scope links
omit `tenant_id`.

## Common State Contract

Common states use:

- `state_type`: `empty`, `filtered_empty`, `denied`, `not_found`,
  `unavailable`, `partial`, `validation_error`, or `unexpected_error`
- `title`: safe title
- `summary`: safe summary
- `next_actions`: allowed actions only
- `trace_id`: optional support trace

No common state may include raw stack traces, secrets, credentials, protected
prompt content, protected memory content, raw run payloads, or cross-tenant
details.

## Audit Contract

Required audit evidence:

- Navigation visibility: one event per request and active scope, with
  item-level outcomes.
- Direct destination access: route-level access decision from existing auth
  dependencies.
- Scope selection: one event per attempted scope selection.
- Saved-filter restoration: one event per restore attempt.

If required audit persistence fails, protected rendering/actions fail closed
with a safe unavailable state or 503 response.

## Accessibility Contract

`admin_shell/base.html` must provide:

- Skip-to-content link
- One primary `main` landmark
- Labeled primary navigation
- `aria-current` for active navigation and breadcrumb links
- Explicit labels for scope and filter forms
- Keyboard-visible focus styles
- `role="status"` for success/info messages and `role="alert"` for blocking
  denied/unavailable/error states
