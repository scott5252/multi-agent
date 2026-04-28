# Admin Console Shell

The admin console shell gives operators one server-rendered frame for the
existing workflow registry, model-skill configuration, run inspection, and
reliability pages. The shell adds active scope display, authorization-aware
navigation, breadcrumbs, common states, safe messages, and saved filters while
preserving the original destination routes.

## Entry Points

- `/admin` opens the shared console landing page.
- `/admin/scope` validates a platform or tenant scope and redirects back to a
  safe admin destination.
- `/admin/workflows/ui` keeps the workflow registry route.
- `/admin/config/ui` and `/admin/config/ui/history` expose the model-skill UI.
- `/admin/runs` keeps the run inspection route.
- `/admin/reliability/ui/`, `/admin/reliability/ui/breakers`, and
  `/admin/reliability/ui/dead-letters` keep reliability UI route identities.

Tenant scope is carried with `tenant_id=<uuid>`. Platform scope omits
`tenant_id`.

## Scopes

Platform administrators default to platform scope. Tenant administrators
default to their tenant scope. A tenant-scoped page validates `tenant_id`
server-side before rendering navigation, breadcrumbs, saved filters, messages,
or page content.

If a tenant scope is forged, suspended, missing, or no longer authorized, the
shell fails closed and renders a safe unavailable or denied state. It does not
reuse saved filters or flash messages across scopes.

## Navigation

Navigation metadata lives in Python in
`multi_agent_platform.api.ui.admin_console`. Templates render only the filtered
navigation groups. The current groups are Workflows, Model And Skill Config,
Run Inspection, Reliability, and Access.

Every navigation evaluation produces item-level audit evidence for the active
scope. Direct bookmarked routes still use route-level authentication and
authorization before the shell context is built.

## Common States

The shell supports shared `empty`, `filtered_empty`, `denied`, `not_found`,
`unavailable`, `partial`, `validation_error`, and `unexpected_error` states.
State text is sanitized before rendering. Support traces are shown as trace
ids, not stack traces or raw payloads.

## Safe Messages

Flash and operational messages are summarized and scope-bound. Messages are
sanitized to avoid raw secrets, credential values, protected prompt text,
memory content, run payloads, stack traces, and cross-tenant labels.

## Saved Filters

Saved filters are stored in `admin_saved_filters` and scoped by principal,
admin area, filter key, and platform or tenant scope. Useful filters are
enabled for workflow lists, model-skill history, run inspection, reliability
breakers, and reliability dead letters.

Saved-filter criteria are validated before save and before restore. Unsupported
criteria are rejected. Tenant criteria must match the active tenant scope.

## No-JS Fallback

All critical behavior is server-rendered. `admin_shell.js` only enhances scope
switching and saved-filter deletion prompts. Navigation, breadcrumbs, common
states, saved-filter forms, and page content work without JavaScript.

## Troubleshooting

- A missing local-principal header returns `401`.
- A forged `tenant_id` returns a fail-closed `403`.
- Audit persistence failures render an unavailable state and increment admin
  shell audit/fail-closed metrics.
- Saved-filter restore failures should be treated as incomplete access because
  restoration is separately audited.

## Review Evidence

Run focused shell tests before the full coverage gate:

```bash
uv run pytest --no-cov \
  tests/unit/api/test_admin_console_ui_models.py \
  tests/unit/api/test_admin_console_access.py \
  tests/unit/api/test_admin_console_filters.py \
  tests/unit/auth/test_admin_console_policy.py \
  tests/unit/audit/test_admin_console_audit.py \
  tests/unit/db/test_admin_console_models.py \
  tests/unit/db/test_admin_console_repository.py \
  tests/integration/api/test_admin_console_shell_routes.py \
  tests/integration/api/test_admin_console_shell_authorization.py \
  tests/integration/api/test_admin_console_templates.py \
  tests/integration/api/test_admin_console_shell_states.py \
  tests/integration/api/test_admin_console_shell_saved_filters.py \
  tests/integration/db/test_admin_console_migration.py \
  tests/contract/test_admin_console_shell_contract.py \
  tests/docs/test_admin_console_shell_docs.py
```

Then run the repository gates:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```
