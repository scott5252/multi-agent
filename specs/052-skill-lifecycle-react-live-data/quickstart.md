# Quickstart: Skill Lifecycle React Live Data

## Goal

Validate that skill lifecycle React routes show authorized live skill package, version, grant, installation, credential readiness, smoke-test, diagnostic, eligibility, quarantine, withdrawal, and audit data, plus truthful empty states, without deterministic QA032 production rows.

## Setup

1. Install dependencies:

   ```bash
   uv sync
   npm --prefix frontend/admin install
   ```

2. Prepare the QA database:

   ```bash
   cp specs/052-skill-lifecycle-react-live-data/.env.qa052 .env
   docker compose up -d postgres
   docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa052 && createdb -U postgres multi_agent_platform_qa052'
   uv run alembic upgrade head
   ```

3. Seed Acme and Globex local tenants, then create skill lifecycle seed records through the documented QA setup flow, services, repositories, or safe seed scripts. Seed data must include at least one safe lifecycle record for the Playwright action and must not be returned by production routes unless persisted.

## Manual Checks

1. Start the app:

   ```bash
   uv run uvicorn multi_agent_platform.api.main:app --reload
   ```

2. Open `/auth/local-login?redirect_to=/admin/app/skills` and choose the principal required by the QA action.
3. Verify empty-state panels in a fresh database.
4. Verify seeded package, candidate, grant, discovery, installation, credential readiness, smoke-test, diagnostic, eligibility, quarantine, withdrawal, and audit panels after QA seed data is created.
5. Run one safe lifecycle action and confirm the saved state remains after refresh or is proven through backend evidence.
6. Confirm no raw manifests, credential values, connector payloads, raw tool output, raw test transcripts, stack traces, local filesystem paths, or unauthorized tenant labels are visible.

## Automated Validation

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/052-skill-lifecycle-react-live-data
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/052-skill-lifecycle-react-live-data/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/052-skill-lifecycle-react-live-data/validation.yml --start-processes
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa052-after-spec
```

## Evidence To Record

- Empty-state API response from `/admin/app/skills/bootstrap.json`.
- Seeded live API response from `/admin/app/skills/bootstrap.json`.
- Lifecycle mutation response and post-refresh API or database evidence.
- Playwright screenshot under `output/playwright/qa052_ui/`.
- `multi-agent-curl-test` output directory `.data/curl_test_runs/qa052-after-spec`.

## Expected Result

Spec 052 is complete only when QA docs, backend quality gates, frontend checks, generated contracts, Playwright, post-UI persistence verification, scanner assertions, and curl validation all pass.
