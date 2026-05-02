# QA015 User Guide: Agent And Workflow Test Bench

## Detailed Overview

The Agent And Workflow Test Bench is an admin feature for checking whether
prompts, agent runtime profiles, workflow drafts, published subworkflows, and
published workflows still behave as expected before they are trusted in a
release path.

Think of a test suite as a release checklist that the platform can run.

Each suite belongs to one tenant and points at one target, such as an Acme
workflow draft named `qa015-draft-triage`.

Each suite contains one or more test cases.

Each case contains fixture input, an expected output shape, and assertions.

Fixture input is sample data for the run.

Expected contract shape describes the top-level fields that must be present in
the result.

Assertions check exact values, text containment, regex matches, JSON schema,
latency, token usage, or evaluator-style scoring.

Runs execute the suite in a selected safe mode.

`mock_model` uses deterministic model output.

`mock_tools` keeps model behavior deterministic and blocks tool side effects.

`real_model_side_effects_disabled` records gateway-style model metadata while
blocking tool writes.

`approved_real_probe` is reserved for explicitly approved real dependency
checks.

QA015 does not require real credentials or real provider calls.

The result page shows safe summaries only.

Raw secrets, credential values, prompt bodies, provider messages, tool payloads,
and transcripts must not appear in the browser.

Run results include pass or fail status, token usage, latency, model/provider
metadata, contract validation, assertion results, side-effect blocks, redaction
summary, and artifact summary.

Publication gates use this evidence to decide whether a workflow candidate is
ready.

A gate is ready when a required suite has a passing run for the current target
version.

A gate is blocked when the required suite has no run, a failing run, or only a
stale run from an older target version.

Tenant isolation is required throughout the feature.

An Acme admin may manage Acme suites and runs.

A Globex admin must not see Acme suite names, target names, fixtures,
transcripts, or run identifiers.

The local QA environment uses fake values and deterministic tenants so the
review can be repeated from a clean checkout.

## Who Should Use This Guide

Use this guide if you are a manual QA reviewer, product reviewer, release
manager, compliance reviewer, or support engineer validating the feature
without reading the implementation.

You do not need to write code.

You should be comfortable copying terminal commands, opening local browser
pages, filling forms, and recording screenshots or notes.

Use `qa015_ui.md` when you want a browser-first checklist.

Use `qa015.md` when you want API commands and automated validation commands.

Use this user guide when you want plain-language context and a slower
step-by-step path.

## Manual QA Prerequisites

Use a local checkout of the repository.

Install Python 3.12.

Install `uv`.

Install Docker Compose v2.

Keep a browser available.

Do not use production hosts.

Do not use real provider keys.

Do not paste customer data into fixture fields.

Do not reset any database except `multi_agent_platform_qa015`.

Before starting, copy the QA environment:

```bash
cp specs/015-agent-workflow-test-bench/.env.qa015 .env
```

Expected result: the command has no output.

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Expected result: Docker reports that the `postgres` service is running.

Reset the QA database:

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa015 && createdb -U postgres multi_agent_platform_qa015'
```

Expected result: the command finishes without affecting any other database.

Apply migrations:

```bash
uv run alembic upgrade head
```

Expected result: Alembic completes successfully.

Seed the Acme and Globex tenants using the SQL command in `qa015.md`.

Expected result: Acme and Globex are available for login and isolation checks.

Start the API server:

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
```

Expected result: the server listens at `http://127.0.0.1:8000`.

## Step-by-Step Manual QA

Step 1: Open the local login page.

Use this URL:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/agent-tests/ui?tenant_id=11111111-1111-1111-1111-111111111111
```

Expected result: the page title is `Local Login`.

Step 2: Sign in as `Acme Tenant Admin`.

Expected result: the browser redirects to the Agent Tests page.

Step 3: Confirm the active scope is Acme.

Expected result: the page is scoped to the Acme tenant and shows no existing
suites in a clean database.

Step 4: Click `Create Suite`.

Expected result: the create suite form opens.

Step 5: Fill the suite form.

Use `QA015 Draft Workflow Guard` for the name.

Use `workflow_draft` or `Workflow draft` for target type.

Use `qa015-draft-triage` for the target id.

Use `draft-rev-1` for the target version.

Use `mock_model` or `Mock model` for safe mode.

Use `mock` for model mode.

Use `mock` for tool mode.

Use `1.0` for pass threshold.

Check `Required for publish`.

Expected result: submitting the form opens a suite detail page.

Step 6: Record the suite id from the URL.

Expected result: the URL contains `/admin/agent-tests/ui/suites/` followed by a
UUID.

Step 7: Review the suite detail page.

Expected result: target, safe mode, publish gate status, add case form, cases
table, and runs table are visible.

Step 8: Add a case.

Use `Passing intake case` for the name.

Use this fixture JSON:

```json
{"request":"summarize intake","priority":"routine","api_key":"qa015-fake-value"}
```

Use this expected contract shape:

```json
{"status":{},"contract":{}}
```

Use this assertions JSON:

```json
[{"kind":"deterministic","path":"status","comparator":"equals","expected_value":"passed"},{"kind":"deterministic","path":"contract.summary","comparator":"contains","expected_value":"intake"}]
```

Expected result: the case appears in the Cases table after submission.

Step 9: Confirm fixture redaction.

Expected result: the raw value `qa015-fake-value` is not displayed.

Step 10: Run the suite with `Mock model`.

Expected result: the browser opens a run detail page and the run passes.

Step 11: Review the run summary.

Expected result: pass status, latency, tokens, target, redaction summary, and
artifact summary are visible.

Step 12: Review trace steps.

Expected result: each step shows status, model metadata, contract result,
assertions, and side-effect decisions.

Step 13: Return to the suite page.

Expected result: the Runs table includes the completed mock-model run.

Step 14: Run the suite with `Real model, side effects disabled`.

Expected result: the run passes and shows `mocked-gateway` metadata.

Step 15: Confirm side effects are blocked.

Expected result: the trace step shows `external_dependency.write blocked`.

Step 16: Review publish gate status.

Expected result: the gate is ready because a passing run exists for
`draft-rev-1`.

Step 17: Open a new browser tab for Globex.

Use this URL:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/agent-tests/ui?tenant_id=22222222-2222-2222-2222-222222222222
```

Expected result: the Globex tenant admin can sign in.

Step 18: Confirm Globex does not see Acme suites.

Expected result: the Globex Agent Tests page is empty for a clean run.

Step 19: Attempt to open the Acme suite URL in the Globex tab.

Expected result: access is denied.

Step 20: Confirm the denial is safe.

Expected result: the denial does not reveal Acme target names, case names,
fixture values, transcripts, prompt text, or artifact references.

## Expected Results

The Acme tenant admin can create a suite.

The suite can target a workflow draft.

The suite can be marked required for publication.

The suite detail page shows a redaction notice.

The Acme tenant admin can add a fixture-backed case.

The case table does not show raw fake credential values.

The mock-model run completes successfully.

The mocked-gateway run completes successfully.

The mocked-gateway run records blocked side effects.

The run detail page shows safe model/provider metadata.

The run detail page shows contract and assertion outcomes.

The run detail page shows token and latency summaries.

The run detail page does not show raw transcript bodies.

The publish gate is ready for the current passing target version.

The stale target version is blocked when checked through API validation.

The approved real probe mode is rejected when no approval metadata is supplied.

Globex cannot see Acme suite data.

Globex direct links fail closed.

No production hostnames or real credentials are needed.

Automated QA docs, API checks, browser checks, linting, typing, and coverage
commands are available in the feature docs.

## Evidence To Capture

Capture the local login page.

Capture the empty Acme Agent Tests page.

Capture the create suite form.

Capture the suite detail page after suite creation.

Capture the suite detail page after case creation.

Capture the mock-model run detail page.

Capture the mocked-gateway run detail page.

Capture the blocked side-effect row.

Capture the publish gate ready status.

Capture the Globex empty list.

Capture the Globex denial or record the status code.

Record the suite id.

Record the mock-model run id.

Record the mocked-gateway run id.

Record the QA docs validation result.

Record the Playwright output directory.

Record the focused pytest result.

Record the full coverage result if it was run.

Store screenshots under `output/playwright/qa015_ui`.

Store notes or API output under `/tmp/qa015-*`.

## Security And Redaction Checks

Search visible pages for `qa015-fake-value`.

Expected result: the value is not visible.

Search visible pages for raw authorization headers.

Expected result: no authorization header values are visible.

Search visible pages for raw prompt bodies.

Expected result: prompt bodies are absent or summarized safely.

Search run details for transcript content.

Expected result: transcripts appear only as redacted summaries.

Review artifact summaries.

Expected result: artifact summaries contain counts or references, not raw
payloads.

Review side-effect blocks.

Expected result: blocked decisions use safe tool names and reasons.

Review the approved-probe behavior through the API guide.

Expected result: unapproved real probe execution returns a rejection.

Review `.env.qa015`.

Expected result: all secrets are fake `qa015/` references.

## Tenant Isolation Checks

Acme can list its own suite.

Acme can run its own suite.

Acme can open its own run detail.

Globex cannot list Acme suites.

Globex cannot open the Acme suite detail URL.

Globex cannot open the Acme run detail URL.

Denied Globex responses must not include Acme target names.

Denied Globex responses must not include Acme fixture values.

Denied Globex responses must not include Acme transcript summaries.

Denied Globex responses must not include artifact paths.

Tenant scope must be visible in the admin shell.

Changing tabs between Acme and Globex should not merge data.

## Troubleshooting

If the login page is not available, confirm the API server is running.

If local-principal cards are missing, confirm `.env.qa015` was copied to
`.env`.

If the Acme page says tenant id is required, reopen the login URL with the
Acme `tenant_id` query value.

If suite creation fails, confirm required fields are filled.

If case creation fails, validate the fixture and assertion JSON.

If the run fails unexpectedly, inspect the contract and assertion diagnostics
on the run detail page.

If mocked-gateway mode does not show a blocked side effect, confirm the
selected safe mode was `real_model_side_effects_disabled`.

If Globex can see Acme data, stop the QA pass and file a tenant isolation
blocker.

If raw fake secret values appear, stop the QA pass and file a redaction
blocker.

If screenshots are missing, create `output/playwright/qa015_ui` and repeat the
browser validation.

If the database reset fails, confirm Docker PostgreSQL is running.

If migrations fail, capture the Alembic output and stop before browser QA.

If the QA docs validator fails, confirm `qa015.md`, `qa015_ui.md`, and
`.env.qa015` are present.

If full coverage is slow, run the focused QA015 pytest command first and then
run the full coverage command before final acceptance.
