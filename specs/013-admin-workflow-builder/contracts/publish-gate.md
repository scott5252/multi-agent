# Publish Gate Service Contract

## Purpose

The publish gate service is the authoritative readiness boundary between a
workflow draft revision and immutable workflow bundle publication. It produces
a safe, reviewable result for the current draft revision and blocks publish
when validation, references, graph semantics, authorization, or required test
evidence are stale, missing, failing, or incompatible.

## Inputs

```text
principal
workflow_draft_id
workflow_draft_revision_id
validation_result_id optional
requested_scope
trace_id
request_id
reason optional
```

The service resolves the latest draft record from the existing workflow
registry repository. If the supplied revision or validation result does not
match the current draft head, the result is `stale`.

## Output

```json
{
  "publish_gate_id": "deterministic-or-persisted-id",
  "workflow_draft_id": "uuid",
  "workflow_draft_revision_id": "uuid",
  "document_sha256": "sha256",
  "validation_result_id": "uuid",
  "status": "ready|blocked|stale|unauthorized",
  "blocking_issue_count": 0,
  "advisory_issue_count": 0,
  "findings": [],
  "reference_readiness": [],
  "pin_summary": {},
  "required_test_summary": {},
  "expires_at": "timestamp|null",
  "digest": "sha256"
}
```

The digest is computed from the revision id, document digest, validation result
id, reference readiness pin payloads, required test evidence, and rule set
version.

## Required Checks

### Current Revision And Validation

- Draft exists and is editable/publishable by the current principal.
- Draft revision is the current head.
- Validation result exists, belongs to the current revision, is latest, is not
  superseded, and has passed.
- Validation rule set version is accepted for this feature.

### Authorization

- Principal can view and publish the draft scope.
- Tenant admins cannot publish platform-scoped workflows.
- Platform references are visible to tenant admins only through explicit
  grants.
- Hidden or unauthorized lookup targets produce safe blocking findings without
  leaking protected names or metadata.

### Prompt/Profile References

- Each agent and sub-agent role resolves to exactly one active authorized
  agent profile version.
- Tenant profile versions take precedence over granted platform profile
  versions.
- Profile prompt references point to active authorized prompt versions.
- Prompt digests match model-skill prompt references.
- Retired, missing, unauthorized, wrong-scope, or digest-mismatched references
  block publish.

### Provider Routing

- Model routing preview resolves through existing `model_skill_config`.
- Selected model/provider route does not bypass routing authorization.
- Provider catalog entry is visible for the workflow tenant/scope.
- Provider connection is active and health-policy compatible.
- Required provider test/health status is available when policy demands it.

### Skills, Tools, And Credentials

- Required skill references map to active exact-versioned skill bindings.
- Skill context is allowed for the role or step.
- Required tool policy, outbound policy, secret reference, and credential
  requirement versions are active and compatible.
- Credential readiness is represented by safe references only.

### Contracts

- Workflow input/output, handoff, artifact, memory, tool, approval, failure,
  and subworkflow contracts are present when referenced.
- Edge contracts are compatible with source output and target input.
- Contract compatibility against previous published bundle and selected
  subworkflow bundle versions is blocking when incompatible.

### Graph Policy

- Entry node exists.
- Required terminal outcomes exist.
- All non-terminal nodes have valid outgoing paths.
- No disconnected nodes are publishable unless explicitly marked inactive or
  draft-only.
- Arbitrary cycles are blocking.
- Retry and approval-resume loops are allowed only with loop type, maximum
  attempts or timeout, failure exit, and audit/resume semantics.
- Join policies reference real inbound edges and valid merge contracts.

### Approval Gates

- Approver scope is valid.
- Named role scope includes approver role.
- Reason, resume behavior, timeout, blocked-state visibility, and decision
  contract are complete when required.

### Reusable Subworkflows

- Subworkflow references point to visible published bundle ids.
- Selected version is exact and not retired for new use.
- Input/output contracts are compatible.
- Publish pin payload records exact subworkflow bundle id.

### Required Test Evidence

- Each required suite has a latest result for the current draft revision,
  selected profile version, or selected subworkflow bundle target.
- Result is passing.
- Result is not stale according to freshness policy.
- Safe summary is available for audit/review.

## Idempotency

Gate id may be deterministic from:

```text
workflow_draft_id
workflow_draft_revision_id
validation_result_id
document_sha256
rule_set_version
principal scope
```

If a persisted gate table is added later, duplicate requests for the same
inputs return the existing gate result while it remains current.

Publish idempotency is derived from:

```text
workflow_draft_id
workflow_draft_revision_id
validation_result_id
publish_gate_digest
```

Duplicate publish requests must not create multiple authoritative bundles.

## Audit

The service records safe audit events for:

- publish gate requested
- publish gate ready
- publish gate blocked
- publish gate stale
- publish gate unauthorized
- reference lookup denied

Audit payload fields:

- actor principal id
- scope type
- tenant id
- workflow lineage id
- draft id
- revision id
- validation result id
- gate status
- blocking/advisory counts
- finding codes
- pin ids and digests
- trace id
- request id

Audit payloads must not include raw prompt text, rendered prompt previews,
provider responses, secrets, credentials, tokens, or unauthorized tenant data.

## Publish Handoff

`publish_draft` must re-check or consume a current ready gate before compiling.
The compiled bundle summary includes the gate digest and pin summary. If any
check becomes stale between gate review and confirmation, publish returns 409
and the active published bundle remains unchanged.
