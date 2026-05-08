# QA051 UI: Governance React Live Data

## Goal

Guide a reviewer through browser evidence for qa051.

The UI review confirms that the governance React workspace opens from local login, renders live prompt governance rows from the database, performs a safe prompt save action, and shows redaction-safe preview output.

The review also confirms that empty governance panels are honest when a scope has no records.

No screenshot should contain raw prompt text.

No screenshot should contain raw completion text.

No screenshot should contain a resolved credential value.

No screenshot should contain provider authorization headers.

No screenshot should contain private run payloads.

Expected: browser evidence matches the API evidence from `qa051.md`.

What is happening: the browser loads the FastAPI-served React bundle and calls governance JSON routes.

Why this matters: qa051 removes deterministic governance rows, so the browser must prove it can function from live backend state.

## How To Use This Guide

Run the setup commands from the repository root.

Use a browser pointed at `http://127.0.0.1:8000/auth/local-login`.

Keep API evidence beside UI evidence so reviewers can compare the same seeded prompt.

Save screenshots and notes under these names.

- `/tmp/qa051-ui-login.png`
- `/tmp/qa051-ui-governance-seeded.png`
- `/tmp/qa051-ui-prompt-save.png`
- `/tmp/qa051-ui-redaction-preview.png`
- `/tmp/qa051-ui-cross-tenant-empty.png`
- `/tmp/qa051-ui-post-api-notes.txt`

Expected: screenshot filenames and reviewer notes contain `qa051`.

Expected: screenshot contents show safe summaries only.

Expected: screenshots avoid raw prompt bodies, raw completions, credential values, external payloads, and local paths.

What is happening: the reviewer is collecting visual proof that the React panels reflect backend state.

Why this matters: a page that only loads is not enough for a live-data migration.

## Environment Setup

### 1. Copy the QA environment

```bash
test ! -f .env || cp .env .env.autopilot-backup
cp specs/051-governance-react-live-data/.env.qa051 .env
uv sync
```

Expected: `.env.qa051` is active and dependencies are available.

What is happening: the app is configured for local-principal qa051 review.

Why this matters: the browser must use the same database and auth mode as the API checks.

### 2. Prepare the QA database

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa051 && createdb -U postgres multi_agent_platform_qa051'
uv run alembic upgrade head
```

Expected: migrations complete without errors.

What is happening: governance routes will read from a clean durable database.

Why this matters: the empty state and seeded state are both meaningful.

### 3. Seed local tenants

```bash
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa051 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
```

Expected: Acme and Globex local tenants exist.

What is happening: tenant-shaped principals can be selected at login.

Why this matters: cross-tenant checks need deterministic tenant identities.

### 4. Seed the governance prompt

```bash
uv run python scripts/qa/seed_governance_qa051.py
```

Expected: output includes `Seeded QA051 governance prompt`.

What is happening: one prompt lineage, draft, revision, validation result, version, and tenant grant are written to the QA database.

Why this matters: the browser prompt row is real live data.

### 5. Build the React assets

```bash
npm run --prefix frontend/admin build
```

Expected: the build writes `src/multi_agent_platform/web_admin/static/react/manifest.json`.

What is happening: FastAPI serves the updated governance React bundle.

Why this matters: browser validation must not run stale assets.

### 6. Start the API

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: the app starts at `http://127.0.0.1:8000`.

What is happening: the browser and API evidence use the same app process.

Why this matters: browser state and API state must agree.

## Browser Walkthrough

### 1. Local login

Open this URL.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/governance
```

Select `platform-admin`.

Expected: the browser lands on `/admin/app/governance`.

Expected: the page heading is `Governance`.

What is happening: the local login route sets the platform admin session cookie.

Why this matters: platform admin can see the seeded prompt and run governance-safe actions.

Reviewer evidence: save `/tmp/qa051-ui-login.png`.

### 2. Review seeded governance state

Open this URL after login.

```text
http://127.0.0.1:8000/admin/app/governance
```

Expected: the page shows `QA051 Governance Prompt`.

Expected: provider and profile panels may be empty if no extra QA seed exists.

Expected: the empty provider or profile panel text says no authorized live records exist.

Expected: the page does not show fixed qa031 provider, prompt, profile, routing, policy, or provenance rows.

What is happening: React is rendering `/admin/app/governance/bootstrap.json`.

Why this matters: the page has to distinguish live seeded state from honest empty state.

Reviewer evidence: save `/tmp/qa051-ui-governance-seeded.png`.

### 3. Save prompt summary

Find the `QA051 Governance Prompt` card.

Select `Save summary`.

Expected: a prompt result section appears.

Expected: the result text includes `Prompt draft summary saved`.

Expected: the result references safe metadata and does not expose prompt body text.

What is happening: React posts to `/admin/app/governance/prompts/{prompt_lineage_id}/save`.

Why this matters: the UI action must write a durable prompt draft revision.

Reviewer evidence: save `/tmp/qa051-ui-prompt-save.png`.

### 4. Run a redaction preview

Select `Preview redaction check`.

Expected: the safe preview panel appears.

Expected: the panel includes `Protected prompt content is summarized.`

Expected: the panel does not reveal `Summarize governance evidence using redaction-safe metadata.`

What is happening: React posts to `/admin/app/governance/prompts/{prompt_lineage_id}/preview`.

Why this matters: prompt preview output must be summary-only.

Reviewer evidence: save `/tmp/qa051-ui-redaction-preview.png`.

### 5. Verify post-UI persistence

Run this command after the browser save action.

```bash
uv run python scripts/qa/verify_governance_qa051.py
```

Expected: output states that the prompt save was verified and the draft revision is at least 2.

What is happening: the database is queried after the browser interaction.

Why this matters: the success message cannot be only React component state.

Reviewer evidence: copy the output to `/tmp/qa051-ui-post-api-notes.txt`.

### 6. Cross-tenant empty check

Clear local login state or open the login page again.

Select `tenant-admin-globex`.

Open this URL.

```text
http://127.0.0.1:8000/admin/app/governance
```

Expected: Globex does not see `QA051 Governance Prompt`.

Expected: the page shows empty or unavailable governance states when no Globex records exist.

What is happening: the active principal changes from platform admin to a different tenant.

Why this matters: live governance data must not leak across tenants.

Reviewer evidence: save `/tmp/qa051-ui-cross-tenant-empty.png`.

## Required Automated Evidence

Run these commands after the browser walkthrough.

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
npm run --prefix frontend/admin typecheck
npm run --prefix frontend/admin test -- --run src/components/governance/GovernancePage.test.tsx src/components/governance/ProviderGovernancePanel.test.tsx src/components/governance/PromptGovernancePanel.test.tsx src/components/governance/ProfileGovernancePanel.test.tsx src/components/governance/RoutingPreviewPanel.test.tsx src/components/governance/ProvenancePanel.test.tsx
```

Expected: generated contracts, TypeScript, and focused governance component tests pass.

What is happening: the browser contract and component behavior are checked without manual clicking.

Why this matters: manual evidence should match automated component behavior.

Run the repository quality commands.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: repository quality gates pass.

What is happening: broader Python quality and coverage gates run after the UI behavior is validated.

Why this matters: qa051 changes backend services, schemas, routers, scripts, and React contracts.

Run the automated UI validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/051-governance-react-live-data/validation.yml --start-processes
```

Expected: Playwright captures `output/playwright/qa051_ui/qa051-live-data-ui-api-smoke.png`.

What is happening: Playwright repeats the login, prompt save, and redaction preview flow.

Why this matters: the required UI action is reproducible.

## UI Evidence Checklist

- Expected: login screenshot shows local principal choices only.
- Expected: governance screenshot shows `QA051 Governance Prompt`.
- Expected: prompt save screenshot shows a backend mutation result.
- Expected: redaction preview screenshot shows summarized prompt output.
- Expected: cross-tenant screenshot does not show Acme seeded prompt data.
- Expected: screenshots do not show qa031 fixed governance markers.
- Expected: screenshots do not show raw prompt or completion text.
- Expected: screenshots do not show credential values.
- Expected: screenshots do not show provider authorization headers.
- Expected: screenshot filenames include qa051.

What is happening: reviewer evidence is checked for both presence and absence.

Why this matters: live-data work can fail by leaking too much, not only by showing too little.

## Acceptance Notes Template

Use this template in `/tmp/qa051-ui-post-api-notes.txt`.

```text
qa051 browser login principal:
qa051 seeded prompt visible:
qa051 prompt save result:
qa051 redaction preview result:
qa051 post-UI database verification:
qa051 cross-tenant empty result:
qa051 screenshot directory:
qa051 reviewer redaction notes:
```

Expected: every line names concrete evidence from the browser or post-UI verification.

What is happening: manual review is converted into a concise acceptance record.

Why this matters: future reviewers can tell exactly what was checked.

## Troubleshooting

If the browser shows a generic unavailable state, confirm the API is running and `.env.qa051` was copied to `.env`.

If `QA051 Governance Prompt` is missing, rerun `uv run python scripts/qa/seed_governance_qa051.py`.

If `Save summary` is missing, check the prompt route with the platform admin header.

If the save action fails, inspect the API log for safe problem details and rerun the seed against a fresh database.

If the redaction preview exposes the seeded template sentence, stop and treat it as a security blocker.

If Globex sees the QA051 prompt, stop and treat it as a tenant isolation blocker.

If Playwright fails on a selector, compare the screenshot with the implemented button labels before changing the manifest.

If React assets look stale, rerun `npm run --prefix frontend/admin build`.

Expected: troubleshooting keeps the browser, API, and database in the same qa051 environment.

What is happening: reviewers narrow failures to environment, seed, route, or component behavior.

Why this matters: qa051 must not be marked complete from partial visual evidence.

## Related Files

- `specs/051-governance-react-live-data/qa051.md`
- `specs/051-governance-react-live-data/.env.qa051`
- `specs/_autopilot/remove-mock-data-roadmap/051-governance-react-live-data/validation.yml`
- `scripts/qa/seed_governance_qa051.py`
- `scripts/qa/verify_governance_qa051.py`
- `frontend/admin/src/components/governance/GovernancePage.tsx`
- `frontend/admin/src/components/governance/PromptGovernancePanel.tsx`
- `src/multi_agent_platform/admin/governance.py`
- `src/multi_agent_platform/api/routers/admin_react.py`

Expected: these files define the browser setup, seed, action, and verification path.

What is happening: the UI guide names the concrete files that support the walkthrough.

Why this matters: qa051 can be audited without relying on memory of the implementation.
