# QA072 UI Walkthrough: Custom Workflow Test Evidence And Publish Setup

## Goal
This walkthrough proves the React Admin workflow builder gives tenant admins a browser-first way to inspect and operate required workflow evidence.
The evidence section must show current, stale, missing, failed, and blocked states through safe labels and backend-owned summaries.
The publish panel must link required evidence blockers back to the workflow evidence section.
The validation panel must link `test_requirements` findings back to the workflow evidence section.
The run launch action must call the existing Test Bench API.
The browser must never synthesize a passing result.
The browser must never expose protected prompts, completions, credentials, provider headers, private payloads, tool payloads, local paths, stack traces, or unauthorized tenant labels.
The seeded workflow draft is `72727272-6669-4672-8672-000000000072`.
The seeded current suite is `72727272-4000-4672-8672-000000000072`.
The seeded current run is `72727272-4003-4672-8672-000000000072`.

## How To Use This Guide
Use this guide after completing the QA072 environment setup.
Run commands from the repository root.
Keep one browser session for `tenant-admin-acme`.
Use a separate private session or API curl for `tenant-admin-globex`.
Capture screenshots under `output/playwright/qa072_ui`.
Capture reviewer notes under `/tmp/qa072-ui-review-notes.txt`.
Stop if protected material appears in the UI.
Stop if a cross-tenant page leaks Acme labels.
Do not use live provider modes during this walkthrough.
Do not paste protected evidence into notes.
Treat backend blockers as expected when evidence is stale or failed.
Treat current passing evidence as ready only when it references the current draft revision.

## Environment Setup
```bash
cp specs/072-custom-workflow-test-evidence-and-publish-setup/.env.qa072 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa072 && createdb -U postgres multi_agent_platform_qa072'
uv run alembic upgrade head
uv run python scripts/qa/seed_workflow_test_evidence_qa072.py
```
Expected: the seed prints the QA072 workflow draft ID and suite IDs.
What is happening: the local database is reset and deterministic workflow evidence records are created.
Why this matters: the UI is validated against persisted Test Bench state, not browser-only data.

```bash
mkdir -p /tmp/qa072-ui
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000 > /tmp/qa072-ui/server.log 2>&1 &
sleep 3
curl --fail --silent http://127.0.0.1:8000/health/live | tee /tmp/qa072-ui/health-live.json
```
Expected: the health command exits 0.
What is happening: the FastAPI app starts with React static assets enabled.
Why this matters: the browser checks use the same local server as manual reviewers.

```bash
cd frontend/admin && npm ci
cd ../..
```
Expected: frontend dependencies are installed.
What is happening: local React tooling is prepared for focused tests and rebuilds.
Why this matters: QA reviewers can reproduce browser behavior and automated UI checks.

## Browser Walkthrough
1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows`.
2. Select `tenant-admin-acme`.
3. Confirm the React Admin shell loads.
4. Confirm the Workflows navigation item is active.
5. Confirm `QA072 Workflow Test Evidence` appears in the workflow list.
6. Open the QA072 workflow if it is not already selected.
7. Confirm the builder header shows the workflow name.
8. Scroll to `Required publish evidence`.
9. Confirm the section has the `Test evidence` eyebrow.
10. Confirm the readiness badge says `ready`.
11. Confirm the summary says `1 current, 0 stale, 0 missing across 1 required evidence item`.
12. Confirm `daily-briefing-required-suite` appears.
13. Confirm the suite ID appears only as an opaque ID.
14. Confirm the result ID appears only as an opaque ID.
15. Confirm the safe summary says the deterministic evidence is passing.
16. Confirm no protected prompt or completion text appears.
17. Confirm no local filesystem path appears.
18. Confirm no stack trace appears.
19. Open the `Authorized suite` selector.
20. Confirm `daily-briefing-required-suite` is an option.
21. Click `Attach suite`.
22. Confirm no duplicate requirement card is added.
23. Click `Add safe case`.
24. Confirm a safe mutation result appears.
25. Confirm the mutation result does not include protected payload text.
26. Click `Launch deterministic run`.
27. Confirm a run result appears.
28. Confirm the run result status is accepted or success.
29. Confirm the requirement card remains safe.
30. Confirm the button text remains readable and does not shift layout.
31. Click `Clear run result`.
32. Confirm the run result card is removed.
33. Scroll to the publish panel.
34. Confirm `Required test evidence` appears in publish readiness.
35. Confirm `Review evidence setup` points to the evidence section.
36. Confirm publish blocker or readiness text is backend-owned.
37. Scroll to backend-owned findings.
38. Confirm any evidence finding link points to `#workflow-test-evidence`.
39. Open `Open Agent Tests`.
40. Confirm the Test Bench workspace opens.
41. Confirm the current suite appears.
42. Confirm safe run diagnostics appear.
43. Return to the workflow builder.
44. Resize the browser to a mobile-width viewport.
45. Confirm evidence cards stack in one column.
46. Confirm buttons remain readable.
47. Confirm select text fits its control.
48. Confirm cards do not nest inside other cards.
49. Confirm no text overlaps.
50. Capture the desktop screenshot.
51. Capture the mobile screenshot.
Expected: the UI presents current evidence, safe controls, and publish readiness without protected content.
What is happening: the workflow builder is using persisted Test Bench summaries and existing mutation APIs.
Why this matters: tenant admins can set up publish evidence without raw JSON editing or copying IDs.

## Desktop Screenshot
```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/072-custom-workflow-test-evidence-and-publish-setup/validation.yml --start-processes
```
Expected: `output/playwright/qa072_ui/qa072-workflow-test-evidence-desktop.png` exists.
Expected: `output/playwright/qa072_ui/qa072-workflow-test-evidence-mobile.png` exists.
What is happening: the manifest signs in, loads the seeded workflow, exercises evidence controls, and captures screenshots.
Why this matters: the screenshots become browser-first review evidence.

## Manual Desktop Checks
```bash
open output/playwright/qa072_ui/qa072-workflow-test-evidence-desktop.png
```
Expected: the desktop screenshot shows `QA072 Workflow Test Evidence`.
Expected: the desktop screenshot shows `Required publish evidence`.
Expected: the desktop screenshot shows the current evidence card.
Expected: the desktop screenshot shows no protected payload text.
What is happening: the desktop viewport captures the full workflow evidence panel.
Why this matters: reviewers can inspect the primary admin workflow.

## Manual Mobile Checks
```bash
open output/playwright/qa072_ui/qa072-workflow-test-evidence-mobile.png
```
Expected: the mobile screenshot shows `Required publish evidence`.
Expected: the evidence cards stack cleanly.
Expected: action buttons remain readable.
Expected: no labels overlap.
What is happening: the mobile viewport verifies responsive evidence controls.
Why this matters: the admin shell must remain usable on constrained screens.

## Required Automated Evidence
```bash
cd frontend/admin && npm test -- workflowTestEvidence WorkflowBuilderPage WorkflowPublishPanel WorkflowValidationPanel workflowDocumentEditor
```
Expected: focused workflow evidence tests pass.
What is happening: React tests verify helper redaction, panel behavior, publish links, validation links, and editor normalization.
Why this matters: browser behavior is covered without relying only on manual screenshots.

```bash
cd frontend/admin && npm run typecheck
```
Expected: TypeScript typecheck exits 0.
What is happening: UI code is checked against generated admin contracts.
Why this matters: evidence mutations and summaries must match backend-owned schemas.

```bash
uv run pytest tests/unit/admin/test_workflow_registry_service.py tests/unit/admin/test_workflow_builder_service.py tests/contract/test_workflow_builder_contract.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py -q --no-cov
```
Expected: focused backend and contract tests pass.
What is happening: publish gate and builder projections are checked outside the browser.
Why this matters: readiness remains backend-owned.

```bash
uv run python scripts/frontend/generate_admin_react_types.py --check
```
Expected: generated React types are fresh.
What is happening: contract generation verifies schema drift did not occur.
Why this matters: the frontend evidence panel must stay aligned with backend responses.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```
Expected: Ruff check, Ruff format check, and mypy pass.
What is happening: Python quality gates run across the repository.
Why this matters: QA072 cannot leave seed or backend changes in a low-confidence state.

```bash
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```
Expected: coverage passes at the required threshold.
What is happening: the full Python test suite validates the broader platform.
Why this matters: workflow setup changes touch shared admin, registry, and Test Bench surfaces.

```bash
cd frontend/admin && npm run build
```
Expected: the frontend build succeeds.
What is happening: production React assets are rebuilt.
Why this matters: FastAPI-served assets must match the implemented UI.

```bash
bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/072-custom-workflow-test-evidence-and-publish-setup
```
Expected: document validation passes.
What is happening: QA docs are checked for required evidence and reviewer guidance.
Why this matters: the feature can be handed to non-developer QA.

```bash
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa072-after-spec
```
Expected: the curl regression passes.
What is happening: existing route families are replayed after the UI feature lands.
Why this matters: the new workflow setup controls did not regress API behavior.

## UI Evidence Checklist
Expected: local login works for `tenant-admin-acme`.
Expected: the workflow list shows `QA072 Workflow Test Evidence`.
Expected: the evidence panel appears in the builder.
Expected: the evidence panel has a stable anchor `workflow-test-evidence`.
Expected: current evidence is displayed as ready.
Expected: stale and failed evidence are inspectable in Test Bench.
Expected: deterministic run launch uses safe mode.
Expected: unsupported live modes are not offered by the workflow evidence panel.
Expected: publish readiness text is backend-owned.
Expected: validation finding links target the evidence section.
Expected: no protected prompts appear.
Expected: no completions appear.
Expected: no credentials appear.
Expected: no provider headers appear.
Expected: no tool payloads appear.
Expected: no stack traces appear.
Expected: no local filesystem paths appear.
Expected: no unauthorized tenant labels appear.
Expected: desktop screenshot is captured.
Expected: mobile screenshot is captured.

## Security Review Notes
Review the evidence panel after launch.
Review the mutation result cards.
Review the publish panel.
Review the validation panel.
Review the Test Bench suite page.
Review the Test Bench run page.
Confirm protected content never appears.
Confirm all IDs are opaque references.
Confirm every external-looking link remains within authorized admin routes.
Confirm no browser field allows editing current evidence status directly.
Confirm failed evidence remains failed until a new deterministic run passes.
Confirm stale evidence remains stale when target revision differs.
Confirm cross-tenant access returns a safe denial.

## Acceptance Notes Template
Reviewer:
Date:
Desktop screenshot: `output/playwright/qa072_ui/qa072-workflow-test-evidence-desktop.png`
Mobile screenshot: `output/playwright/qa072_ui/qa072-workflow-test-evidence-mobile.png`
Workflow builder evidence panel: passed or failed
Test Bench suite link: passed or failed
Deterministic run launch: passed or failed
Publish evidence link: passed or failed
Validation evidence link: passed or failed
Redaction review: passed or failed
Tenant isolation review: passed or failed
Responsive layout review: passed or failed
Reviewer notes: `/tmp/qa072-ui-review-notes.txt`

## Troubleshooting
If login loops, clear the local principal cookie and revisit the login URL.
If the workflow page is empty, rerun the QA072 seed command.
If the evidence panel is absent, rebuild frontend assets.
If `Authorized suite` is empty, reload with the QA072 workflow draft ID in the URL.
If launch fails, confirm the Acme principal has `agent-tests:run`.
If suite creation fails, confirm the Acme principal has `agent-tests:manage`.
If publish readiness is blocked for validation, rerun the seed command.
If publish readiness is blocked for evidence, confirm the current suite ID and run ID match the seed output.
If mobile layout overlaps, inspect evidence grid CSS.
If screenshots show protected content, discard them and rerun from a clean database.
If Playwright fails on a selector, open the page manually and check visible text.
If Docker is unavailable, start Docker and rerun setup.
If Node dependencies are stale, run `cd frontend/admin && npm ci`.
If Python dependencies are stale, run `uv sync`.
If the curl regression fails, inspect `.data/curl_test_runs/qa072-after-spec`.

## Related Files
Feature guide: `specs/072-custom-workflow-test-evidence-and-publish-setup/qa072.md`.
Manual user guide: `specs/072-custom-workflow-test-evidence-and-publish-setup/qa072_user_guide.md`.
Environment: `specs/072-custom-workflow-test-evidence-and-publish-setup/.env.qa072`.
Validation manifest: `specs/_autopilot/workflow-setup-roadmap/072-custom-workflow-test-evidence-and-publish-setup/validation.yml`.
Seed script: `scripts/qa/seed_workflow_test_evidence_qa072.py`.
Evidence panel: `frontend/admin/src/components/workflows/WorkflowTestEvidencePanel.tsx`.
Evidence helper: `frontend/admin/src/components/workflows/workflowTestEvidence.ts`.
Publish panel: `frontend/admin/src/components/workflows/WorkflowPublishPanel.tsx`.
Validation panel: `frontend/admin/src/components/workflows/WorkflowValidationPanel.tsx`.
Style sheet: `frontend/admin/src/styles/admin.css`.
