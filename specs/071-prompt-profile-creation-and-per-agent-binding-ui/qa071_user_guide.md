# QA071 User Guide: Spec 071 - Prompt Profile Creation And Per-Agent Binding UI

## Detailed Overview
QA071 adds prompt/profile binding work to the React Admin workflow setup experience.
The feature gives tenant admins a visible way to connect role-level prompt references and runtime profile references.
The feature is intentionally centered inside the workflow builder instead of a separate raw JSON editor.
The workflow document remains the durable source of role binding state.
The backend remains the durable owner of save, validation, stale conflict, idempotent replay, authorization, and audit summaries.
The browser presents safe reference keys, readiness badges, and version labels.
The browser does not present raw prompt template content in workflow summaries.
The browser does not present raw prompt template content in graph panels.
The browser does not present raw prompt template content in mutation summaries.
The browser does not present raw prompt template content in validation finding lists.
The browser does not present credential values.
The browser does not present provider authorization headers.
The browser does not present private channel messages.
The browser does not present raw tool payloads.
The browser does not present raw completions.
The browser does not present memory contents.
The browser does not present local filesystem paths.
The browser does not present unauthorized tenant labels.
The QA071 seeded workflow is `QA071 Prompt Profile Builder`.
The QA071 seeded workflow draft ID is `71717171-6669-4671-8671-000000000071`.
The QA071 seeded prompt lineage ID is `71717171-1000-4671-8671-000000000071`.
The QA071 seeded prompt version ID is `71717171-1004-4671-8671-000000000071`.
The QA071 seeded runtime profile ID is `71717171-2000-4671-8671-000000000071`.
The QA071 seeded runtime profile version ID is `71717171-2004-4671-8671-000000000071`.
The QA071 Acme tenant ID is `11111111-1111-1111-1111-111111111111`.
The QA071 Globex tenant ID is `22222222-2222-2222-2222-222222222222`.
The QA071 workflow starts with three roles.
The Coordinator role starts ready.
The Research agent role starts incomplete.
The Review agent role starts blocked.
The intended manual journey moves Research agent to ready.
The intended manual journey leaves Review agent blocked.
That mixed state proves the matrix can show progress without hiding incomplete work.
The prompt editor disclosure exists for authoring.
The prompt editor disclosure should stay closed during screenshot capture.
The runtime profile controls show safe routing hints.
The runtime profile controls do not show credential values.
The generated prompt reference action produces a reference key.
The generated runtime profile reference action produces a reference key.
The save action posts the workflow document to the existing workflow save route.
The save response returns a safe mutation result.
The reload path proves the binding state is durable.
The mobile path proves the binding matrix and controls remain readable.
The backend validation path proves non-ready prompt/profile references can block publish readiness.
The cross-tenant path proves a Globex principal cannot read Acme workflow state.
The redaction path proves QA evidence stays safe for review.

## Step-by-Step Manual QA
1. Copy the QA071 environment file to the active local environment.
2. Run `uv sync`.
3. Start PostgreSQL with `docker compose up -d postgres`.
4. Drop and recreate `multi_agent_platform_qa071`.
5. Run `uv run alembic upgrade head`.
6. Run `uv run python scripts/qa/seed_workflow_prompt_profile_qa071.py`.
7. Confirm the seed prints the QA071 workflow draft ID.
8. Confirm the seed prints the QA071 prompt lineage ID.
9. Confirm the seed prints the QA071 prompt version ID.
10. Confirm the seed prints the QA071 runtime profile ID.
11. Confirm the seed prints the QA071 runtime profile version ID.
12. Start the API with `uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000`.
13. Visit `http://127.0.0.1:8000/health/live`.
14. Confirm the health endpoint succeeds.
15. Visit `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows`.
16. Choose `tenant-admin-acme`.
17. Confirm the React Admin shell loads.
18. Confirm the workflow page is visible.
19. Confirm `QA071 Prompt Profile Builder` appears.
20. Scroll to `Per-Agent Bindings`.
21. Confirm the section heading is visible.
22. Confirm `Binding Matrix` is visible.
23. Confirm `Role Binding Controls` is visible.
24. Confirm `Runtime Profile` is visible.
25. Confirm the readiness badge starts at `1/3 ready`.
26. Review the Coordinator row.
27. Confirm Coordinator shows a prompt reference.
28. Confirm Coordinator shows a profile reference.
29. Confirm Coordinator has a ready badge.
30. Review the Research agent row.
31. Confirm Research agent shows a prompt reference.
32. Confirm Research agent shows a missing profile.
33. Confirm Research agent is not ready.
34. Review the Review agent row.
35. Confirm Review agent shows missing prompt and profile values.
36. Confirm Review agent is blocked.
37. In Role Binding Controls, open the Role selector.
38. Select `Research agent`.
39. Confirm the selected role changes.
40. Confirm the prompt controls remain visible.
41. Confirm the runtime profile controls remain visible.
42. Click `Activate profile reference`.
43. Confirm the readiness badge changes to `2/3 ready`.
44. Click `Publish prompt reference`.
45. Confirm no raw prompt body appears after the click.
46. Confirm the Research agent row still uses safe reference keys.
47. Click `Save draft`.
48. Confirm `Draft saved` appears.
49. Confirm the mutation result does not show a raw prompt body.
50. Reload the page.
51. Confirm `2/3 ready` remains visible.
52. Scroll to `Roles`.
53. Confirm the profile reference fields include safe values.
54. Confirm the prompt reference fields include safe values.
55. Confirm `Use binding matrix` links are present near manual role fields.
56. Scroll to `Workflow structure`.
57. Confirm the graph summary includes prompt/profile binding counts.
58. Confirm the graph node summaries mention binding readiness safely.
59. Confirm no raw prompt body appears in the graph panel.
60. Scroll to `Backend-owned findings`.
61. Confirm validation findings show safe messages.
62. Confirm any finding links target visible workflow sections.
63. Confirm no stack trace appears.
64. Resize the browser to a narrow mobile viewport.
65. Confirm the binding matrix stacks in one column.
66. Confirm the controls stack in one column.
67. Confirm text does not overlap.
68. Confirm buttons remain readable.
69. Confirm `2/3 ready` remains visible.
70. Capture the desktop screenshot.
71. Capture the mobile screenshot.
72. Run the focused frontend tests.
73. Run the focused backend tests.
74. Run generated type freshness.
75. Run the QA docs validation command.
76. Run the Spec QA manifest.
77. Run the Playwright manifest.
78. Run the multi-agent curl regression.
79. Save evidence under `/tmp/qa071-*`.
80. Keep screenshots under `output/playwright/qa071_ui`.

## Expected Results
Expected: `.env.qa071` uses the QA071 database.
Expected: `.env.qa071` uses local-principal auth.
Expected: `.env.qa071` uses fake `qa071/` secret references.
Expected: the seed command creates the workflow draft.
Expected: the seed command creates the prompt lineage.
Expected: the seed command creates the prompt version.
Expected: the seed command creates the runtime profile.
Expected: the seed command creates the runtime profile version.
Expected: the workflow page loads for `tenant-admin-acme`.
Expected: the workflow page is denied to `tenant-admin-globex` for the Acme draft.
Expected: `QA071 Prompt Profile Builder` is visible.
Expected: `Per-Agent Bindings` is visible.
Expected: `Binding Matrix` is visible.
Expected: `Role Binding Controls` is visible.
Expected: `Runtime Profile` is visible.
Expected: `1/3 ready` is visible before editing.
Expected: `2/3 ready` is visible after activating the Research profile reference.
Expected: `Draft saved` is visible after save.
Expected: `2/3 ready` remains visible after reload.
Expected: the graph panel remains nonblank.
Expected: graph summaries mention binding readiness.
Expected: role fields include safe reference keys.
Expected: generated prompt references do not include prompt template content.
Expected: generated profile references do not include credential values.
Expected: the JSON inspector remains read-only and redacted.
Expected: validation findings show safe field paths and recovery text.
Expected: desktop screenshots show the binding matrix.
Expected: mobile screenshots show the stacked binding matrix.
Expected: screenshots do not contain raw prompt bodies.
Expected: screenshots do not contain secrets.
Expected: screenshots do not contain provider authorization headers.
Expected: screenshots do not contain local filesystem paths.
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

## Troubleshooting
If the local login page does not appear, confirm the server is running on port 8000.
If `tenant-admin-acme` is missing, confirm `.env.qa071` was copied to `.env`.
If the workflow page shows an empty state, rerun the QA071 seed command.
If the workflow page still shows an empty state, open `/admin/app/workflows?workflow_draft_id=71717171-6669-4671-8671-000000000071`.
If the prompt select is empty, call the lookups API with the workflow draft ID.
If the profile select is empty, confirm the workflow document contains `coordinator-binding`.
If the readiness badge does not change, confirm `Research agent` is selected before clicking `Activate profile reference`.
If the save button does not produce `Draft saved`, check the safe error message at the top of the page.
If the API server returns a validation error, inspect the field path and linked section.
If the API server returns a stale conflict, reload the draft and retry the action.
If the graph panel is blank, rerun the frontend build and reload the page.
If mobile layout overlaps, inspect the binding CSS in `frontend/admin/src/styles/admin.css`.
If screenshots show raw prompt content, close the prompt editor disclosure and recapture them.
If screenshots show a stack trace, treat the run as failed and inspect `/tmp/qa071-ui/server.log`.
If tests fail after static asset rebuild, rerun the generated type check and frontend tests.
If the curl regression fails, inspect `.data/curl_test_runs/qa071-after-spec`.
If Docker is not running, start Docker and rerun the validation command.
If PostgreSQL has stale local data, drop and recreate `multi_agent_platform_qa071`.
If a command cannot find Python, run it through `uv run python`.
If Node dependencies are stale, run `cd frontend/admin && npm ci`.
If reviewer evidence contains protected material, discard that evidence and rerun from a clean log directory.

## Related Evidence
Desktop screenshot: `output/playwright/qa071_ui/qa071-prompt-profile-binding-desktop.png`.
Mobile screenshot: `output/playwright/qa071_ui/qa071-prompt-profile-binding-mobile.png`.
QA guide: `specs/071-prompt-profile-creation-and-per-agent-binding-ui/qa071.md`.
UI guide: `specs/071-prompt-profile-creation-and-per-agent-binding-ui/qa071_ui.md`.
Validation manifest: `specs/_autopilot/workflow-setup-roadmap/071-prompt-profile-creation-and-per-agent-binding-ui/validation.yml`.
Seed script: `scripts/qa/seed_workflow_prompt_profile_qa071.py`.
Curl output: `.data/curl_test_runs/qa071-after-spec`.
