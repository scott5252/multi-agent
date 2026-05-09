# QA061 UI Walkthrough: Spec 061 - Model-Backed Graph Role Executor

## Goal

This walkthrough verifies browser-visible evidence for the model-backed graph
role executor.

Spec 061 is mostly runtime and worker infrastructure.

There is no dedicated React workspace for model-backed role execution yet.

The browser evidence therefore focuses on local login, health readiness,
OpenAPI visibility, and screenshot-safe runtime metadata.

The walkthrough confirms the app starts with the QA061 environment.

The walkthrough confirms local-principal authentication remains usable.

The walkthrough confirms health and dependency screens do not expose raw model
content, credentials, provider headers, prompts, completions, memory contents,
or tool payloads.

Expected: the API serves `http://127.0.0.1:8000/health/ready`.

Expected: the API serves `http://127.0.0.1:8000/openapi.json`.

Expected: local login is available at `http://127.0.0.1:8000/auth/local-login`.

Expected: automated Playwright evidence is written under `output/playwright/qa061_ui`.

Expected: screenshots are safe to attach to QA evidence.

Expected: no browser page requires a live provider credential.

Expected: no browser page performs a real model provider call.

Expected: no browser page displays unsafe model output.

## How To Use This Guide

Run the environment setup before opening the browser.

Use the QA environment file for this spec.

Use `qa061` as the evidence id in notes and screenshots.

Record reviewer notes in `/tmp/qa061-ui-notes.md`.

Record screenshot paths in `/tmp/qa061-ui-action-evidence.txt`.

Keep browser screenshots focused on health, OpenAPI, local login, and safe JSON
responses.

Do not paste raw prompts or completions into reviewer notes.

Do not replace fake secret references with real credentials.

What is happening: the browser is checking the visible platform shell around a
runtime feature that is validated primarily through backend tests.

Why this matters: browser QA proves the feature can run inside the normal local
admin environment without leaking provider or runtime payload details.

Expected: the reviewer can sign in as `platform-admin`.

Expected: the reviewer can see a ready health response.

Expected: the reviewer can capture a Playwright screenshot path.

Expected: the reviewer can explain that Spec 061 has runtime behavior but no
new public UI route family.

## Environment Setup

Use `specs/061-model-backed-graph-role-executor/.env.qa061`.

Start from the repository root.

Copy the QA environment.

```bash
cp specs/061-model-backed-graph-role-executor/.env.qa061 .env
uv sync
docker compose up -d postgres
```

Reset the QA database and apply migrations.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa061 && createdb -U postgres multi_agent_platform_qa061'
uv run alembic upgrade head
uv run python scripts/qa/seed_model_backed_roles_qa061.py
```

Expected: seed output says `Seeded QA061 model-backed role executor evidence`.

Expected: seed output writes evidence under `.data/qa061-artifacts/evidence`.

Start the API if reviewing manually.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker in a second terminal if the full manifest is not managing it.

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: `http://127.0.0.1:8000/health/live` returns success.

Expected: `http://127.0.0.1:8000/health/ready` returns success.

Expected: `/tmp/qa061-api.log` and `/tmp/qa061-worker.log` remain safe to share.

## Browser Walkthrough

Open local login.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/health/ready
```

What is happening: local-principal login sets a deterministic reviewer identity.

Why this matters: QA061 must not depend on Auth0 or external identity services.

Expected: the login form is available.

Expected: the form includes local principals.

Choose `platform-admin`.

Expected: the browser redirects to `/health/ready`.

Expected: the visible response includes `ready`.

Expected: the visible response does not include provider secrets.

Open the OpenAPI document.

```text
http://127.0.0.1:8000/openapi.json
```

What is happening: FastAPI renders the currently mounted route contracts.

Why this matters: Spec 061 did not add a public route family, so OpenAPI should
remain stable while health and platform routes continue to work.

Expected: the page loads without authentication errors after local login.

Expected: the page contains route metadata.

Expected: the page does not include raw prompts or completions.

Open dependency readiness.

```text
http://127.0.0.1:8000/dependencies
```

What is happening: the platform reports configured dependency readiness.

Why this matters: model-backed execution is wired through worker bootstrap
dependencies, and readiness must describe availability without exposing secrets.

Expected: the dependency response is JSON.

Expected: the dependency response is safe for screenshots.

Expected: no field reveals model provider authorization headers.

Run the automated Playwright smoke.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/061-model-backed-graph-role-executor/validation.yml --start-processes
```

Expected: the command prints a screenshot path.

Expected: `output/playwright/qa061_ui/qa061-scenario-enhancement-smoke.png`
exists.

Expected: the screenshot shows health readiness.

Record the screenshot path.

```bash
printf 'qa061 screenshot: output/playwright/qa061_ui/qa061-scenario-enhancement-smoke.png\n' > /tmp/qa061-ui-action-evidence.txt
```

Expected: `/tmp/qa061-ui-action-evidence.txt` contains the screenshot path.

Expected: the screenshot path is specific to `qa061`.

## Required Automated Evidence

Run Playwright UI validation through the manifest.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/061-model-backed-graph-role-executor/validation.yml --start-processes
```

Expected: the command exits with status zero.

Expected: the command writes a screenshot under `output/playwright/qa061_ui`.

Run the QA verifier after browser checks.

```bash
uv run python scripts/qa/verify_model_backed_roles_qa061.py | tee /tmp/qa061-post-ui-evidence.txt
```

Expected: the verifier prints `Verified QA061 model-backed role executor evidence`.

Run the document and quality gates.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/061-model-backed-graph-role-executor
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

Record the QA environment file path.

Record the local login URL.

Record the selected principal.

Record the health readiness URL.

Record the OpenAPI URL.

Record the dependency readiness URL.

Record the Playwright screenshot path.

Record the post-UI verifier output path.

Record whether screenshots show only safe metadata.

Record whether any unexpected provider, prompt, completion, or credential text
appeared.

Expected: evidence uses `qa061` names.

Expected: evidence references `.env.qa061`.

Expected: evidence includes the screenshot location.

Expected: evidence includes no raw secret material.

## Acceptance Notes Template

Use this section to write a short reviewer note.

QA id: qa061.

Environment file: `specs/061-model-backed-graph-role-executor/.env.qa061`.

Principal used: `platform-admin`.

Health URL reviewed: `http://127.0.0.1:8000/health/ready`.

Login URL reviewed: `http://127.0.0.1:8000/auth/local-login?redirect_to=/health/ready`.

Screenshot path: `output/playwright/qa061_ui/qa061-scenario-enhancement-smoke.png`.

Post-UI verifier: `/tmp/qa061-post-ui-evidence.txt`.

What is happening: the browser checks local operational readiness for runtime
executor validation.

Why this matters: the runtime can be validated in the same app surface that
later scenario specs will extend.

Expected: reviewer notes say that Spec 061 adds runtime behavior, not a new
React page.

Expected: reviewer notes say that model output is validated by backend tests.

Expected: reviewer notes say that UI evidence stays redaction-safe.

## Troubleshooting

If local login does not load, confirm the API is running on `127.0.0.1:8000`.

If health readiness fails, inspect `/tmp/qa061-api.log`.

If the worker exits, inspect `/tmp/qa061-worker.log`.

If the browser shows stale output, reload after the API process restarts.

If Playwright cannot connect, confirm no other process owns port 8000.

If the screenshot is missing, rerun the Playwright command and inspect terminal
output.

If the OpenAPI document is unavailable, confirm migrations completed.

If dependency readiness shows a missing optional dependency, compare it with the
expected QA061 manifest before treating it as a regression.

If unsafe text appears in a screenshot, stop and inspect the failing runtime
path before attaching evidence.

Expected: troubleshooting does not require real provider credentials.

Expected: troubleshooting does not require live external calls.

## Related Files

- `specs/061-model-backed-graph-role-executor/qa061.md`
- `specs/061-model-backed-graph-role-executor/.env.qa061`
- `specs/061-model-backed-graph-role-executor/qa061_user_guide.md`
- `specs/_autopilot/scenario-enhancement-roadmap/061-model-backed-graph-role-executor/validation.yml`
- `scripts/qa/seed_model_backed_roles_qa061.py`
- `scripts/qa/verify_model_backed_roles_qa061.py`
- `src/multi_agent_platform/runtime/orchestration/model_backed_roles.py`
- `src/multi_agent_platform/runtime/orchestration/role_output_contracts.py`
- `src/multi_agent_platform/workers/orchestration.py`
