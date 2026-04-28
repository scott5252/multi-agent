# Research: Admin Console Shell

**Feature**: Admin Console Shell
**Date**: 2026-04-27
**Status**: Complete

## Sources Checked

- Feature spec: `specs/010-admin-console-shell/spec.md`
- Constitution: `.specify/memory/constitution.md`
- Existing FastAPI app and dependency wiring:
  `src/multi_agent_platform/api/main.py`,
  `src/multi_agent_platform/api/deps.py`,
  `src/multi_agent_platform/bootstrap/container.py`
- Existing auth and tenancy:
  `src/multi_agent_platform/auth/dependencies.py`,
  `src/multi_agent_platform/auth/service.py`,
  `src/multi_agent_platform/auth/policy.py`,
  `src/multi_agent_platform/auth/local_principals.py`,
  `src/multi_agent_platform/tenancy/context.py`,
  `src/multi_agent_platform/tenancy/guards.py`
- Existing admin UI routes, helpers, templates, and static assets under
  `src/multi_agent_platform/api/routers/`,
  `src/multi_agent_platform/api/ui/`, and
  `src/multi_agent_platform/web_admin/`
- Existing audit/access and observability helpers:
  `src/multi_agent_platform/audit/access.py`,
  `src/multi_agent_platform/audit/service.py`,
  `src/multi_agent_platform/observability/metrics.py`,
  `src/multi_agent_platform/observability/logging.py`

## Server-Rendered Shell Integration

**Decision**: Add a shared Jinja2 base template under
`web_admin/templates/admin_shell/` and convert current admin templates to
extend it while preserving their existing route handlers and page-specific
builders.

**Rationale**: Existing routes already use FastAPI and Jinja2 through
`container.workflow_ui_templates` or the same template directory. A base
template gives consistent navigation, breadcrumbs, scope display, messages, and
states without replacing routes or moving page business logic.

**Alternatives considered**: A separate frontend app was rejected because the
spec requires server rendering and small JavaScript only. A new set of wrapper
URLs around every page was rejected because it would weaken route preservation
and duplicate authorization behavior.

## Route Strategy

**Decision**: Add a shell landing route, scope-selection route, and
saved-filter routes. Existing workflow, run inspection, and reliability UI
routes remain the direct destinations. Model-skill gets server-rendered UI
routes that reuse existing templates/helpers without changing the JSON API
routes.

**Rationale**: Workflows and run inspection already have HTML routes.
Reliability has UI routes under `/admin/reliability/ui`. Model-skill has
templates and page model builders but no registered HTML route, so the shell
needs a thin UI route layer to make those pages reachable while keeping JSON
contracts intact.

**Alternatives considered**: Reusing JSON endpoints as HTML routes was
rejected because it would conflate API and UI contracts. Moving all admin pages
under `/admin/console/...` was rejected because existing direct routes must
remain valid.

## Scope Transport

**Decision**: Carry active tenant scope as a validated `tenant_id` query
parameter on shell links and forms. Platform scope omits `tenant_id`.

**Rationale**: This matches the clarification in the spec, keeps bookmarks
understandable, and avoids hidden client-only state. Server-side validation can
fail closed before rendering, restoring filters, or performing actions.

**Alternatives considered**: Session-only scope was rejected because bookmarks
and direct links would be ambiguous. Path-prefix tenant scope was rejected
because it would require replacing existing admin route identities.

## Authorization-Aware Navigation

**Decision**: Store navigation metadata in Python and evaluate every item
against surface policy metadata and the active scope before rendering. Render
only allowed items and audit the full item-level outcome set once per request
and active scope.

**Rationale**: Templates should not be the authorization source of truth.
Python metadata can be unit-tested, audited, and reused by shell routes and
future admin pages.

**Alternatives considered**: Hard-coded template links were rejected because
they cannot reliably filter by scope or produce item-level audit evidence.
Per-link database navigation configuration was rejected for the first delivery
because the destination set is static and code-reviewed.

## Direct Destination Authorization

**Decision**: Register shell and UI surfaces in `auth.policy.SURFACE_POLICIES`
and continue using `require_authorized_principal` on direct routes. Add a shell
access helper that performs scope validation and shell-specific audit before
template rendering.

**Rationale**: Existing Auth0/local-principal behavior already records access
decisions and handles local development ergonomics. The shell should extend
that model instead of introducing a second authorization framework.

**Alternatives considered**: A template-only navigation check was rejected
because direct typed URLs would bypass it. A completely new policy engine was
rejected because it would duplicate existing `AuthService` and surface policy
behavior.

## Audit Failure Handling

**Decision**: Treat shell navigation, scope selection, direct access, and
saved-filter restoration audit writes as required. If required audit
persistence fails, block protected rendering/actions, render a safe unavailable
state or return 503 for form/API actions, increment a metric, and emit redacted
structured logs.

**Rationale**: The spec explicitly requires fail-closed behavior when access
decision audit evidence cannot be persisted. This keeps the shell consistent
with the platform's security and operability principles.

**Alternatives considered**: Best-effort audit was rejected by the spec.
Rendering the page while logging an error was rejected because it would create
unaudited admin access.

## Saved Filter Persistence

**Decision**: Persist saved filters server-side in PostgreSQL, scoped by
principal identity, admin area, filter key, and platform or tenant scope.
Validate criteria before save and before restore.

**Rationale**: The spec requires server-side persistence and strict scope
isolation. PostgreSQL fits the existing transactional source-of-truth pattern,
and saved filters are compact metadata rather than large payloads.

**Alternatives considered**: Browser local storage or query-only persistence
was rejected because filters need user/scope isolation and auditability.
Persisting filters in cookies was rejected because criteria can become stale or
unauthorized and must be validated server-side.

## Common States And Safe Messages

**Decision**: Centralize empty, denied, unavailable, not-found, validation,
partial, and unexpected-error states in typed shell view models and partial
templates. Flash messages are safe, summarized, request/scope-bound content.

**Rationale**: Shared admin pages currently render their own empty states.
Centralizing shell states improves consistency and makes sensitive-data
sanitization testable.

**Alternatives considered**: Letting each page define all states was rejected
because it would duplicate wording and increase the risk of leaking
cross-tenant or secret details.

## Accessibility

**Decision**: Make the shell base template responsible for accessible
landmarks, skip link, labels, active navigation state, focus styles, and
status/alert regions, then test representative server-rendered pages.

**Rationale**: Accessibility belongs in the shared page frame so future admin
pages inherit it by default.

**Alternatives considered**: Page-by-page accessibility work was rejected
because it would be easy for future admin pages to drift.

## Future Page Plug-In Model

**Decision**: Future admin specs plug into the shell by adding a surface
policy, navigation item, page builder, template extending the base shell, and
optional saved-filter definition.

**Rationale**: A simple code-reviewed registration path keeps ownership clear
and avoids dynamic navigation complexity while the admin surface is still small.

**Alternatives considered**: Runtime plugin registration was rejected for the
first delivery because no current admin page needs it and it would complicate
authorization/audit review.
