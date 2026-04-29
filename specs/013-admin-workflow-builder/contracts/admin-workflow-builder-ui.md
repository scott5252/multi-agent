# Admin Workflow Builder UI Contract

## Purpose

Define the server-rendered guided workflow builder UX that extends the existing
admin workflow registry pages. The UI must let authorized platform and tenant
admins create, edit, validate, review, and publish workflow definitions without
editing raw JSON, while preserving no-JS review paths and safe audit behavior.

## Routes

| Route | Purpose | Data Source |
|---|---|---|
| `/admin/workflows/ui` | Registry list with builder status, filters, and create action | `GET /admin/workflows` |
| `/admin/workflows/new` | Guided draft creation form, if implemented as a full page | `GET /admin/workflows/editor-metadata` |
| `/admin/workflows/drafts/{workflow_draft_id}/editor` | Main builder editor for latest draft revision | Draft detail, editor metadata, lookups, graph preview |
| `/admin/workflows/drafts/{workflow_draft_id}/revisions/ui` | Draft revision history and restore/copy controls | `GET /admin/workflows/drafts/{id}/revisions` |
| `/admin/workflows/drafts/{workflow_draft_id}/publish-gate/ui` | Publish readiness review and confirmation | `POST /admin/workflows/drafts/{id}/publish-gate` |
| `/admin/workflows/versions/{workflow_version_bundle_id}/detail` | Published bundle detail with builder pins | Existing version detail plus bundle summaries |

## Shared UX Rules

- All primary actions are server-postable forms.
- JavaScript may enhance graph editing, dynamic repeated sections, validation
  refresh, lookup filtering, and unsaved-change warnings.
- The page remains usable for review and basic save/validate/publish actions
  when optional JavaScript is disabled.
- Raw JSON may be shown as a read-only advanced inspector, not as the primary
  authoring mechanism.
- Inputs render labels, field help icon buttons, validation message containers,
  and stable field paths.
- No visible text may expose raw secrets, provider tokens, credential values,
  unsafe rendered prompt content, unauthorized tenant data, or raw provider
  responses.

## Registry List

Required controls:

- Search by display name, slug, owner, tag, role key, prompt/profile reference,
  and subworkflow alias.
- Scope filters: all, current tenant, platform.
- Status filters: active draft, validation failed, publish ready, published,
  hidden, retired.
- Create workflow button when actor can create in the selected scope.
- Saved filter integration through the existing admin shell.

Required item fields:

- Display name and slug.
- Workflow kind and scope badge.
- Current revision or published version.
- Latest validation status.
- Publish readiness badge.
- Last edited or published timestamp.
- Authorized action links: open draft, validate, publish gate, version detail,
  revision history.

## Draft Editor Sections

Sections render in this order:

1. Overview
2. Roles And Sub-Agent Roles
3. Prompt And Runtime Profile References
4. Model Routing Preview
5. Skill Installations
6. Contracts
7. Graph Builder
8. Join Policies
9. Approval Gates
10. Reusable Subworkflows
11. Test Requirements
12. Validation And Publish
13. Revision History

### Overview

Fields:

- scope type
- tenant
- workflow kind
- slug
- display name
- description
- owner
- tags
- publication intent
- reviewer notes

### Roles And Sub-Agent Roles

Each role card supports:

- role key
- display name
- role kind
- purpose
- responsibilities
- allowed references
- input and output contracts
- graph participation
- handoff expectations

### Prompt And Runtime Profile References

Controls:

- Profile chooser filtered by agent key, agent kind, scope, and grants.
- Prompt reference summary showing prompt reference version ids and prompt
  version ids when authorized.
- Status badge for active, retired, missing, unauthorized, or digest mismatch.
- Links to prompt/profile detail pages only when authorized.

### Model Routing Preview

Controls:

- Preview trigger or link to existing model-skill routing preview.
- Safe summary of selected model routing version, provider catalog entry,
  provider health, policy result, and evaluated version ids.
- Blocking state when the route cannot resolve, provider is unavailable,
  policy fails, or health status blocks publication.

### Skill Installations

Each skill dependency includes:

- skill slug
- exact skill version
- required or optional binding mode
- scope
- compatibility expectation
- credential readiness
- policy notes
- tool and outbound policy references

### Contracts

Contract cards support workflow input/output, handoff, artifact, memory,
tool-access, approval decision, and failure outcome contracts. Contract
validation messages must identify schema path, compatibility issue, producer,
and consumer when available.

### Graph Builder

The graph builder shows a server-derived preview and form-backed editors for
nodes and edges. Required behavior:

- Nodes render as stable graph elements with labels and validation badges.
- Edges render direction, edge type, contract, branch condition, failure path,
  and loop metadata.
- Selecting a graph element opens the matching form section or detail panel.
- Arbitrary cycles are highlighted as blocking.
- Retry and approval-resume loops show configured bounds and failure exits.
- Layout changes are non-authoritative annotations; semantic saves submit the
  typed document.

### Join Policies

Controls:

- strategy
- inbound edge selection
- quorum count
- timeout
- failure behavior
- output merge contract

### Approval Gates

Controls:

- approver scope
- named approver role when required
- reason
- decision contract
- resume behavior
- timeout
- blocked-state visibility
- reviewer instructions

### Reusable Subworkflows

Controls:

- published subworkflow bundle chooser
- selected exact bundle version
- scope and grant status
- input/output contract compatibility
- authorized detail link

### Test Requirements

Controls:

- required suite selection
- target type
- latest result status
- freshness status
- safe summary link when authorized

Publication is blocked when a required result is missing, failing, or stale for
the current draft revision or selected profile/subworkflow target.

## Validation Panel

The validation panel groups findings by:

- blocking first, advisory second
- section
- category
- graph element
- external reference

Each finding renders:

- severity
- short message
- remediation
- field link or section link
- graph highlight when available
- authorized external detail link when available

## Publish Gate Panel

The publish gate panel shows:

- current revision number and document digest
- latest validation result id
- validation freshness
- blocking issue count
- reference readiness table
- prompt/profile pins
- provider routing readiness
- skill readiness
- subworkflow bundle pins
- contract compatibility
- approval gate completeness
- required test evidence
- immutable bundle impact
- confirmation button disabled unless status is ready

The confirmation form submits `validation_result_id`, optional
`publish_gate_id`, and reason.

## Conflict UX

When a save, restore, or publish action returns a stale revision conflict:

- Show a non-destructive banner with current revision number when available.
- Do not claim the submitted changes were saved.
- Offer refresh, open revision history, and copy submitted content guidance.
- Preserve client-side unsaved form state when JavaScript is available.

## Accessibility

- All controls have associated labels.
- Graph elements have keyboard focus targets and text alternatives in the
  adjacent node/edge list.
- Help buttons use `aria-haspopup="dialog"`.
- Modals close by button and Escape.
- Validation summaries use `role="alert"` only for newly returned blocking
  feedback.
- Disabled publish controls include a server-rendered reason.

## View Models

Required page models:

- `WorkflowRegistryPageModel`
- `WorkflowDraftEditorPageModel`
- `WorkflowRevisionHistoryPageModel`
- `WorkflowGraphPreviewPageModel`
- `WorkflowPublishGatePageModel`
- `WorkflowVersionDetailPageModel`

View models are assembled from service/API response schemas, not raw ORM rows.
