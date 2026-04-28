# PR Review Notes: Admin Console Shell

## Scope Handling

The implementation adds `/admin` and uses `tenant_id` query parameters for
tenant scope. Platform scope omits `tenant_id`. Tenant administrators cannot
forge another tenant id. Suspended or unavailable tenants fail closed.

## Authorization

Admin shell route surfaces are registered in `auth.policy.SURFACE_POLICIES`
with non-public classifications. Navigation filtering is centralized in
`api/ui/admin_console.py`; templates render already-filtered items.

Direct routes remain direct. Workflow, model-skill, run inspection, and
reliability pages are wrapped through shell context without route replacement.

## Denied Navigation And Fail-Closed Behavior

Navigation visibility evaluates every item and omits denied destinations. A
forged tenant scope or non-admin principal receives a safe denial. Audit
persistence failures raise a shell access error and render an unavailable
state, with metrics and redacted log context.

## Audit Coverage

Audit builders record:

- `admin_shell.navigation_visibility`
- `admin_shell.scope_selection`
- `admin_shell.saved_filter_restore`

Navigation events include item outcomes, role context, active scope, request
path, and trace id. Scope and filter restoration are separate audit actions.

## Common States And Safe Messages

Common states cover empty, filtered-empty, denied, not-found, unavailable,
partial, validation, and unexpected-error cases. Breadcrumbs and flash messages
go through sanitizers that redact secrets, credential values, prompt text,
memory content, run payloads, and stack traces.

## Saved Filters

`admin_saved_filters` stores validated criteria scoped by principal, admin
area, filter key, and platform or tenant scope. Useful filter profiles are
enabled for workflows, model-skill history, run inspection, reliability
breakers, and reliability dead letters.

## Route Preservation

The following routes keep their identities while rendering inside the shell:

- `/admin/workflows/ui`
- `/admin/workflows/drafts/{workflow_draft_id}/editor`
- `/admin/workflows/versions/{workflow_version_bundle_id}/detail`
- `/admin/config/ui`
- `/admin/config/ui/history`
- `/admin/config/ui/runs/{workflow_run_id}/provenance`
- `/admin/runs`
- `/admin/runs/{workflow_run_id}`
- `/admin/runs/{workflow_run_id}/replay` for HTML `Accept` requests
- `/admin/reliability/ui/`
- `/admin/reliability/ui/breakers`
- `/admin/reliability/ui/dead-letters`

## Coverage Evidence

Focused admin shell tests passed:

```text
39 passed in 2.34s
```

Full coverage passed:

```text
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
470 passed, 1 warning in 38.81s
Required test coverage of 90% reached. Total coverage: 90.04%
```

## Known Risks

- Model-skill UI pages are intentionally thin wrappers around existing service
  helpers and safe empty states.
- Run replay keeps JSON behavior for default API clients and renders HTML when
  the request explicitly accepts `text/html`.
- Navigation performance is request-local and uses static metadata; saved
  filters add one indexed database list query on pages that expose filters.

## Route Reachability And Timing

Route preservation and tenant-scope query behavior are covered by focused
integration tests for `/admin`, workflow, run inspection, saved-filter, and
reliability routes.

Representative in-process shell timing evidence using SQLite test storage:

```text
overall_p95_ms=4.72
/admin p95_ms=4.34
/admin/workflows/ui p95_ms=4.94
/admin/runs p95_ms=4.25
/admin/reliability/ui/breakers p95_ms=4.37
```

The measurement is below the 150 ms p95 budget and should be repeated against
QA010 PostgreSQL during manual review.
