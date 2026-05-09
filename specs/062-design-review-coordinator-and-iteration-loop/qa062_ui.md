# QA062 UI Walkthrough: Spec 062 - Design Review Coordinator And Iteration Loop

## Goal

This walkthrough verifies browser-visible evidence for coordinator APIs.

Spec 062 is backend-first.

The dedicated React design review workspace is planned for Spec 063.

Browser evidence therefore focuses on local login, OpenAPI visibility, and safe
JSON route discovery.

The walkthrough confirms coordinator route contracts are discoverable.

The walkthrough confirms local-principal authentication works.

The walkthrough confirms screenshots do not expose raw prompts, completions,
provider payloads, credentials, private messages, memory contents, or raw tool
payloads.

Expected: `http://127.0.0.1:8000/auth/local-login` is available.

Expected: `/openapi.json` contains `coordinator`.

Expected: `/openapi.json` contains `launch-round`.

Expected: `/openapi.json` contains `manual-decisions`.

Expected: Playwright writes a screenshot under `output/playwright/qa062_ui`.

Expected: screenshots are safe to attach.

Expected: no real provider credential is needed.

Expected: no live external call is made.

## How To Use This Guide

Run environment setup first.

Use `qa062` as the evidence id.

Use `.env.qa062` for local QA.

Use `/tmp/qa062-ui-notes.md` for reviewer notes.

Use `/tmp/qa062-ui-action-evidence.txt` for screenshot paths.

Keep screenshots focused on OpenAPI, health, and safe JSON output.

Do not attach raw prompts or completions.

Do not use real credentials.

What is happening: the browser is validating the visible route surface for a
backend coordinator feature.

Why this matters: Spec 063 will build UI on these live-data APIs, so route
contracts must be visible and safe before the workspace is added.

Expected: reviewer notes mention backend-first scope.

Expected: reviewer notes mention no dedicated React workspace in Spec 062.

Expected: reviewer notes include screenshot evidence.

Expected: reviewer notes include no raw protected content.

## Environment Setup

Use `specs/062-design-review-coordinator-and-iteration-loop/.env.qa062`.

Start from the repository root.

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

Start the API if reviewing manually.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker in another terminal if needed.

```bash
uv run python -m multi_agent_platform.workers.main
```

Seed coordinator evidence.

```bash
uv run python scripts/qa/seed_design_review_coordinator_qa062.py | tee /tmp/qa062-seed.txt
```

Expected: seed output says `Seeded QA062 design review coordinator loop`.

Expected: `http://127.0.0.1:8000/health/live` returns success.

Expected: `http://127.0.0.1:8000/health/ready` returns success.

## Browser Walkthrough

Open local login.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/openapi.json
```

What is happening: local-principal login sets a deterministic reviewer identity.

Why this matters: QA062 must not depend on Auth0.

Expected: the login form is available.

Expected: the form includes local principals.

Choose `platform-admin`.

Expected: the browser redirects to `/openapi.json`.

Expected: the page contains `design-reviews`.

Expected: the page contains `coordinator`.

Expected: the page contains `launch-round`.

Expected: the page contains `manual-decisions`.

Open coordinator state after seeding.

```text
http://127.0.0.1:8000/admin/design-reviews/sessions
```

What is happening: seeded API state can be inspected through safe JSON routes.

Why this matters: later UI must render live persisted sessions rather than mock
rows.

Expected: Acme session JSON contains safe summaries and ids.

Expected: no provider credential is visible.

Run automated Playwright.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/062-design-review-coordinator-and-iteration-loop/validation.yml --start-processes
```

Expected: the command prints a screenshot path.

Expected: `output/playwright/qa062_ui/qa062-scenario-enhancement-smoke.png`
exists.

Record the screenshot path.

```bash
printf 'qa062 screenshot: output/playwright/qa062_ui/qa062-scenario-enhancement-smoke.png\n' > /tmp/qa062-ui-action-evidence.txt
```

Expected: `/tmp/qa062-ui-action-evidence.txt` contains the screenshot path.

## Required Automated Evidence

Run Playwright validation.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/062-design-review-coordinator-and-iteration-loop/validation.yml --start-processes
```

Expected: the command exits with status zero.

Expected: screenshot evidence is under `output/playwright/qa062_ui`.

Run the post-UI verifier.

```bash
uv run python scripts/qa/verify_design_review_coordinator_qa062.py | tee /tmp/qa062-post-ui-evidence.txt
```

Expected: verifier output includes `Verified QA062 design review coordinator loop`.

Run document and quality gates.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/062-design-review-coordinator-and-iteration-loop
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Expected: QA document validation passes.

Expected: Ruff passes.

Expected: format checking passes.

Expected: mypy passes.

Expected: coverage remains at or above 90 percent.

## UI Evidence Checklist

Record the local login URL.

Record the selected principal.

Record the OpenAPI URL.

Record whether `coordinator` appears.

Record whether `launch-round` appears.

Record whether `manual-decisions` appears.

Record the Playwright screenshot path.

Record the verifier output path.

Record whether screenshots contain only safe metadata.

Expected: evidence references `qa062`.

Expected: evidence references `.env.qa062`.

Expected: evidence includes screenshot language.

Expected: evidence includes no raw secret material.

## Acceptance Notes Template

QA id: qa062.

Environment file: `specs/062-design-review-coordinator-and-iteration-loop/.env.qa062`.

Login URL: `http://127.0.0.1:8000/auth/local-login?redirect_to=/openapi.json`.

OpenAPI URL: `http://127.0.0.1:8000/openapi.json`.

Screenshot path: `output/playwright/qa062_ui/qa062-scenario-enhancement-smoke.png`.

What is happening: the browser checks route visibility for backend coordinator
APIs.

Why this matters: Spec 063 depends on these live-data contracts.

Expected: notes say the UI workspace is deferred.

Expected: notes say coordinator routes are live-data backed.

Expected: notes say screenshots are redaction-safe.

## Troubleshooting

If local login does not load, confirm the API is running.

If `/openapi.json` is unavailable, confirm migrations completed.

If coordinator routes are missing, inspect `admin_design_review.py`.

If seed fails, confirm the API can reach the QA database.

If Playwright fails, inspect `/tmp/qa062-api.log`.

If the screenshot is missing, rerun the Playwright command.

If unsafe text appears, stop and inspect the route response before attaching
evidence.

Expected: troubleshooting does not require real credentials.

Expected: troubleshooting does not require live provider calls.

## Related Files

- `specs/062-design-review-coordinator-and-iteration-loop/qa062.md`
- `specs/062-design-review-coordinator-and-iteration-loop/.env.qa062`
- `specs/062-design-review-coordinator-and-iteration-loop/qa062_user_guide.md`
- `specs/_autopilot/scenario-enhancement-roadmap/062-design-review-coordinator-and-iteration-loop/validation.yml`
- `scripts/qa/seed_design_review_coordinator_qa062.py`
- `scripts/qa/verify_design_review_coordinator_qa062.py`
- `src/multi_agent_platform/api/routers/admin_design_review.py`
- `src/multi_agent_platform/admin/design_review/coordinator.py`
