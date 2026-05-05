# QA033 UI Walkthrough

## Goal

QA033 UI validation proves the React test bench page renders safe suite authoring, target binding, run launch, progress, diagnostics, artifact metadata, publish gate evidence, and audit records.

The route under review is `/admin/app/test-bench`.

The browser should show the test bench as the first usable screen.

The browser should show sections for Suites, Runs, Results, Gates, and Audit.

The browser should show suite authoring controls.

The browser should show structured assertion metadata.

The browser should show safe execution mode choices.

The browser should show deterministic run status from the backend.

The browser should show assertion diagnostics and trace summaries.

The browser should show artifact references as metadata only.

The browser should show publish gate evidence states.

The browser should show bounded audit timeline records.

The browser should not show raw prompts, raw completions, raw transcripts, private messages, memory contents, credential values, authorization headers, provider tokens, connector request bodies, connector response bodies, raw tool outputs, stack traces, local paths, artifact storage paths, or unauthorized tenant labels.

Expected: screenshots show only safe summaries, checksums, audit references, and evidence references.

Expected: no screenshot contains `qa033-secret-value`.

Expected: no screenshot contains `Globex` when signed in as an Acme tenant admin.

## How To Use This Guide

Use a private browser window or a clean local browser profile.

Start from `.env.qa033`.

Capture screenshots when instructed.

Record reviewer notes for overlap, clipping, unclear focus, unsafe text, missing status context, or confusing tenant scope.

Do not paste real secrets into the browser.

Do not paste raw prompts, raw completions, connector payloads, tool outputs, private messages, stack traces, local paths, or cross-tenant labels into reviewer notes.

Expected: QA evidence can be shared with reviewers without cleanup.

Expected: every action is explicit and user initiated.

What is happening: the browser is exercising the same React route administrators use for test bench review.

Why this matters: UI validation catches layout, focus, and unsafe presentation issues that API tests cannot see.

## Environment Setup

Prepare the environment:

```bash
cp specs/033-react-agent-and-workflow-test-bench/.env.qa033 .env
uv sync
cd frontend/admin
npm install
npm run build
cd ../..
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa033 && createdb -U postgres multi_agent_platform_qa033'
uv run alembic upgrade head
docker compose exec -T postgres psql -U postgres -d multi_agent_platform_qa033 -v ON_ERROR_STOP=1 -c "INSERT INTO tenants (tenant_id, slug, display_name, status, created_at, updated_at) VALUES ('11111111-1111-1111-1111-111111111111', 'acme', 'Acme', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP), ('22222222-2222-2222-2222-222222222222', 'globex', 'Globex', 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) ON CONFLICT (slug) DO NOTHING"
mkdir -p .data/qa033-artifacts output/playwright/qa033_ui
```

Expected: database, React assets, and evidence folders are ready.

Start the API:

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Start the worker:

```bash
uv run python -m multi_agent_platform.workers.main
```

Expected: worker starts without live provider, Telegram, credential, or connector calls.

Open the local browser login page:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench
```

Expected: local login offers `platform-admin` and `tenant-admin-acme`.

## Required Automated Evidence

Run QA document validation:

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/033-react-agent-and-workflow-test-bench
```

Run backend quality gates:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Run frontend checks:

```bash
cd frontend/admin
npm run typecheck
npm run test
npm run build
cd ../..
```

Run full QA033 validation:

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/033-react-agent-and-workflow-test-bench/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/033-react-agent-and-workflow-test-bench/validation.yml --start-processes
```

Expected: all automated commands pass before screenshots are accepted.

What is happening: the QA033 manifest resets the database, builds assets, starts app processes, and captures screenshots.

Why this matters: manual observations should match automated evidence.

## Browser Walkthrough

### Step 1: Denied Test Bench Route

Open:

```text
http://127.0.0.1:8000/admin/app/test-bench
```

Expected: a 401 response appears when not logged in.

Expected: no suite, run, trace, artifact, gate, or audit data appears.

What is happening: the shell route is guarded before React data can render.

Why this matters: test bench metadata cannot leak anonymously.

Screenshot evidence: `output/playwright/qa033_ui/qa033-react-test-bench-denied.png`.

### Step 2: Tenant Login

Open:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench
```

Choose `tenant-admin-acme`.

Expected: the browser redirects to `/admin/app/test-bench`.

Expected: the shell shows `React Admin`.

Expected: the page heading says `Test Bench`.

Expected: the page shows `Release confidence`.

Expected: the page shows `Daily briefing release gate`.

Expected: the page shows `Reusable suites`.

What is happening: the tenant principal can see authorized test bench evidence.

Why this matters: suite and run metadata must be scoped to the active tenant.

Screenshot evidence: `output/playwright/qa033_ui/qa033-react-test-bench-tenant.png`.

### Step 3: Suite And Case Authoring

Click `Save suite`.

Expected: the page shows `audit-test-suite-save-qa033`.

Click `Save case`.

Expected: the page shows `audit-test-case-save-qa033`.

Expected: the page still shows structured assertion labels.

Expected: the page does not reveal raw fixture bodies.

What is happening: React posts safe suite and case descriptors to backend routes.

Why this matters: authoring decisions remain server validated and auditable.

Screenshot evidence: `output/playwright/qa033_ui/qa033-react-test-bench-authoring.png`.

### Step 4: Run Launch

Review the safe mode selector.

Expected: `Mock model and tools` is available.

Expected: `Side-effect-disabled gateway` is available.

Expected: live dependency probe text appears only as a denied local option.

Click `Launch run`.

Expected: the page shows `audit-test-run-launch-qa033`.

Expected: the page shows `Test run queued with backend-owned progress evidence`.

Expected: the page shows backend-owned progress and run status.

Expected: the page does not call real providers, Telegram, or external tools.

What is happening: React requests a run and renders the returned backend snapshot.

Why this matters: the browser must not decide pass or fail locally.

Screenshot evidence: `output/playwright/qa033_ui/qa033-react-test-bench-run.png`.

### Step 5: Result Details And Trace

Review `Run detail`.

Expected: the page shows `Blocked side-effect assertion failed`.

Expected: the page shows usage and latency summaries.

Expected: the page shows safe transcript excerpts only.

Expected: artifact rows show checksum, size, retention, redaction class, and access state.

What is happening: diagnostic details are server-owned summaries.

Why this matters: failures should be actionable without exposing raw runtime payloads.

Screenshot evidence: `output/playwright/qa033_ui/qa033-react-test-bench-result.png`.

### Step 6: Publish Gate Evidence

Review `Publish gate evidence`.

Expected: missing, stale, running, failing, passing, and unavailable states are understandable.

Expected: stale evidence points to the current target revision.

Click `Refresh evidence`.

Expected: the page shows `Publish-gate evidence is current for the selected target revision`.

Expected: remediation text is visible for stale or failing gate states.

What is happening: React asks the backend to refresh gate evidence for the current revision.

Why this matters: workflow publication must depend on current required evidence.

Screenshot evidence: `output/playwright/qa033_ui/qa033-react-test-bench-gates.png`.

### Step 7: Audit Timeline

Review `Audit timeline`.

Expected: lifecycle events show actor summaries, target summaries, outcomes, safe diffs, redaction class, and audit references.

Expected: denied access evidence is summarized without leaking resource details.

Expected: artifact retention and side-effect posture are visible as safe governance evidence.

What is happening: audit records are bounded and safe for reviewer inspection.

Why this matters: administrators need traceability without cross-tenant leakage.

Screenshot evidence: `output/playwright/qa033_ui/qa033-react-test-bench-audit.png`.

### Step 8: Cross-Tenant Review

Open local login again:

```text
http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/test-bench
```

Choose `tenant-admin-globex`.

Expected: Globex can only see its own scoped shell and safe fixture summaries.

Expected: an Acme screenshot must not show Globex data.

Expected: a Globex screenshot must not show Acme-only run or artifact details.

What is happening: active tenant scope controls every test bench contract.

Why this matters: test evidence can include sensitive operational context even when redacted.

Screenshot evidence: `output/playwright/qa033_ui/qa033-react-test-bench-cross-tenant.png`.

## UI Evidence Checklist

- Capture denied route evidence.
- Capture tenant dashboard evidence.
- Capture suite and case authoring evidence.
- Capture run launch evidence.
- Capture result detail evidence.
- Capture trace and artifact evidence.
- Capture publish gate evidence.
- Capture audit timeline evidence.
- Capture cross-tenant evidence.
- Confirm no screenshot contains `qa033-secret-value`.
- Confirm no Acme screenshot contains `Globex`.
- Confirm no screenshot contains local paths or artifact storage paths.
- Confirm buttons and selectors do not overlap on desktop.
- Confirm text fits inside cards and controls.
- Confirm keyboard focus remains visible on buttons and selectors.

## Acceptance Notes Template

Reviewer:

Date:

Branch:

QA database:

Browser:

Screenshots captured:

Unsafe text scan result:

Layout notes:

Authorization notes:

Tenant isolation notes:

Follow-up items:

## Troubleshooting

If local login is unavailable, confirm `AUTH_MODE=local_principal`.

If the page shows `Test bench unavailable`, confirm the API restarted after copying `.env.qa033`.

If screenshots are blank, rebuild React assets and refresh the browser.

If `Save suite` fails, verify the current revision token is `suite-rev-qa033-current`.

If `Launch run` returns a stale conflict, verify the current target revision is `workflow-draft-rev-qa033-current`.

If `Refresh evidence` returns a stale conflict, refresh the page and use the current target revision.

If a live dependency probe is denied, that is expected in local QA.

If a screenshot contains unsafe text, stop and file a regression.

Expected: troubleshooting remains local and deterministic.

Expected: troubleshooting does not require any live external dependency.

## Related Files

- `specs/033-react-agent-and-workflow-test-bench/qa033.md`
- `specs/033-react-agent-and-workflow-test-bench/qa033_user_guide.md`
- `specs/_autopilot/react-ui-roadmap/033-react-agent-and-workflow-test-bench/validation.yml`
- `frontend/admin/src/components/testBench/TestBenchPage.tsx`
- `frontend/admin/src/components/testBench/RunLauncherPanel.tsx`
- `frontend/admin/src/components/testBench/PublishGateEvidencePanel.tsx`
- `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
