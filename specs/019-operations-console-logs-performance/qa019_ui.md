# QA019 UI Walkthrough: Operations Console Logs And Performance

## Flow 1: Local Login To Console

1. Copy `specs/019-operations-console-logs-performance/.env.qa019` to `.env`.
2. Start PostgreSQL and run `uv run alembic upgrade head`.
3. Start the API on `127.0.0.1:8000`.
4. Navigate to `/auth/local-login?redirect_to=/admin/operations`.
5. Confirm the Local Login page lists `platform-admin`.
6. Click `platform-admin`.
7. Confirm `/admin/operations` renders `Operations Console`.
8. Capture `01-local-login.png` and
   `02-operations-console-logs-performance-target.png`.

## Flow 2: Direct Target

1. With the platform admin session active, navigate directly to
   `/admin/operations`.
2. Confirm the admin shell navigation contains `Operations Console`.
3. Confirm the dashboard cards are visible.
4. Confirm the redaction notice says raw prompts, model responses, channel
   messages, secrets, credentials, payloads, memory content, and stack traces
   are excluded.
5. Capture `03-operations-console-logs-performance-direct-target.png`.

## Dashboard Review

1. Review the System Health card.
2. Review Worker Capacity, DB Pool Pressure, and Object Storage.
3. Review Model Providers and Telegram And Channels.
4. Review Reliability State.
5. Review Request Latency, Run Throughput, Token Throughput, and Error Rate.
6. Follow links only when the current principal is authorized.
7. Confirm empty or partial data states are explained safely.

## Log Filtering

1. Enter a trace id value when seeded data provides one.
2. Enter a tenant id value only for platform-level inspection.
3. Enter a run id value only when known.
4. Enter component, severity, status, and dependency filters.
5. Submit the filter form.
6. Confirm the rendered table shows only matching rows.
7. Confirm the filter summary does not expose raw customer or model content.

## Export

1. Confirm the platform admin can see the export button.
2. Submit an export with the current filters.
3. Confirm the response includes artifact metadata.
4. Inspect the CSV through the configured filesystem storage root if needed.
5. Confirm the CSV has safe summaries and safe details only.
6. Confirm an audit event id is present for successful export.

## Authorization

1. Sign out or open a fresh session.
2. Sign in as `auditor`.
3. Confirm `/admin/operations` renders read and log views.
4. Sign in as `tenant-admin-acme`.
5. Navigate to `/admin/operations`.
6. Confirm access is denied.
7. Confirm no platform operational records are visible.

## Required Automated Evidence

Run the focused tests:

```bash
uv run pytest --no-cov \
  tests/unit/operations \
  tests/unit/api/test_operations_schemas.py \
  tests/unit/api/test_operations_ui_models.py \
  tests/unit/auth/test_operations_policy.py \
  tests/contract/test_operations_console_contract.py \
  tests/integration/api/test_admin_operations_api.py \
  tests/integration/api/test_admin_operations_ui.py \
  tests/performance/operations/test_log_filtering.py \
  tests/docs/test_operations_console_docs.py
```

Run the browser validation:

```bash
uv run python scripts/qa/run_playwright_ui.py \
  specs/_autopilot/019-operations-console-logs-performance/validation.yml \
  --start-processes
```

Expected screenshots:

- `output/playwright/qa019_ui/01-local-login.png`
- `output/playwright/qa019_ui/02-operations-console-logs-performance-target.png`
- `output/playwright/qa019_ui/03-operations-console-logs-performance-direct-target.png`

## Screenshot Safety Checklist

- No prompt text is visible.
- No model completion text is visible.
- No provider API key is visible.
- No Authorization header is visible.
- No channel message body is visible.
- No raw payload is visible.
- No memory content is visible.
- No stack trace is visible.
- No unauthorized tenant data is visible.

## Detailed Reviewer Script

Use this script when the reviewer needs repeatable evidence beyond the
automated screenshots.

1. Open a fresh browser context.
2. Navigate to the local login URL.
3. Confirm the browser is on `127.0.0.1`.
4. Confirm the page is not using a production hostname.
5. Confirm `platform-admin` is visible.
6. Click `platform-admin`.
7. Wait for the Operations Console title.
8. Record whether the admin shell sidebar is present.
9. Record whether breadcrumbs are present.
10. Record whether the platform scope label is present.
11. Scroll through the dashboard cards.
12. Confirm System Health appears before log rows.
13. Confirm Worker Capacity appears before log rows.
14. Confirm DB Pool Pressure appears before log rows.
15. Confirm Object Storage appears before log rows.
16. Confirm Model Providers appears before log rows.
17. Confirm Telegram And Channels appears before log rows.
18. Confirm Reliability State appears before log rows.
19. Confirm Request Latency appears before log rows.
20. Confirm Run Throughput appears before log rows.
21. Confirm Token Throughput appears before log rows.
22. Confirm Error Rate appears before log rows.
23. Scroll to dependency readiness.
24. Confirm dependency names are short and readable.
25. Confirm dependency details do not include tracebacks.
26. Scroll to the filter form.
27. Enter `runtime` in the component field if present.
28. Enter `25` in the limit field.
29. Submit the form.
30. Confirm the URL keeps safe query parameters only.
31. Confirm rows are bounded by the limit.
32. Confirm empty results show a safe common state.
33. Confirm non-empty results show safe summaries.
34. Confirm detail chips or values are redacted.
35. Confirm sensitive keys are masked or omitted.
36. Confirm links stay inside admin routes.
37. Confirm run links include tenant context only when safe.
38. Confirm provider links target `/admin/model-providers`.
39. Confirm usage links target `/admin/usage`.
40. Confirm reliability links target `/admin/reliability`.
41. Submit an export as `platform-admin`.
42. Confirm export metadata is returned.
43. Confirm no CSV content is rendered inline as raw payload text.
44. Confirm the export artifact URI is a storage reference.
45. Confirm the export response includes an audit event id.
46. Save the export response to `/tmp/qa019-export.json`.
47. Open a fresh browser context.
48. Sign in as `auditor`.
49. Navigate to `/admin/operations`.
50. Confirm the page loads.
51. Confirm redaction notice is still visible.
52. Confirm operational rows remain safe.
53. Open a fresh browser context.
54. Sign in as `tenant-admin-acme`.
55. Navigate to `/admin/operations`.
56. Confirm the page is denied.
57. Confirm no dashboard card is visible.
58. Confirm no operational row is visible.
59. Capture a note if the denial page text is unclear.
60. Close all browser contexts after evidence is captured.

## Visual Acceptance Notes

- Cards should be readable at desktop width.
- Cards should not overlap.
- Filter labels should not overlap inputs.
- The log table should remain scannable.
- Long identifiers should wrap or truncate cleanly.
- Empty states should be calm and clear.
- Error states should not reveal stack traces.
- The export button should be easy to find for authorized actors.
- The export button should not be usable for denied actors.
- The redaction notice should be visible without searching.
- The page should remain useful when the QA database has sparse data.
- The page should remain useful when gateway data is absent.
- The page should remain useful when provider data is absent.
- The page should remain useful when usage data is absent.
- The page should explain unavailable dependencies safely.

## Reviewer Stop Conditions

- Stop if a raw prompt is visible.
- Stop if a model completion is visible.
- Stop if a private channel message is visible.
- Stop if a secret value is visible.
- Stop if a credential reference reveals a credential value.
- Stop if an Authorization header is visible.
- Stop if memory content is visible.
- Stop if a raw payload is visible.
- Stop if a stack trace is visible.
- Stop if `tenant-admin-acme` can view the console.
- Stop if `tenant-admin-globex` can view the console.
- Stop if a CSV export includes forbidden content.
- Stop if a link bypasses admin authorization.
- Stop if screenshots contain forbidden content.

## Goal

The goal of this UI walkthrough is to prove the Operations Console is usable,
authorized, and screenshot-safe.
Expected: local login reaches `/admin/operations`.
Expected: platform admins can see dashboard cards.
Expected: auditors can inspect redacted operations data.
Expected: tenant admins are denied in v1.
Expected: filters and exports are discoverable.
Expected: forbidden sensitive content is excluded.

## How To Use This Guide

Run this guide after copying `.env.qa019`.
Run this guide with the API listening on port 8000.
Run this guide with the local browser or Playwright.
Capture screenshots in `output/playwright/qa019_ui`.
Keep reviewer notes in `/tmp/qa019-ui-notes.txt`.
Do not use production data.
Do not use real model provider credentials.
Do not paste private channel messages.

## Environment Setup

Copy the environment file.

```bash
cp specs/019-operations-console-logs-performance/.env.qa019 .env
```

Expected: `.env.qa019` is the source for this walkthrough.
What is happening: the local-principal QA catalog is being activated.
Why this matters: reviewers can validate authorization without Auth0.

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: the browser can reach `http://127.0.0.1:8000`.
What is happening: the FastAPI app is serving the admin console.
Why this matters: the browser walkthrough uses the same route reviewers use.

Confirm the login URL.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/operations
```

Expected: the Local Login page opens.
What is happening: local-principal test mode is offering QA identities.
Why this matters: operations access is role and permission sensitive.

## Browser Walkthrough

Open local login.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/operations
```

Expected: the page lists `platform-admin`.
What is happening: the test catalog is available.
Why this matters: platform operations checks require platform authority.

Click `platform-admin`.

```text
Expected target: /admin/operations
```

Expected: the console title is `Operations Console`.
What is happening: the admin shell wraps the feature route.
Why this matters: navigation and breadcrumbs should match other admin pages.

Run full quality gates for UI release evidence:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: all quality gates pass.
What is happening: repository-wide checks verify style, types, and coverage.
Why this matters: the browser UI ships with the same evidence as the API.

## UI Evidence Checklist

- Screenshot `01-local-login.png` exists.
- Screenshot `02-operations-console-logs-performance-target.png` exists.
- Screenshot `03-operations-console-logs-performance-direct-target.png` exists.
- Reviewer notes mention the principal used.
- Reviewer notes mention the route visited.
- Reviewer notes mention redaction review.
- Reviewer notes mention tenant isolation review.
- Reviewer notes mention export review.
- Reviewer notes mention sparse-data behavior when the QA database is empty.
- Reviewer notes mention any unexpected visual issue.

## Acceptance Notes Template

Reviewer:
Date:
Browser:
Branch:
Environment file:
Platform admin screenshot:
Auditor review:
Tenant denial review:
Export review:
Redaction review:
Responsive or layout concerns:
Unexpected states:
Decision:

## Troubleshooting

- If local login is missing, verify `AUTH_MODE=local_principal`.
- If `platform-admin` is missing, recopy `.env.qa019`.
- If the target page is denied for platform admin, verify operations
  permissions in `LOCAL_PRINCIPAL_CATALOG_JSON`.
- If the dashboard is sparse, remember the QA database may be empty.
- If export fails, verify the filesystem artifact root exists.
- If screenshots are blank, verify the API process is still running.
- If Playwright cannot click the login card, inspect the local-login screenshot.
- If a tenant admin reaches the console, stop and report a blocker.
- If forbidden content appears, stop and report a blocker.

## Related Files

- `specs/019-operations-console-logs-performance/qa019.md`
- `specs/019-operations-console-logs-performance/qa019_user_guide.md`
- `specs/019-operations-console-logs-performance/testing-instructions.md`
- `specs/019-operations-console-logs-performance/pr-review-notes.md`
- `src/multi_agent_platform/api/routers/admin_operations.py`
- `src/multi_agent_platform/web_admin/templates/operations/index.html`
- `tests/integration/api/test_admin_operations_ui.py`
