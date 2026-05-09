# Data Model: Design Review Coordinator And Iteration Loop

## Existing Durable Records Used

### DesignReviewSession

- `design_review_session_id`
- `tenant_id`
- `status`
- `request_summary`
- `active_revision_number`
- `quorum_policy_key`
- `workflow_version_bundle_id`
- `owner_principal_id`
- `idempotency_key`

Coordinator updates `status`, `active_revision_number`, and optionally the
selected `workflow_version_bundle_id`.

### DesignRevision

- `design_revision_id`
- `design_review_session_id`
- `tenant_id`
- `revision_number`
- `author_role_key`
- `safe_summary`
- `artifact_id`
- `payload_digest`
- `previous_revision_id`

Coordinator creates new revisions for revision-required outcomes. Existing
revisions are never mutated.

### DesignReviewRound

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
- `started_at`
- `completed_at`

Coordinator creates rounds, links runtime runs, and updates round status.

### DesignReviewerAssignment

Coordinator records one assignment per enabled reviewer in a round.

### DesignReviewerVerdict

Coordinator records safe reviewer verdicts with `approved`,
`changes_requested`, `blocked`, `skipped`, or `failed` values.

### DesignQuorumDecision

Coordinator records one decision per completed round.

### DesignManualDecision

Coordinator uses durable manual decisions for revise, approve-exception, retry,
and cancel actions.

### DesignDevelopmentHandoff

Coordinator creates one handoff when quorum passes or approval by exception is
accepted.

### RuntimeExecutionBundleRecord

Coordinator creates a runtime bundle with selected published workflow version
metadata and design review input.

### WorkflowRunRecord

Coordinator creates a runnable DB-backed runtime run for worker execution.

## New In-Memory Domain Models

### CoordinatorReviewer

- `reviewer_key`
- `role_key`
- `prompt_version_id`
- `profile_version_id`
- `provider_reference`
- `enabled`

### CoordinatorLaunchRequest

- `tenant_id`
- `session_id`
- `workflow_version_bundle_id`
- `reviewers`
- `idempotency_key`
- `max_rounds`
- `execution_mode`

### CoordinatorCompletionVerdict

- `reviewer_key`
- `verdict`
- `score`
- `blocking_issue_count`
- `safe_feedback_summary`
- `output_digest`
- `artifact_id`
- `usage_summary`

### CoordinatorResult

- `state`
- `session`
- `round`
- `revision`
- `quorum_decision`
- `handoff`
- `runtime_run_id`
- `replayed`
- `next_action`

## State Transitions

```text
draft -> reviewing -> approved
draft -> reviewing -> revision_required -> reviewing
draft -> reviewing -> manual_resolution -> revision_required
draft -> reviewing -> manual_resolution -> approved
draft -> reviewing -> manual_resolution -> reviewing
draft -> reviewing -> manual_resolution -> cancelled
reviewing -> failed
```

## Quorum Policy Matrix

| Policy | Enabled reviewers | Required approvals | Blocking issues |
| --- | ---: | ---: | ---: |
| `four_of_five_no_blockers` | 5 | 4 | 0 |
| `three_of_four_no_blockers` | 4 | 3 | 0 |

If enabled reviewer count differs from the named policy, the coordinator uses
the explicit policy requirement and fails to manual resolution when evidence is
incomplete.
