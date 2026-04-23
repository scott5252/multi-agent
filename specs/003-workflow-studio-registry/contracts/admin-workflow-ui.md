# Admin Workflow UI Contract

## Purpose

Define the initial embedded admin Web UI for workflow registry authoring and
publishing. This contract describes the expected screens, view models, and
field-help modal behavior so backend and UI work stay aligned.

## Routes

| Route | Purpose | Data Source |
|---|---|---|
| `/admin/workflows/ui` | Registry list for drafts and published versions | `GET /admin/workflows` |
| `/admin/workflows/drafts/{workflow_draft_id}/editor` | Draft editor for the active draft revision | `GET /admin/workflows/drafts/{workflow_draft_id}` + `GET /admin/workflows/editor-metadata` |
| `/admin/workflows/versions/{workflow_version_bundle_id}/detail` | Published version detail and dependency view | `GET /admin/workflows/versions/{workflow_version_bundle_id}` |

## Registry Page

### Primary elements

- Search input for workflow name or slug
- Scope filter chips: `All`, `Tenant`, `Platform`
- Status filter chips: `Draft`, `Published`, `Hidden`, `Retired`
- Create-draft button
- Registry table cards showing:
  - display name
  - workflow kind
  - current draft revision or published version
  - scope badge
  - last updated timestamp
  - action button: `Open Draft` or `View Version`

### Empty states

- No visible workflows: explain the current scope filter and how platform
  sharing grants affect platform-scoped assets.

## Draft Editor Layout

### Navigation sections

1. Overview
2. Roles And Skills
3. Contracts
4. Nodes And Flow
5. Subworkflow References
6. Join Policies
7. Approval Gates
8. Validation And Publish

### Shared field pattern

Every editable field renders:

- field label
- input control
- help icon button immediately beside the label
- inline validation message area

### Help modal contract

The help icon button opens an accessible modal dialog driven by
`FieldHelpDefinition`.

Required modal content:

- title
- short explanation of what the field controls
- why the field matters for validation or runtime behavior
- example values or formatting guidance
- optional note about related validation rules

Required interaction behavior:

- button uses `aria-haspopup="dialog"`
- modal traps focus while open
- modal closes with explicit close button and `Escape`
- modal content is read-only and never modifies the draft

## Section-specific expectations

### Overview

- Inputs: scope, slug, display name, description, workflow kind
- Modal examples:
  - scope explains tenant versus platform reuse
  - workflow kind explains main workflow versus reusable subworkflow

### Roles And Skills

- Repeating role cards
- Each role card supports:
  - role display name
  - role kind
  - purpose
  - input contract
  - output contract
  - one or more skill bindings
- Skill binding fields include help for:
  - skill slug
  - exact skill version
  - binding mode

### Contracts

- Repeating contract schema cards
- Fields:
  - contract key
  - semantic version
  - contract kind
  - JSON schema editor
  - example payload
- Help modals explain compatibility behavior and breaking-change rules

### Nodes And Flow

- Ordered node editor with edge mapping
- Node fields:
  - node type
  - display name
  - attached role, approval gate, subworkflow, or join policy
- Flow guidance explains acyclic graph expectations and edge contract usage

### Subworkflow References

- Repeating referenced-subworkflow cards
- Fields:
  - alias
  - published subworkflow version
  - input contract
  - output contract
- UI must show whether the asset is tenant-scoped or platform-scoped via a
  sharing grant

### Join Policies

- Repeating join policy cards
- Fields:
  - strategy
  - required branches
  - quorum count when needed
  - failure behavior
- Help modals explain the behavioral difference between `all_success`,
  `quorum`, `first_success`, and `manual_resolution`

### Approval Gates

- Repeating approval gate cards
- Fields:
  - display name
  - approver scope
  - named role when applicable
  - decision contract
  - timeout policy
  - instructions
- Help modals explain how design-time approval metadata becomes runtime wait
  states later

### Validation And Publish

- Validation summary panel with:
  - blocking findings count
  - advisory findings count
  - grouped findings by category
  - field-targeted messages when available
- Publish panel with:
  - publish-eligible indicator
  - immutable publish explanation
  - action button disabled until latest validation passes

## Local QA Access

- In `AUTH_MODE=local_principal`, browser access is expected to start from
  `/auth/local-login?redirect_to=/admin/workflows/ui`.
- The UI should not require a browser header extension for local QA.

## Conflict And Error UX

- Stale save conflict shows a non-destructive banner explaining that a newer
  draft revision exists and prompting reload.
- Validation errors stay anchored to the relevant section and field paths.
- Publish failures show whether the issue is:
  - stale validation
  - compilation failure
  - artifact persistence failure
  - authorization failure

## View Model Requirements

The UI depends on these backend payloads:

- `WorkflowDraftResponse`
- `ValidationResultResponse`
- `WorkflowVersionResponse`
- `WorkflowEditorMetadataResponse`

The UI must not hardcode field-help copy that duplicates server metadata. The
modal content should render from `field_help` entries keyed by field path so the
same help text can be validated and evolved centrally.
