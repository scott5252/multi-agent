# Data Model: End-To-End Custom Workflow Setup Wizard And Runtime Launch

## Workflow Setup Step

- `key`: stable step key for metadata, agents, bindings, graph, contracts, evidence, validation, publish, or runtime.
- `title`: user-facing section label.
- `summary`: safe progress summary derived from document or backend readiness.
- `href`: in-page recovery anchor.
- `status`: `complete`, `active`, or `blocked`.

Derived from:

- `WorkflowEditorDocument`
- `WorkflowValidationSummary`
- `WorkflowPublishReadiness`
- published workflow version id

## Three-Agent Starter Document

Adds or replaces editable workflow document collections:

- `roles`: intake, research, synthesis.
- `prompt_profile_references`: one prompt and one runtime profile reference per role.
- `contracts`: request, analysis handoff, result.
- `nodes`: three role nodes, one join node, one terminal node.
- `edges`: fan-out, join, and terminal edges.
- `join_policies`: all-success review join.
- `editor_annotations`: graph layout and setup note.

The starter uses existing document save contracts and does not persist until the user saves the draft.

## Runtime Launch Handoff

- `workflow_id`: safe workflow id string, using the published bundle id when available and workflow key as a pre-publish fallback.
- `tenant_id`: active tenant scope when present.

Consumed by User Run workspace to prefill the workflow input. Backend run start remains authoritative.

## Design Review Handoff

- `workflow_version_bundle_id`: published workflow bundle id when available.
- `tenant_id`: active tenant scope when present.

Consumed by Design Reviews workspace only when the requested bundle is present in authorized workflow options.

## Persistence Impact

No new tables or columns.

## Validation Rules

- Setup steps can be complete only when their local/backend inputs meet explicit rules.
- Publish and runtime steps require backend-published state.
- Evidence step may show local passing state but publish still depends on backend publish readiness.
