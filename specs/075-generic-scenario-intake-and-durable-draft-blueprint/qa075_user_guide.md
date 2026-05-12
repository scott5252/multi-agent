# QA075 User Guide: Generic Scenario Intake And Durable Draft Blueprint

## Detailed Overview

This guide explains Generic Scenario Intake And Durable Draft Blueprint for non-developer manual QA reviewers. The feature focus is scenario-neutral intake, workflow key normalization, generic editable blueprint generation, durable draft creation, revision-safe saves, and tutorial label guardrails. The wizard helps an authorized user set up a generic workflow-driven system from Console Home, then continue through draft configuration, resource readiness, evidence, validation, publish, launch, and safe inspection surfaces. The guide uses qa075 local QA data and .env.qa075.

The wizard is generic and should work with many workflow scenarios.
The wizard does not require the user to know Workflow Registry internals before starting.
The wizard can link to advanced editors, but the happy path should remain inside the bounded flow.
The backend owns tenant scope, authorization, validation, publish readiness, evidence freshness, and runtime eligibility.
The browser may show progress, but it must never claim a backend gate passed unless backend state says so.
The reviewer should use visible UI controls after local login.
The reviewer should not edit the browser URL to force a state.
The reviewer should capture screenshots for every important state.

## Who Should Use This Guide

- Manual QA reviewers validating the wizard.
- Product reviewers checking the workflow setup path.
- Engineers confirming acceptance evidence.
- Design reviewers checking no-scroll fixed-frame behavior.
- Security reviewers checking redaction and tenant scope.

## Manual QA Prerequisites

- Docker is running.
- PostgreSQL service is available through docker compose.
- Python dependencies are installed with uv sync.
- Frontend dependencies are installed with npm ci in frontend/admin.
- The file specs/075-generic-scenario-intake-and-durable-draft-blueprint/.env.qa075 has been copied to .env.
- The API is running on http://127.0.0.1:8000.
- The viewport can be set to 1280 x 800.
- The reviewer can save screenshots and notes.

## Step-by-Step Manual QA

### Manual Step 1: Prepare environment

Action: Copy specs/075-generic-scenario-intake-and-durable-draft-blueprint/.env.qa075 to .env, run uv sync, start PostgreSQL, and migrate the database.

Expected: The local QA database and artifact directory are ready.

### Manual Step 2: Start API

Action: Run uvicorn on 127.0.0.1 port 8000.

Expected: The API health endpoint returns live.

### Manual Step 3: Open login

Action: Visit http://127.0.0.1:8000/auth/local-login.

Expected: The local login choices are visible.

### Manual Step 4: Choose tenant

Action: Select tenant-admin-acme.

Expected: Console Home opens for the Acme tenant.

### Manual Step 5: Open wizard

Action: Activate Set up workflow from Console Home.

Expected: The onboarding route opens with a fixed frame.

### Manual Step 6: Check scope

Action: Confirm tenant scope remains visible and links include the tenant context where applicable.

Expected: The wizard does not cross into another tenant.

### Manual Step 7: Use scenario

Action: Enter a neutral scenario such as Supplier Risk Intake.

Expected: The wizard creates or displays neutral editable workflow state.

### Manual Step 8: Save draft

Action: Use the visible create or save action.

Expected: The result confirms backend persistence.

### Manual Step 9: Review steps

Action: Visit scenario, draft, agents, contracts, graph, resources, evidence, publish, and launch steps as available.

Expected: Each step fits in 1280 x 800 without vertical scroll.

### Manual Step 10: Attach evidence

Action: Use the evidence action when a deterministic suite is available.

Expected: A required evidence entry is saved without raw transcripts.

### Manual Step 11: Validate

Action: Run validation from the wizard.

Expected: The validation state comes from the backend.

### Manual Step 12: Publish

Action: Publish only when readiness allows it.

Expected: Publish succeeds or shows truthful blockers.

### Manual Step 13: Launch

Action: Open runtime or Design Reviews links from the finish step.

Expected: The target workspace opens through a visible UI link.

### Manual Step 14: Inspect evidence

Action: Open operations or graph evidence links when available.

Expected: Evidence is summarized safely.

### Manual Step 15: Check redaction

Action: Review screenshots and logs.

Expected: No unsafe raw payload appears.

### Manual Step 16: Check no-scroll

Action: Measure document and wizard frame dimensions.

Expected: No vertical scroll is required.

## Expected Results

Expected: Result 1 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 2 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 3 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 4 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 5 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 6 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 7 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 8 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 9 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 10 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 11 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 12 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 13 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 14 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 15 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 16 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 17 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 18 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 19 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 20 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 21 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 22 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 23 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.
Expected: Result 24 confirms the wizard is generic, fixed-frame, tenant-scoped, and backend-owned for QA075.

## Evidence To Capture

- Console Home quick action
- Wizard route with tenant scope
- Scenario or relevant step
- Draft mutation result
- Agent or contract summary
- Graph summary
- Resource readiness summary
- Evidence save result
- Validation or publish state
- Launch or handoff links
- No-scroll measurement
- Redaction review notes
- Automated command output

## Security And Redaction Checks

- No raw credential values.
- No provider authorization headers.
- No raw prompt bodies outside authorized editors.
- No raw completions.
- No raw memory contents.
- No private channel messages.
- No raw external tool payloads.
- No raw test transcripts.
- No local filesystem paths.
- No stack traces.
- No unauthorized tenant labels.

## Tenant Isolation Checks

- Repeat login with tenant-admin-globex if the test path needs a denial check.
- Confirm Acme workflow names do not appear for Globex.
- Confirm cross-tenant URLs fail closed or redirect safely.
- Confirm scope chips and breadcrumbs do not imply access to another tenant.
- Capture denial states without copying identifiers into notes.

## Troubleshooting

- Missing quick action means the principal may lack workflow access.
- Dependency unavailable usually means the API or database setup failed.
- Stale draft means reload and retry through visible recovery.
- Blocked publish means evidence or validation is incomplete.
- Scrollable screen means the fixed-frame requirement failed.
- Tutorial-specific text means the scenario-neutral guardrail failed.
- Raw unsafe data means stop and repair redaction before continuing.
- Single selected pytest runs may fail the global coverage threshold even when the selected test passed.
