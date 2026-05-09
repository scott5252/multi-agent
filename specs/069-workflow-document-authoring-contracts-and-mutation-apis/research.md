# Research: Workflow Document Authoring Contracts And Mutation APIs

## Decision: Full Document Save Is The Required React Mutation

**Rationale**: The roadmap requires browser saves to persist every `WorkflowDraftDocument` section. A full document save keeps Spec 069 focused and gives later graph/prompt/evidence UI work one reliable persistence boundary. Optional section patch endpoints can be added later only if they call the same backend validation, revision, idempotency, authorization, and audit path.

**Alternatives considered**:
- Patch-only endpoints. Rejected because patch composition would spread validation and conflict behavior across many route handlers before the full authoring contract is proven.
- Browser-only local document assembly. Rejected because authorization, tenant scope, validation, publish readiness, and redaction must remain backend-owned.

## Decision: React Editor State Wraps The Canonical WorkflowDraftDocument

**Rationale**: The registry schema already models roles, prompt/profile references, skills, contracts, nodes, edges, joins, approval gates, subworkflows, tests, and annotations. The React contract should carry the canonical document plus safe summaries, sections, validation mappings, and references instead of creating a second authoring model.

**Alternatives considered**:
- Replace the canonical registry schema. Rejected because lower-level APIs, validation, graph preview, publish gate, and runtime bundle generation already consume it.
- Keep the current simplified React `WorkflowDraftDocument`. Rejected because it cannot round-trip the full document.

## Decision: Persist Idempotency Fingerprints On Draft Revisions

**Rationale**: Durable idempotency must survive process restarts and must reject same-key/different-payload misuse. The current workflow draft revision row stores document hash and change summary but not the idempotency key or scoped request hash. Additive nullable fields on `workflow_draft_revisions` are the smallest durable place to associate an accepted save with its exact tenant, principal, draft, route family, revision intent, and payload hash.

**Alternatives considered**:
- In-memory idempotency. Rejected because API restart would lose replay state.
- Audit-only lookup. Rejected because audit events are redacted, not modeled as mutation replay records.
- Stale-revision heuristic only. Rejected because it cannot prove idempotency-key reuse with different payloads.

## Decision: Validation Findings Use Existing Section Mapping

**Rationale**: `validate_authoring_document` already returns field paths, section keys, graph element IDs, and safe remediation hints. Spec 069 should normalize Pydantic and workflow validation errors into the same `BuilderValidationFinding`/React field-path shape.

**Alternatives considered**:
- Return raw Pydantic errors. Rejected because they are not stable UI section contracts and may expose internal schema details.
- Let the browser infer sections. Rejected because validation guidance must be backend-owned.

## Decision: Raw Prompt Bodies Stay Outside Workflow Save Diagnostics

**Rationale**: Prompt/profile references already exist on the workflow document, while prompt authoring belongs to governance/prompt APIs and Spec 071 UI work. Workflow save responses, audit summaries, screenshots, and curl artifacts should reference prompt/profile IDs and safe labels only.

**Alternatives considered**:
- Embed prompt templates in workflow document saves. Rejected because it would expand raw prompt exposure and duplicate prompt lifecycle rules.

## Decision: Extend Existing React Admin Workflow Route Family

**Rationale**: The React Admin shell, workflow registry, builder envelope, generated contract script, API client, and Playwright smoke flow already use `/admin/app/workflows/...`. Extending that family avoids a second admin app and preserves visible navigation.

**Alternatives considered**:
- Add a parallel `/admin/app/workflow-setup` API. Rejected for Spec 069 because it would duplicate shell, authorization, and route discovery before the existing builder contract is expanded.
