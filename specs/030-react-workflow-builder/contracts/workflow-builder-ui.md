# UI Contract: React Workflow Builder

## Route

- Primary React route: `/admin/app/workflows`
- Builder envelope: `/admin/app/workflows/builder.json`
- Existing Jinja fallback: `/admin/workflows/ui`

## First Screen

The first viewport must be the builder workspace:

- React admin shell chrome.
- Active platform or tenant scope.
- Workflow title and revision state.
- Dirty/save state.
- Primary actions: Save, Validate, Review publish.
- Guided section navigation.
- Graph/list workspace.

Do not add a marketing hero or explanatory landing page.

## Major Regions

- **Draft header**: workflow name, status, revision, validation freshness, publish readiness.
- **Section rail or tabs**: Metadata, Roles, References, Graph, Gates, Evidence, Publish, Revisions, Advanced.
- **Guided form panel**: Section-specific form controls using existing `AdminForm` patterns.
- **Graph workspace**: React graph canvas with zoom controls, minimap or fit controls if enabled, and non-authoritative layout.
- **Accessible graph lists**: Node list, edge list, branch list, join policy list, and selected-element inspector.
- **Validation panel**: Findings, blockers, warnings, affected sections, remediation links, and refresh action.
- **Evidence panel**: Required test suites, repository-backed evidence freshness, artifact references, and publish blockers.
- **Publish panel**: Decision summary, immutable bundle preview, confirmation prompt, and audit reference after acceptance.
- **Revision history**: Safe revision summaries and compare links.
- **Read-only JSON inspector**: Collapsed by default and safe/redacted.

## Interaction Rules

- Saves are explicit backend submissions.
- Validation runs on demand and after save.
- Graph layout changes do not define execution semantics.
- Join policy controls use menus or segmented controls, not free-form JSON.
- Approval gates use toggles, checkboxes, and confirmation controls.
- Reference pickers use backend-owned option lists with readiness badges.
- Publish requires explicit confirmation.
- Stale conflicts show safe recovery guidance and current revision metadata.
- Cross-tenant or denied states render common safe state panels.

## Accessibility

- Graph nodes and edges must be keyboard focusable when the graph canvas is enabled.
- Equivalent node and edge editing/review must be available outside the canvas.
- Buttons must have icon and/or text labels with accessible names.
- Dense panels must keep text within containers at desktop and mobile widths.
- Validation findings must be reachable by keyboard and screen-reader users.

## Redaction

Never render:

- Raw secrets or credential values.
- Provider authorization headers.
- Raw prompts or completions.
- Memory contents.
- Private channel messages.
- Provider responses.
- Telegram update payloads.
- Raw connector outputs.
- Local filesystem paths.
- Stack traces.
- Unauthorized tenant labels.

Render only safe summaries, readiness categories, artifact references, revision tokens, and audit references.

## Playwright Evidence

Required QA030 flows:

- Denied route fails closed.
- Local-principal login opens builder.
- Create/edit/save draft.
- Validate draft and inspect graph/list alternatives.
- Show stale conflict.
- Show publish blocked by missing/stale evidence.
- Show publish accepted for ready fixture after confirmation.
- Verify tenant scope and cross-tenant denial.
