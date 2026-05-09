# QA062 User Guide: Spec 062 - Design Review Coordinator And Iteration Loop

## Detailed Overview

Spec 062 adds a coordinator for design review sessions.

A coordinator turns one design review session into review rounds.

Each round reviews one immutable design revision.

Each round launches one runtime workflow run.

The runtime workflow graph is acyclic.

If a revision needs another review, the coordinator launches another round.

The coordinator records which reviewers are assigned.

The coordinator records each safe reviewer verdict.

The coordinator evaluates quorum.

A four-of-five policy needs at least four approvals.

A three-of-four policy needs at least three approvals.

Both policies require zero blocking issues.

If quorum passes, the coordinator creates a development handoff.

If quorum does not pass but feedback is complete, the coordinator creates a new
revision.

If evidence is incomplete, blocked, or ambiguous, the coordinator pauses for
manual resolution.

Manual decisions can revise, approve by exception, retry, or cancel.

All records are local in QA.

No real provider call is required.

No raw prompt or completion is stored.

No real credential is needed.

## Who Should Use This Guide

Use this guide if you are manually reviewing QA062.

Use this guide if you need a plain-language explanation of the coordinator.

Use this guide if you are checking QA screenshots.

Use this guide if you are checking curl evidence.

Use this guide if you are checking tenant isolation.

Use this guide if you are checking manual-resolution behavior.

Use this guide if you are preparing for the Spec 063 Admin workspace.

Do not use this guide with production data.

Do not use this guide with real provider credentials.

Do not use this guide for live external calls.

## Manual QA Prerequisites

Work from the repository root.

Confirm Docker is running.

Confirm PostgreSQL can start through Docker Compose.

Confirm `uv` is available.

Confirm the QA environment file exists.

Confirm the validation manifest exists.

Confirm the seed script exists.

Confirm the verifier script exists.

Prepare the environment.

```bash
cp specs/062-design-review-coordinator-and-iteration-loop/.env.qa062 .env
uv sync
docker compose up -d postgres
```

Reset and migrate the QA database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa062 && createdb -U postgres multi_agent_platform_qa062'
uv run alembic upgrade head
```

Start the API.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker in another terminal.

```bash
uv run python -m multi_agent_platform.workers.main
```

Seed coordinator evidence.

```bash
uv run python scripts/qa/seed_design_review_coordinator_qa062.py
```

Expected result: seed output says `Seeded QA062 design review coordinator loop`.

Expected result: seed output prints a session id.

Expected result: seed output prints a round id.

## Step-by-Step Manual QA

Open local login.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/openapi.json
```

Choose `platform-admin`.

Expected result: the browser opens `/openapi.json`.

Expected result: the page includes `coordinator`.

Expected result: the page includes `launch-round`.

Expected result: the page includes `manual-decisions`.

Run the focused backend tests.

```bash
uv run pytest tests/unit/admin/design_review/test_design_review_coordinator.py tests/contract/test_design_review_coordinator_contracts.py tests/integration/api/test_admin_design_review_coordinator_api.py tests/integration/runtime/test_design_review_coordinator_runtime.py --no-cov
```

Expected result: all focused tests pass.

Run the verifier.

```bash
uv run python scripts/qa/verify_design_review_coordinator_qa062.py
```

Expected result: verifier output says `Verified QA062 design review coordinator loop`.

Run Playwright.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/062-design-review-coordinator-and-iteration-loop/validation.yml --start-processes
```

Expected result: screenshot exists under `output/playwright/qa062_ui`.

Run Spec Kit QA.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/scenario-enhancement-roadmap/062-design-review-coordinator-and-iteration-loop/validation.yml
```

Expected result: the command prints `Spec QA validation completed`.

Run curl regression.

```bash
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa062-after-spec
```

Expected result: no curl commands fail.

## Expected Results

A coordinator launch creates one round.

A coordinator launch creates one runtime workflow run.

The round references exactly one revision.

Launch replay returns the same round.

Approval quorum creates a handoff.

Revision-required quorum creates a next revision.

Blocking issues pause for manual resolution.

Manual revise creates a next revision.

Manual approve-exception creates a handoff only with accepted risk.

Manual retry allows another round.

Manual cancel marks the session cancelled.

Globex cannot operate on Acme sessions.

Evidence contains only safe summaries, ids, digests, and artifact references.

## Evidence To Capture

Capture the focused test result.

Capture the QA document validation result.

Capture the seed script output.

Capture the verifier output.

Capture the Playwright screenshot path.

Capture the Spec Kit QA result.

Capture the curl regression output directory.

Capture the curl section numbers for coordinator routes.

Use `/tmp/qa062-seed.txt` for seed evidence.

Use `/tmp/qa062-post-ui-evidence.txt` for verifier evidence.

Use `/tmp/qa062-ui-action-evidence.txt` for screenshot paths.

Use `.data/curl_test_runs/qa062-after-spec` for curl evidence.

## Security And Redaction Checks

Check that screenshots do not include `Authorization:`.

Check that evidence does not include provider API keys.

Check that evidence does not include raw prompts.

Check that evidence does not include raw completions.

Check that evidence does not include raw provider payloads.

Check that evidence does not include memory contents.

Check that evidence does not include private channel messages.

Check that evidence does not include raw external tool payloads.

Expected result: evidence is safe to share.

Expected result: no reviewer needs live provider credentials.

## Tenant Isolation Checks

Use Acme tenant id `11111111-1111-1111-1111-111111111111`.

Use Globex tenant id `22222222-2222-2222-2222-222222222222`.

Confirm Acme can create and launch coordinator sessions.

Confirm Globex receives denial for Acme coordinator state.

Confirm Globex does not see Acme sessions in its empty state.

Confirm platform-admin uses explicit tenant context.

Expected result: Acme and Globex evidence do not mix.

Expected result: cross-tenant denial does not reveal private details.

## Troubleshooting

If seeding fails, confirm API and database are running.

If verifier fails, inspect `.data/qa062-artifacts/evidence`.

If launch fails, confirm the workflow bundle was seeded.

If completion fails, inspect verdict payloads and quorum policy.

If manual decisions fail, confirm the session is in manual resolution.

If Playwright fails, confirm `/openapi.json` loads.

If curl fails, inspect `.data/curl_test_runs/qa062-after-spec`.

Expected result: troubleshooting stays local and deterministic.

Expected result: no troubleshooting path needs real credentials.
