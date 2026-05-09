# QA073 UI Walkthrough: End-To-End Custom Workflow Setup Wizard And Runtime Launch

## Goal

Prove the qa073 browser journey works end to end.
Prove the journey starts at local login.
Prove the journey uses visible links after login.
Prove the workflow setup checklist is visible.
Prove the starter creates a three-agent workflow.
Prove deterministic evidence can be created and launched.
Prove validation and publish are backend-owned.
Prove runtime launch and Design Reviews handoff are reachable.
Prove graph evidence is visible and readable.
Prove desktop and mobile layouts do not overlap.

## How To Use This Guide

Use this guide while running Playwright or manual browser QA.
Save screenshots under `output/playwright/qa073_ui`.
Save reviewer notes under `/tmp/qa073-ui-review-notes.md`.
Use `.env.qa073`.
Use local-principal login.
Use `tenant-admin-acme` for the main path.
Use `tenant-admin-globex` only for isolation checks.
Do not edit raw JSON.
Do not edit the browser URL after login for the primary flow.
What is happening: the reviewer is proving the browser experience, not only APIs.
Why this matters: users must be able to configure custom workflows without copied ids.

## Environment Setup

Copy the environment file.

```bash
cp specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/.env.qa073 .env
```

Prepare the database.

```bash
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa073 && createdb -U postgres multi_agent_platform_qa073'
uv run alembic upgrade head
```

Run core quality before browser review.

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Run frontend checks before browser review.

```bash
cd frontend/admin && npm test -- workflowSetupWizard WorkflowBuilderPage UserRunPage DesignReviewWorkspacePage
npm run typecheck
npm test
npm run build
cd ../..
```

Expected: all commands pass before screenshots are accepted.
Expected: no command uses production credentials.

## Browser Walkthrough

Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows`.
What is happening: the local login page is setting the qa073 principal.
Why this matters: Auth0 is not required for deterministic local QA.
Select `tenant-admin-acme`.
Expected: the Admin shell opens to Workflows.
Expected: Workflow Registry is visible.
Click `Create draft`.
What is happening: the browser posts to the existing workflow create route.
Why this matters: the draft is durable backend state.
Expected: a workflow draft created result appears.
Click `Open draft`.
Expected: the Workflow Builder opens.
Expected: `Custom workflow launch checklist` is visible.
Expected: a progressbar is visible.
Click `Apply three-agent starter`.
What is happening: the visible setup action updates the editable document.
Why this matters: clean tenants need a fast path without fake backend data.
Expected: the checklist reports three agent roles.
Expected: role editor cards are visible.
Expected: prompt/profile binding section is visible.
Expected: graph topology section is visible.
Expected: contracts section is visible.
Click `Save draft`.
What is happening: the full document is persisted through the backend save contract.
Why this matters: setup state must survive reloads.
Expected: save result is accepted.
Click `Create suite`.
What is happening: Test Bench suite creation is launched in safe mock mode.
Why this matters: publish evidence must be durable and tenant-scoped.
Expected: Suite result appears.
Click `Save draft`.
Expected: the evidence requirement is persisted.
Click `Add safe case`.
Expected: Case result appears.
Click `Launch deterministic run`.
Expected: Run result appears.
Click `Run validation`.
What is happening: backend validation evaluates graph, references, and evidence.
Why this matters: the browser checklist is not the publish authority.
Expected: Validation result appears.
Click `Prepare publish`.
Expected: confirmation required appears when ready.
Click `Confirm publish`.
Expected: Published version appears.
Expected: Published version communication appears.
Take screenshot `qa073-workflow-setup-desktop.png`.
Click `Select in Design Reviews`.
What is happening: the setup flow opens the existing Design Reviews workspace.
Why this matters: custom workflows must be selectable from supported review surfaces.
Expected: Design Reviews page appears.
Expected: workflow selector is visible.
Return to Workflows from the Admin shell or browser history.
Set viewport to 390 by 920.
Expected: checklist cards stack.
Expected: action links wrap.
Expected: evidence controls remain readable.
Expected: graph summaries remain readable.
Take screenshot `qa073-workflow-setup-mobile.png`.
Click `Open runtime launch`.
What is happening: the setup flow opens the retained user run workspace.
Why this matters: users need a launch path after publish.
Expected: Run workspace appears.
Expected: Start run form appears.
Expected: workflow field is prefilled.

## Required Automated Evidence

Run the Spec QA command.

```bash
uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/validation.yml
```

Run the Playwright command.

```bash
uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/validation.yml --start-processes
```

Run the curl regression.

```bash
uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa073-after-spec
```

Expected: Spec QA exits with code 0.
Expected: Playwright exits with code 0.
Expected: screenshots are written under `output/playwright/qa073_ui`.
Expected: curl regression exits with code 0.

## UI Evidence Checklist

Screenshot shows Workflow Registry.
Screenshot shows create result.
Screenshot shows checklist.
Screenshot shows three-agent starter result.
Screenshot shows roles.
Screenshot shows prompt/profile bindings.
Screenshot shows graph topology.
Screenshot shows evidence controls.
Screenshot shows validation result.
Screenshot shows publish result.
Screenshot shows published version graph.
Screenshot shows runtime launch page.
Screenshot shows Design Reviews page.
Screenshot shows mobile stacked checklist.
Expected: no text overlaps.
Expected: no button label is clipped.
Expected: no long id escapes its container.
Expected: no raw prompt appears in summaries.
Expected: no raw transcript appears.
Expected: no local filesystem path appears.
Expected: no credential appears.
Expected: no unauthorized tenant label appears.

## Acceptance Notes Template

Reviewer:
Date:
Branch:
Viewport desktop:
Viewport mobile:
Desktop screenshot:
Mobile screenshot:
Runtime screenshot:
Design Reviews screenshot:
Focused frontend result:
Spec QA result:
Playwright result:
Curl result:
Redaction issues:
Tenant isolation issues:
Layout issues:
What is happening: these notes preserve the QA decision trail.
Why this matters: reviewers can audit browser evidence without replaying every step.

## Troubleshooting

If login loops, verify `.env.qa073` is active.
If Workflows is empty, create a workflow from the visible create control.
If create fails, inspect `/tmp/qa073-api.log`.
If save is stale, reload the draft.
If evidence is missing, create a suite and save before launch.
If evidence is stale, launch a deterministic run after the latest save.
If publish is blocked, read the publish gate findings.
If Design Reviews does not show the workflow, confirm publish succeeded.
If runtime launch lacks prefill, inspect the link query in the browser status bar.
If mobile overlaps, record viewport size and screenshot.
If raw unsafe content appears, stop the QA run.
If an external call is attempted, stop the QA run.

## Related Files

`specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/qa073.md`
`specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/.env.qa073`
`frontend/admin/src/components/workflows/WorkflowSetupWizardPanel.tsx`
`frontend/admin/src/components/workflows/workflowSetupWizard.ts`
`frontend/admin/src/components/userRuns/UserRunPage.tsx`
`frontend/admin/src/components/designReviews/DesignReviewWorkspacePage.tsx`
`specs/_autopilot/workflow-setup-roadmap/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/validation.yml`
