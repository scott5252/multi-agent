# QA059 UI Walkthrough: Spec 059 - Admin UI Transitional React Label Removal

## Goal

This walkthrough verifies the browser-facing Admin terminology cleanup.

The reviewer should see Admin product wording on the entry shell.

The reviewer should see domain-specific wording on representative pages.

The reviewer should see developer-only migration evidence clearly separated in
the migration hardening workspace.

The reviewer should not see blocked product labels such as `React Admin` in
ordinary navigation, breadcrumbs, headings, document titles, error states, or
fallback copy.

Expected: the first visible product signal is Admin.

Expected: migration evidence shows `Transitional label gate`.

Expected: screenshots are safe to attach to QA evidence.

## How To Use This Guide

Run this walkthrough after the QA059 database is migrated and seeded.

Use local-principal login.

Capture screenshots only after the page has settled.

Use reviewer notes to record what is visible.

Keep notes under `/tmp/qa059-ui-notes.md` if manual review is needed.

What is happening: the UI reads backend-owned shell, domain, and migration
contracts.

Why this matters: a static frontend string swap is not enough; route responses
and browser rendering must agree.

Expected: UI evidence matches the API scanner report.

## Environment Setup

Use `specs/059-admin-ui-transitional-react-label-removal/.env.qa059`.

Start from the repository root.

```bash
cp specs/059-admin-ui-transitional-react-label-removal/.env.qa059 .env
uv sync
docker compose up -d postgres
```

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa059 && createdb -U postgres multi_agent_platform_qa059'
uv run alembic upgrade head
uv run python scripts/qa/seed_transitional_labels_qa059.py
```

Expected: seed output says `Seeded QA059 transitional label records`.

Start the API and worker if reviewing manually.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: `/health/live` returns success.

Expected: `/health/ready` returns success.

## Browser Walkthrough

Open the local login route.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app
```

What is happening: local-principal login sets the reviewer identity without
using Auth0.

Why this matters: QA remains deterministic and does not call external auth.

Expected: the login form lists platform and tenant principals.

Select `platform-admin`.

Expected: the browser opens `/admin/app`.

Expected: the top heading says `Admin`.

Expected: the sidebar brand says `Multi-Agent Admin` and `Admin workspace`.

Expected: breadcrumb text says `Admin`.

Expected: navigation entries do not append implementation labels.

Capture the entry screenshot.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/validation.yml --start-processes
```

Expected: `output/playwright/qa059_ui/qa059-admin-entry.png` exists.

Open the skill lifecycle page.

```text
http://127.0.0.1:8000/admin/app/skills
```

What is happening: a representative domain page renders live seeded data and
shared shell chrome.

Why this matters: the cleanup must cover domain pages, not only the root shell.

Expected: the page heading includes `Skill lifecycle`.

Expected: status, readiness, diagnostics, and audit sections use domain terms.

Expected: visible copy does not say `React Admin`.

Expected: visible copy does not say `React-only`.

Open migration hardening.

```text
http://127.0.0.1:8000/admin/app/migration
```

What is happening: the reviewer opens the developer-only evidence workspace.

Why this matters: this is where allowed implementation references are explained.

Expected: the page title says `Admin browser UI`.

Expected: the parity matrix says `Admin and legacy destinations`.

Expected: the Jinja inventory panel says `Browser UI readiness`.

Expected: the live-data panel says `Live-data guardrails`.

Expected: the new panel says `Transitional label gate`.

Expected: the new panel says `Admin terminology gate passed`.

Capture the domain and migration screenshot.

Expected: `output/playwright/qa059_ui/qa059-domain-pages.png` exists.

Open the gate route directly.

```bash
curl --fail --silent -H 'X-Local-Principal: platform-admin' 'http://127.0.0.1:8000/admin/app/migration/transitional-labels.json?ci_mode=true' > /tmp/qa059-transitional-labels.json
```

Expected: `/tmp/qa059-transitional-labels.json` contains `"blocked_count":0`.

Expected: `/tmp/qa059-transitional-labels.json` contains `"ci_status":"pass"`.

Expected: `/tmp/qa059-transitional-labels.json` does not contain `React Admin`.

Expected: `/tmp/qa059-transitional-labels.json` does not contain absolute home-directory paths.

## Required Automated Evidence

Run the UI flow through the validation manifest.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/validation.yml --start-processes
```

Expected: the command prints both screenshot paths.

Run the post-UI verifier.

```bash
uv run python scripts/qa/verify_transitional_labels_qa059.py
```

Expected: the verifier prints `Verified QA059 transitional label gate`.

Expected: the verifier prints `blocked_count=0`.

Run the document and quality gates.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/059-admin-ui-transitional-react-label-removal
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: the QA document validator passes.

Expected: Ruff, format, mypy, and coverage pass.

Run frontend checks.

```bash
npm run --prefix frontend/admin test -- --run migrationHardening
npm run --prefix frontend/admin test -- --run App bootstrapContract shell
npm run --prefix frontend/admin typecheck
npm run --prefix frontend/admin build
```

Expected: frontend checks pass.

## UI Evidence Checklist

Record the browser URL for each screenshot.

Record the signed-in principal.

Record the active scope label.

Record the Admin shell heading.

Record the skill lifecycle heading.

Record the migration hardening heading.

Record the transitional label gate status.

Record any allowed implementation references that remain visible in the gate.

Record that ordinary navigation does not expose blocked labels.

Record that fallback copy uses Admin terminology.

Record that no Globex data appears while using Acme scope.

Expected: all notes are safe to share with reviewers.

## Acceptance Notes Template

Reviewer:

Date:

Principal: platform-admin

Scope: Platform

Entry screenshot: output/playwright/qa059_ui/qa059-admin-entry.png

Domain screenshot: output/playwright/qa059_ui/qa059-domain-pages.png

Gate report: .data/qa059-artifacts/transitional-label-gate-report.json

What is happening: the browser renders backend-owned Admin terminology.

Why this matters: the final migration cleanup is visible in the same UI that
reviewers use.

Expected: no blocked transitional labels were observed.

Expected: route scanner and browser screenshots agree.

## Troubleshooting

If login does not open, confirm the API is running.

If login redirects to an error, confirm `.env.qa059` is copied to `.env`.

If the skill page is empty, rerun the QA seed script.

If migration evidence is unavailable, check `/tmp/qa059-api.log`.

If screenshots are missing, check `output/playwright/qa059_ui`.

If a blocked label appears, capture the URL and stop validation.

If the gate route contains local paths, stop validation.

If Globex appears in an Acme scoped page, treat it as tenant isolation blocker.

If generated types are stale, run the generator and rerun frontend checks.

Expected: troubleshooting does not require a Git commit.

## Related Files

`specs/059-admin-ui-transitional-react-label-removal/qa059.md`

`specs/059-admin-ui-transitional-react-label-removal/qa059_user_guide.md`

`specs/059-admin-ui-transitional-react-label-removal/.env.qa059`

`frontend/admin/src/components/migrationHardening/TransitionalLabelGatePanel.tsx`

`frontend/admin/src/components/migrationHardening/MigrationHardeningPage.tsx`

`src/multi_agent_platform/api/routers/admin_react.py`

`src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`

`scripts/qa/verify_transitional_labels_qa059.py`
