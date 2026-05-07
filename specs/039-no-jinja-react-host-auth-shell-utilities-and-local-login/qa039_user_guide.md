# QA039 User Guide: Spec 039 - No-Jinja React Host, Auth, Shell Utilities, And Local Login

## Detailed Overview

Spec 039 changes how reviewers and administrators enter the admin UI.
Before this change, the visible UI was mostly React, but the first HTML document for `/admin/app` still came from a Jinja template.
The local-principal login page also came from a Jinja template.
The old `/admin` landing page rendered an admin shell template.
Saved-filter utility pages rendered shell templates too.
This spec removes those shell/auth template dependencies from the admin entry path.
The React admin app is now served by a backend HTML response assembled without Jinja.
The local login page is now a safe non-Jinja response backed by a JSON contract.
The old `/admin` route redirects to `/admin/app`.
The saved-filter utility route redirects to a React route.
The saved-filter data itself comes from `/admin/filters/workflows.json`.
Authorization decisions still belong to the backend.
Tenant scope decisions still belong to the backend.
Redirect sanitization still belongs to the backend.
Action-token checking for local login still belongs to the backend.
The browser renders what the backend allows.
The browser does not invent roles or tenant labels.
The browser does not decide which saved filters are visible.
The browser does not decide whether old Jinja templates are safe to delete.
Only two templates are deleted in this spec.
The deleted templates are the React host template and local-login template.
The shared `admin_shell` templates are retained for later specs.
Those shared templates are still used by domain-specific legacy pages.
Later specs remove those domain pages one group at a time.
This guide helps a non-developer reviewer verify the change safely.
The reviewer will use local-principal login, inspect the React host, follow redirects, and capture evidence.
The reviewer will not use real Auth0.
The reviewer will not use real provider credentials.
The reviewer will not make real Telegram calls.
The reviewer will not call external tools.
All checks use deterministic local data and fake secret references.

## Who Should Use This Guide

Use this guide if you are reviewing Spec 039 manually.
Use this guide if you need to confirm that local login still works.
Use this guide if you need to confirm that `/admin/app` loads React.
Use this guide if you need to confirm that `/admin` redirects to React.
Use this guide if you need to confirm that saved-filter utility links do not render Jinja.
Use this guide if you need to collect screenshots for release review.
Use this guide if you are validating tenant isolation in the browser.
Use this guide if you are checking for unsafe raw details in screenshots.
Use this guide before approving Spec 040 to start domain-specific Jinja deletion.

## Manual QA Prerequisites

1. You have the repository checked out on the Spec 039 branch.
2. You have Docker available for PostgreSQL.
3. You have Python dependencies installed through `uv`.
4. You have frontend dependencies installed in `frontend/admin`.
5. You have copied `.env.qa039` to `.env`.
6. You have built React assets with `npm run build`.
7. You have run database migrations.
8. You have started the API on `127.0.0.1:8000`.
9. You know the QA local principals.
10. You will save screenshots under `output/playwright/qa039_ui`.
11. You will save notes under `/tmp/qa039-ui-notes.md`.
12. You will stop if a response shows a stack trace.
13. You will stop if a response shows a real credential.
14. You will stop if an Acme user can see Globex-only information.
15. You will stop if `/admin/app` renders a Jinja template.

## Step-by-Step Manual QA

1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app`.
2. Confirm the page says `Local Login`.
3. Confirm the page says `Choose a local principal`.
4. Confirm `platform-admin` is visible.
5. Confirm `tenant-admin-acme` is visible.
6. Confirm `tenant-user-acme` is visible.
7. Confirm there is no stack trace on the page.
8. Confirm there is no local filesystem path on the page.
9. Capture a screenshot named `qa039-local-login.png`.
10. Click the `platform-admin` sign-in button.
11. Confirm the browser redirects to `/admin/app`.
12. Wait for the React admin page to finish loading.
13. Confirm the page contains `Admin`.
14. Confirm shell navigation is visible.
15. Confirm command or search UI is available if the shell exposes it in this viewport.
16. Capture a screenshot named `qa039-admin-app-platform.png`.
17. Refresh the browser.
18. Confirm the page still loads.
19. Navigate to `http://127.0.0.1:8000/admin`.
20. Confirm the browser redirects back to `/admin/app`.
21. Record the final URL in your notes.
22. Navigate to `http://127.0.0.1:8000/admin/app/migration`.
23. Confirm the migration dashboard loads.
24. Confirm it does not ask you to open an old admin console.
25. Capture a screenshot named `qa039-migration.png`.
26. Navigate to `http://127.0.0.1:8000/admin/filters/workflows`.
27. Confirm the browser redirects to `/admin/app/saved-filters/workflows`.
28. Confirm the page shows saved filters or a safe empty state.
29. Capture a screenshot named `qa039-saved-filters.png`.
30. Navigate to `http://127.0.0.1:8000/auth/local-logout?redirect_to=/auth/local-login`.
31. Confirm the browser returns to local login.
32. Sign in as `tenant-admin-acme`.
33. Confirm `/admin/app` loads.
34. Confirm the tenant-scoped experience does not show platform-only dangerous actions.
35. Navigate to a Globex tenant URL by replacing Acme tenant id with Globex tenant id where a query parameter is visible.
36. Confirm the response is denied or unavailable.
37. Confirm the response does not include the word `Globex`.
38. Return to local login.
39. Sign in as `tenant-user-acme`.
40. Confirm the user can load only authorized safe destinations.
41. Record any denied state text exactly as displayed.
42. Confirm denied text does not reveal whether a protected resource exists.
43. Open browser developer tools.
44. Inspect the first `/admin/app` document response.
45. Confirm the response header `X-React-Admin-Host` is `non-jinja`.
46. Inspect `/auth/local-login`.
47. Confirm the response header `X-Local-Login-Response` is `non-jinja`.
48. Inspect `/admin/filters/workflows.json`.
49. Confirm the JSON contains `admin_area`.
50. Confirm the JSON contains `active_scope`.
51. Confirm the JSON contains `saved_filters`.
52. Confirm the JSON contains `actions`.
53. Search visible text for raw secret-like values.
54. Search visible text for local filesystem paths.
55. Search visible text for stack traces.
56. Save final notes under `/tmp/qa039-ui-notes.md`.

## Expected Results

Expected: local login renders without any Jinja template markers.
Expected: local login lists only enabled local principals.
Expected: local login sanitizes unsafe redirect destinations back to `/admin/app`.
Expected: platform-admin can reach `/admin/app`.
Expected: tenant-admin-acme can reach `/admin/app`.
Expected: tenant-user-acme can reach only authorized surfaces.
Expected: `/admin` redirects to `/admin/app`.
Expected: `/admin/app` returns a non-Jinja host header.
Expected: `/admin/app/migration` loads through the same React host.
Expected: `/admin/filters/workflows` redirects to React saved filters.
Expected: `/admin/filters/workflows.json` returns safe JSON.
Expected: denied states do not expose unauthorized tenant labels.
Expected: screenshots do not contain raw secrets.
Expected: screenshots do not contain local paths.
Expected: screenshots do not contain stack traces.
Expected: reviewer notes identify retained shared shell templates.

## Evidence To Capture

- `output/playwright/qa039_ui/qa039-react-ui2-smoke.png`
- `output/playwright/qa039_ui/qa039-local-login.png`
- `output/playwright/qa039_ui/qa039-admin-app-platform.png`
- `output/playwright/qa039_ui/qa039-migration.png`
- `output/playwright/qa039_ui/qa039-saved-filters.png`
- `/tmp/qa039-ui-notes.md`
- `/tmp/qa039-admin-app.headers`
- `/tmp/qa039-local-login.headers`
- `/tmp/qa039-local-login.json`
- `/tmp/qa039-saved-filters.json`
- `/tmp/qa039-redaction.log`
- `/tmp/qa039-playwright.log`

## Security And Redaction Checks

Check that the UI does not show raw secrets.
Check that the UI does not show credential values.
Check that the UI does not show provider authorization headers.
Check that the UI does not show raw prompts.
Check that the UI does not show raw completions.
Check that the UI does not show memory contents.
Check that the UI does not show raw run payloads.
Check that the UI does not show raw tool payloads.
Check that the UI does not show raw test transcripts.
Check that the UI does not show full Telegram identifiers.
Check that the UI does not show link tokens after creation.
Check that the UI does not show local filesystem paths.
Check that the UI does not show stack traces.
Check that the UI does not show unauthorized tenant labels.
Check that the local-principal login page is unavailable unless local-principal mode is active.
Check that unsafe redirect URLs are not accepted.
Check that denied states have safe summaries.

## Tenant Isolation Checks

Use `tenant-admin-acme` for the Acme checks.
Use Acme tenant id `11111111-1111-1111-1111-111111111111`.
Use Globex tenant id `22222222-2222-2222-2222-222222222222`.
Open an Acme route first.
Confirm Acme-scoped behavior is allowed.
Change the tenant id query to the Globex tenant id.
Confirm the request is denied.
Confirm the response does not reveal the Globex display name.
Confirm saved-filter JSON does not show filters from another tenant.
Confirm platform-admin can still switch to platform scope.
Confirm tenant-user-acme cannot see platform-only controls.
Record the exact status and route in reviewer notes.

## Troubleshooting

If the local login page is missing, confirm `.env.qa039` is copied to `.env`.
If local principals are missing, inspect `LOCAL_PRINCIPAL_CATALOG_JSON`.
If `/admin/app` shows an asset warning, rebuild frontend assets.
If `/admin/app` returns 401, sign in again through local login.
If `/admin` does not redirect, run the backend route tests.
If saved filters do not load, open `/admin/filters/workflows.json` directly.
If a screenshot shows unsafe data, stop and record a blocker.
If a route renders an old shell page, stop and record the route.
If Docker resets a different database, stop immediately.
If Playwright cannot find `Admin`, confirm the login click succeeded.
If full validation is slow, keep the focused command evidence while it runs.

## Related Files

- `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/qa039.md`
- `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/qa039_ui.md`
- `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/.env.qa039`
- `specs/039-no-jinja-react-host-auth-shell-utilities-and-local-login/pr_notes.md`
- `src/multi_agent_platform/api/routers/admin_react.py`
- `src/multi_agent_platform/api/routers/auth.py`
- `src/multi_agent_platform/api/routers/admin_console.py`
- `frontend/admin/src/App.tsx`
- `frontend/admin/src/components/savedFilters/SavedFilterManagementPage.tsx`
- `tests/integration/api/test_admin_react_no_jinja_host_routes.py`
