# QA038 User Guide: Spec 038 - Jinja Surface Inventory And Deletion Plan

## Detailed Overview

QA038 is a review of the Jinja surface inventory.

The purpose is to make sure the team knows every old server-rendered Jinja surface before any of those surfaces are removed.

The inventory includes templates.

The inventory includes template include and extend relationships.

The inventory includes legacy JavaScript and CSS files that belong to the old admin experience.

The inventory includes Python code that creates `TemplateResponse` output.

The inventory includes `Jinja2Templates` imports and template provider usage.

The inventory includes browser routes that still depend on Jinja rendering.

The inventory includes helper files that feed Jinja pages.

The inventory includes documentation and QA links that point directly to legacy admin or run URLs.

The inventory is grouped by the future spec that owns the later removal work.

Spec 038 does not delete anything.

Spec 038 does not mark anything safe to delete.

Spec 038 creates the baseline that later specs must use.

The React migration dashboard shows the inventory in a reviewer-friendly panel.

The backend also exposes the inventory as JSON.

The JSON route is protected by the same local-principal and tenant-scope checks as other admin React routes.

Platform reviewers use the full service-level inventory.

Tenant reviewers use tenant-safe scoped views.

Acme users must not see Globex data.

Reviewer evidence must not include secrets.

Reviewer evidence must not include raw prompts or raw completions.

Reviewer evidence must not include private messages.

Reviewer evidence must not include raw run payloads.

Reviewer evidence must not include local absolute workstation paths.

Reviewer evidence should use the QA038 local database only.

Reviewer evidence should use fake secret references only.

The expected inventory snapshot is 533 total items.

The expected template count is 160.

The expected route count is 182.

The expected static asset count is 9.

The expected direct-link count is 157.

The expected blocked count is 33.

The expected safe-to-delete count is 0.

## Who Should Use This Guide

Use this guide if you are reviewing whether Spec 038 is ready to support later Jinja removal specs.

Use this guide if you need to confirm that the migration dashboard shows Jinja inventory evidence.

Use this guide if you need to confirm tenant-safe inventory behavior.

Use this guide if you need to confirm redaction-safe evidence.

Use this guide if you are not changing code but need to approve the inventory baseline.

Use this guide if you need a plain-language companion to `qa038.md`.

Do not use this guide to approve template deletion.

Do not use this guide to approve removal of Jinja dependencies.

Do not use this guide against production data.

Do not use this guide with real provider credentials.

## Manual QA Prerequisites

You need a local checkout of the repository.

You need Docker available for PostgreSQL.

You need the QA038 branch checked out.

You need the file `specs/038-jinja-surface-inventory-and-deletion-plan/.env.qa038`.

You need the React admin dependencies installed.

You need the Python dependencies installed through `uv sync`.

You need the local database named `multi_agent_platform_qa038`.

You need Acme tenant id `11111111-1111-1111-1111-111111111111`.

You need Globex tenant id `22222222-2222-2222-2222-222222222222`.

You need local-principal login enabled.

You need fake secret references beginning with `qa038/`.

You need a browser for the manual walkthrough.

You need a place to store screenshots.

Use `output/playwright/qa038_ui` for automated browser evidence.

Use `/tmp/qa038-*` for command evidence.

Keep the evidence until review is complete.

## Step-by-Step Manual QA

1. Back up any existing local `.env` file.

2. Copy `specs/038-jinja-surface-inventory-and-deletion-plan/.env.qa038` to `.env`.

3. Run `uv sync`.

4. Go to `frontend/admin`.

5. Run `npm install`.

6. Run `npm run build`.

7. Return to the repository root.

8. Start PostgreSQL with `docker compose up -d postgres`.

9. Drop only the `multi_agent_platform_qa038` database.

10. Recreate only the `multi_agent_platform_qa038` database.

11. Run `uv run alembic upgrade head`.

12. Seed the Acme and Globex tenants.

13. Create `.data/qa038-artifacts`.

14. Create `output/playwright/qa038_ui`.

15. Start the API with `uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000`.

16. Start the worker with `uv run python -m multi_agent_platform.workers.main`.

17. Open `http://127.0.0.1:8000/auth/local-login`.

18. Select `platform-admin`.

19. Open `http://127.0.0.1:8000/admin/app/migration`.

20. Wait for the migration dashboard to finish loading.

21. Confirm the page has a migration heading.

22. Find the Jinja inventory area.

23. Confirm the area is titled `Deletion readiness`.

24. Confirm the summary shows templates.

25. Confirm the summary shows routes.

26. Confirm the summary shows assets.

27. Confirm the summary shows direct links.

28. Confirm the summary shows blocked items.

29. Confirm the summary shows safe items.

30. Confirm the safe item count is zero.

31. Review the group for Spec 039.

32. Review the group for Spec 040.

33. Review the group for Spec 041.

34. Review the group for Spec 042.

35. Review the group for Spec 043.

36. Review the group for Spec 044.

37. Review the group for Spec 045.

38. Review the group for Spec 046.

39. Review the group for Spec 047.

40. Confirm representative rows show repo-relative paths.

41. Confirm representative rows show replacement targets.

42. Confirm representative rows show readiness labels.

43. Confirm representative rows show evidence references.

44. Confirm representative rows show blocker references when blocked.

45. Confirm at least one row says `Blocked`.

46. Confirm at least one row says `Compatibility needed`.

47. Confirm no row says deletion is approved by QA038.

48. Capture a platform screenshot.

49. Return to `http://127.0.0.1:8000/auth/local-login`.

50. Select `tenant-admin-acme`.

51. Open `http://127.0.0.1:8000/admin/app/migration?tenant_id=11111111-1111-1111-1111-111111111111`.

52. Confirm the tenant-scoped page loads.

53. Confirm tenant-safe inventory is visible.

54. Confirm platform-only operations deletion inventory is not shown in tenant-only context.

55. Capture a tenant screenshot.

56. While still signed in as Acme, try `http://127.0.0.1:8000/admin/app/migration?tenant_id=22222222-2222-2222-2222-222222222222`.

57. Confirm the page does not show Globex inventory details.

58. Capture a note about the denied or redirected state.

59. Return to platform admin.

60. Refresh the migration page.

61. Confirm the inventory panel still loads.

62. Resize the browser to a mobile width.

63. Confirm the summary remains readable.

64. Confirm table rows can be inspected without text overlap.

65. Capture a mobile screenshot.

66. Run the focused backend tests from `qa038.md`.

67. Run the focused frontend tests from `qa038.md`.

68. Run the QA document validator.

69. Run the generated API and quality validation.

70. Run the generated Playwright validation.

71. Save the Playwright screenshot path in your notes.

72. Save the inventory JSON path in your notes.

73. Record whether the reviewer approves the inventory baseline.

74. Record that no deletion is approved by Spec 038.

## Expected Results

Expected: the API health check passes.

Expected: the React admin shell loads.

Expected: the migration dashboard loads.

Expected: the Jinja inventory panel is visible.

Expected: the panel title is `Deletion readiness`.

Expected: total inventory is nonzero.

Expected: template inventory is nonzero.

Expected: route inventory is nonzero.

Expected: static asset inventory is nonzero.

Expected: direct-link inventory is nonzero.

Expected: blocked inventory is nonzero.

Expected: safe-to-delete inventory is zero.

Expected: each visible source path is repo-relative.

Expected: evidence labels are short and safe.

Expected: no raw secret value appears.

Expected: no raw prompt appears.

Expected: no raw completion appears.

Expected: no private message appears.

Expected: no local absolute workstation path appears.

Expected: Acme tenant admin can view Acme scope.

Expected: Acme tenant admin cannot view Globex scope.

Expected: focused backend tests pass.

Expected: focused frontend tests pass.

Expected: QA document validation passes.

Expected: Playwright captures `qa038-react-ui2-smoke.png`.

Expected: reviewer notes say that no deletion is approved.

## Evidence To Capture

Capture `/tmp/qa038-health-live.txt`.

Capture `/tmp/qa038-health-ready.txt`.

Capture `/tmp/qa038-version.json`.

Capture `/tmp/qa038-dependencies.json`.

Capture `/tmp/qa038-platform-migration.json`.

Capture `/tmp/qa038-tenant-inventory.json`.

Capture `/tmp/qa038-cross-tenant-code.txt`.

Capture `/tmp/qa038-inventory-summary.json`.

Capture `specs/038-jinja-surface-inventory-and-deletion-plan/jinja_inventory.json`.

Capture the focused backend test result.

Capture the focused frontend test result.

Capture the QA document validation result.

Capture the generated Spec Kit QA result.

Capture the generated Playwright result.

Capture `output/playwright/qa038_ui/qa038-react-ui2-smoke.png`.

Capture a platform browser screenshot.

Capture an Acme tenant browser screenshot.

Capture a mobile browser screenshot.

Capture reviewer notes in `pr_notes.md` or the pull request body.

## Security And Redaction Checks

Search the inventory JSON for `qa038-secret-value`.

Search the inventory JSON for `authorization header`.

Search the inventory JSON for `raw prompt`.

Search the inventory JSON for `raw completion`.

Search the inventory JSON for `memory content`.

Search the inventory JSON for `private message`.

Search the inventory JSON for `raw run`.

Search the inventory JSON for `raw tool payload`.

Search the inventory JSON for `/Users/`.

Search browser screenshots for obvious raw secrets.

Search browser screenshots for local absolute paths.

Confirm evidence references are identifiers, not payloads.

Confirm source paths are repo-relative.

Confirm schema tests reject unsafe values.

Stop review if an unsafe value appears.

Do not approve later deletion work until unsafe evidence is removed.

## Tenant Isolation Checks

Sign in as platform admin for the full inventory view.

Sign in as Acme tenant admin for tenant-safe inventory.

Confirm Acme tenant admin can view Acme scope.

Confirm Acme tenant admin cannot view Globex scope.

Confirm denied responses do not reveal Globex display data.

Confirm tenant-scoped inventory omits platform-only deletion groups.

Confirm tenant filtering is tested by backend integration tests.

Confirm Auth0-shaped principal behavior is tested by backend integration tests.

Record the tenant role used for each screenshot.

Record the tenant id used for each scoped URL.

## Troubleshooting

If the login page is missing, confirm `AUTH_MODE=local_principal` in `.env`.

If the API is unavailable, confirm the uvicorn command is still running.

If the worker exits, check its terminal output and restart it.

If the database migration fails, confirm PostgreSQL is running.

If tenant scope fails, reseed the Acme and Globex tenants.

If the inventory JSON is missing, regenerate it with the Python command from `qa038.md`.

If the inventory count changes, inspect recent source changes before approving the baseline.

If the React panel is missing, rebuild the frontend bundle.

If browser text overlaps, capture a screenshot and stop review.

If the redaction scan finds unsafe text, stop review.

If the cross-tenant request shows Globex data to Acme, stop review.

If focused tests pass but full validation fails, use the failing command output to identify the broader gate.

If Playwright times out, check `/tmp/qa038-api.log` and rebuild assets.

If screenshots show stale UI, clear the browser session and restart the API.

If the safe-to-delete count is not zero, stop review because Spec 038 should not approve deletion.

If reviewer signoff is missing, keep the spec in review.

If any command would touch a database other than `multi_agent_platform_qa038`, stop before running it.
