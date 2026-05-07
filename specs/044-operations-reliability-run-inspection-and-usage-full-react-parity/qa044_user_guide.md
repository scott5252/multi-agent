# QA044 User Guide: Spec 044 - Operations, Reliability, Run Inspection, And Usage Full React Parity

## Detailed Overview

Spec 044 is part of the React UI2 migration. It removes the old Jinja browser
pages for operations, reliability controls, admin run inspection, user-facing
run compatibility, usage analytics, and usage export detail.

The feature does not remove the backend APIs that React needs. Operations JSON,
reliability data, run debug contracts, usage summaries, usage events, usage
exports, and channel run APIs remain backend-owned and authorization-checked.

The visible behavior should feel practical: old URLs redirect to React, the
React operations workspace remains the triage center, the React usage workspace
keeps filters and export metadata, and deleted templates do not reappear.

The main React route is `/admin/app/operations`. It covers operations summary,
logs, reliability signals, breaker and dead-letter views, run inspection, replay
context, lineage context, and safe fallback links.

The secondary React route is `/admin/app/usage`. It covers usage totals, usage
rollups, usage events, export creation, and export metadata.

The compatibility route for user-facing runs is `/admin/app/channels`. Old
`/runs` links should lead users into the React channel workspace or a React run
detail route when the target run exists and the principal is authorized.

The old operations templates were deleted. These include operations index,
reliability index, reliability breakers, reliability dead letters, run index,
run detail, run replay, usage index, usage export detail, and
`run_inspection.js`.

The reviewer should not see server-rendered admin shell pages for those
surfaces. Seeing the React shell is expected. Seeing a Jinja template, raw stack
trace, source file path, raw secret, raw provider header, raw prompt, raw
completion, raw memory content, or raw CSV rows is a regression.

## Who Should Use This Guide

Use this guide if you are reviewing the product behavior of Spec 044.

Use this guide if you are a platform operator checking operations and
reliability workflows.

Use this guide if you are an auditor checking usage export metadata and tenant
isolation.

Use this guide if you are a QA reviewer confirming old bookmarks and saved links
still lead somewhere safe.

Use this guide if you are a developer validating that the correct Jinja files
were deleted and no runtime route renders them.

You do not need to understand the full database schema. The guide explains which
principal to select, which pages to open, what to look for, and which evidence
to capture.

## Manual QA Prerequisites

1. Start from the repository root.

2. Copy `specs/044-operations-reliability-run-inspection-and-usage-full-react-parity/.env.qa044` to `.env`.

3. Run `uv sync`.

4. Start PostgreSQL with `docker compose up -d postgres`.

5. Drop and recreate only `multi_agent_platform_qa044`.

6. Run `uv run alembic upgrade head`.

7. Seed the Acme and Globex tenant rows.

8. Start the API with `uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000`.

9. Use `http://127.0.0.1:8000/auth/local-login` for browser sign-in.

10. Capture notes and screenshots under `/tmp/qa044-*`.

11. Keep `.data/qa044-artifacts` for generated export and evidence metadata.

12. Do not connect to live providers, real Telegram, real credentials, or
    external tools during this review.

13. Use `platform-admin` for platform operations and reliability checks.

14. Use `tenant-admin-acme` for same-tenant usage checks.

15. Use `tenant-admin-globex` only when you need a cross-tenant comparison.

## Step-by-Step Manual QA

1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations`.

2. Select `platform-admin`.

3. Confirm the browser lands on `/admin/app/operations`.

4. Confirm the page shows operations content in the React shell.

5. Capture `/tmp/qa044-operations-screen.png`.

6. Open `/admin/operations?trace_id=trace-qa044&panel=runs`.

7. Confirm the browser redirects to `/admin/app/operations`.

8. Confirm `trace_id=trace-qa044` remains visible in the URL.

9. Confirm `panel=runs` remains visible in the URL.

10. Write the old URL and destination URL in `/tmp/qa044-legacy-redirect-notes.txt`.

11. Open `/admin/reliability/ui/?tenant_id=11111111-1111-1111-1111-111111111111`.

12. Confirm the browser redirects to `/admin/app/operations` with `panel=reliability`.

13. Confirm the Acme tenant id remains in the URL.

14. Capture `/tmp/qa044-reliability-screen.png`.

15. Open `/admin/reliability/ui/breakers?state=open`.

16. Confirm the browser redirects to `/admin/app/operations` with `panel=breakers`.

17. Confirm `state=open` remains in the URL.

18. Open `/admin/reliability/ui/dead-letters?status=pending`.

19. Confirm the browser redirects to `/admin/app/operations` with `panel=dead-letters`.

20. Confirm `status=pending` remains in the URL.

21. Open `/admin/runs?tenant_id=11111111-1111-1111-1111-111111111111`.

22. Confirm the browser redirects to `/admin/app/operations` with `panel=runs`.

23. Capture `/tmp/qa044-run-debug-screen.png` if run search or run detail content is visible.

24. Open `/runs`.

25. Confirm the browser redirects to `/admin/app/channels`.

26. Confirm no deleted `runs/index.html` page appears.

27. Open `/admin/usage?tenant_id=11111111-1111-1111-1111-111111111111&group_by=provider`.

28. Confirm the browser redirects to `/admin/app/usage`.

29. Confirm the Acme tenant id and `group_by=provider` remain in the URL.

30. Capture `/tmp/qa044-usage-screen.png`.

31. In the usage page, review totals, rollups, and events if seed data is present.

32. Confirm usage rows do not display raw prompts, raw completions, raw provider
    authorization headers, or raw CSV contents.

33. Create or open a usage export detail if deterministic export data is
    available.

34. Confirm export detail shows metadata only: status, row count, checksum,
    artifact reference, created time, completed time, and safe filters.

35. Switch local login to `tenant-admin-acme`.

36. Open `/admin/app/usage?tenant_id=11111111-1111-1111-1111-111111111111`.

37. Confirm same-tenant usage is allowed or shows an authorized empty state.

38. Open `/admin/app/usage?tenant_id=22222222-2222-2222-2222-222222222222`.

39. Confirm cross-tenant data is denied or hidden.

40. Switch back to `platform-admin` for platform operations checks.

41. Open the React operations route again.

42. Check the visible links from the operations page.

43. Confirm internal links point to React destinations, such as
    `/admin/app/operations` and `/admin/app/usage`.

44. Confirm old links do not point back to deleted Jinja pages.

45. Run the focused backend tests from `qa044.md`.

46. Run the focused frontend tests from `qa044.md`.

47. Run the QA document validator.

48. Run Spec QA and Playwright validation.

49. Open `output/playwright/qa044_ui/qa044-react-ui2-smoke.png`.

50. Confirm the screenshot shows the React operations workspace.

51. Attach notes describing any empty-state behavior.

52. Stop if a deleted Jinja page renders, a redirect loses tenant context, or
    raw sensitive data appears.

## Expected Results

Expected: `/admin/operations` returns a browser redirect to `/admin/app/operations`.

Expected: operations query values such as `trace_id`, `run_id`, `tenant_id`,
`panel`, and `saved_filter_id` are preserved when safe.

Expected: `/admin/operations/api/dashboard` still returns JSON for React.

Expected: `/admin/reliability/ui/` redirects to React reliability state.

Expected: `/admin/reliability/ui/breakers` redirects to React breaker state.

Expected: `/admin/reliability/ui/dead-letters` redirects to React dead-letter state.

Expected: `/admin/runs` redirects to React run search state.

Expected: admin run detail and browser replay links redirect to React when the
principal is authorized.

Expected: JSON replay and retained run APIs still work for React and API callers.

Expected: `/runs`, `/runs/new`, and `/runs/{run_id}` do not render deleted Jinja
templates.

Expected: `/admin/usage` redirects to `/admin/app/usage`.

Expected: usage export detail redirects only after authorization succeeds.

Expected: same-tenant usage access is allowed for the tenant principal.

Expected: cross-tenant usage access fails closed.

Expected: no visible page exposes secrets, provider headers, raw prompts, raw
completions, private channel messages, raw memory contents, raw CSV rows, or
stack traces.

Expected: the retirement scanner test proves the deleted template and static
paths remain absent.

## Evidence To Capture

Capture `/tmp/qa044-env-summary.txt` after checking the environment file.

Capture `/tmp/qa044-operations-screen.png` from the React operations route.

Capture `/tmp/qa044-reliability-screen.png` from the reliability panel.

Capture `/tmp/qa044-run-debug-screen.png` from the run search or run detail area.

Capture `/tmp/qa044-usage-screen.png` from the usage dashboard.

Capture `/tmp/qa044-legacy-redirect-notes.txt` with old URL, destination URL,
principal, and expected result.

Capture `/tmp/qa044-focused-backend.txt` from the focused backend tests.

Capture `/tmp/qa044-frontend-tests.txt` and `/tmp/qa044-frontend-build.txt` from
the React tests and production build.

Capture the QA document validator output.

Capture the Spec QA command output.

Capture the Playwright screenshot path
`output/playwright/qa044_ui/qa044-react-ui2-smoke.png`.

Capture any denied-state screenshots that prove cross-tenant protection.

Do not capture database passwords, external credentials, private tokens, raw
provider request headers, or raw customer content.

## Security And Redaction Checks

Search visible browser text for secret-like values.

Search QA output files under `/tmp/qa044-*` for `authorization`, `bearer`,
`sk-`, raw prompts, raw completions, raw memory, private channel messages, and
raw CSV rows.

Confirm usage export detail shows metadata only.

Confirm run replay and lineage views do not show unauthorized run payloads.

Confirm operations logs are summarized and redacted.

Confirm reliability dead-letter views do not reveal private payload bodies.

Confirm local-principal `.env.qa044` uses fake static secret references with
the `qa044/` prefix.

Confirm external connector and live provider settings are disabled.

Stop validation if any real credential-looking value appears.

Stop validation if a stack trace or raw exception appears in a browser page.

Stop validation if a deleted template path is rendered as visible page content.

## Tenant Isolation Checks

Use `platform-admin` for platform operations.

Use `tenant-admin-acme` for same-tenant usage.

Use `tenant-admin-globex` only for cross-tenant comparison.

Acme tenant id is `11111111-1111-1111-1111-111111111111`.

Globex tenant id is `22222222-2222-2222-2222-222222222222`.

Same-tenant Acme usage should be allowed for `tenant-admin-acme`.

Globex usage should not be visible to `tenant-admin-acme`.

Platform-only operations data should not become available to a tenant-only
principal through an old redirect.

Run detail links should not reveal whether a cross-tenant run exists.

Usage export detail should check authorization before redirecting to React.

Redirects may carry safe tenant ids, filters, and panel names.

Redirects must not carry raw payloads, secrets, provider headers, or private
message bodies.

## Troubleshooting

If the browser does not show local login, confirm `AUTH_MODE=local_principal`
is present in `.env`.

If local login returns to the wrong page, use
`http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/operations`.

If a route still shows an old page, restart the API process.

If React assets look stale, run `cd frontend/admin && npm run build` and restart
the API.

If the QA database has old rows, recreate only `multi_agent_platform_qa044`.

If usage pages are empty, that can be acceptable when the database has no usage
events; the redirect and safe empty state still matter.

If reliability panels are empty, that can be acceptable when no breaker or
dead-letter rows are seeded; the redirect and governed empty state still matter.

If Playwright cannot find `Operations`, sign in with `platform-admin`, rebuild
React, and rerun the Playwright validation.

If the retirement scanner fails, do not approve the spec until the remaining
reference is removed or the route is proven safe another way.

If a cross-tenant check returns data, stop immediately and record the URL,
principal, screenshot, and response body path.

If any command tries to drop a database other than `multi_agent_platform_qa044`,
stop immediately.
