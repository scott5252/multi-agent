# QA040 User Guide: Spec 040 - Workflow Registry Full React Parity And Jinja Removal

## Detailed Overview

Spec 040 changes the workflow administration experience so the browser uses React instead of workflow-owned Jinja templates.

The workflow registry is the place where an administrator reviews workflow drafts, creates new drafts, edits the active draft, validates readiness, checks publish gates, reviews revision history, and inspects published version details.

Before this spec, several browser pages were rendered from workflow templates.

After this spec, those browser pages are served by the React admin app.

The backend still owns the important decisions.

The browser does not decide who can see a workflow.

The browser does not decide whether a workflow can be published.

The browser does not decide whether a test-bench evidence item is current.

The browser reads safe JSON contracts from the backend and renders them.

Old workflow links still matter because they can live in bookmarks, support notes, audit records, and QA documents.

This spec keeps those links useful by redirecting them to React routes.

If an old link cannot safely map to React, the system must fail closed with a safe response.

The deleted files are workflow-owned templates and the workflow-specific JavaScript file.

The retained file is `workflow_studio.css`.

That CSS remains because shared non-Jinja login and admin styling still reference it.

Retaining the CSS is expected.

Restoring workflow templates is not expected unless rollback is explicitly needed.

Your job as a QA reviewer is to prove that the React workflow route works, the old links recover, the deleted templates are not needed, and no sensitive data leaks into screenshots or notes.

## Who Should Use This Guide

Use this guide if you are manually reviewing Spec 040.

Use this guide if you are validating the React UI2 Jinja removal roadmap.

Use this guide if you need to confirm workflow direct links still work after template deletion.

Use this guide if you are checking tenant isolation or redaction for workflow admin pages.

You do not need to be a Python or React developer.

You do need to be comfortable running local commands.

You do need to be able to capture screenshots and short notes.

You should not use real customer data.

You should not use real provider credentials.

You should not use real Auth0, Telegram, connector, or model calls.

The local QA setup uses fake secrets and deterministic principals.

## Manual QA Prerequisites

Confirm you are in the repository root.

Confirm Docker is available.

Confirm PostgreSQL can start through Docker Compose.

Confirm `uv` is available.

Confirm Node and npm are available for the React admin build.

Copy the QA environment file from the feature directory to `.env`.

Use only the `multi_agent_platform_qa040` database.

Do not drop any other database.

Run migrations before opening the browser.

Build the React admin assets before opening the browser.

Start the API on `http://127.0.0.1:8000`.

Use the local login page at `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows`.

Create an evidence folder under `/tmp/qa040-evidence`.

Keep browser screenshots under `output/playwright/qa040_ui`.

Use `platform-admin` for the first pass.

Use `tenant-admin-acme` for the tenant-scoped pass.

Use `tenant-admin-globex` only for isolation checks.

Never paste real secrets or private text into workflow fields.

## Step-by-Step Manual QA

1. Copy `.env.qa040` to `.env`.

2. Start PostgreSQL with Docker Compose.

3. Drop and recreate only `multi_agent_platform_qa040`.

4. Run Alembic migrations.

5. Seed the Acme and Globex local tenants.

6. Run `uv sync` if dependencies are not current.

7. Run `cd frontend/admin && npm run build`.

8. Start the API on port 8000.

9. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows`.

10. Confirm the local login page appears.

11. Confirm `platform-admin` is listed.

12. Click the `platform-admin` sign-in button.

13. Confirm the browser lands on `/admin/app/workflows`.

14. Wait for the React admin shell to finish loading.

15. Confirm the page contains the word `Workflow`.

16. Capture a screenshot of the loaded workflow page.

17. Inspect the workflow registry panel.

18. Confirm list, filter, or empty-state information is visible.

19. Inspect the create workflow panel.

20. Confirm template or create action state is visible.

21. Inspect the draft details form.

22. Confirm the draft name and description fields are visible.

23. Inspect prompt and profile reference selectors.

24. Confirm no raw prompt body is displayed.

25. Inspect the graph preview panel.

26. Confirm both visual graph content and list-style node or edge information are available.

27. Inspect the validation panel.

28. Run validation if the button is enabled.

29. Confirm the result updates without a full page reload.

30. Inspect the publish readiness panel.

31. Confirm blockers or ready state are shown from backend data.

32. Inspect the sharing summary.

33. Confirm no cross-tenant details are shown.

34. Inspect revision history.

35. Confirm revision summaries are visible.

36. Inspect the published version detail panel.

37. Confirm version and digest labels are visible.

38. Open `/admin/app/workflows/new` directly.

39. Confirm the React app loads after refresh.

40. Open an old workflow list URL such as `/admin/workflows/ui`.

41. Confirm it redirects to `/admin/app/workflows`.

42. Open an old workflow create URL such as `/admin/workflows/new`.

43. Confirm it redirects to `/admin/app/workflows/new`.

44. Open an old draft editor URL with a fake UUID.

45. Confirm it redirects to the matching React draft route or shows a safe React unavailable state.

46. Open an old publish gate URL with a fake UUID.

47. Confirm it redirects to the matching React publish gate route.

48. Open an old revision history URL with a fake UUID.

49. Confirm it redirects to the matching React revision route.

50. Open an old published version detail URL with a fake UUID.

51. Confirm it redirects to the matching React version route.

52. Sign out through local logout.

53. Sign in as `tenant-admin-acme`.

54. Confirm `/admin/app/workflows` loads under tenant scope.

55. Try a Globex tenant id while signed in as Acme.

56. Confirm the system denies access or shows a safe unavailable state.

57. Sign out and sign in as `tenant-admin-globex`.

58. Confirm Globex can use its own tenant scope.

59. Review page source for Jinja markers such as `{%` or `{{`.

60. Confirm no workflow template names appear in page source.

61. Review screenshots for secrets, stack traces, local paths, raw prompts, and raw completions.

62. Save all notes under `/tmp/qa040-evidence`.

## Expected Results

The local login page loads without using a Jinja template.

The workflow route loads through `/admin/app/workflows`.

The React shell displays workflow content.

The registry panel is visible.

The create panel is visible.

The draft editing form is visible.

The reference picker is visible.

The graph preview is visible.

The graph has a keyboard-readable or list alternative.

The validation panel is visible.

The publish readiness panel is visible.

The sharing summary is visible.

The revision history is visible.

The published version detail panel is visible.

Old workflow list URLs redirect to React.

Old workflow create URLs redirect to React.

Old workflow draft URLs redirect to React.

Old workflow publish gate URLs redirect to React.

Old workflow revision URLs redirect to React.

Old workflow version URLs redirect to React.

Unsafe query parameters are not preserved in redirects.

Safe tenant, filter, status, saved-filter, revision, and conflict intent may be preserved.

Acme users do not see Globex workflow details.

Unauthenticated users do not receive workflow data.

Workflow-owned templates remain deleted.

`workflow_studio.js` remains deleted.

`workflow_studio.css` remains present.

The retained CSS is documented in PR notes.

No screenshot or note contains sensitive payloads.

## Evidence To Capture

Capture the local login screen.

Capture `/admin/app/workflows` after platform-admin sign-in.

Capture the registry panel.

Capture the create panel.

Capture the draft form.

Capture the graph preview and list alternative.

Capture the validation panel.

Capture the publish readiness panel.

Capture the sharing summary.

Capture the revision history.

Capture the published version detail.

Capture at least one old workflow URL redirect.

Capture one cross-tenant denied or unavailable state.

Record the exact time of the test.

Record the principal used for each screenshot.

Record the browser URL for each screenshot.

Record whether the result matched the expected outcome.

Record any unexpected warning, loading state, or console error.

Store notes under `/tmp/qa040-evidence`.

Store screenshots under `output/playwright/qa040_ui`.

## Security And Redaction Checks

Do not use real customer workflow names.

Do not use real prompts.

Do not use real completions.

Do not use real provider credentials.

Do not use real Telegram identifiers.

Do not use real connector payloads.

Do not paste private channel messages.

Check screenshots for local file paths.

Check screenshots for stack traces.

Check screenshots for authorization headers.

Check screenshots for link tokens.

Check screenshots for raw tool payloads.

Check downloaded or saved JSON files for the same sensitive values.

If a sensitive value appears, discard the evidence and report a blocker.

If a stack trace appears, report a blocker.

If an unauthorized tenant label appears, report a blocker.

## Tenant Isolation Checks

Use Acme tenant id `11111111-1111-1111-1111-111111111111`.

Use Globex tenant id `22222222-2222-2222-2222-222222222222`.

Sign in as `tenant-admin-acme`.

Open the workflow route with the Acme tenant id.

Expected result: the route loads or shows Acme-safe workflow content.

Open the workflow route with the Globex tenant id.

Expected result: access is denied or unavailable.

Confirm the response does not reveal Globex workflow names.

Sign in as `tenant-admin-globex`.

Open the workflow route with the Globex tenant id.

Expected result: the route loads or shows Globex-safe workflow content.

Confirm Acme workflow details are not shown to Globex.

Record the outcome for both tenants.

Treat any cross-tenant leak as a stop condition.

## Troubleshooting

If the login page does not show local principals, confirm `.env` came from `.env.qa040`.

If the workflow page is blank, rebuild React assets.

If the browser shows a 404 on a React child route, confirm the admin React fallback includes workflow paths.

If old workflow URLs render HTML with workflow page content instead of redirecting, stop and inspect the legacy route handler.

If the CSS looks plain, confirm `workflow_studio.css` still exists.

If a JavaScript error blocks the workflow panels, save the console message and stop before queue advancement.

If validation buttons are disabled, note whether the panel gives a backend-owned reason.

If a publish action is blocked, note the blocker text and confirm it does not expose private evidence.

If the cross-tenant check reveals the wrong tenant label, stop and report a security blocker.

If Playwright fails to find `Workflow`, inspect the API log and the screenshot.

If full coverage fails, preserve the output and identify whether the failure belongs to Spec 040 before making changes.

If a deleted template file reappears, stop and identify which command restored it.

If `workflow_studio.js` reappears, stop and identify which static asset process restored it.

If only `workflow_studio.css` remains, that is expected for Spec 040.
