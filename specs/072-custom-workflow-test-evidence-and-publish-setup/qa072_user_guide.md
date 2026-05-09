# QA072 User Guide: Spec 072 - Custom Workflow Test Evidence And Publish Setup

## Detailed Overview
QA072 adds required publish evidence setup to the React Admin workflow builder.
The feature helps tenant admins attach Test Bench suites to a workflow draft.
The feature helps tenant admins add a safe deterministic test case.
The feature helps tenant admins launch a safe deterministic evidence run.
The feature helps tenant admins see whether required evidence is current, stale, missing, failed, or blocked.
The feature keeps the backend in charge of publish readiness.
The feature keeps Test Bench tables as the source of truth.
The workflow document stores safe requirement references.
The workflow document does not store protected run payloads.
The workflow document does not store protected prompt content.
The workflow document does not store provider authorization headers.
The workflow document does not store credentials.
The workflow document does not store external tool payloads.
The workflow document does not store private channel messages.
The workflow document does not store local filesystem paths.
The workflow document does not store stack traces.
The workflow builder shows only safe summaries.
The workflow builder shows opaque suite IDs and run IDs when needed.
The workflow builder links reviewers to the Test Bench workspace.
The publish panel links evidence blockers back to the evidence setup section.
The validation panel links evidence findings back to the evidence setup section.
The seeded Acme workflow is `QA072 Workflow Test Evidence`.
The seeded Acme workflow draft ID is `72727272-6669-4672-8672-000000000072`.
The seeded workflow revision ID is `72727272-3333-4672-8672-000000000072`.
The seeded current suite ID is `72727272-4000-4672-8672-000000000072`.
The seeded current run ID is `72727272-4003-4672-8672-000000000072`.
The seeded stale suite ID is `72727272-4100-4672-8672-000000000072`.
The seeded failed suite ID is `72727272-4200-4672-8672-000000000072`.
The Acme tenant ID is `11111111-1111-1111-1111-111111111111`.
The Globex tenant ID is `22222222-2222-2222-2222-222222222222`.
The positive reviewer account is `tenant-admin-acme`.
The cross-tenant reviewer account is `tenant-admin-globex`.
The expected first evidence status is ready.
The expected current evidence count is one.
The expected stale evidence count in the workflow requirement summary is zero.
The expected missing evidence count in the workflow requirement summary is zero.
The seeded stale suite remains available in Test Bench for negative review.
The seeded failed suite remains available in Test Bench for negative review.
The browser should never claim stale or failed evidence is current.

## Who Should Use This Guide
Use this guide if you are manually reviewing workflow setup.
Use this guide if you are checking release readiness.
Use this guide if you are validating screenshots for QA072.
Use this guide if you are checking redaction behavior.
Use this guide if you are checking tenant isolation.
Use this guide if you are not editing code but need to verify the feature.
Use this guide if you need plain-language expected outcomes.
Use this guide after the implementation branch has been built locally.
Do not use this guide for production data.
Do not use this guide with real credentials.
Do not use this guide with live provider probes.
Do not use this guide with live Telegram delivery.
Do not use this guide with external connector side effects.

## Manual QA Prerequisites
Confirm Docker is running.
Confirm PostgreSQL can start through Docker Compose.
Confirm `uv` is installed.
Confirm Node.js satisfies the repository version requirement.
Confirm browser access to `http://127.0.0.1:8000` works.
Confirm you are on the QA072 branch or a branch containing QA072 changes.
Confirm no important local `.env` changes will be lost before copying `.env.qa072`.
Confirm you can run `uv sync`.
Confirm you can run `cd frontend/admin && npm ci`.
Confirm you can run Playwright locally if screenshots are required.
Confirm you can save notes under `/tmp/qa072-*`.
Confirm the repository has no production secrets in the QA environment file.

## Step-by-Step Manual QA
1. Copy `specs/072-custom-workflow-test-evidence-and-publish-setup/.env.qa072` to `.env`.
2. Run `uv sync`.
3. Start PostgreSQL with `docker compose up -d postgres`.
4. Drop and recreate `multi_agent_platform_qa072`.
5. Run `uv run alembic upgrade head`.
6. Run `uv run python scripts/qa/seed_workflow_test_evidence_qa072.py`.
7. Confirm the seed prints `workflow_draft_id=72727272-6669-4672-8672-000000000072`.
8. Confirm the seed prints `current_suite_id=72727272-4000-4672-8672-000000000072`.
9. Confirm the seed prints `current_run_id=72727272-4003-4672-8672-000000000072`.
10. Confirm the seed prints the stale suite ID.
11. Confirm the seed prints the failed suite ID.
12. Start the API with `uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000`.
13. Visit `http://127.0.0.1:8000/health/live`.
14. Confirm the health endpoint returns success.
15. Visit `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows`.
16. Choose `tenant-admin-acme`.
17. Confirm the React Admin shell loads.
18. Confirm the Workflows area is visible.
19. Confirm `QA072 Workflow Test Evidence` appears.
20. Open the QA072 workflow builder.
21. Scroll to `Required publish evidence`.
22. Confirm the evidence panel is visible.
23. Confirm the evidence panel readiness badge says `ready`.
24. Confirm the summary says one current evidence item.
25. Confirm `daily-briefing-required-suite` appears.
26. Confirm the safe evidence summary appears.
27. Confirm the current suite ID appears as an opaque reference.
28. Confirm the current run ID appears as an opaque reference.
29. Open the authorized suite selector.
30. Confirm the current suite option is visible.
31. Click `Attach suite`.
32. Confirm the requirement is not duplicated.
33. Click `Add safe case`.
34. Confirm a safe case mutation result appears.
35. Confirm the mutation result text is safe.
36. Click `Launch deterministic run`.
37. Confirm a run mutation result appears.
38. Confirm no protected transcript appears.
39. Confirm no provider payload appears.
40. Confirm no tool payload appears.
41. Confirm no credential value appears.
42. Confirm no local filesystem path appears.
43. Click `Clear run result`.
44. Confirm the run result card disappears.
45. Scroll to the publish readiness panel.
46. Confirm `Required test evidence` appears.
47. Confirm the publish panel includes `Review evidence setup`.
48. Click `Review evidence setup`.
49. Confirm focus or scroll returns to the evidence section.
50. Scroll to backend-owned findings.
51. Confirm evidence-related findings link to the evidence section when present.
52. Open `Open Agent Tests`.
53. Confirm the Test Bench workspace opens.
54. Open the current suite detail.
55. Confirm the current suite is required for publish.
56. Confirm the latest run status is passed.
57. Open the current run detail.
58. Confirm the current run targets the QA072 workflow revision.
59. Confirm the run steps show safe summaries.
60. Return to the workflow builder.
61. Resize the browser to a mobile viewport.
62. Confirm the evidence panel stacks cleanly.
63. Confirm buttons remain readable.
64. Confirm the selector remains readable.
65. Confirm text does not overlap.
66. Capture a desktop screenshot.
67. Capture a mobile screenshot.
68. Open a separate request as `tenant-admin-globex`.
69. Attempt to load the Acme workflow draft detail.
70. Confirm the response is denied.
71. Confirm the denied response does not include Acme workflow labels.
72. Confirm the denied response does not include Acme suite IDs.
73. Run the focused frontend workflow evidence tests.
74. Run the focused backend workflow evidence tests.
75. Run generated type freshness.
76. Run Ruff check.
77. Run Ruff format check.
78. Run mypy.
79. Run frontend build.
80. Run QA docs validation.
81. Run Spec QA.
82. Run Playwright validation.
83. Run the multi-agent curl regression.
84. Save review notes under `/tmp/qa072-review-notes.txt`.
85. Save API snippets under `/tmp/qa072-api`.
86. Keep screenshots under `output/playwright/qa072_ui`.

## Expected Results
Expected: `.env.qa072` uses local-principal authentication.
Expected: `.env.qa072` uses database `multi_agent_platform_qa072`.
Expected: `.env.qa072` uses `.data/qa072-artifacts`.
Expected: `.env.qa072` uses `qa072/` fake static secret references.
Expected: live provider probes are disabled.
Expected: live Telegram delivery is disabled.
Expected: external connectors are disabled.
Expected: the seed command creates the QA072 workflow draft.
Expected: the seed command creates the current suite.
Expected: the seed command creates the current run.
Expected: the seed command creates a stale suite.
Expected: the seed command creates a failed suite.
Expected: the workflow builder loads for `tenant-admin-acme`.
Expected: the workflow builder is denied to `tenant-admin-globex`.
Expected: `QA072 Workflow Test Evidence` is visible.
Expected: `Required publish evidence` is visible.
Expected: `daily-briefing-required-suite` is visible.
Expected: current evidence is ready.
Expected: the current suite is required for publish.
Expected: the current run status is passed.
Expected: the current run revision matches the QA072 workflow revision.
Expected: stale evidence remains distinguishable from current evidence.
Expected: failed evidence remains distinguishable from passing evidence.
Expected: the evidence panel does not duplicate an already attached suite.
Expected: the safe case action uses deterministic safe fixtures.
Expected: the launch action uses safe mode.
Expected: the publish panel links back to the evidence section.
Expected: validation findings for test requirements link back to the evidence section.
Expected: no protected prompt content appears.
Expected: no completion content appears.
Expected: no credential appears.
Expected: no provider authorization header appears.
Expected: no external tool payload appears.
Expected: no private channel payload appears.
Expected: no local filesystem path appears.
Expected: no stack trace appears.
Expected: no unauthorized tenant label appears.
Expected: desktop screenshot exists.
Expected: mobile screenshot exists.
Expected: focused frontend tests pass.
Expected: focused backend tests pass.
Expected: generated React types are fresh.
Expected: Ruff check passes.
Expected: Ruff format check passes.
Expected: mypy passes.
Expected: frontend build passes.
Expected: QA docs validation passes.
Expected: Spec QA passes.
Expected: Playwright validation passes.
Expected: multi-agent curl regression passes.

## Evidence To Capture
Capture `/tmp/qa072-api/health-live.json`.
Capture `/tmp/qa072-detail.json` if you run API checks manually.
Capture `/tmp/qa072-current-suite.json` if you run Test Bench checks manually.
Capture `/tmp/qa072-current-run.json` if you run run checks manually.
Capture `/tmp/qa072-publish-gate.json` if you run publish gate checks manually.
Capture `/tmp/qa072-cross-tenant.json` for tenant isolation.
Capture `output/playwright/qa072_ui/qa072-workflow-test-evidence-desktop.png`.
Capture `output/playwright/qa072_ui/qa072-workflow-test-evidence-mobile.png`.
Capture focused frontend test output.
Capture focused backend test output.
Capture generated type freshness output.
Capture Ruff, format, and mypy output.
Capture frontend build output.
Capture QA docs validation output.
Capture Spec QA output.
Capture Playwright output.
Capture curl regression output under `.data/curl_test_runs/qa072-after-spec`.
Do not capture protected prompts.
Do not capture protected completions.
Do not capture credentials.
Do not capture provider headers.
Do not capture external tool payloads.
Do not capture local filesystem paths beyond repository-relative QA artifact paths.

## Security And Redaction Checks
Check the workflow evidence panel for protected content.
Check mutation result cards for protected content.
Check publish readiness cards for protected content.
Check validation findings for protected content.
Check Test Bench suite details for protected content.
Check Test Bench run details for protected content.
Check screenshots for protected content.
Check API denial bodies for protected content.
Protected prompts must not appear.
Protected completions must not appear.
Credentials must not appear.
Provider authorization headers must not appear.
External tool payloads must not appear.
Private channel payloads must not appear.
Unauthorized tenant labels must not appear.
Local filesystem paths must not appear.
Stack traces must not appear.
If protected content appears, mark QA072 failed and discard the affected evidence.

## Tenant Isolation Checks
Use `tenant-admin-acme` for normal workflow setup.
Use `tenant-admin-globex` for denial checks.
Load the Acme workflow detail with the Globex principal.
Confirm the HTTP response is 403.
Confirm the body does not include `QA072 Workflow Test Evidence`.
Confirm the body does not include `daily-briefing-required-suite`.
Confirm the body does not include `72727272-4000`.
Load the current suite detail with the Globex principal.
Confirm the response is denied or not found.
Confirm no Acme-safe summary leaks through the denial response.
Do not treat a safe generic error message as a failure.
Do treat Acme labels in a Globex response as a failure.

## Troubleshooting
If the login page does not appear, confirm the API process is listening on port 8000.
If local principals are missing, confirm `.env.qa072` was copied to `.env`.
If the workflow list is empty, rerun the QA072 seed command.
If the evidence panel is missing, rebuild React assets.
If the current suite option is missing, reload the workflow builder with the QA072 draft ID.
If run launch fails, confirm the Acme principal has `agent-tests:run`.
If suite creation fails, confirm the Acme principal has `agent-tests:manage`.
If publish readiness is blocked by validation, rerun the seed command.
If publish readiness is blocked by missing evidence, confirm the current suite ID matches the workflow document.
If publish readiness is stale, confirm the current run target revision matches the workflow revision ID.
If protected content appears, stop and rerun from a clean database.
If mobile layout overlaps, inspect `frontend/admin/src/styles/admin.css`.
If Playwright fails, open the page manually and confirm visible text.
If Docker is stopped, start Docker and rerun setup.
If PostgreSQL has stale data, drop and recreate `multi_agent_platform_qa072`.
If Python dependencies are missing, rerun `uv sync`.
If Node dependencies are missing, run `cd frontend/admin && npm ci`.
If the curl regression fails, inspect `.data/curl_test_runs/qa072-after-spec`.

## Related Evidence
QA guide: `specs/072-custom-workflow-test-evidence-and-publish-setup/qa072.md`.
UI walkthrough: `specs/072-custom-workflow-test-evidence-and-publish-setup/qa072_ui.md`.
Environment file: `specs/072-custom-workflow-test-evidence-and-publish-setup/.env.qa072`.
Validation manifest: `specs/_autopilot/workflow-setup-roadmap/072-custom-workflow-test-evidence-and-publish-setup/validation.yml`.
Seed script: `scripts/qa/seed_workflow_test_evidence_qa072.py`.
Evidence panel source: `frontend/admin/src/components/workflows/WorkflowTestEvidencePanel.tsx`.
Evidence helper source: `frontend/admin/src/components/workflows/workflowTestEvidence.ts`.
Desktop screenshot: `output/playwright/qa072_ui/qa072-workflow-test-evidence-desktop.png`.
Mobile screenshot: `output/playwright/qa072_ui/qa072-workflow-test-evidence-mobile.png`.
Curl output: `.data/curl_test_runs/qa072-after-spec`.
