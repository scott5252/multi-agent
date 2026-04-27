# Implementation Plan: Admin Console Shell

**Branch**: `010-admin-console-shell` | **Date**: 2026-04-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-admin-console-shell/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/commands/plan.md` for project-specific planning rules.

## Summary

Add a shared server-rendered admin console shell that wraps the existing
workflow registry, model-skill configuration, run inspection, and reliability
admin pages without replacing their route identities. The shell uses the
current FastAPI dependency model, Auth0/local-principal authentication,
tenant-scope helpers, SQLAlchemy async sessions, Jinja2 templates under
`web_admin`, and small optional JavaScript in `web_admin/static`. It introduces
shared navigation metadata, tenant-scope resolution from a validated
`tenant_id` query parameter, authorization-aware menu filtering, auditable
navigation and destination decisions, common empty/error/flash states,
breadcrumbs, and server-persisted saved filters scoped by user, admin area, and
platform or tenant scope.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Starlette/Jinja2 template responses,
Pydantic v2, Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic,
PostgreSQL 16+, psycopg 3, Auth0 JWT validation plus deterministic
local-principal mode, prometheus-client, pytest, pytest-asyncio, httpx, Ruff,
mypy, uv
**Storage**: PostgreSQL for persisted admin saved filters and existing access
decision/audit records. Existing workflow, model-skill, run inspection,
reliability, tenant, role grant, and audit tables remain authoritative.
**Testing**: pytest unit tests for shell context builders, navigation metadata,
scope validation, authorization-aware menu filtering, breadcrumb redaction,
safe messages, saved-filter validation, and common states; FastAPI
server-rendered route tests with Jinja2 templates; authorization tests for
platform admin, tenant admin, multi-tenant admin, unauthorized users, forged
`tenant_id`, direct-route denial, and audit-persistence failure; migration and
repository tests for saved filters; docs tests for README, operator docs,
testing instructions, and PR notes; coverage enforced at >=90 percent for
submitted shell code.
**Target Platform**: Linux container deployment for the existing FastAPI API
with local macOS/Linux development.
**Project Type**: Multi-tenant backend platform with FastAPI JSON APIs,
server-rendered admin UI, Auth0/local-principal auth, PostgreSQL persistence,
and operator-facing documentation.
**Performance Goals**: Shell context, navigation filtering, scope validation,
and saved-filter lookup add no more than three indexed database lookups and
complete within 150 ms p95 per shell-rendered admin request in local integration
tests; authorized admins can reach existing admin pages in three navigation
actions or fewer; shell rendering remains usable without optional client-side
JavaScript.
**Constraints**: Do not replace existing admin routes; platform scope omits
`tenant_id`; tenant scope always uses a server-validated `tenant_id` query
parameter on shell links and forms; denied, unavailable, or indeterminate
access fails closed; navigation visibility is audited once per request and
active scope with item-level outcomes; direct destination access, scope
selection, and saved-filter restoration are separately audited; audit
persistence failure blocks protected destinations/actions and renders a safe
unavailable state with log/metric evidence; flash messages, breadcrumbs,
filters, and errors must not expose secrets, protected prompts, unauthorized
run content, memory content, stack traces, or cross-tenant details.
**Scale/Scope**: First delivery wraps all current server-rendered `web_admin`
pages for workflows, model-skill config/history/provenance, run
inspection/replay, and reliability dashboard/breakers/dead letters. It adds one
persisted saved-filter model and migration, shared shell helpers/templates, and
documentation/review artifacts. It does not redesign the underlying workflow,
model-skill, run inspection, or reliability business flows.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Shell state is request-derived except saved filters, which are persisted and auditable; audit-persistence failures fail closed. |
| Immutable State And Memory | PASS | Access and navigation evidence is append-only in audit/access records; saved filters are versioned with timestamps and replaceable by explicit user action. |
| Contract-First Agent Coordination | PASS | No agent runtime contract changes; UI route, template context, navigation, and saved-filter contracts are defined before implementation. |
| Security With Practical Development Ergonomics | PASS | Auth0 and local-principal flows reuse `require_authorized_principal`, role grants, and deterministic local principals while preserving scope and audit checks. |
| Operability Is A Product Requirement | PASS | The shell adds operator navigation, safe states, audit evidence, metrics/logs for fail-closed paths, README guidance, PR notes, and testing instructions. |
| Spec-Driven Delivery | PASS | Plan, research, data model, contracts, and quickstart trace to the admin shell specification and clarifications. |
| Test And Documentation Discipline | PASS | Plan requires >=90 percent coverage, server-rendered tests, authorization tests, docs tests, README updates, testing instructions, and PR notes. |
| Clear Ownership And Small Safe Changes | PASS | Work is scoped to a shell helper/service layer, templates/static assets, small route integrations, saved-filter storage, tests, and docs. |
| Tenant Isolation And Fair Scheduling | PASS | Tenant scope is explicit, validated server-side, propagated through query parameters, and enforced on navigation, direct routes, filters, messages, and breadcrumbs. |
| Version-Pinned Execution | PASS | No runtime execution bundle changes; run inspection links continue to respect existing pinned bundle/debug surfaces. |
| Secret Hygiene And Controlled Tool Access | PASS | Shared sanitizers redact unsafe message, error, breadcrumb, and filter content; saved filters persist only validated criteria and safe labels. |
| Tiered Storage For Large Payloads | PASS | No large payload storage is introduced; saved filters store compact JSON criteria in PostgreSQL. |
| Human Approval Is Durable State | PASS | No approval/resume flows are introduced; existing run approval surfaces remain linked and protected by existing routes. |

Post-Phase-1 re-check: design artifacts keep every constitution gate in
`PASS` status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/010-admin-console-shell/
+-- plan.md
+-- research.md
+-- data-model.md
+-- quickstart.md
+-- contracts/
|   +-- admin-console-shell-ui.md
|   +-- admin-console-shell.openapi.yaml
+-- testing-instructions.md
+-- pr-review-notes.md
+-- tasks.md
```

### Source Code (repository root)

```text
src/
+-- multi_agent_platform/
    +-- api/
    |   +-- routers/
    |   |   +-- admin_console.py                # console landing, scope selection, saved-filter actions
    |   |   +-- admin_workflow_ui.py            # wrap existing workflow UI routes
    |   |   +-- admin_model_skill_config.py     # keep JSON APIs; add or include model-skill UI routes
    |   |   +-- admin_run_inspection.py         # wrap existing run inspection UI routes
    |   +-- ui/
    |       +-- admin_console.py                # context, navigation, access, states, messages, filters
    +-- db/
    |   +-- models/
    |   |   +-- admin_console.py                # persisted saved filters only
    |   +-- repositories/
    |       +-- admin_console.py                # saved-filter CRUD and scoped lookup
    +-- observability/
    |   +-- metrics.py                          # admin-shell fail-closed/audit counters
    |   +-- logging.py                          # admin-shell safe log context
    +-- web_admin/
        +-- static/
        |   +-- admin_shell.js                  # optional scope/filter UI enhancement
        |   +-- workflow_studio.css             # extend shared admin styles
        +-- templates/
            +-- admin_shell/
            |   +-- base.html
            |   +-- breadcrumbs.html
            |   +-- flash_messages.html
            |   +-- navigation.html
            |   +-- saved_filters.html
            |   +-- scope_selector.html
            |   +-- state.html
            |   +-- unavailable.html
            +-- workflows/
            +-- model_skill_config/
            +-- runs/
            +-- reliability/
alembic/versions/
+-- 0010_admin_console_shell.py
tests/
+-- contract/
|   +-- test_admin_console_shell_contract.py
+-- integration/
|   +-- api/
|       +-- test_admin_console_shell_routes.py
|       +-- test_admin_console_shell_authorization.py
|       +-- test_admin_console_shell_saved_filters.py
|       +-- test_admin_console_shell_states.py
|       +-- test_admin_console_templates.py
|   +-- db/
|       +-- test_admin_console_migration.py
+-- docs/
|   +-- test_admin_console_shell_docs.py
+-- unit/
    +-- api/
    |   +-- test_admin_console_ui_models.py
    |   +-- test_admin_console_access.py
    |   +-- test_admin_console_filters.py
    +-- audit/
    |   +-- test_admin_console_audit.py
    +-- db/
        +-- test_admin_console_models.py
        +-- test_admin_console_repository.py
README.md
docs/admin-console-shell.md
```

**Structure Decision**: Keep the feature in the existing Python/FastAPI backend
and `web_admin` template tree. Add shared shell helpers and a single shell
router, wrap existing UI route handlers by passing `shell` context to their
current templates, convert current full-document templates to extend
`admin_shell/base.html`, and avoid moving or renaming existing destination
routes. Add persisted storage only for saved filters.

## Admin Shell Design Decisions

### Routes And Route Preservation

- Add `/admin` as the shared console landing page. It renders the same shell
  frame and links to authorized destinations.
- Add `/admin/scope` as a GET endpoint that validates requested `tenant_id`
  and redirects to a safe admin destination with the selected scope. Platform
  scope uses no `tenant_id`.
- Add saved-filter HTML/form endpoints where the page has meaningful filter
  criteria:
  `/admin/filters/{admin_area}` GET for listing,
  `/admin/filters/{admin_area}` POST for save/update,
  `/admin/filters/{admin_area}/{filter_id}/restore` GET for restore, and
  `/admin/filters/{admin_area}/{filter_id}` POST/DELETE for removal.
- Wrap existing workflow UI routes:
  `/admin/workflows/ui`,
  `/admin/workflows/drafts/{workflow_draft_id}/editor`,
  `/admin/workflows/versions/{workflow_version_bundle_id}/detail`.
- Expose/wrap model-skill server-rendered pages using existing helpers and
  templates without changing JSON API routes:
  `/admin/config/ui`,
  `/admin/config/ui/history`,
  `/admin/config/ui/runs/{workflow_run_id}/provenance`.
- Wrap existing run inspection routes:
  `/admin/runs`,
  `/admin/runs/{workflow_run_id}`,
  `/admin/runs/{workflow_run_id}/replay`.
- Wrap existing reliability UI routes:
  `/admin/reliability/ui/`,
  `/admin/reliability/ui/breakers`,
  `/admin/reliability/ui/dead-letters`.
- Register new UI surfaces in `auth.policy.SURFACE_POLICIES` so direct access
  uses the same Auth0/local-principal and audit path as navigation.

### Template Composition

- Add `admin_shell/base.html` with skip link, landmark regions, primary
  navigation, scope display/selector, breadcrumbs, flash/message area, page
  actions, optional saved-filter region, common state rendering, and a main
  content block.
- Keep current workflow, model-skill, run, and reliability templates in their
  directories and convert them to `{% extends "admin_shell/base.html" %}`.
  Their existing page bodies move into a `content` block.
- Shared partials render `navigation`, `scope_selector`, `breadcrumbs`,
  `flash_messages`, `saved_filters`, and `state`. Templates must work when
  `admin_shell.js` is absent.
- Use `workflow_studio.css` as the shared stylesheet and add shell styles there
  unless the implementation needs a small `admin_shell.css`. No new frontend
  build step is introduced.

### UI Helper Modules

- `api/ui/admin_console.py` owns typed view models, scope resolution,
  navigation filtering, audit orchestration helpers, common states,
  breadcrumb/message sanitization, and saved-filter validation/form models.
- Existing page-specific builders in `api/ui/admin_workflows.py`,
  `api/ui/model_skill_config.py`, `api/ui/run_details.py`, and
  `api/ui/reliability_controls.py` remain focused on page content and accept
  shell context rather than duplicating shell logic.
- Existing reliability server-rendered UI routes currently live in
  `api/ui/reliability_controls.py`; this feature may update that file for
  reliability route wrapping while keeping shared shell behavior centralized in
  `api/ui/admin_console.py`.

### Navigation Metadata

- Define a static navigation registry in Python, not templates, so it can be
  tested and audited. Each item includes:
  `item_id`, `label`, `group`, `href`, `route_surface_key`,
  `required_scope` (`platform`, `tenant`, or `either`), `admin_area`,
  `preserve_tenant_scope`, `active_matchers`, `order`, and optional
  `filter_profile`.
- Initial groups:
  `Workflows`, `Model And Skill Config`, `Run Inspection`, `Reliability`, and
  `Access`.
- Navigation filtering evaluates every item for the active scope and records
  item-level outcomes in one navigation audit event per request/scope. Denied
  items are omitted from the rendered menu.
- Direct requests remain protected by route-level authorization and produce
  separate direct access decisions.

### Tenant Scope Rendering

- Platform scope is represented by `AdminScope(scope_type="platform",
  tenant_id=None)` and all generated platform links omit `tenant_id`.
- Tenant scope is represented by `AdminScope(scope_type="tenant",
  tenant_id=<uuid>)` and all shell links/forms for tenant-scoped destinations
  include the validated `tenant_id` query parameter.
- Scope options are resolved from platform-admin authority plus active tenant
  role grants; local-principal tests seed deterministic principals and role
  grants.
- Forged, missing, suspended, archived, deleted, or no-longer-authorized tenant
  IDs fail closed, clear unsafe saved-filter/message state, and produce scope
  selection audit evidence.

### Authorization And Audit Behavior

- Use existing `require_authorized_principal` for request authentication and
  direct-route authorization.
- Add a public shell access service that evaluates navigation items against the
  same surface policy metadata used by `AuthService.authorize_request`.
- Navigation visibility audit payloads include actor, role context, active
  scope, request path, item id, destination surface, outcome, reason category,
  and time.
- Scope selection and saved-filter restoration use separate audit events.
- If any required shell audit write fails, render `admin_shell/unavailable.html`
  or raise a safe 503 for non-HTML actions, increment an admin-shell audit
  failure metric, and log redacted operational context.

### Empty, Error, Flash, And Breadcrumb States

- Use `CommonState` for `empty`, `filtered_empty`, `denied`, `not_found`,
  `unavailable`, `partial`, `validation_error`, and `unexpected_error`.
- Page builders provide page purpose and permitted next actions; the shell
  decides safe wording and whether an action can be shown.
- Flash messages are server-side summaries tied to principal id and active
  scope for the current request. If persistent flash storage is later needed,
  it must return to planning before adding a data model.
- Breadcrumbs use safe labels from route/page metadata. Resource names are
  shown only after the destination access decision allows the active scope.

### Saved Filters

- Persist only useful filters for list/investigation pages:
  workflows list, model-skill history, run search, reliability breakers, and
  reliability dead letters.
- Do not add saved-filter controls to pages without meaningful filters, such as
  workflow draft editor, version detail, run detail, run replay, or model-skill
  provenance detail.
- Saved filters are keyed by principal identity, admin area, filter key, and
  normalized scope (`platform` or tenant UUID).
- Every criterion is validated before save and before restore. Unsupported,
  malformed, expired, unauthorized, or scope-mismatched criteria are rejected or
  dropped safely before query execution.
- Restore decisions are audited separately from navigation visibility.

### Accessibility

- Base shell includes a skip-to-content link, one `main` landmark, labeled
  navigation (`aria-label="Admin"`), visible focus states, semantic headings,
  explicit form labels, `aria-current` on active navigation/breadcrumb items,
  and `role="status"` or `role="alert"` for flash/common states as appropriate.
- Empty/error states use text and icons/decorative styling only when semantic
  meaning is also present in text.
- Server-rendered tests assert accessible landmarks and labels are present in
  representative pages.

### Future Admin Page Plug-In Contract

- Future admin specs add pages by defining a route surface policy, a navigation
  item metadata entry, a page content builder, a template that extends
  `admin_shell/base.html`, and optional saved-filter definitions.
- Future pages must pass shell context through their route handler and must not
  compute menu visibility in templates.
- Future saved filters must add validators and docs before enabling controls.
- Future direct routes must use `require_admin_destination` or equivalent
  route-level authorization and must record direct access decisions.

## Complexity Tracking

No constitution violations require justification.
