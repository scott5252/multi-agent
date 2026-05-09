# QA060 User Guide: Spec 060 - Design Review Domain Foundation

## Detailed Overview

Spec 060 creates the durable foundation for a design review workflow.

A design review session represents a request to review a design before it moves
to development.

A revision records the safe summary and digest for a submitted design version.

A review round records which revision is being evaluated.

Reviewer assignments record which reviewer roles participated.

Reviewer verdicts record safe summaries, scores, blocking issue counts, and
artifact references.

Quorum decisions record whether the review passed, needs revision, needs manual
resolution, failed, or has no next action.

Manual decisions record human resolution choices such as revise, retry, cancel,
or approve by exception.

Development handoff records safe metadata for an approved revision.

The feature is backend-first.

There is no dedicated design review React workspace in this spec.

Manual QA uses JSON API routes, OpenAPI discovery, and safe local-principal
browser checks.

The goal is to prove the storage, authorization, idempotency, and safe response
contracts before the later orchestration and UI specs build on them.

All test data is local.

All provider, Telegram, and connector behavior is mocked or disabled.

No real credential is needed.

No real design artifact is needed.

## Who Should Use This Guide

Use this guide if you are manually reviewing QA060.

Use this guide if you need a plain-language explanation of the new records.

Use this guide if you are checking screenshots created by Playwright.

Use this guide if you are checking API responses captured during validation.

Use this guide if you need to verify tenant isolation.

Use this guide if you need to verify redaction and safe summaries.

Use this guide if you are helping decide whether Spec 060 can hand off to Spec
061.

Do not use this guide for a shared environment.

Do not use this guide with real provider credentials.

Do not use this guide to make live external calls.

## Manual QA Prerequisites

Work from the repository root.

Confirm Docker is running.

Confirm the PostgreSQL service can start through Docker Compose.

Confirm `uv` is available.

Confirm the QA environment file exists.

Confirm the validation manifest exists.

Confirm the seed script exists.

Confirm the verifier script exists.

Confirm the local branch includes the design review migration.

Prepare the environment.

```bash
cp specs/060-design-review-domain-foundation/.env.qa060 .env
uv sync
docker compose up -d postgres
```

Reset and migrate the QA database.

```bash
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa060 && createdb -U postgres multi_agent_platform_qa060'
uv run alembic upgrade head
```

Seed QA060 design review evidence.

```bash
uv run python scripts/qa/seed_design_review_qa060.py
```

Expected result: the seed script prints `Seeded QA060 design review live records`.

Expected result: the seed script prints a design review session id.

Expected result: the seed script prints a design review round id.

## Step-by-Step Manual QA

Start the API in one terminal.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker in another terminal.

```bash
uv run python -m multi_agent_platform.workers.main
```

Open local login in the browser.

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/openapi.json
```

Choose `platform-admin`.

Expected result: the browser opens `/openapi.json`.

Expected result: the page contains `design-reviews`.

Expected result: the page contains `/admin/design-reviews/sessions`.

Create a design review session as Acme.

```bash
curl --fail --silent --show-error -X POST -H 'Content-Type: application/json' -H 'X-Local-Principal: tenant-admin-acme' 'http://127.0.0.1:8000/admin/design-reviews/sessions' -d '{"tenant_id":"11111111-1111-1111-1111-111111111111","request_summary":"QA060 manual design review.","quorum_policy_key":"four_of_five_no_blockers","idempotency_key":"qa060-manual-create"}' > /tmp/qa060-manual-create.json
```

Expected result: the response contains `design_review_session_id`.

Expected result: the response contains `"replayed":false` or equivalent JSON
spacing.

Replay the same request.

```bash
curl --fail --silent --show-error -X POST -H 'Content-Type: application/json' -H 'X-Local-Principal: tenant-admin-acme' 'http://127.0.0.1:8000/admin/design-reviews/sessions' -d '{"tenant_id":"11111111-1111-1111-1111-111111111111","request_summary":"QA060 manual design review replay.","quorum_policy_key":"four_of_five_no_blockers","idempotency_key":"qa060-manual-create"}' > /tmp/qa060-manual-replay.json
```

Expected result: the response contains `"replayed":true` or equivalent JSON
spacing.

List Acme sessions.

```bash
curl --fail --silent --show-error -H 'X-Local-Principal: tenant-admin-acme' 'http://127.0.0.1:8000/admin/design-reviews/sessions?tenant_id=11111111-1111-1111-1111-111111111111' > /tmp/qa060-acme-sessions.json
```

Expected result: the response contains `items`.

Expected result: the response contains `QA060`.

List Globex sessions.

```bash
curl --fail --silent --show-error -H 'X-Local-Principal: tenant-admin-globex' 'http://127.0.0.1:8000/admin/design-reviews/sessions?tenant_id=22222222-2222-2222-2222-222222222222' > /tmp/qa060-globex-sessions.json
```

Expected result: the response contains an empty state.

Try an Acme detail route as Globex.

Expected result: the response status is `403`.

Record a manual decision as Acme.

Expected result: the first manual decision returns `201`.

Expected result: the replay returns `200`.

Run the verifier.

```bash
uv run python scripts/qa/verify_design_review_qa060.py
```

Expected result: the verifier prints `Verified QA060 design review live-data persistence`.

Run Playwright.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/060-design-review-domain-foundation/validation.yml --start-processes
```

Expected result: the screenshot exists under `output/playwright/qa060_ui`.

## Expected Results

Acme can create a design review session.

Acme can replay the same create request.

Acme can list its sessions.

Acme can inspect a session detail response.

Acme can list session revisions.

Acme can list session rounds.

Acme can list manual decisions.

Acme can record a manual decision.

Platform admin can inspect Acme data with explicit tenant context.

Globex receives an empty state for Globex data.

Globex is denied when trying to read Acme data.

OpenAPI includes the design review route family.

The QA verifier finds sessions, revisions, rounds, assignments, verdicts,
quorum decisions, manual decisions, and handoffs.

Responses include safe summaries.

Responses include digests and artifact references where applicable.

Responses do not include raw secrets.

Responses do not include provider authorization headers.

Responses do not include raw prompts.

Responses do not include raw completions.

Responses do not include private channel messages.

Responses do not include raw external tool payloads.

## Evidence To Capture

Capture `/tmp/qa060-manual-create.json`.

Capture `/tmp/qa060-manual-replay.json`.

Capture `/tmp/qa060-acme-sessions.json`.

Capture `/tmp/qa060-globex-sessions.json`.

Capture the cross-tenant denial status.

Capture the verifier output.

Capture the Playwright screenshot path.

Capture the QA document validation result.

Capture the focused backend test result.

Capture the final curl-test run directory.

Capture any reviewer notes in `/tmp/qa060-ui-notes.md`.

## Security And Redaction Checks

Search the API captures for `Authorization:`.

Search the API captures for provider token patterns.

Search the API captures for private key markers.

Search the API captures for raw prompt wording.

Search the API captures for raw completion wording.

Search the API captures for raw tool payload wording.

Confirm the environment file uses `qa060/` secret references.

Confirm the environment file uses `.data/qa060-artifacts`.

Confirm no reviewer copied real credentials into evidence.

Expected result: every redaction check passes.

## Tenant Isolation Checks

Use Acme tenant id for Acme create, list, and detail routes.

Use Globex tenant id for Globex empty-state routes.

Use Globex principal against Acme tenant id to prove denial.

Use platform-admin with Acme tenant id to prove platform inspection.

Confirm Globex has zero design review sessions after seeding.

Confirm Acme records do not appear in Globex responses.

Confirm manual decisions are scoped to Acme.

Confirm verifier output reports no Globex sessions.

Expected result: cross-tenant access fails closed.

## Troubleshooting

If the API returns `401`, check local-principal authentication.

If the API returns `403`, check tenant id and principal pairing.

If the API returns `404`, check the session id belongs to the supplied tenant.

If the API returns `422`, check the JSON body for required fields.

If seed output is missing ids, rerun the seed script after migration.

If OpenAPI does not mention design reviews, confirm the router import in the app.

If the verifier fails on Globex records, reset the QA database.

If Playwright fails, inspect `/tmp/qa060-api.log`.

If quality checks fail, fix the reported file before continuing to Spec 061.

Expected result: reruns remain deterministic.
