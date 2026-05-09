# Implementation Plan: End-To-End Custom Workflow Setup Wizard And Runtime Launch

**Branch**: `codex/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch` | **Date**: 2026-05-09 | **Spec**: `specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/spec.md`

## Summary

Add a guided workflow setup checklist to the existing React Workflow Builder, provide a visible three-agent starter document transformation, refresh builder state after publish, and wire runtime/design-review handoff links that carry safe workflow identifiers into existing Admin surfaces. No new backend route family is planned; backend-owned save, validation, evidence, publish, runtime, and Design Review contracts stay authoritative.

## Technical Context

- Python 3.12, FastAPI, Pydantic v2, SQLAlchemy async ORM, PostgreSQL.
- React 19, TypeScript strict mode, Vite, Vitest, Testing Library, Playwright.
- Existing React Admin shell, workflow builder, Test Bench, user run workspace, Design Reviews workspace, operations/runtime graph, and generated TypeScript contracts.
- Local QA uses `AUTH_MODE=local_principal`, deterministic Test Bench `mock_model`, mocked external integrations, and PostgreSQL QA database `multi_agent_platform_qa073`.

## Constitution Check

- Durable state remains backend-owned through existing workflow draft, validation, evidence, and publish services.
- No browser-only publish readiness or synthetic evidence is introduced.
- Tenant scope is preserved in links and API requests.
- Redaction boundaries remain unchanged: raw prompts outside authorized editors, raw completions, transcripts, secrets, credentials, provider payloads, local paths, stack traces, memory contents, and private payloads stay absent from summaries and QA artifacts.

## Project Structure

```text
frontend/admin/src/components/workflows/
- WorkflowSetupWizardPanel.tsx
- workflowSetupWizard.ts
- workflowSetupWizard.test.ts
- WorkflowBuilderPage.tsx

frontend/admin/src/components/userRuns/UserRunPage.tsx
frontend/admin/src/components/designReviews/DesignReviewWorkspacePage.tsx
frontend/admin/src/styles/admin.css
specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/
specs/_autopilot/workflow-setup-roadmap/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/validation.yml
```

## Implementation Phases

1. Specify and clarify the final guided setup behavior and trust boundaries.
2. Add checklist helper logic and a three-agent starter document transformation.
3. Render the checklist inside Workflow Builder with recovery anchors and launch handoff links.
4. Refresh durable builder state after successful publish.
5. Prefill user run workflow id and Design Review workflow selection from safe query parameters.
6. Add focused tests and styling for desktop/mobile layouts.
7. Add QA docs, validation manifest flows, and curl coverage decision.
8. Run per-spec validation and final roadmap stability gate.

## Data Model

No database migration is required. The feature derives setup state from existing `WorkflowDraftDocument`, `WorkflowValidationSummary`, `WorkflowPublishReadiness`, published version detail, and tenant scope.

## API Contract Impact

No new public JSON route family is introduced. Query parameters on existing Admin React routes are used as safe UI handoff hints:

- `/admin/app/channels/runs?workflow_id=<safe-id>&tenant_id=<tenant-id>`
- `/admin/app/design-reviews?workflow_version_bundle_id=<bundle-id>&tenant_id=<tenant-id>`

## Risk Review

- Evidence freshness: QA must save the requirement, then launch deterministic evidence against the current revision before validation/publish.
- Launch links before publish: UI must label the state truthfully and avoid implying a runtime bundle exists.
- Design Review selection: requested workflow id is honored only when present in authorized workflow options.
- Runtime prefill: workflow id query input is safe but still submitted through retained backend run start validation.

## Validation Strategy

- Frontend unit tests for checklist, starter, Workflow Builder wiring, runtime query prefill, and Design Reviews selection.
- Focused backend route/contract smoke tests for unchanged workflow builder surfaces.
- QA document validation.
- Spec QA manifest with generated contracts, frontend quality, backend quality, and safe API checks.
- Playwright desktop and mobile journeys through local login, workflow setup, evidence, validation, publish, runtime launch, Design Reviews selection, and graph evidence.
- `multi-agent-curl-test` after per-spec validation.
