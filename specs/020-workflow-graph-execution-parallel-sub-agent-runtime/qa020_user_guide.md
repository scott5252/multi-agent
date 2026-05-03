# QA020 User Guide: Workflow Graph Execution And Parallel Sub-Agent Runtime

## Detailed Overview

QA020 validates workflow graph execution inside the multi-agent platform.

The feature lets a worker load a published workflow bundle, read the graph
document inside that bundle, and execute the nodes in dependency order.

A node can represent a role, a join, an approval point, a subworkflow boundary,
or a terminal outcome.

The most important reviewer scenario is the Daily Intelligence Briefing graph.

That graph starts with an orchestrator role.

It then fans out to four scout roles.

The scout roles are independent.

Because they are independent, the scheduler should place them in the same
parallel wave.

After the scout wave, the graph reaches a join.

The join decides whether enough branches succeeded to continue.

The graph then continues to focus, synthesis, and terminal nodes.

The runtime records durable evidence while it works.

Evidence includes run steps, timeline events, checkpoint references, handoff
envelopes, side-effect intent summaries, approval gates, and final status.

The feature also protects tenant boundaries.

A run for Acme must not execute a Globex workflow bundle.

The feature protects resume safety.

If a worker restarts after some nodes already succeeded, those nodes should not
execute a second time.

The feature protects sensitive information.

Reviewer-facing records must not contain raw secrets, raw prompt text, raw
model responses, raw tool payloads, or unauthorized tenant data.

QA020 uses deterministic mock role execution.

That means the reviewer does not need any real model provider account.

It also means no real calendar, email, weather, maps, Telegram, or other
external tool call is required.

The browser portion is intentionally small.

Spec 020 does not add a new screen.

It uses existing admin shell, workflow studio, run inspection, and operations
pages for visual review.

The deeper graph behavior is proven by automated tests and validation scripts.

## Who Should Use This Guide

Use this guide if you are a non-developer reviewer.

Use this guide if you need to collect manual QA evidence for Spec 020.

Use this guide if you need to confirm the feature can be reviewed locally.

Use this guide if you are checking that tenant boundaries remain understandable.

Use this guide if you are checking that sensitive values are not visible.

You do not need to understand Python internals to follow this guide.

You do need access to the repository checkout.

You do need Docker and the local development commands described below.

Ask an engineer for help if Docker cannot start PostgreSQL.

Ask an engineer for help if the full automated test suite fails.

## Manual QA Prerequisites

Start from the repository root.

Confirm that the current branch is the QA020 feature branch.

The expected branch name is
`codex/020-workflow-graph-execution-parallel-sub-agent-runtime`.

Confirm that the QA environment file exists.

The expected file is
`specs/020-workflow-graph-execution-parallel-sub-agent-runtime/.env.qa020`.

Confirm that the main QA guide exists.

The expected file is
`specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020.md`.

Confirm that the UI walkthrough exists.

The expected file is
`specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020_ui.md`.

Prepare two terminal windows.

Use Terminal A for the API and worker.

Use Terminal B for commands and tests.

Prepare one browser window.

Use the browser only with `http://127.0.0.1:8000`.

Do not use shared staging services for this review.

Do not enter real provider credentials.

Do not paste customer data into test inputs.

## Step-by-Step Manual QA

Step 1: Copy the QA020 environment file.

Run `cp specs/020-workflow-graph-execution-parallel-sub-agent-runtime/.env.qa020 .env`.

Expected result: the command has no output.

What it proves: local settings now target the QA020 database and fake
credential references.

Step 2: Install dependencies.

Run `uv sync`.

Expected result: dependencies install or are already installed.

What it proves: the local machine can run the app and tests.

Step 3: Start PostgreSQL.

Run `docker compose up -d postgres`.

Expected result: Docker reports the PostgreSQL container is running.

What it proves: the database service required by runtime evidence is
available.

Step 4: Reset the QA020 database.

Run `docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa020 && createdb -U postgres multi_agent_platform_qa020'`.

Expected result: the command completes successfully.

What it proves: the review starts from a clean isolated database.

Step 5: Apply migrations.

Run `uv run alembic upgrade head`.

Expected result: migrations complete successfully.

What it proves: all existing runtime tables are present.

Step 6: Run the focused graph tests.

Run `uv run pytest --no-cov tests/unit/runtime/orchestration/test_graph_execution.py tests/unit/runtime/orchestration/test_graph_roles.py tests/unit/runtime/orchestration/test_graph_redaction.py tests/integration/runtime/test_workflow_graph_execution.py tests/integration/workers/test_orchestration_worker.py`.

Expected result: every focused graph test passes.

What it proves: graph planning, fan-out, join policies, redaction, tenant
denial, resume safety, and worker integration work together.

Step 7: Run the Daily Intelligence Briefing test.

Run `uv run pytest --no-cov -vv tests/integration/runtime/test_workflow_graph_execution.py::test_daily_briefing_graph_schedules_four_scouts_in_one_wave`.

Expected result: the test passes.

What it proves: four scout nodes were scheduled in one parallel wave.

Step 8: Run the manual resolution test.

Run `uv run pytest --no-cov -vv tests/integration/runtime/test_workflow_graph_execution.py::test_manual_resolution_join_pauses_and_persists_approval`.

Expected result: the test passes.

What it proves: a join can pause the run and persist approval evidence.

Step 9: Run the tenant isolation test.

Run `uv run pytest --no-cov -vv tests/integration/runtime/test_workflow_graph_execution.py::test_cross_tenant_bundle_execution_fails_closed`.

Expected result: the test passes.

What it proves: a tenant run cannot execute another tenant's bundle.

Step 10: Run the redaction test.

Run `uv run pytest --no-cov -vv tests/integration/runtime/test_workflow_graph_execution.py::test_graph_execution_redacts_sensitive_step_and_timeline_values`.

Expected result: the test passes.

What it proves: sensitive-looking values are replaced before reviewer evidence
is stored.

Step 11: Start the API.

In Terminal A, run `uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000`.

Expected result: the API listens locally.

What it proves: the app boots with QA020 settings.

Step 12: Open the local login page.

Use the browser to open `http://127.0.0.1:8000/auth/local-login`.

Expected result: local principals are listed.

What it proves: review can proceed without external identity setup.

Step 13: Sign in as `platform-admin`.

Use the login page and choose `platform-admin`.

Expected result: `/admin` opens.

What it proves: platform-level review surfaces are reachable.

Step 14: Open `/admin/workflows/ui`.

Expected result: the workflow studio loads.

What it proves: published workflow bundle management remains visible.

Step 15: Open `/admin/runs`.

Expected result: the run inspection page loads with a safe list or empty
state.

What it proves: graph run evidence uses existing inspection surfaces.

Step 16: Open `/admin/operations`.

Expected result: the operations console loads with health and dependency
information or a safe local warning.

What it proves: operational review still works after worker changes.

Step 17: Sign in as `tenant-admin-acme`.

Expected result: the admin shell opens under Acme tenant context.

What it proves: tenant-scoped review remains available.

Step 18: Review `/admin/runs` as Acme.

Expected result: only authorized Acme information or a safe empty state is
visible.

What it proves: browser inspection does not cross tenant boundaries.

Step 19: Sign in as `tenant-admin-globex`.

Expected result: the admin shell opens under Globex tenant context.

What it proves: the second tenant identity is configured.

Step 20: Review screenshots and notes.

Expected result: no captured page shows raw secrets, raw prompt text, raw model
responses, raw tool payloads, or unauthorized tenant data.

What it proves: manual browser evidence matches the runtime redaction contract.

## Expected Results

The focused graph test suite passes.

The Daily Intelligence Briefing test shows four scout branches in one wave.

The manual resolution test pauses the run with approval evidence.

The tenant isolation test fails closed.

The redaction test stores safe summaries and digests only.

The API starts with `.env.qa020`.

The worker starts with graph execution imports.

The local login page lists QA principals.

The admin shell opens for `platform-admin`.

The workflow studio opens for `platform-admin`.

The run inspection page opens for platform and tenant reviewers.

The operations page opens for platform reviewers.

No browser screenshot contains raw sensitive values.

No browser screenshot contains unauthorized tenant data.

The QA document validator passes.

The Spec Kit validation script passes.

The Playwright smoke script passes.

The full quality gates pass.

## Evidence To Capture

Capture the terminal output for focused graph tests.

Capture the terminal output for the Daily Intelligence Briefing test.

Capture the terminal output for the manual resolution test.

Capture the terminal output for the tenant isolation test.

Capture the terminal output for the redaction test.

Capture the terminal output for QA document validation.

Capture the terminal output for Spec Kit validation.

Capture the terminal output for Playwright smoke validation.

Capture screenshots for local login, admin shell, workflow studio, run
inspection, operations, Acme tenant review, and Globex tenant review.

Record which local principal was used for each screenshot.

Record whether each screenshot showed safe data only.

Record any dependency warning exactly as it appears.

Record any failed command and stop the review until it is triaged.

## Security And Redaction Checks

Search screenshots for credential-looking values.

Search screenshots for raw prompt text.

Search screenshots for raw model output.

Search screenshots for raw tool payloads.

Search screenshots for raw memory content.

Search screenshots for cross-tenant labels that should not be visible.

Run the redaction integration test.

Confirm it passes.

Open the QA guide.

Confirm it says deterministic mock role execution only.

Open `.env.qa020`.

Confirm secret values are fake QA020 placeholders.

Do not add real keys to `.env.qa020`.

Do not add customer data to fixtures.

Do not attach raw database rows to reviewer notes if they contain sensitive
payloads.

Use safe summaries, screenshots, and test output instead.

## Tenant Isolation Checks

Sign in as `platform-admin`.

Confirm platform pages are reachable.

Sign in as `tenant-admin-acme`.

Confirm Acme pages render only authorized Acme information or safe empty
states.

Sign in as `tenant-admin-globex`.

Confirm Globex pages render only authorized Globex information or safe empty
states.

Run the cross-tenant graph execution test.

Confirm it passes.

Record that the graph executor denied a mismatched tenant bundle.

Record that browser inspection did not show another tenant's graph evidence.

If any tenant boundary is unclear, stop and ask an engineer to inspect the
authorization decision.

## Troubleshooting

If dependency installation fails, rerun `uv sync` and save the error output.

If PostgreSQL does not start, run `docker compose ps postgres`.

If migration fails, confirm `.env` was copied from `.env.qa020`.

If the focused tests fail, do not continue to browser review.

If the API does not start, inspect the terminal output for missing environment
keys.

If the login page does not show QA principals, restart the API after copying
`.env.qa020`.

If the browser keeps an old login, clear cookies for `127.0.0.1`.

If `/admin/runs` is empty, that is acceptable when focused tests provide graph
execution evidence.

If operations shows local dependency warnings, compare them with the
`/dependencies` endpoint.

If the Playwright smoke command fails because port `8000` is busy, stop the
other local server and rerun.

If full coverage fails after focused tests pass, review the coverage report
with an engineer before changing QA020 behavior.

If any screenshot contains sensitive data, stop the review and report the
exact page and principal.

If tenant isolation appears broken, stop the review and keep the evidence for
debugging.
