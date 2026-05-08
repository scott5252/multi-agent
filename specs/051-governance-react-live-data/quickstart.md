# Quickstart: Governance React Live Data

## Goal

Validate that governance React routes show authorized live governance data, truthful empty states, and safe mutation/persistence evidence without deterministic QA031 production rows.

## Setup

1. Install dependencies:

   ```bash
   uv sync
   npm --prefix frontend/admin install
   ```

2. Prepare the QA database:

   ```bash
   cp specs/051-governance-react-live-data/.env.qa051 .env
   docker compose up -d postgres
   docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa051 && createdb -U postgres multi_agent_platform_qa051'
   uv run alembic upgrade head
   ```

3. Seed Acme and Globex local tenants, then create governance seed records through the documented QA setup flow or backend services. Seed data must include at least one safe prompt/profile record for the Playwright save action and must not be returned by production routes unless persisted.

## Manual Checks

1. Start the app:

   ```bash
   uv run uvicorn multi_agent_platform.api.main:app --reload
   ```

2. Open `/auth/local-login?redirect_to=/admin/app/governance` and choose `tenant-admin-acme`.
3. Verify empty-state panels in a fresh database.
4. Verify seeded provider, prompt, profile, routing, history, and provenance panels after QA seed data is created.
5. Run one safe prompt or profile save action and confirm the saved state remains after refresh.
6. Confirm no raw secrets, raw prompts, raw completions, provider authorization headers, private run payloads, stack traces, local filesystem paths, or unauthorized tenant labels are visible.

## Automated Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/051-governance-react-live-data
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/051-governance-react-live-data/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/051-governance-react-live-data/validation.yml --start-processes
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa051-after-spec
```

## Evidence To Record

- Empty-state API response from `/admin/app/governance/bootstrap.json`.
- Seeded live API response from `/admin/app/governance/bootstrap.json`.
- Prompt/profile save mutation response and post-refresh API or database evidence.
- Playwright screenshot under `output/playwright/qa051_ui/`.
- `multi-agent-curl-test` output directory `.data/curl_test_runs/qa051-after-spec`.

## Expected Result

Spec 051 is complete only when QA docs, backend quality gates, frontend checks, generated contracts, Playwright, post-UI persistence verification, scanner assertions, and curl validation all pass.
