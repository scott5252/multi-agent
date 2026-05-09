# QA061 User Guide: Spec 061 - Model-Backed Graph Role Executor

## Detailed Overview

Spec 061 adds model-backed execution for workflow graph role nodes.

A graph role node is one step in a workflow graph.

Before this spec, role execution was deterministic by default.

Deterministic execution is still the default.

The new path runs only when a role node explicitly asks for model-backed
execution.

The new path resolves tenant-scoped model, prompt, profile, provider, and policy
pins before any model call.

The new path calls the governed `ModelGateway` instead of calling a provider
client directly.

Local QA uses mocked gateway behavior.

Local QA does not call OpenAI, Telegram, Auth0, or any external connector.

The executor builds model input from safe summaries.

The executor rejects unsafe input field names.

The executor validates model output against a role output contract.

The executor stores oversized structured output as an artifact reference when a
storage provider is available.

The executor returns safe usage, provenance, and artifact metadata through
`RoleExecutionResult`.

The graph runner records failed model-backed execution as a failed node result.

The graph runner does not treat malformed model output as success.

The worker bootstrap wires model gateway dependencies into graph orchestration.

This user guide is for manual QA review.

It explains what to check and what evidence to capture.

It does not replace automated tests.

It helps reviewers understand why the automated checks matter.

All examples use the QA061 environment.

All examples use local test data.

All examples avoid real credentials.

## Who Should Use This Guide

Use this guide if you are manually reviewing QA061.

Use this guide if you need a plain-language explanation of model-backed role
execution.

Use this guide if you are checking Playwright screenshots.

Use this guide if you are checking runtime QA evidence.

Use this guide if you are checking redaction behavior.

Use this guide if you are confirming tenant isolation.

Use this guide if you are preparing notes before Spec 062 starts.

Use this guide if you need to explain why there is no dedicated React page in
Spec 061.

Do not use this guide against a shared database.

Do not use this guide with production credentials.

Do not use this guide to run live provider probes.

Do not use this guide to inspect raw prompts or completions.

## Manual QA Prerequisites

Work from the repository root.

Confirm Docker is running.

Confirm PostgreSQL can start with Docker Compose.

Confirm `uv` is available.

Confirm the QA environment file exists.

Confirm the validation manifest exists.

Confirm the seed script exists.

Confirm the verifier script exists.

Confirm the runtime executor files are present.

Confirm the focused test files are present.

Prepare the QA environment.

```bash
cp specs/061-model-backed-graph-role-executor/.env.qa061 .env
uv sync
docker compose up -d postgres
```

Reset and migrate the QA database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa061 && createdb -U postgres multi_agent_platform_qa061'
uv run alembic upgrade head
```

Seed QA061 evidence.

```bash
uv run python scripts/qa/seed_model_backed_roles_qa061.py
```

Expected result: the seed script prints `Seeded QA061 model-backed role executor evidence`.

Expected result: evidence is written under `.data/qa061-artifacts/evidence`.

Expected result: no real provider credential is required.

Expected result: no live external call is made.

## Step-by-Step Manual QA

Start the API in one terminal.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker in another terminal.

```bash
uv run python -m multi_agent_platform.workers.main
```

Open local login in a browser.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/health/ready
```

Choose `platform-admin`.

Expected result: the browser opens `/health/ready`.

Expected result: the page includes `ready`.

Expected result: the page does not include a provider credential.

Open the OpenAPI document.

```text
http://127.0.0.1:8000/openapi.json
```

Expected result: the page loads.

Expected result: the page shows platform route metadata.

Expected result: no raw prompts or completions are visible.

Run the focused model-backed role tests.

```bash
uv run pytest tests/contract/test_model_backed_role_executor_contracts.py tests/unit/runtime/orchestration/test_model_backed_roles.py tests/unit/runtime/orchestration/test_graph_roles.py tests/unit/bootstrap/test_worker_gateway_bootstrap.py tests/integration/runtime/test_model_backed_graph_execution.py --no-cov
```

Expected result: the tests pass.

Expected result: deterministic role execution remains unchanged.

Expected result: mocked model-backed execution uses the governed gateway path.

Run the verifier.

```bash
uv run python scripts/qa/verify_model_backed_roles_qa061.py
```

Expected result: the verifier prints `Verified QA061 model-backed role executor evidence`.

Run Playwright.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/061-model-backed-graph-role-executor/validation.yml --start-processes
```

Expected result: the screenshot exists under `output/playwright/qa061_ui`.

Run the Spec Kit QA manifest.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/scenario-enhancement-roadmap/061-model-backed-graph-role-executor/validation.yml
```

Expected result: the manifest prints `Spec QA validation completed`.

Expected result: quality checks pass.

Expected result: seed and verifier commands pass.

Run the full curl regression after the spec checks pass.

```bash
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa061-after-spec
```

Expected result: the curl regression has no failed commands.

## Expected Results

Deterministic role execution is still the default.

A role must explicitly request model-backed execution.

Missing tenant context fails closed.

Missing run step context fails closed.

Missing output contract metadata fails closed.

Missing model pins fail closed.

Denied model policy fails closed.

Unsafe input field names fail closed.

Malformed model output fails closed.

Output that violates the role contract fails closed.

Successful model-backed output includes a safe summary.

Successful model-backed output includes a payload digest.

Successful model-backed output includes usage metadata.

Successful model-backed output includes provenance metadata.

Oversized successful output is represented by an artifact reference.

The gateway call includes workflow, step, trace, idempotency, prompt, profile,
and model context.

No direct provider client call is used by runtime role execution.

No raw prompt or completion appears in screenshots.

No raw credential appears in QA evidence.

## Evidence To Capture

Capture the focused test command and result.

Capture the QA document validation result.

Capture the seed script output path.

Capture the verifier output path.

Capture the Playwright screenshot path.

Capture the Spec Kit QA manifest result.

Capture the curl regression output directory.

Capture a note that `curl_testing.md` did not need a new section because Spec
061 added no public JSON API route family.

Capture a note that deterministic behavior remains unchanged.

Capture a note that model-backed behavior uses mocked gateway execution locally.

Capture a note that invalid model output fails safely.

Capture a note that evidence is redaction-safe.

Use `/tmp/qa061-seed.txt` for seed evidence.

Use `/tmp/qa061-post-ui-evidence.txt` for verifier evidence.

Use `/tmp/qa061-ui-action-evidence.txt` for screenshot paths.

Use `.data/curl_test_runs/qa061-after-spec` for curl evidence.

## Security And Redaction Checks

Check that screenshots do not include `Authorization:`.

Check that screenshots do not include provider API keys.

Check that evidence files do not include raw prompts.

Check that evidence files do not include raw completions.

Check that evidence files do not include raw memory contents.

Check that evidence files do not include private channel messages.

Check that evidence files do not include raw external tool payloads.

Check that static secrets use the `qa061/` prefix.

Check that the verifier rejects unsafe markers in QA evidence.

Check that contract-invalid output is reported as a safe failure.

Expected result: evidence contains only safe summaries, ids, digests, and
artifact references.

Expected result: no reviewer needs access to a live provider secret.

## Tenant Isolation Checks

Use Acme tenant id `11111111-1111-1111-1111-111111111111` for positive QA.

Use Globex tenant id `22222222-2222-2222-2222-222222222222` for empty or denied
QA.

Confirm local principals in `.env.qa061` map Acme and Globex separately.

Confirm model-backed role context requires a tenant id.

Confirm missing tenant id fails before a gateway call.

Confirm pin resolution is tenant scoped.

Confirm QA artifacts live under `.data/qa061-artifacts`.

Confirm evidence does not mix tenant ids in one successful role result.

Expected result: Acme evidence remains Acme-scoped.

Expected result: Globex does not read Acme runtime evidence.

Expected result: platform-admin checks still require explicit tenant context.

## Troubleshooting

If the seed script fails, confirm the QA database exists and migrations have
run.

If the verifier fails, inspect `.data/qa061-artifacts/evidence`.

If focused tests fail, inspect the failing model-backed role test first.

If deterministic behavior changed, inspect `graph_roles.py` and
`graph_execution.py`.

If gateway context assertions fail, inspect `model_backed_roles.py`.

If output contract checks fail, inspect `role_output_contracts.py`.

If the API does not start, inspect `/tmp/qa061-api.log`.

If the worker does not start, inspect `/tmp/qa061-worker.log`.

If Playwright fails, confirm `http://127.0.0.1:8000/health/ready` loads.

If the curl regression fails, inspect `.data/curl_test_runs/qa061-after-spec`.

If a QA command attempts a live external call, stop and inspect `.env.qa061`.

Expected result: every troubleshooting path remains local and deterministic.

Expected result: no troubleshooting path requires real provider credentials.

