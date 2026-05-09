# Data Model: Design Review Domain Foundation

## Design Review Session

Represents one tenant-owned Design Reviewer Council scenario request.

**Fields**

- `design_review_session_id`: UUID primary key.
- `tenant_id`: tenant owner.
- `owner_principal_id`: principal that created the session.
- `status`: draft, reviewing, revision_required, manual_resolution, approved,
  cancelled, or failed.
- `request_summary`: safe summary supplied at creation.
- `active_revision_number`: current revision number.
- `quorum_policy_key`: policy name such as `four_of_five_no_blockers`.
- `workflow_version_bundle_id`: optional future published workflow bundle
  reference.
- `idempotency_key`: tenant-scoped create-session retry key.
- `created_at`, `updated_at`: timestamps.

**Validation rules**

- `(tenant_id, idempotency_key)` must be unique when an idempotency key is
  supplied.
- `request_summary` is bounded and must not contain raw prompts, completions,
  secrets, provider payloads, private messages, memory contents, or raw tools.
- Cross-tenant lookups fail closed.

## Design Revision

Represents immutable metadata for one design packet revision.

**Fields**

- `design_revision_id`
- `design_review_session_id`
- `tenant_id`
- `revision_number`
- `author_role_key`
- `safe_summary`
- `artifact_id`
- `payload_digest`
- `previous_revision_id`
- `created_at`

**Validation rules**

- `(design_review_session_id, revision_number)` is unique.
- Revisions are immutable after creation except through future explicit
  migration paths.
- Artifact content is never stored in the revision row.

## Design Review Round

Represents one future acyclic runtime review run against one revision.

**Fields**

- `design_review_round_id`
- `design_review_session_id`
- `design_revision_id`
- `tenant_id`
- `round_number`
- `status`
- `workflow_run_id`
- `reviewer_count`
- `quorum_count`
- `idempotency_key`
- `started_at`, `completed_at`, `created_at`

**Validation rules**

- `(design_review_session_id, round_number)` is unique.
- `workflow_run_id` is nullable in Spec 060 because coordinator launch is
  deferred.
- Counts must be non-negative and quorum count cannot exceed reviewer count.

## Reviewer Assignment

Represents a reviewer role assignment for one round.

**Fields**

- `design_reviewer_assignment_id`
- `design_review_round_id`
- `tenant_id`
- `reviewer_key`
- `role_key`
- `prompt_version_id`
- `profile_version_id`
- `provider_reference`
- `enabled`
- `created_at`

**Validation rules**

- `(design_review_round_id, reviewer_key)` is unique.
- Prompt/profile/provider references are metadata only in Spec 060.

## Reviewer Verdict

Represents immutable safe reviewer output evidence.

**Fields**

- `design_reviewer_verdict_id`
- `design_review_round_id`
- `tenant_id`
- `reviewer_key`
- `verdict`
- `score`
- `blocking_issue_count`
- `safe_feedback_summary`
- `artifact_id`
- `output_digest`
- `usage_summary`
- `idempotency_key`
- `created_at`

**Validation rules**

- Verdict values are bounded to approved, changes_requested, blocked,
  skipped, or failed.
- Safe feedback summary must be bounded and redaction-safe.
- Output digest can exist without storing raw output.

## Quorum Decision

Represents immutable aggregate decision evidence for one round.

**Fields**

- `design_quorum_decision_id`
- `design_review_round_id`
- `tenant_id`
- `status`
- `approval_count`
- `blocking_issue_count`
- `next_action`
- `policy_version`
- `safe_rationale`
- `created_at`

**Validation rules**

- One current quorum decision is allowed per round in Spec 060.
- Counts must be non-negative.
- Decisions do not rewrite verdict records.

## Manual Decision

Represents append-only operator intervention metadata.

**Fields**

- `design_manual_decision_id`
- `design_review_session_id`
- `design_review_round_id`
- `tenant_id`
- `decision_type`
- `actor_principal_id`
- `safe_rationale`
- `accepted_risk`
- `idempotency_key`
- `created_at`

**Validation rules**

- Decision type is revise, approve_exception, retry, or cancel.
- `(tenant_id, idempotency_key)` is unique when supplied.
- Manual decisions append; they do not delete or mutate prior reviewer evidence.

## Development Handoff

Represents final handoff metadata for an approved session.

**Fields**

- `design_development_handoff_id`
- `design_review_session_id`
- `tenant_id`
- `approved_revision_id`
- `artifact_id`
- `safe_summary`
- `output_digest`
- `status`
- `idempotency_key`
- `created_at`

**Validation rules**

- One active handoff is allowed per session.
- Handoff artifact content is not returned inline.
- Handoff creation is idempotent for retries.
