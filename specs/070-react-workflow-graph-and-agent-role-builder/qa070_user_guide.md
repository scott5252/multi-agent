# QA070 User Guide: Spec 070 - React Workflow Graph And Agent Role Builder

## Detailed Overview
Spec 070 adds browser controls for the structure of a custom workflow.
The workflow builder now has sections for roles, contracts, graph topology, join policies, approval gates, subworkflow references, and graph layout.
The goal is to let authorized admins create and edit a multi-agent workflow without writing raw JSON.
The browser still sends a full workflow document to the backend save route.
The backend still owns validation, revision checks, tenant scope, idempotency, stale conflict behavior, audit summaries, and publish readiness.
The graph canvas is visual only.
The node, edge, join, approval, and subworkflow lists provide keyboard-readable equivalents.
Prompt and runtime profile creation are not part of this spec.
Test evidence setup is not part of this spec.
Publishing a complete workflow remains blocked until later specs add prompt/profile binding and evidence setup.

## Who Should Use This Guide
Use this guide if you are reviewing the workflow setup UI.
Use this guide if you are validating role and graph controls.
Use this guide if you are checking mobile layout screenshots.
Use this guide if you are checking tenant isolation.
Use this guide if you are checking redaction behavior.
You do not need to know the internal database schema.
You do not need to edit JSON.
You do not need production credentials.
You should be comfortable copying commands into a terminal.
You should save evidence paths when a check fails.

## Manual QA Prerequisites
Use a local checkout of the repository.
Use Docker with PostgreSQL available.
Use Python dependencies installed by `uv sync`.
Use Node dependencies installed by the validation runner or `npm ci`.
Use the QA070 environment file only for this pass.
Use local-principal login.
Use `tenant-admin-acme` for positive checks.
Use `tenant-admin-globex` for cross-tenant checks.
Do not use real provider credentials.
Do not enable live Telegram.
Do not enable external connectors.
Do not paste secrets into workflow fields.

```bash
cp specs/070-react-workflow-graph-and-agent-role-builder/.env.qa070 .env
uv sync
docker compose up -d postgres
docker compose exec -T postgres sh -c 'dropdb -U postgres --if-exists multi_agent_platform_qa070 && createdb -U postgres multi_agent_platform_qa070'
uv run alembic upgrade head
uv run python scripts/qa/seed_workflow_graph_role_builder_qa070.py
```

Expected: the seed command prints the QA070 workflow draft ID.

```bash
uv run uvicorn multi_agent_platform.api.main:app --host 127.0.0.1 --port 8000
```

Expected: the local API starts on port 8000.

## Step-by-Step Manual QA
Step 1: Open local login.
Use `http://127.0.0.1:8000/auth/local-login?redirect_to=/admin/app/workflows`.
Choose `tenant-admin-acme`.
Expected: Workflow Registry opens.

Step 2: Confirm the seeded workflow.
Look for `QA070 Graph Role Builder`.
Expected: the workflow appears under the Acme tenant scope.

Step 3: Review section status.
Look at the section rail.
Expected: sections for Metadata, Roles, References, Contracts, Graph, Joins, Approvals, Subworkflows, Tests, Annotations, and Publish are visible.

Step 4: Check metadata controls.
Change the Name field.
Expected: dirty state changes to Unsaved changes.

Step 5: Check role cards.
Review Coordinator, Research agent, and Review agent.
Expected: each card has editable key, name, kind, contract selectors, references, purpose, and responsibilities.

Step 6: Add a role.
Click Add role.
Expected: New agent appears.

Step 7: Check role actions.
Use move, duplicate, and delete icons on a safe role if needed.
Expected: controls are labeled and do not resize the layout unexpectedly.

Step 8: Check dependency warnings.
Review Coordinator.
Expected: visible warnings show graph node references.

Step 9: Check contract cards.
Review Request, Result, and Approval decision.
Expected: key, kind, schema type, producer, consumer, version, and notes fields are visible.

Step 10: Add a contract.
Click Add contract.
Expected: New contract appears.

Step 11: Check graph topology.
Review Entry node, Nodes, and Edges.
Expected: topology is editable through fields and selectors.

Step 12: Check layout controls.
Review X and Y fields on nodes.
Expected: layout fields are numeric and do not overlap other controls.

Step 13: Check join policy.
Review Evidence join.
Expected: strategy, inbound edges, required branches, quorum, timeout, failure behavior, and output contract fields are visible.

Step 14: Check approval gate.
Review Manager approval.
Expected: approver scope, role code, decision contract, resume behavior, and instructions fields are visible.

Step 15: Add subworkflow reference.
Click Add subworkflow.
Expected: New subworkflow appears with alias and version reference fields.

Step 16: Review graph canvas.
Scroll to Workflow structure.
Expected: canvas is nonblank.

Step 17: Review graph lists.
Read Nodes and Edges and joins lists.
Expected: labels match the canvas.

Step 18: Save.
Click Save draft.
Expected: Draft saved appears.

Step 19: Reload.
Reload the browser.
Expected: New agent remains visible.

Step 20: Validate.
Click Run validation.
Expected: backend-owned findings refresh safely.

Step 21: Simulate stale save.
Click Simulate stale save.
Expected: stale conflict recovery appears and does not expose raw payloads.

Step 22: Check mobile.
Resize to a narrow viewport.
Expected: controls become one column and remain usable.

Step 23: Check cross-tenant access.
Login as `tenant-admin-globex`.
Expected: Acme QA070 workflow labels are not visible.

Step 24: Check redaction.
Review visible text and screenshots.
Expected: no raw secrets, credentials, prompts, completions, provider payloads, tool payloads, transcripts, stack traces, or local filesystem paths appear.

## Expected Results
The workflow builder loads from durable seed data.
The role editor shows at least three roles.
The contract editor shows at least three contracts.
The graph topology editor shows role, join, approval, and terminal nodes.
The join editor shows quorum behavior.
The approval editor shows tenant-admin approval scope.
The subworkflow editor can add a safe reference placeholder.
The graph canvas is nonblank.
The graph lists are readable by keyboard users.
The Save draft action persists a new role after reload.
The stale save action shows safe recovery.
The validation panel uses backend-owned findings.
The Globex user cannot see Acme workflow data.
Screenshots do not contain protected material.

## Evidence To Capture
Capture the Workflow Registry screen.
Capture the Roles editor.
Capture the Contracts editor.
Capture the Graph Topology editor.
Capture the Joins and Approvals editor.
Capture the Workflow structure canvas.
Capture the mobile view.
Save `/tmp/qa070-detail.json`.
Save `/tmp/qa070-save.json`.
Save Playwright screenshots from `output/playwright/qa070_ui`.
Save curl test output from `.data/curl_test_runs/qa070-after-spec`.
Record any safe audit references shown by mutation results.

## Security And Redaction Checks
Never paste a real secret into the UI.
Never paste a real provider header into the UI.
Never paste private prompt content outside authorized prompt editing forms.
Search screenshots for `sk-`.
Search screenshots for `authorization`.
Search screenshots for `bearer`.
Search logs for `begin private key`.
Search logs for local filesystem home paths.
Expected: none of those strings appear.

## Tenant Isolation Checks
Use `tenant-admin-acme` for positive checks.
Use `tenant-admin-globex` for negative checks.
The Acme workflow should be visible only to Acme-scoped principals.
The Globex principal should not see QA070 workflow labels.
The Globex denied response should not name Acme records.
Expected: cross-tenant access fails closed.

## Troubleshooting
If the workflow is missing, rerun the seed script.
If login fails, check `.env.qa070`.
If the save button is disabled, check whether the page is still loading.
If save returns validation error, inspect the section link and field path.
If stale conflict appears unexpectedly, reload and retry.
If the graph is blank, confirm the node list is populated.
If mobile text overlaps, capture the screenshot and viewport.
If Playwright fails, run the browser steps manually.
If redaction checks fail, stop the QA pass.
If tenant isolation fails, stop the QA pass.
If tests fail, preserve terminal output.
