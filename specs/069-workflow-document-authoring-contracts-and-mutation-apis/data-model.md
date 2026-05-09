# Data Model: Workflow Document Authoring Contracts And Mutation APIs

## Workflow Document Editor State

Safe React-facing load contract for a workflow draft editor.

| Field | Type | Notes |
| --- | --- | --- |
| `workflow_draft_id` | UUID string | Target durable draft |
| `workflow_lineage_id` | UUID string | Owning workflow lineage |
| `revision` | string | Current revision token for mutations |
| `document` | `WorkflowDraftDocument` | Canonical full authoring document |
| `section_summaries` | list | Safe per-section status, counts, dirty hints, and field paths |
| `validation` | summary nullable | Latest safe validation summary for current revision |
| `publish_readiness` | summary nullable | Existing backend-owned publish gate projection |
| `reference_catalog` | object | Authorized prompt/profile/skill/subworkflow/test lookup summaries |
| `stale_conflict` | object nullable | Present only in mutation result contexts |

## Workflow Document Save Request

React-facing mutation payload.

| Field | Type | Notes |
| --- | --- | --- |
| `revision` | string | Submitted base revision token |
| `idempotency_key` | string | Required client-generated key |
| `document` | `WorkflowDraftDocument` | Complete desired document |
| `change_summary` | string nullable | Safe author-entered or generated save summary |
| `client_context` | object nullable | Safe UI context such as active section and form version |

## Workflow Document Mutation Result

Safe response for accepted, validation-error, stale-conflict, denied, or replayed saves.

| Field | Type | Notes |
| --- | --- | --- |
| `status` | enum | Existing `AdminMutationStatus`, including accepted, validation error, stale conflict, idempotent replay |
| `summary` | string | Safe human-readable result |
| `revision` | string nullable | Current revision token when available |
| `editor_state` | object nullable | Updated safe editor state after accepted/replayed save |
| `validation_findings` | list | Section and field-path findings |
| `stale_conflict` | object nullable | Safe reload/recovery guidance |
| `audit_reference_id` | string nullable | Safe audit/revision reference |
| `idempotency` | object nullable | Existing safe idempotency replay metadata |

## Section Validation Finding

Normalized backend-owned finding for React field focus.

| Field | Type | Notes |
| --- | --- | --- |
| `code` | string | Stable validation code |
| `severity` | enum | info, warning, blocking, critical |
| `section_key` | string | metadata, roles, references, contracts, graph, joins, approvals, subworkflows, tests, annotations, publish |
| `field_path` | string nullable | Stable document field path |
| `message` | string | Redaction-safe finding |
| `remediation` | string nullable | Safe suggested correction |
| `graph_element_id` | string nullable | Existing graph mapping when relevant |
| `safe_links` | list | Safe UI anchors only |

## Workflow Draft Revision Idempotency Fingerprint

Additive nullable fields on `workflow_draft_revisions` so old revisions remain valid.

| Field | Type | Notes |
| --- | --- | --- |
| `react_save_idempotency_key` | string nullable | Submitted React save idempotency key |
| `react_save_scope_hash` | string nullable | Hash of tenant, principal, draft, route family, and revision intent |
| `react_save_payload_hash` | string nullable | Hash of the canonical request payload |

## State Transitions

1. Browser loads editor state at revision N.
2. Browser submits full document, revision N, and idempotency key.
3. Backend checks authorization and tenant/platform scope.
4. Backend validates payload size, safe text, Pydantic shape, document references, and workflow authoring rules.
5. If the same idempotency fingerprint already saved revision N+1, backend returns the prior safe mutation result as replay.
6. If the key exists with different scope or payload, backend rejects the request.
7. If the draft current revision is not N and no exact replay applies, backend returns stale conflict without saving.
8. If validation passes, backend appends revision N+1 with idempotency fingerprints, supersedes validation for the draft, emits safe audit summary, and returns updated editor state.

## Redaction Model

- Raw secrets, credentials, provider authorization headers, raw completions, memory contents, private messages, raw tool payloads, raw test transcripts, stack traces, local filesystem paths, and unauthorized tenant labels are never returned.
- Raw prompt template bodies are not part of workflow save diagnostics or general workflow editor summaries.
- Audit summaries contain safe section names, counts, identifiers, document digest prefixes, and validation outcome categories only.

## Retention And Compatibility

Revision idempotency fields follow workflow draft revision retention. Existing lower-level `/admin/workflows/...` save APIs remain compatible and may leave the new React idempotency fields null unless they explicitly adopt the same replay behavior later.
