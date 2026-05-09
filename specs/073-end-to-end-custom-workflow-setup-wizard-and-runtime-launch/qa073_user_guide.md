# QA073 User Guide: Spec 073 - End-To-End Custom Workflow Setup Wizard And Runtime Launch

## Detailed Overview

This guide helps a manual QA reviewer validate the complete custom workflow setup path.
The feature is for tenant admins who want to configure their own multi-agent workflow in the browser.
The path begins in the Workflow Registry.
The path continues through the Workflow Builder.
The path uses visible controls instead of raw JSON editing.
The path creates a realistic three-agent workflow.
The path binds prompt and runtime profile references to every agent.
The path builds a graph with a join node.
The path creates required deterministic Test Bench evidence.
The path runs backend-owned validation.
The path publishes only after backend-owned gates pass.
The path then opens runtime launch and Design Reviews handoff surfaces.
The checklist is a guide, not a source of truth for publish readiness.
Backend validation remains the source of truth for workflow findings.
Backend Test Bench evidence remains the source of truth for required evidence.
Backend publish readiness remains the source of truth for publication.
The browser may summarize progress and link to sections.
The browser must not invent fake workflows.
The browser must not invent fake agents.
The browser must not invent fake prompts.
The browser must not invent fake runtime profiles.
The browser must not invent fake evidence.
The browser must not invent fake published bundles.
The browser must not expose raw prompts outside authorized edit forms.
The browser must not expose raw completions.
The browser must not expose raw test transcripts.
The browser must not expose credentials.
The browser must not expose provider authorization headers.
The browser must not expose local filesystem paths.
The browser must not expose stack traces.
The browser must not expose private channel payloads.
The browser must not expose memory contents.

## Who Should Use This Guide

Use this guide if you are validating Spec 073.
Use this guide if you need to test a clean-tenant workflow setup.
Use this guide if you are reviewing runtime launch handoff behavior.
Use this guide if you are reviewing Design Reviews workflow selection.
Use this guide if you are checking mobile layout.
Use this guide if you are checking redaction behavior.
Use this guide if you are checking tenant isolation.
Developers may also use the automated commands at the end of this guide.
Non-developer reviewers can follow the browser steps without writing API calls.
API calls are secondary validation only.

## Manual QA Prerequisites

Confirm Docker is running.
Confirm PostgreSQL is available through Docker Compose.
Confirm the repository is on the Spec 073 branch.
Confirm `.env.qa073` exists in this feature directory.
Copy `.env.qa073` to `.env`.
Run `uv sync` if dependencies are not current.
Run Alembic migrations against `multi_agent_platform_qa073`.
Start the FastAPI server on `127.0.0.1:8000`.
Open a browser that can access `http://127.0.0.1:8000`.
Use local-principal authentication.
Do not use real Auth0.
Do not use real Telegram delivery.
Do not use real provider credentials.
Do not use live external connector calls.
Do not paste secrets into the browser.
Do not paste raw prompts into summaries.
Do not paste private channel data into forms.
The expected tenant is Acme.
The expected local principal is `tenant-admin-acme`.
The isolation principal is `tenant-admin-globex`.

## Step-by-Step Manual QA

1. Open `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows`.
2. Select `tenant-admin-acme`.
3. Wait for the Admin shell to load.
4. Confirm the Workflows page is visible.
5. Confirm the Workflow Registry is visible.
6. Confirm a create action is visible.
7. Click `Create workflow`.
8. Wait for the create result.
9. Confirm the create result has an `Open draft` action.
10. Click `Open draft`.
11. Confirm the Workflow Builder opens.
12. Confirm `Custom workflow launch checklist` is visible.
13. Confirm the checklist shows progress as a percentage.
14. Confirm checklist steps include Metadata.
15. Confirm checklist steps include Agents.
16. Confirm checklist steps include Prompts And Profiles.
17. Confirm checklist steps include Graph.
18. Confirm checklist steps include Contracts.
19. Confirm checklist steps include Evidence.
20. Confirm checklist steps include Validation.
21. Confirm checklist steps include Publish.
22. Confirm checklist steps include Launch.
23. Click `Apply three-agent starter`.
24. Confirm the Roles section now includes three agent roles.
25. Confirm the roles include an intake coordinator.
26. Confirm the roles include a research agent.
27. Confirm the roles include a synthesis agent.
28. Confirm each role has prompt reference text.
29. Confirm each role has runtime profile reference text.
30. Confirm the Graph Topology section includes role nodes.
31. Confirm the Graph Topology section includes a join node.
32. Confirm the Joins section includes a join policy.
33. Confirm the Contracts section includes request and result contracts.
34. Click `Save draft`.
35. Confirm the save result is accepted.
36. Confirm the dirty state clears.
37. Navigate to the Evidence checklist step.
38. Confirm Required publish evidence is visible.
39. Click `Create suite` if no suite is attached.
40. Confirm suite creation returns a safe mutation result.
41. Click `Attach suite` if an authorized suite is available.
42. Click `Save draft` after the evidence requirement is attached.
43. Confirm save is accepted.
44. Click `Add safe case`.
45. Confirm the case result is accepted.
46. Click `Launch deterministic run`.
47. Confirm the run result is accepted.
48. Confirm no raw transcript is shown.
49. Confirm no local path is shown.
50. Click `Run validation`.
51. Confirm validation returns safe findings or a ready state.
52. If validation reports blockers, use the `Open section` links.
53. Resolve any missing section through visible controls.
54. Click `Mark evidence current` only after deterministic evidence exists.
55. Confirm validation is ready or has no blockers.
56. Navigate to the Publish checklist step.
57. Click `Check publish gate`.
58. Confirm missing evidence blocks publish if evidence is not ready.
59. Click `Prepare publish`.
60. Confirm a confirmation requirement appears when the gate is ready.
61. Click `Confirm publish`.
62. Confirm the publish result is accepted.
63. Confirm the published version panel appears after refresh.
64. Confirm the published graph panel appears after refresh.
65. Navigate to the Launch checklist step.
66. Click `Open runtime launch`.
67. Confirm the Run workspace opens.
68. Confirm the Workflow field is prefilled.
69. Confirm no run starts until `Start Run` is clicked.
70. Return to the Workflow Builder.
71. Click `Select in Design Reviews`.
72. Confirm the Design Reviews workspace opens.
73. Confirm the workflow selector contains the published custom workflow.
74. Confirm the workflow selector chooses the requested workflow when authorized.
75. Do not launch a live external review.
76. If launching a deterministic review round, confirm runtime graph link appears.
77. Open graph inspection from the workflow builder published graph section.
78. Confirm graph node summaries are readable.
79. Confirm graph edge summaries are readable.
80. Confirm mobile layout by resizing to about 390 by 920.
81. Confirm checklist cards stack.
82. Confirm buttons do not overlap.
83. Confirm long ids wrap.
84. Confirm evidence cards do not overflow.
85. Confirm publish blockers remain readable.
86. Confirm runtime handoff buttons wrap cleanly.
87. Capture desktop screenshot.
88. Capture mobile screenshot.

## Expected Results

The reviewer can create a workflow from the Workflows page.
The reviewer can open the created draft through a visible link.
The checklist appears near the top of the builder.
The checklist exposes a progressbar.
The starter action is visible.
The starter creates three editable roles.
The starter creates ready prompt references.
The starter creates ready profile references.
The starter creates contracts.
The starter creates nodes and edges.
The starter creates a join node.
The starter creates a join policy.
The save action persists the generated document.
Evidence setup remains in the workflow builder.
Evidence setup links to Agent Tests when needed.
Evidence launch uses deterministic mock mode.
Validation results are backend-owned.
Publish readiness is backend-owned.
Publish succeeds only after gates pass.
Runtime launch preselects the workflow id.
Design Reviews can select the published workflow.
Published graph evidence is readable.
Desktop layout has no overlap.
Mobile layout has no overlap.

## Evidence To Capture

Capture a screenshot of the checklist before starter application.
Capture a screenshot after starter application.
Capture a screenshot after evidence setup.
Capture a screenshot after validation.
Capture a screenshot after publish.
Capture a screenshot of runtime launch prefill.
Capture a screenshot of Design Reviews workflow selection.
Capture a screenshot of published graph evidence.
Record the workflow draft id if visible.
Record the published bundle id if visible.
Record the deterministic run id if visible.
Record whether publish blockers linked to evidence.
Record whether any layout overflow was observed.
Record whether any redaction issue was observed.

## Security And Redaction Checks

Search the page for `secret`.
Search the page for `token`.
Search the page for `authorization`.
Search the page for `password`.
Search the page for `raw prompt`.
Search the page for `raw transcript`.
Search the page for `stack trace`.
Search the page for `/Users/`.
Search the page for `postgresql://`.
Search the page for private channel content.
Confirm authorized prompt editor content is not copied into summaries.
Confirm generated checklist summaries do not expose prompt body text.
Confirm evidence cards show safe summaries only.
Confirm artifact ids are opaque references.
Confirm runtime launch query values are safe ids only.

## Tenant Isolation Checks

Log out or open a fresh session.
Log in as `tenant-admin-globex`.
Open the Acme workflow draft URL if you recorded it.
Confirm access is denied.
Open Workflows for Globex.
Confirm Acme workflow names are not visible.
Open Design Reviews for Globex.
Confirm Acme published workflow is not listed.
Open runtime launch with the Acme workflow id under Globex.
Confirm backend run start rejects unauthorized or unavailable workflow use if submitted.
Return to `tenant-admin-acme` for remaining QA.

## Troubleshooting

If local login fails, confirm `.env` uses `AUTH_MODE=local_principal`.
If Workflows fails to load, confirm FastAPI is running.
If the database is missing tenants, rerun the QA setup commands.
If save returns stale conflict, reload the draft and retry.
If evidence is stale, save the requirement first, then launch a deterministic run against the current revision.
If publish is blocked, inspect validation findings and evidence cards.
If runtime launch does not prefill, verify the link contains `workflow_id`.
If Design Reviews does not select the workflow, verify the workflow is published and authorized.
If screenshots show overlap, capture viewport size and browser zoom.
If raw unsafe text appears, stop validation and file a blocking issue.
If a real external provider call is attempted, stop validation and file a blocking issue.
If curl regression fails, keep the artifact directory and inspect the first failed command.
