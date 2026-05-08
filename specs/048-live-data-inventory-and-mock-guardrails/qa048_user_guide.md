# QA048 User Guide: Spec 048 - Live Data Inventory And Mock Guardrails

## Detailed Overview

QA048 creates the inventory reviewers use to remove mock data from the React admin platform.

The expected state is a controlled warning.

The warning means there are mapped legacy findings.

The warning does not mean new unclassified mock data is acceptable.

Every existing finding must have an owner spec.

Every owner spec must point to one of Specs 049 through 058 when cleanup remains.

Computed scanner metadata is allowed only through narrow allowlist entries.

Route target coverage is mandatory for static admin React JSON and mutation routes.

The React migration page is the browser-first view for this inventory.

The live-data route is `/admin/app/migration/live-data-inventory.json`.

The migration page is `/admin/app/migration`.

The generated TypeScript contract includes `LiveDataInventoryDashboard`.

The React client fetches the live-data dashboard independently of the bootstrap payload.

The dashboard bootstrap still embeds `live_data_inventory` as a fallback.

The scanner searches production source paths, generated contracts, and built assets.

Test-only markers are counted but not treated as production findings.

New unallowlisted production markers become blocking findings.

Blocking findings must stop the spec until fixed or explicitly mapped.

The UI panel intentionally shows the cleanup queue.

The UI panel must not show raw prompts.

The UI panel must not show credential values.

The UI panel must not show local absolute paths.

The UI panel must not show private messages.

The UI panel must not expose unauthorized tenant labels.

The route coverage helper compares registered admin React routes with the live-data target registry.

The backend route tests prove local-principal and Auth0-shaped principals receive safe payloads.

The contract tests prove OpenAPI names the live-data endpoint.

The component tests prove the React panel renders mapped findings and safe evidence.

The Playwright flow proves the browser workspace displays the panel.

The post-UI API check proves the browser-facing endpoint returns zero blocking findings.

The curl regression proves the rest of the local API surface still works.

The `.env.qa048` file isolates database, storage, auth, and fake secret references.

No live provider, Telegram, or external connector calls are required.

QA048 completion is allowed only after docs, focused tests, Spec QA, Playwright QA, post-UI API evidence, and curl regression pass.

## Who Should Use This Guide

Use this guide if you are reviewing qa048 from the browser.

Use this guide if you need to confirm the mock-data inventory warning state.

Use this guide if you are collecting evidence for PR review.

Use this guide if you are preparing Specs 049 through 058 cleanup work.

Use this guide if you need a non-code explanation of why warning state is expected.

Do not use this guide to approve unmapped production fixture regressions.

Do not use this guide to run live provider probes.

Do not use this guide to copy raw logs into QA evidence.

## Manual QA Prerequisites

You need local access to the repository.

You need Docker available for PostgreSQL.

You need `uv` available for Python commands.

You need Node and npm through the project-supported frontend toolchain.

You need `.env.qa048` copied to `.env`.

You need the React admin assets built.

You need the FastAPI server running locally.

You need the `platform-admin` local principal.

You need enough time to run the Playwright and curl validations.

You need a place to record screenshots and notes.

## Step-by-Step Manual QA

1. Copy `specs/048-live-data-inventory-and-mock-guardrails/.env.qa048` to `.env`.

2. Run `uv sync`.

3. Start PostgreSQL with `docker compose up -d postgres`.

4. Recreate `multi_agent_platform_qa048`.

5. Run `uv run alembic upgrade head`.

6. Seed Acme and Globex tenant rows.

7. Run focused backend tests for the live-data scanner, contract, and route.

8. Run generated TypeScript contract check.

9. Run migration hardening React tests.

10. Run frontend typecheck.

11. Run frontend build.

12. Run `uv run ruff check .`.

13. Run `uv run ruff format --check .`.

14. Run `uv run mypy src`.

15. Run full coverage with the repository threshold.

16. Start the app with `uv run uvicorn multi_agent_platform.api.main:app --reload`.

17. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/migration`.

18. Sign in as `platform-admin`.

19. Confirm the migration page loads.

20. Confirm the `React-only browser UI` heading appears.

21. Confirm the `React-only readiness` panel still appears.

22. Confirm the `Live-data guardrails` panel appears.

23. Confirm summary metrics include findings.

24. Confirm summary metrics include mapped findings.

25. Confirm summary metrics include blocking findings.

26. Confirm blocking findings are zero.

27. Confirm computed metadata appears as its own count.

28. Confirm route targets appear.

29. Confirm seeded scans appear.

30. Confirm the findings table uses repository-relative source paths.

31. Confirm replacement specs are displayed for mapped entries.

32. Confirm evidence IDs are safe QA references.

33. Click Refresh.

34. Confirm the live-data panel remains visible after refresh.

35. Capture a full-page screenshot.

36. Save reviewer notes under `/tmp/qa048-ui-evidence.txt`.

37. Run the post-UI API check for `/admin/app/migration/live-data-inventory.json`.

38. Confirm the post-UI API check returns HTTP 200.

39. Confirm route target count is greater than zero.

40. Confirm blocking finding count is zero.

41. Run the route-target coverage helper.

42. Confirm it prints an empty tuple.

43. Run Spec QA with the qa048 validation manifest.

44. Run Playwright QA with `--start-processes`.

45. Run the multi-agent curl regression.

46. Confirm curl evidence is written under `.data/curl_test_runs/qa048-after-spec`.

47. Update the spec status file with command results.

48. Mark qa048 tasks complete only after evidence is present.

49. Stop if any blocking finding appears.

50. Stop if the curl regression fails after one focused repair attempt.

## Expected Results

Expected: `.env.qa048` uses `multi_agent_platform_qa048`.

Expected: `.env.qa048` stores artifacts under `.data/qa048-artifacts`.

Expected: `.env.qa048` uses `qa048/` fake secret references.

Expected: focused backend tests pass.

Expected: generated TypeScript check passes.

Expected: migration hardening React tests pass.

Expected: frontend typecheck passes.

Expected: frontend build passes.

Expected: Ruff passes.

Expected: format check passes.

Expected: mypy passes.

Expected: coverage passes.

Expected: Spec QA passes.

Expected: Playwright QA passes.

Expected: the live-data panel appears in the browser.

Expected: the live-data endpoint returns HTTP 200 for `platform-admin`.

Expected: the live-data endpoint returns zero blocking findings.

Expected: mapped findings remain warnings until Specs 049 through 058 remove them.

Expected: route-target coverage has no static gaps.

Expected: curl regression passes.

Expected: reviewer evidence contains qa048 references.

Expected: reviewer evidence avoids raw prompts.

Expected: reviewer evidence avoids credential values.

Expected: reviewer evidence avoids private messages.

Expected: reviewer evidence avoids local absolute paths.

Expected: reviewer evidence avoids stack traces.

Expected: reviewer evidence avoids unauthorized tenant labels.

Expected: status evidence records the Playwright screenshot path.

Expected: status evidence records the curl output directory.

Expected: qa048 remains a warning-state inventory, not a complete live-data cleanup.

## Evidence To Capture

Capture `/tmp/qa048-api-evidence.txt`.

Capture `/tmp/qa048-quality-evidence.txt`.

Capture `/tmp/qa048-ui-evidence.txt`.

Capture `/tmp/qa048-curl-evidence.txt`.

Capture the Playwright screenshot path.

Capture focused backend test output.

Capture frontend test output.

Capture generated TypeScript check output.

Capture QA document validation output.

Capture Spec QA output.

Capture Playwright QA output.

Capture curl regression output.

Capture the post-UI endpoint status and counts.

Capture the route-target coverage result.

## Security And Redaction Checks

Confirm evidence does not contain raw prompts.

Confirm evidence does not contain raw completions.

Confirm evidence does not contain credential values.

Confirm evidence does not contain authorization headers.

Confirm evidence does not contain private channel messages.

Confirm evidence does not contain raw memory contents.

Confirm evidence does not contain raw run payloads.

Confirm evidence does not contain raw external tool payloads.

Confirm evidence does not contain local absolute paths.

Confirm evidence does not contain stack traces.

Confirm evidence uses safe QA references and relative source paths.

## Tenant Isolation Checks

Confirm `tenant-admin-acme` can only read Acme-scoped tenant views.

Confirm the cross-tenant live-data route test returns 403.

Confirm the cross-tenant response does not name the other tenant in the response body.

Confirm the platform admin route remains safe for platform-scoped inventory.

Confirm Auth0-shaped principal evidence does not serialize token subject values.

Confirm tenant query parameters are preserved when the React page reloads.

Confirm evidence does not contain unauthorized tenant labels.

## Troubleshooting

If backend tests report a new regression, inspect the finding source path.

If the path is a real production source path, remove the marker or map it to the correct cleanup spec.

If the path is test-only, update the scanner exclusion rather than allowlisting production roots.

If computed metadata is blocked, verify the allowlist scope is narrow.

If route coverage reports a missing static route, add a route target or justify a parameterized deferred route.

If generated TypeScript is stale, run the generator without `--check`.

If the React panel fails to render, verify `live_data_inventory` is present in test fixtures.

If optional fetches fail, confirm the page falls back to the bootstrap payload.

If the browser shows an unavailable state, verify local-principal auth is active.

If the local login page lacks `platform-admin`, inspect `LOCAL_PRINCIPAL_CATALOG_JSON`.

If the endpoint returns 403, check the principal and tenant query.

If the endpoint returns unsafe text, replace the raw value with an existing safe summary or evidence reference.

If Playwright cannot start processes, rerun the manifest dry-run and inspect the qa048 env path.

If screenshot text overlaps, fix CSS before accepting UI evidence.

If frontend build fails after generated contracts change, rerun type generation and review imports.

If Ruff flags the OpenAPI test, prefer `Path.open` over direct file handles.

If mypy flags route helpers, keep public return types explicit.

If coverage falls below threshold, add focused tests for the changed scanner or route branch.

If curl regression fails, capture the first failing command and stop after one focused repair attempt.

If docs validation fails, inspect required headings and line counts before changing implementation code.

If status files drift from queue state, update both before moving to the next spec.

If branch state is dirty from unrelated user work, do not revert it.

If evidence mentions qa047 by mistake, regenerate qa048-specific evidence.

If the dashboard status is warning, verify the warning is caused by mapped legacy findings rather than blocking regressions.

If blocking findings are nonzero, qa048 is not complete.
