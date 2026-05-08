# Contract: Workflow React Live Data

## Scope

This contract defines the production behavior expected from the React workflow registry and builder JSON/API surfaces after Spec 050. Route responses must be backed by durable workflow services or truthful empty, denied, not-found, stale-conflict, or unavailable states.

## Common Rules

- All routes require the existing admin React authentication and authorization behavior.
- `tenant_id` may be supplied only when authorized for the active principal.
- Responses must include backend-owned scope and provenance/empty-state metadata where the schema supports it.
- Route payloads must never include fixed `qa030` workflow IDs, fake graph nodes, fake publish evidence, fake audit references, raw workflow payloads, raw secrets, raw prompts, raw completions, stack traces, local filesystem paths, or unauthorized tenant labels.
- Empty workflow databases return empty-state metadata and create actions, not demo workflow rows.
- Seeded workflow databases return records matching durable lineages, drafts, revisions, validation results, published bundles, sharing grants, artifacts, and test-bench evidence.

## Routes

### GET `/admin/app/workflows/registry.json`

Returns a live workflow registry envelope.

**Query parameters**:

- `tenant_id`: Optional authorized tenant scope.
- `search`: Optional backend-owned search query.
- `status`: Optional workflow status filter.
- `scope_filter`: Optional `all`, `tenant`, or `platform` scope filter.
- `sort`: Optional supported sort key; default latest-updated.
- `cursor`: Optional pagination cursor.
- `limit`: Optional bounded page size.

**Success expectations**:

- Empty database: `items` is empty, `empty_state` explains that no workflows exist, and create action is present when authorized.
- Seeded database: `items` contains only authorized workflow rows and each row links to durable draft or version detail.
- Pagination/filter metadata reflects backend decisions.

### GET `/admin/app/workflows/create.json`

Returns live create-state metadata and allowed create actions.

**Success expectations**:

- Templates and create actions are backend-owned and safe for the caller.
- No route returns a fake created workflow before a durable create action succeeds.

### GET `/admin/app/workflows/builder.json`

Returns the latest authorized active draft for the current workflow entry context.

**Query parameters**:

- `tenant_id`: Optional authorized tenant scope.
- `workflow_lineage_id`: Optional durable lineage identifier.
- `workflow_draft_id`: Optional durable draft identifier retained for compatibility with the existing route family.

**Success expectations**:

- If no durable draft exists, returns a truthful empty/not-found/unavailable state.
- If a lineage is supplied, resolves to the latest authorized active draft.
- If a draft is supplied, returns that authorized durable draft or fails safely.

### GET `/admin/app/workflows/drafts/{workflow_draft_id}/detail.json`

Returns a live builder envelope for an explicit durable draft ID.

**Success expectations**:

- `draft.workflow_draft_id` equals the requested durable ID.
- `draft.revision` matches durable latest revision state.
- Graph preview, sections, validation, publish readiness, revisions, references, sharing, and actions derive from durable services.

### GET `/admin/app/workflows/drafts/{workflow_draft_id}/publish-gate.json`

Returns current publish readiness for an explicit durable draft ID.

**Success expectations**:

- Required evidence comes from existing validation and test-bench evidence records.
- Missing, stale, failing, passing, denied, and unavailable states are distinguishable.

### GET `/admin/app/workflows/versions/{workflow_version_bundle_id}/detail.json`

Returns an immutable published bundle detail projection.

**Success expectations**:

- The response references a durable published bundle.
- Sharing and evidence summaries reflect durable records and caller authorization.

### GET `/admin/app/workflows/lookups.json`

Returns live reference options available to the builder.

**Success expectations**:

- Prompt, profile, provider, skill, test-suite, subworkflow, and policy options are authorized and backend-owned.
- Missing dependencies return empty option groups or unavailable state, not fake references.

### POST `/admin/app/workflows`

Creates a durable workflow draft when the caller is authorized.

**Success expectations**:

- Response includes durable lineage/draft IDs, revision token, audit summary, and navigation/refresh metadata.
- Idempotent replay returns the same durable result where supported.

### POST `/admin/app/workflows/drafts/{workflow_draft_id}/save`

Saves a new draft revision.

**Success expectations**:

- Success persists a new revision and returns the new revision token.
- Stale revision token returns a stale-conflict result with safe current revision metadata.

### POST `/admin/app/workflows/drafts/{workflow_draft_id}/validate`

Runs durable workflow validation.

**Success expectations**:

- Response includes a durable validation summary for the current revision.
- Findings are safe and contain no raw workflow document or stack trace.

### POST `/admin/app/workflows/drafts/{workflow_draft_id}/restore`

Restores a prior durable revision by creating a new current revision.

**Success expectations**:

- Response returns new revision metadata and audit summary.
- Unknown or unauthorized revisions fail safely.

### POST `/admin/app/workflows/drafts/{workflow_draft_id}/copy`

Copies a durable draft into a new lineage/draft when authorized.

**Success expectations**:

- Response returns the new durable lineage/draft identifiers and revision metadata.
- The copied workflow remains tenant-scoped and auditable.

### POST `/admin/app/workflows/drafts/{workflow_draft_id}/publish`

Publishes a durable workflow bundle only when validation and publish-gate evidence allow it.

**Success expectations**:

- Missing or stale evidence returns publish-gate denial.
- Passing evidence creates a durable published bundle and returns bundle metadata.
- Stale revision token returns stale-conflict metadata.

## Validation Contract

Completion for Spec 050 requires:

- Empty-database backend route tests for registry, builder, lookups, publish-gate, and version/draft not-found behavior.
- Seeded-database backend route tests for live registry rows, draft detail, graph preview, validation, publish readiness, sharing, version detail, mutations, and tenant denial.
- Contract tests proving generated TypeScript models match Pydantic contracts.
- Frontend tests proving empty state, live list, live builder, stale conflict, and publish-gate rendering.
- Scanner tests proving old workflow deterministic markers are absent from production source, generated contracts, and built assets.
- Playwright workflow flow that creates or edits/validates/publishes or verifies publish-gate state through the UI.
- Post-UI API/database verification that proves Playwright state persisted.
- `multi-agent-curl-test` passes after Spec QA and Playwright.
