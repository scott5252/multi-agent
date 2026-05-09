# QA071 UI Walkthrough: Prompt Profile Creation And Per-Agent Binding UI

## Goal
This walkthrough validates the browser-first experience for prompt and runtime profile binding inside the React Admin workflow builder.
It focuses on what a tenant admin can see and do without opening raw JSON.
It verifies that each agent role can show prompt readiness, profile readiness, and a safe binding status.
It verifies that prompt creation controls do not leak template text into role summaries, graph panels, screenshots, or mutation result messages.
It verifies that profile controls show safe routing and credential expectations without credential values.
It verifies desktop and mobile screenshots for the QA071 workflow setup journey.
The QA run uses `qa071`.
The QA environment file is `.env.qa071`.
The local browser login begins at `http://127.0.0.1:8000/auth/local-login`.

## How To Use This Guide
Run all commands from the repository root.
Use the QA071 environment only.
Do not run this walkthrough against shared development data.
Do not open a prompt draft edit page while collecting screenshot evidence.
Do not capture raw prompt template content in screenshots.
Do not copy prompt template text into reviewer notes.
Do not add real credentials to the local environment.
Use `tenant-admin-acme` for the positive browser journey.
Use `tenant-admin-globex` only for denial checks.
Save terminal and screenshot evidence under `/tmp/qa071-*` and `output/playwright/qa071_ui`.
If any Expected result fails, stop and inspect the server log before continuing.

## Environment Setup
```bash
cp specs/071-prompt-profile-creation-and-per-agent-binding-ui/.env.qa071 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa071 && createdb -U postgres multi_agent_platform_qa071'
uv run alembic upgrade head
uv run python scripts/qa/seed_workflow_prompt_profile_qa071.py
```
Expected: the seed prints `workflow_draft_id=71717171-6669-4671-8671-000000000071`.
What is happening: the database is reset and populated with a workflow draft, prompt version, runtime profile version, and a mixed binding matrix.
Why this matters: the browser journey starts from known complete, incomplete, and blocked role states.

```bash
mkdir -p /tmp/qa071-ui
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000 > /tmp/qa071-ui/server.log 2>&1 &
sleep 2
curl --fail --silent http://127.0.0.1:8000/health/live
```
Expected: the health check succeeds.
What is happening: the local FastAPI server is serving React Admin and JSON APIs.
Why this matters: Playwright and manual browser checks must hit the same local application.

```bash
curl --fail --silent \
  -H "X-Local-Principal: tenant-admin-acme" \
  "http://127.0.0.1:8000/admin/app/workflows/drafts/71717171-6669-4671-8671-000000000071/detail.json?tenant_id=11111111-1111-1111-1111-111111111111" \
  | tee /tmp/qa071-ui/detail.json \
  | jq '.draft.name, .draft.document.roles[0].profile_reference_key'
```
Expected: the workflow name and `coordinator-binding` are printed.
What is happening: the seeded draft is readable by the Acme tenant admin.
Why this matters: the page should open directly to a durable draft, not an empty state.

## Browser Walkthrough
Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows`.
Expected: the local-principal chooser is displayed.
What is happening: the app is waiting for a deterministic local identity.
Why this matters: QA071 avoids real Auth0 and remains repeatable.

Choose `tenant-admin-acme`.
Expected: the React Admin shell loads and the workflow page opens.
What is happening: the local principal cookie is set and the active tenant is Acme.
Why this matters: prompt/profile data must be tenant-scoped.

Find `QA071 Prompt Profile Builder` in the registry or page header.
Expected: the workflow is visible without manually entering a draft ID.
What is happening: the builder selected the seeded active draft.
Why this matters: the common workflow landing page supports the feature.

Scroll to `Per-Agent Bindings`.
Expected: `Binding Matrix` and `Role Binding Controls` are visible.
What is happening: role-level prompt/profile controls are rendered as first-class UI.
Why this matters: users should not use raw JSON to bind prompts or profiles.

Review the top readiness badge.
Expected: `1/3 ready` is visible before any edits.
What is happening: Coordinator is fully bound, Research has only a prompt, and Review is incomplete.
Why this matters: mixed readiness states are understandable at a glance.

Review the Coordinator row.
Expected: the Prompt and Profile fields show `coordinator-binding`.
What is happening: the role reads safe reference keys from the workflow document.
Why this matters: the UI displays safe references, not raw prompt content.

Review the Research agent row.
Expected: the Prompt field shows `coordinator-binding` and the Profile field shows `Missing`.
What is happening: the matrix highlights an incomplete role.
Why this matters: users can recover incomplete bindings before publishing.

Review the Review agent row.
Expected: the row shows missing prompt and profile values.
What is happening: the matrix highlights a blocked role.
Why this matters: blocked roles should be visible before validation or publish attempts.

In Role Binding Controls, select `Research agent`.
Expected: the controls remain focused on prompt and runtime profile options.
What is happening: the selected role changes without leaving the page.
Why this matters: per-agent binding should be fast and local to the workflow builder.

Click `Activate profile reference`.
Expected: the badge changes to `2/3 ready`.
What is happening: the Research agent receives a safe profile reference.
Why this matters: profile activation can be represented in the workflow document as safe metadata.

Click `Publish prompt reference`.
Expected: the Research agent keeps a safe prompt reference and no prompt body appears.
What is happening: the UI creates or selects a prompt reference key.
Why this matters: prompt authoring controls must not leak template content into workflow summaries.

Click `Save draft`.
Expected: `Draft saved` appears.
What is happening: the browser posts the complete workflow document through the backend-owned save route.
Why this matters: persistence, idempotency, validation, and audit summaries remain server-owned.

Reload the page.
Expected: `2/3 ready` remains visible.
What is happening: the saved workflow document is loaded again from the repository.
Why this matters: the binding matrix reflects durable state, not transient component state.

Scroll to `Workflow structure`.
Expected: the graph summary mentions prompt/profile binding counts and no prompt template text appears.
What is happening: graph panels summarize binding readiness without sensitive content.
Why this matters: users can inspect topology without seeing raw prompt bodies.

Scroll to `Backend-owned findings`.
Expected: validation findings, if present, link to visible workflow sections and show safe field paths.
What is happening: validation output remains recoverable and redacted.
Why this matters: users need to fix binding blockers without seeing private content.

Open the page at a mobile viewport.
Expected: the binding matrix and controls stack in one column without overlapping text.
What is happening: responsive layout constrains the workflow editor panels.
Why this matters: browser-first QA requires desktop and mobile usability.

## Required Automated Evidence
```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
cd frontend/admin && npm test -- workflowPromptProfileBinding WorkflowBuilderPage
cd frontend/admin && npm run typecheck
cd frontend/admin && npm run build
```
Expected: generated types, focused tests, TypeScript, and build all pass.
What is happening: frontend contracts and component behavior are validated.
Why this matters: UI evidence should not depend on stale generated types or broken builds.

```bash
uv run pytest tests/contract/test_admin_react_contract.py tests/contract/test_workflow_builder_contract.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_workflow_builder_service.py tests/unit/admin/test_workflow_registry_service.py -q --no-cov
```
Expected: focused backend and contract tests pass.
What is happening: workflow, prompt/profile lookup, save, and route protections are checked.
Why this matters: the UI depends on backend-owned authorization and validation.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```
Expected: repository lint, format, typing, and coverage gates pass.
What is happening: QA071 is validated against the broader Python quality gates.
Why this matters: browser behavior should not mask backend regressions.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/071-prompt-profile-creation-and-per-agent-binding-ui
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/071-prompt-profile-creation-and-per-agent-binding-ui/validation.yml
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/071-prompt-profile-creation-and-per-agent-binding-ui/validation.yml --start-processes
```
Expected: QA docs, Spec QA, and Playwright validation pass.
What is happening: the formal validation manifest runs setup, seed, quality checks, and browser flows.
Why this matters: acceptance evidence is reproducible from one source of truth.

## UI Evidence Checklist
Capture `output/playwright/qa071_ui/qa071-prompt-profile-binding-desktop.png`.
Capture `output/playwright/qa071_ui/qa071-prompt-profile-binding-mobile.png`.
Record that `QA071 Prompt Profile Builder` is visible.
Record that `Per-Agent Bindings` is visible.
Record that `Binding Matrix` is visible.
Record that `Role Binding Controls` is visible.
Record that `Runtime Profile` is visible.
Record that the readiness badge reaches `2/3 ready`.
Record that `Draft saved` is visible after save.
Record that the graph panel does not display raw prompt template content.
Record that screenshots do not include secrets, credentials, provider payloads, private messages, raw completions, raw tool payloads, stack traces, or local filesystem paths.
Expected: every evidence item is visible and redaction-safe.
What is happening: reviewer evidence proves the feature without exposing protected content.
Why this matters: QA071 is explicitly about safe binding authoring.

## Acceptance Notes Template
QA run ID: `qa071`.
Environment file: `specs/071-prompt-profile-creation-and-per-agent-binding-ui/.env.qa071`.
Seed command: `uv run python scripts/qa/seed_workflow_prompt_profile_qa071.py`.
Workflow draft: `71717171-6669-4671-8671-000000000071`.
Prompt lineage: `71717171-1000-4671-8671-000000000071`.
Prompt version: `71717171-1004-4671-8671-000000000071`.
Profile: `71717171-2000-4671-8671-000000000071`.
Profile version: `71717171-2004-4671-8671-000000000071`.
Desktop screenshot: `output/playwright/qa071_ui/qa071-prompt-profile-binding-desktop.png`.
Mobile screenshot: `output/playwright/qa071_ui/qa071-prompt-profile-binding-mobile.png`.
Focused frontend result: recorded under `/tmp/qa071-*`.
Focused backend result: recorded under `/tmp/qa071-*`.
Spec QA result: recorded under `/tmp/qa071-*`.
Curl regression result: `.data/curl_test_runs/qa071-after-spec`.
Expected: the notes identify all deterministic evidence needed for review.
What is happening: review data is summarized without copying raw API payloads into the PR.
Why this matters: review remains fast and safe.

## Troubleshooting
If local login does not show `tenant-admin-acme`, confirm `.env.qa071` is copied to `.env`.
If the workflow is missing, rerun the QA071 seed command after migrations.
If the page shows an empty workflow state, open `/admin/app/workflows?workflow_draft_id=71717171-6669-4671-8671-000000000071`.
If the prompt select is empty, call the lookups API with the workflow draft ID.
If the profile select is empty, confirm the seeded document contains `coordinator-binding`.
If `Activate profile reference` does not change readiness, confirm `Research agent` is selected.
If `Draft saved` does not appear, inspect `/tmp/qa071-ui/server.log`.
If the browser shows a stack trace, treat it as a QA failure and save only the safe error category.
If mobile text overlaps, capture the screenshot and inspect `frontend/admin/src/styles/admin.css`.
If Playwright screenshots include raw prompt template text, close the prompt details disclosure and rerun the flow.
If validation reports blocked references after save, confirm the generated profile reference uses readiness `ready`.
If `npm run build` changes static assets, rerun the Playwright flow against the rebuilt assets.

## Related Files
`specs/071-prompt-profile-creation-and-per-agent-binding-ui/qa071.md`
`specs/071-prompt-profile-creation-and-per-agent-binding-ui/qa071_user_guide.md`
`specs/071-prompt-profile-creation-and-per-agent-binding-ui/.env.qa071`
`specs/_autopilot/workflow-setup-roadmap/071-prompt-profile-creation-and-per-agent-binding-ui/validation.yml`
`scripts/qa/seed_workflow_prompt_profile_qa071.py`
`frontend/admin/src/components/workflows/WorkflowPromptProfileBinder.tsx`
`frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
`frontend/admin/src/components/workflows/workflowPromptProfileBinding.ts`
`src/multi_agent_platform/admin/workflow_registry/reference_validation.py`
