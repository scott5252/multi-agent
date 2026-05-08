# Data Model: Workflow React Live Data

## Overview

Spec 050 does not introduce a new source-of-truth schema. It defines React admin projection entities backed by existing workflow registry, validation, artifact, sharing, audit, and test-bench evidence records. Every projection must be derived from durable state, computed validation metadata, or a truthful empty/denied/unavailable state.

## Entities

### Workflow Live Registry Envelope

Represents the workflow registry page for the authorized scope.

**Fields**:

- `page_id`: Stable page identifier for the workflow registry.
- `title` and `summary`: Safe page copy.
- `scope`: Authorized React admin scope.
- `provenance`: Source metadata identifying live persisted workflow data, computed metadata, empty state, denied state, or unavailable dependency.
- `empty_state`: Present when no authorized workflow records exist.
- `filters`: Backend-owned status, scope, search, sort, and pagination metadata.
- `items`: Ordered workflow live registry items.
- `create_action`: Backend-owned create action when the caller can create drafts.

**Validation rules**:

- `items` is empty only when `empty_state` or an unavailable/denied state explains why.
- Search, sort, pagination, and scope filters are computed server-side.
- No item may contain a workflow lineage, draft, version, tenant, or owner outside caller authorization.

### Workflow Live Registry Item

Represents one live workflow draft or published bundle row.

**Fields**:

- `workflow_lineage_id`: Durable lineage identifier.
- `workflow_draft_id`: Durable active draft identifier when the row is editable.
- `workflow_version_bundle_id`: Durable published bundle identifier when the row is immutable.
- `name`, `workflow_kind`, `status`, `owner_label`, `tenant_label`: Safe workflow summary fields.
- `updated_at_label`: Safe age or timestamp label derived from durable records.
- `sharing_summary`: Durable sharing state summary.
- `required_evidence_summary`: Publish/test-bench evidence summary.
- `href`: React route for the authorized detail view.
- `actions`: Backend-owned allowed actions.

**Validation rules**:

- Draft rows and version rows must not reuse fake IDs when no matching durable record exists.
- Tenant labels are omitted or generalized when the caller cannot view them.
- `actions` must reflect authorization and workflow state.

### Workflow Live Builder Envelope

Represents the workflow builder detail state for an authorized draft or lineage-oriented latest active draft.

**Fields**:

- `registry`: Live registry envelope for surrounding navigation.
- `create_state`: Live create-state envelope.
- `draft`: Workflow draft document summary.
- `sections`: Editable/inspectable builder sections derived from the stored document.
- `reference_catalog`: Live reference options for prompts, profiles, providers, skills, test suites, subworkflows, and policies.
- `validation`: Latest durable validation summary.
- `publish_readiness`: Current publish-gate decision.
- `revisions`: Durable draft revision history.
- `version_detail`: Published bundle detail when available.
- `sharing`: Durable sharing summary.
- `json_inspector`: Redacted safe document preview.
- `actions`: Backend-owned save, validate, publish, restore, and copy actions.
- `state`: Optional empty, denied, unavailable, or stale state metadata.

**Validation rules**:

- A lineage-oriented request resolves to the latest authorized active draft.
- Explicit draft detail requests fail safely when the draft ID is unknown or unauthorized.
- The envelope never substitutes a default draft when the database is empty.
- Raw workflow documents may be summarized only through safe previews.

### Workflow Draft Document Projection

Represents a safe summary of the stored workflow draft document.

**Fields**:

- `workflow_draft_id`
- `workflow_lineage_id`
- `revision`
- `name`
- `description`
- `status`
- `tenant_label`
- `metadata_summary`
- `roles_summary`
- `references_summary`
- `graph`

**Validation rules**:

- `revision` must be the latest durable draft revision token.
- Summaries must be safe text and must not expose raw prompts, completions, secrets, private messages, memory contents, or raw tool payloads.
- `graph` is generated from the stored document, not a fallback fixture.

### Workflow Graph Preview

Represents the accessible graph view derived from a stored workflow document.

**Fields**:

- `layout_revision`
- `layout_is_authoritative`
- `nodes`
- `edges`
- `join_policies`
- `accessibility_summary`
- `validation_findings` where the contract is extended for live invalid states.

**Validation rules**:

- Nodes and edges correspond to stored roles, handoffs, contracts, and joins.
- Invalid documents produce safe findings and blocked/unavailable state.
- No fake nodes, fake roles, fake providers, fake prompts, fake skills, or fake artifacts are generated.

### Workflow Reference Catalog

Represents live authoring choices for references.

**Fields**:

- `prompt_options`
- `profile_options`
- `provider_options`
- `skill_options`
- `test_suite_options`
- `subworkflow_options`
- Future-safe policy/contract option groups if required by existing services.

**Validation rules**:

- Options are authorized for the caller's tenant/platform scope.
- Missing dependencies return empty option groups with safe unavailable state where needed.
- Credential readiness and policy decisions remain backend-owned.

### Workflow Validation Summary

Represents latest durable validation state for a draft revision.

**Fields**:

- `validation_id`
- `status`
- `revision`
- `generated_at_label`
- `summary`
- `findings`
- `artifact_reference_ids`

**Validation rules**:

- Validation summaries must match the selected draft revision.
- Findings contain safe messages and recommended actions only.
- Artifact references are opaque safe IDs, not local filesystem paths.

### Workflow Publish Readiness

Represents publish-gate decision and required evidence for a draft or bundle.

**Fields**:

- `decision`
- `revision`
- `summary`
- `blockers`
- `warnings`
- `required_evidence`
- `confirmation`
- `published_bundle_summary`

**Validation rules**:

- Required evidence uses existing validation and test-bench evidence.
- Missing, stale, failing, passing, denied, and unavailable states are distinct.
- Passing evidence is never fabricated.

### Workflow Action Result

Represents mutation output for create, save, validate, restore, copy, and publish actions.

**Fields**:

- `status`
- `summary`
- `revision`
- `validation`
- `publish_readiness`
- `stale_conflict`
- `audit_reference_id`
- `idempotency_replayed`
- `refresh`

**Validation rules**:

- Successful mutations correspond to persisted workflow state.
- Stale conflict responses include safe current revision metadata.
- Audit references are safe identifiers or summaries and never raw audit payloads.

## Relationships

- A workflow lineage owns zero or one active draft and zero or more published bundles.
- A workflow draft owns one or more immutable draft revisions.
- A draft revision can have zero or more validation results.
- A published bundle references a lineage, draft, draft revision, version snapshot, bundle digest, and activation state.
- Publish readiness combines validation records and required test-bench evidence.
- Sharing summaries describe grants for published bundles and caller-allowed actions.
- Artifact references are metadata links to stored evidence, not raw files or local paths.

## State Transitions

```text
empty workspace -> draft created -> draft saved -> validation run
validation run -> publish gate missing/stale/failing/passing
publish gate passing -> bundle published
draft saved with stale token -> stale conflict
revision restored -> new draft revision
draft copied -> new lineage/draft
published bundle shared -> sharing grant active
```

## Redaction And Safety Rules

- Never expose raw prompt bodies, raw completions, private channel messages, raw memory contents, raw run payloads, raw tool payloads, secrets, credential values, provider authorization headers, stack traces, local filesystem paths, or unauthorized tenant labels.
- Use safe summaries for workflow documents, validation findings, graph parsing failures, publish evidence, audit references, and artifacts.
- Only test-only paths may retain deterministic `qa030` fixtures.

## Empty And Seeded QA States

- **Empty QA state**: No workflow lineages, drafts, versions, validation results, or sharing records for the authorized scope. Routes return empty state metadata and create actions only.
- **Seeded QA state**: Acme has one tenant-scoped workflow draft with revision history, validation evidence, publish-gate evidence, and a published bundle. Optional isolation records can prove Globex/platform boundaries without rendering unauthorized labels.
