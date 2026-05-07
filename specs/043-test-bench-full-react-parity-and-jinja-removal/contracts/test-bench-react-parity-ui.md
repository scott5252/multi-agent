# UI Contract: Test Bench React Parity

## React Entry

- Route: `/admin/app/test-bench`
- Bootstrap: `/admin/app/test-bench/bootstrap.json`
- Auth: existing admin React shell principal and active-scope resolution.
- Behavior: renders suites, authoring, run launch/progress, run detail, trace/artifact evidence, gates, and audit without any server-rendered `agent_tests` template.

## Required React Child Destinations

- `/admin/app/test-bench?suite_id={suite_id}`
- `/admin/app/test-bench?mode=create-suite`
- `/admin/app/test-bench?suite_id={suite_id}&mode=edit-suite`
- `/admin/app/test-bench?suite_id={suite_id}&mode=create-case`
- `/admin/app/test-bench?suite_id={suite_id}&case_id={case_id}&mode=edit-case`
- `/admin/app/test-bench?run_id={run_id}`
- `/admin/app/test-bench?artifact_reference_id={artifact_reference_id}`
- `/admin/app/test-bench?gate_id={gate_id}`
- `/admin/app/test-bench?audit_ref={audit_reference_id}`

## Legacy Browser Route Mapping

| Legacy route | Behavior | React destination |
|--------------|----------|-------------------|
| `GET /admin/agent-tests/ui` | Redirect | `/admin/app/test-bench` |
| `GET /admin/agent-tests/ui/suites/new` | Redirect | `/admin/app/test-bench?mode=create-suite` |
| `GET /admin/agent-tests/ui/suites/{suite_id}` | Redirect | `/admin/app/test-bench?suite_id={suite_id}` |
| `GET /admin/agent-tests/ui/runs/{run_id}` | Redirect | `/admin/app/test-bench?run_id={run_id}` |
| `POST /admin/agent-tests/ui/suites` | Preserve mutation, then redirect | `/admin/app/test-bench?suite_id={suite_id}&mutation=created` |
| `POST /admin/agent-tests/ui/suites/{suite_id}/cases` | Preserve mutation, then redirect | `/admin/app/test-bench?suite_id={suite_id}&mutation=case-created` |
| `POST /admin/agent-tests/ui/suites/{suite_id}/runs` | Preserve mutation, then redirect | `/admin/app/test-bench?run_id={run_id}&mutation=run-launched` |

## Safe Problem Behavior

- Unsafe `next`, `return_to`, or absolute URL values are discarded or rejected.
- Cross-tenant ids return denied or not-found safe problems with no protected labels.
- Missing tenant scope for non-platform users returns a safe problem.
- Form validation errors return safe problem summaries or React redirects with conflict state; raw form payloads are not echoed.

## Browser Validation Journeys

- Suite list and detail load from legacy index redirect.
- Suite create/edit and case create flows show validation, stale revision, and success states.
- Run launch shows safe execution modes, backend-owned progress, and terminal status.
- Run detail shows pass/fail diagnostics, trace steps, artifacts, and audit references.
- Publish-gate evidence distinguishes current, stale, missing, running, failing, audit-unavailable, and redaction-unavailable states.
- Cross-tenant direct links fail closed.
