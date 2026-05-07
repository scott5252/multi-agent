# QA047 User Guide: Spec 047 - Jinja Infrastructure Decommission

## Detailed Overview

This guide is for reviewers validating the final React UI2 roadmap step.
Spec 047 removes the runtime Jinja browser infrastructure after Specs 038
through 046 proved parity, redirects, route compatibility, and browser-first
React coverage for the formerly server-rendered admin and user surfaces.

The expected product state is React-only browser UI. FastAPI still owns JSON
contracts, authentication, authorization, redirects, health checks, and safe
HTML host responses for the React app, but it no longer renders admin pages
from Jinja templates.

The decommission has five reviewer themes:

1. No runtime Jinja infrastructure remains.
2. React static assets still serve correctly.
3. Old browser links resolve through non-Jinja redirects or compatibility
   responses.
4. Local-principal QA covers platform and tenant admin access.
5. Evidence stays redaction-safe and never exposes raw secrets or private data.

The primary evidence page is `/admin/app/migration`. It should show
`React-only browser UI`, `React-only readiness`, and final decommission
evidence such as `runtime-import-scan-qa047`.

The primary user-run compatibility path is `/runs`. It should route users into
the React run workspace rather than a server template.

Rollback is operational. There is no in-process feature flag that turns Jinja
rendering back on. If a rollback is needed, deploy the previous reviewed
release and verify the release artifact that contained the older browser stack.

Spec 047 intentionally keeps the Vite-built files under
`src/multi_agent_platform/web_admin/static/react`. Those files are not legacy
Jinja assets; they are the production React bundle and manifest.

The removed legacy static assets include files such as `prompt_runtime.js`,
`workflow_studio.css`, `admin_shell.js`, and the old one-off page scripts
outside `static/react`.

The removed template directory is
`src/multi_agent_platform/web_admin/templates`. A passing review should not
find runtime template files under that path.

The direct `jinja2` project dependency should be absent from `pyproject.toml`
and `uv.lock`.

Schema names may still contain historical terms where they are API contract
types used by the React migration dashboard. The runtime requirement is about
Jinja rendering infrastructure and server template assets, not old type names.

Use the automated commands in `qa047.md` for command-level evidence. Use this
guide for a human review pass over behavior, screenshots, and release notes.

The guide assumes `AUTH_MODE=local_principal` and the QA environment from
`specs/047-jinja-infrastructure-decommission/.env.qa047`.

The QA database name is `multi_agent_platform_qa047`.

The expected tenant is Acme.

The expected platform principal is `platform-admin`.

The expected tenant admin principal is `tenant-admin-acme`.

The expected tenant user principal is `tenant-user-acme`.

The expected artifact directory is `.data/qa047-artifacts`.

The expected screenshot directory is `output/playwright/qa047_ui`.

The browser screenshot produced by the Playwright manifest is
`qa047-react-ui2-smoke.png`.

Do not use real provider credentials, real Telegram tokens, real Auth0
tenants, or external connector calls for this review.

Do not paste raw prompts, raw completions, private channel messages, provider
authorization headers, credential values, or unauthorized run payloads into
review notes.

## Step-by-Step Manual QA

1. Confirm the active feature directory exists:

```bash
test -d specs/047-jinja-infrastructure-decommission
```

2. Confirm the QA environment file exists:

```bash
test -s specs/047-jinja-infrastructure-decommission/.env.qa047
```

3. Confirm the required QA guide exists:

```bash
test -s specs/047-jinja-infrastructure-decommission/qa047.md
```

4. Confirm the required UI walkthrough exists:

```bash
test -s specs/047-jinja-infrastructure-decommission/qa047_ui.md
```

5. Confirm this user guide exists:

```bash
test -s specs/047-jinja-infrastructure-decommission/qa047_user_guide.md
```

6. Confirm the PR notes exist:

```bash
test -s specs/047-jinja-infrastructure-decommission/pr_notes.md
```

7. Confirm runtime Jinja import markers are absent:

```bash
rg "Jinja2Templates|TemplateResponse|workflow_ui_templates|import jinja2|from jinja2" src/multi_agent_platform
```

8. The previous command should return no runtime matches.

9. Confirm the template tree is gone:

```bash
test ! -e src/multi_agent_platform/web_admin/templates
```

10. Confirm the legacy prompt-runtime script is gone:

```bash
test ! -e src/multi_agent_platform/web_admin/static/prompt_runtime.js
```

11. Confirm the legacy workflow stylesheet is gone:

```bash
test ! -e src/multi_agent_platform/web_admin/static/workflow_studio.css
```

12. Confirm the React manifest remains:

```bash
test -s src/multi_agent_platform/web_admin/static/react/manifest.json
```

13. Confirm `jinja2` is not a direct dependency:

```bash
rg '"jinja2|name = "jinja2"|jinja2' pyproject.toml uv.lock
```

14. The previous command should return no matches.

15. Copy the QA env into place if you are running manually:

```bash
test ! -f .env || cp .env .env.qa047-review-backup
cp specs/047-jinja-infrastructure-decommission/.env.qa047 .env
```

16. Start dependencies:

```bash
docker compose up -d postgres
```

17. Reset only the QA047 database:

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa047 && createdb -U postgres multi_agent_platform_qa047'
```

18. Apply migrations:

```bash
uv run alembic upgrade head
```

19. Seed the local tenants:

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa047 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

20. Run the focused decommission scanner tests:

```bash
uv run pytest --no-cov tests/unit/admin/test_jinja_infrastructure_decommission.py -q
```

21. Run the focused container and settings tests:

```bash
uv run pytest --no-cov tests/unit/bootstrap/test_container.py tests/unit/config/test_settings.py tests/unit/api/test_dependency_helpers.py -q
```

22. Run the focused migration service and route tests:

```bash
uv run pytest --no-cov tests/unit/admin/test_migration_hardening_service.py tests/integration/api/test_admin_react_migration_inventory_routes.py tests/integration/test_admin_react_routes.py -q
```

23. Run the auth and compatibility tests:

```bash
uv run pytest --no-cov tests/integration/api/test_auth_routes.py tests/integration/api/test_local_browser_login.py tests/integration/api/test_web_run_ui.py -q
```

24. Run the frontend migration tests:

```bash
cd frontend/admin && npm test -- --run src/components/migrationHardening src/App.test.tsx
```

25. Return to the repository root after frontend tests:

```bash
cd ../..
```

26. Run the frontend typecheck:

```bash
cd frontend/admin && npm run typecheck
```

27. Build the frontend:

```bash
cd frontend/admin && npm run build
```

28. Return to the repository root again:

```bash
cd ../..
```

29. Run generated contract verification:

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```

30. Run lint:

```bash
uv run ruff check .
```

31. Run format check:

```bash
uv run ruff format --check .
```

32. Run mypy:

```bash
uv run mypy src
```

33. Run the full coverage gate:

```bash
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

34. Run the Spec QA manifest:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/047-jinja-infrastructure-decommission/validation.yml
```

35. Run the Playwright UI manifest:

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/047-jinja-infrastructure-decommission/validation.yml --start-processes
```

36. Open the Playwright screenshot:

```bash
test -s output/playwright/qa047_ui/qa047-react-ui2-smoke.png
```

37. Verify the migration page screenshot shows `React-only browser UI`.

38. Verify the migration page screenshot shows `React-only readiness`.

39. Verify the screenshot does not show a raw secret value.

40. Verify the screenshot does not show a provider authorization header.

41. Verify the screenshot does not show a private channel message.

42. Verify the screenshot does not show a raw prompt or completion.

43. Visit local login manually if needed:

```text
/auth/local-login?redirect_to=/admin/app/migration
```

44. Sign in as `platform-admin`.

45. Confirm the page lands on `/admin/app/migration`.

46. Confirm the header identifies the React migration workspace.

47. Confirm the decommission inventory shows zero retained server-rendered
rows.

48. Confirm the evidence list contains `runtime-import-scan-qa047`.

49. Confirm rollback text says release rollback or redeploy previous release.

50. Visit local login for a tenant user run flow:

```text
/auth/local-login?redirect_to=/runs
```

51. Sign in as `tenant-admin-acme`.

52. Confirm the run workspace opens in React.

53. Start a deterministic run if the QA environment is active.

54. Confirm the accepted-run status message appears.

55. Confirm old direct links do not render a Jinja template.

56. Confirm old direct links do not reveal cross-tenant existence.

57. Confirm every failure state is a safe problem detail or React-safe
message.

58. Preserve evidence files under `/tmp/qa047-*` when reviewing manually.

59. Restore a previous `.env` if you backed one up:

```bash
test ! -f .env.qa047-review-backup || mv .env.qa047-review-backup .env
```

## Expected Results

The runtime import scanner reports no `Jinja2Templates` usage.

The runtime import scanner reports no `TemplateResponse` usage.

The runtime import scanner reports no `workflow_ui_templates` usage.

The runtime import scanner reports no direct `jinja2` imports.

The template directory is absent.

Legacy static files outside `static/react` are absent.

The React static manifest is present.

The React build emits a current JavaScript bundle and stylesheet.

`pyproject.toml` does not list `jinja2`.

`uv.lock` does not contain the `jinja2` package.

The container has no template renderer field.

Settings have no `web_admin_templates_dir`.

Local login is rendered without a deleted stylesheet dependency.

The local login page includes safe inline styling only.

`/admin/app` returns a non-Jinja React host.

The React host response includes `X-React-Admin-Host: non-jinja`.

The React host fallback contains `Skip to content`.

The React host fallback contains `id="admin-main-content"`.

The React host fallback contains `aria-label="Admin"`.

`/admin` redirects to `/admin/app` while preserving safe tenant query data.

`/admin/app/migration` shows `React-only browser UI`.

`/admin/app/migration/decommission-inventory.json` returns zero inventory rows.

The legacy inventory alias remains available but is hidden from the OpenAPI
contract.

Old prompt runtime browser links redirect to React governance routes.

Old operations links redirect to React operations routes.

Old workflow links redirect to React workflow routes.

Old user run links redirect or alias into the React run workspace.

No route returns a server-rendered Jinja page.

No route exposes whether an unauthorized tenant resource exists.

The frontend migration tests pass.

The frontend typecheck passes.

The frontend build passes.

The generated contract check passes.

Ruff passes.

Ruff format check passes.

Mypy passes.

The full coverage gate passes at or above 90 percent.

The Spec QA manifest passes.

The Playwright UI manifest passes.

The Playwright screenshot is present under `output/playwright/qa047_ui`.

The screenshot shows React-only migration evidence.

The screenshot shows the React run workspace after the legacy run route.

The screenshot and terminal output contain no raw secrets.

The screenshot and terminal output contain no raw prompts.

The screenshot and terminal output contain no provider authorization headers.

The screenshot and terminal output contain no private channel messages.

The PR notes include a decommission summary and validation list.

The queue state marks Spec 047 complete only after all validation passes.

The queue state sets `next_spec` to null when Spec 047 completes.

## Troubleshooting

If the QA document validator fails, check this file first. It must retain the
exact top-level title and the `Detailed Overview`, `Step-by-Step Manual QA`,
`Expected Results`, and `Troubleshooting` headings.

If the document validator reports line count, keep this guide expanded enough
for a reviewer to run the full manual path without relying on memory.

If the Spec QA runner cannot connect to PostgreSQL, confirm Docker is running
and that the compose service name is `postgres`.

If the database reset fails, stop immediately unless the database name is
`multi_agent_platform_qa047`.

If migrations fail, capture the migration error under `/tmp/qa047-db.txt` and
do not continue to browser validation.

If the runtime scanner finds `TemplateResponse`, inspect whether the match is
runtime code under `src/multi_agent_platform` or historical docs/tests.

If the runtime scanner finds `Jinja2Templates`, treat it as a blocker unless it
is in archived documentation outside runtime code.

If the dependency scanner finds `jinja2`, confirm `uv lock` was run after
removing the direct dependency.

If React assets are missing, rerun `cd frontend/admin && npm run build`.

If the generated contract check fails after backend schema edits, regenerate
contracts once and review the diff before continuing.

If frontend tests fail because migration evidence text changed, align the
component copy and tests with the final React-only language.

If Playwright cannot reach the app, rerun with `--start-processes` and inspect
the process logs in the QA output.

If local login redirects to an unexpected path, check `redirect_to` sanitation
and safe redirect handling.

If `/admin` does not redirect to `/admin/app`, inspect the non-Jinja
compatibility route for safe tenant query preservation.

If `/runs` does not reach the React run workspace, inspect the user-run facade
routes and the local-principal catalog.

If a page shows a missing asset warning, inspect
`src/multi_agent_platform/web_admin/static/react/manifest.json`.

If the screenshot is blank, rerun the React build and Playwright manifest.

If the screenshot is visually cropped, review responsive CSS in the React
admin shell and rerun Playwright.

If a route returns raw stack traces, stop and fix safe problem handling before
marking validation complete.

If evidence contains raw credential values, stop and fix redaction before
marking validation complete.

If a reviewer asks how to roll back, point to the release rollback plan:
redeploy the previous reviewed release and verify its release artifact.

If a reviewer asks why no Jinja feature flag remains, explain that Spec 047 is
the final infrastructure decommission and rollback is release-based.

If a reviewer asks why historical schema names remain, explain that runtime
rendering infrastructure is removed while existing React contract type names
can remain for compatibility.

If queue.json and status.json disagree, trust successful command evidence,
update both files consistently, and validate both with `jq`.

If any stop condition touches tenant isolation, secrets, external calls, or
destructive data outside the QA047 database, stop the run and ask for review.
