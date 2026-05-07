# Spec 044 Reviewer Notes

## Summary

Spec 044 converts the operations, reliability controls, admin run inspection,
user-facing run compatibility, usage analytics, and usage export browser
surfaces to React destinations.

The retained JSON APIs remain in place for React and API callers.

## Retired Jinja Surfaces

- `src/multi_agent_platform/web_admin/templates/operations/index.html`
- `src/multi_agent_platform/web_admin/templates/reliability/index.html`
- `src/multi_agent_platform/web_admin/templates/reliability/breakers.html`
- `src/multi_agent_platform/web_admin/templates/reliability/dead_letters.html`
- `src/multi_agent_platform/web_admin/templates/runs/index.html`
- `src/multi_agent_platform/web_admin/templates/runs/detail.html`
- `src/multi_agent_platform/web_admin/templates/runs/replay.html`
- `src/multi_agent_platform/web_admin/templates/usage/index.html`
- `src/multi_agent_platform/web_admin/templates/usage/export_detail.html`
- `src/multi_agent_platform/web_admin/static/run_inspection.js`

## Compatibility Behavior

- `/admin/operations` redirects to `/admin/app/operations`.
- `/admin/reliability/ui/` redirects to `/admin/app/operations?panel=reliability`.
- `/admin/reliability/ui/breakers` redirects to `/admin/app/operations?panel=breakers`.
- `/admin/reliability/ui/dead-letters` redirects to `/admin/app/operations?panel=dead-letters`.
- `/admin/runs` redirects to `/admin/app/operations?panel=runs`.
- `/admin/runs/{workflow_run_id}` redirects to React run detail query state.
- Browser replay requests redirect to React replay query state.
- JSON replay requests keep the existing API contract.
- `/runs`, `/runs/new`, and `/runs/{run_id}` redirect to React channel surfaces.
- `/admin/usage` redirects to `/admin/app/usage`.
- `/admin/usage/exports/{usage_export_request_id}` validates access before redirecting to React export detail.

## Validation Notes

Focused backend tests cover legacy redirects, retained JSON APIs, tenant denial,
usage export compatibility, user-facing run redirects, and retirement scanning.

Focused frontend tests cover the React workbench, React usage workspace, and
route registration through `App.test.tsx`.

Playwright validation logs in with local-principal auth and captures the React
operations route under `output/playwright/qa044_ui`.

## Redaction Notes

No route should render raw prompts, raw completions, memory contents, private
channel messages, provider authorization headers, raw CSV rows, or raw external
tool payloads.

Usage export detail is metadata-only.

Operations and reliability panels use safe summaries and redacted evidence.

## Reviewer Decision

Approve Spec 044 only after QA docs validation, Spec QA, and Playwright
validation pass with the React operations screenshot attached.
