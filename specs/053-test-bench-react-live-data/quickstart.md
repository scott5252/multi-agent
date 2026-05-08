# Quickstart: Test Bench React Live Data

## Purpose

Validate that the React test bench workspace reads live repository-backed suites, cases, runs, artifacts, publish-gate evidence, and audit records, while rendering truthful empty states when no records exist.

## Local Setup

1. Install dependencies:

   ```bash
   uv sync
   npm install --prefix frontend/admin
   ```

2. Start PostgreSQL:

   ```bash
   docker compose up -d postgres
   ```

3. Prepare the QA053 database after implementation:

   ```bash
   cp specs/053-test-bench-react-live-data/.env.qa053 .env
   docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa053 && createdb -U postgres multi_agent_platform_qa053'
   uv run alembic upgrade head
   uv run python scripts/qa/seed_test_bench_qa053.py
   ```

## Expected Empty-State Check

Before seeding test bench rows, the browser and JSON routes should show empty or unavailable state instead of fixed QA033/QA043 data.

```bash
curl --fail --silent \
  -H 'X-Local-Principal: tenant-admin-globex' \
  'http://127.0.0.1:8000/admin/app/test-bench/bootstrap.json?tenant_id=22222222-2222-2222-2222-222222222222'
```

Expected result:

- no QA053 seeded Acme suite names
- no QA033 or QA043 deterministic suite, run, artifact, gate, or audit markers
- empty-state metadata explains that no live test bench records exist for the scope

## Expected Seeded Check

After seeding QA053 records, the Acme test bench route should show only persisted QA053 suite/run evidence:

```bash
curl --fail --silent \
  -H 'X-Local-Principal: tenant-admin-acme' \
  'http://127.0.0.1:8000/admin/app/test-bench/bootstrap.json?tenant_id=11111111-1111-1111-1111-111111111111'
```

Expected result:

- seeded QA053 suite and case names are visible
- run launcher safe mode is local-safe or mocked-safe
- recent run and publish-gate evidence come from persisted run and publication requirement records
- raw transcripts, prompts, completions, local paths, and stack traces are absent

## Browser Validation

Run the required Playwright validation after implementation:

```bash
uv run python scripts/qa/run_playwright_ui.py \
  specs/_autopilot/remove-mock-data-roadmap/053-test-bench-react-live-data/validation.yml \
  --start-processes
```

The flow must log in with a local principal, open `/admin/app/test-bench`, perform a safe visible test bench action such as launching a seeded suite, verify the mutation result in the UI, and capture a screenshot under `output/playwright/qa053_ui/`.

## Post-UI Persistence Verification

Run the post-UI verifier before resetting the QA053 database:

```bash
uv run python scripts/qa/verify_test_bench_qa053.py
```

The verifier should prove that the Playwright action persisted a run, suite/case revision, or publish-gate evidence through backend state.

## Required Final Gates

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/053-test-bench-react-live-data
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/053-test-bench-react-live-data/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/053-test-bench-react-live-data/validation.yml --start-processes
uv run python scripts/qa/verify_test_bench_qa053.py
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa053-after-spec
```

Do not advance the autopilot queue until every command passes and status history includes implement, validation, and spec completion entries.
