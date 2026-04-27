# Contract: Worker Reliability Protocol

**Feature**: Reliability And Scale Hardening  
**Date**: 2026-04-26

## Purpose

Define the runtime contract workers must follow for admission, leasing,
checkpoint resume, retry, circuit breaker checks, compensation, dead-letter
routing, and artifact throughput. The contract complements the public
operator APIs in `reliability-scale.openapi.yaml`.

## Required Worker Context

Every worker action that mutates runtime or reliability state must include:

- `tenant_id`
- `workflow_run_id`
- `run_step_id` when acting on a step
- `worker_id`
- `worker_lease_id`
- `claim_attempt`
- `run_bundle_id`
- `bundle_digest`
- `trace_id`
- `policy_id`
- `policy_version`

Repository writes reject missing context or stale lease fencing tokens.

## Lease Claim Contract

Workers claim work through the queue/runtime repository using tenant-aware
fair scheduling.

Input:

```json
{
  "worker_id": "worker-a-1",
  "worker_pool": "default",
  "max_items": 1,
  "supported_job_kinds": ["workflow_step", "retry", "compensation"],
  "now": "2026-04-26T16:00:00Z"
}
```

Output when work is available:

```json
{
  "tenant_id": "00000000-0000-0000-0000-000000000001",
  "workflow_run_id": "00000000-0000-0000-0000-000000000101",
  "run_step_id": "00000000-0000-0000-0000-000000000201",
  "worker_lease_id": "00000000-0000-0000-0000-000000000301",
  "claim_attempt": 7,
  "lease_expires_at": "2026-04-26T16:02:00Z",
  "run_bundle_id": "00000000-0000-0000-0000-000000000401",
  "bundle_digest": "sha256...",
  "trace_id": "trace-123",
  "policy_version": 4
}
```

Rules:

- Only one active lease may exist for the same run or step.
- Claim order must respect tenant fairness and eligibility time.
- Terminal runs and open-breaker-blocked work are not claimable.
- Claims must create an audit-visible lease/control event.

## Lease Renewal Contract

Workers renew before the renewal deadline.

Rules:

- Renewal requires the same `worker_id`, `worker_lease_id`, and
  `claim_attempt`.
- Renewal updates `last_renewed_at` and `expires_at`.
- Renewals after another worker recovered the work are rejected as stale.

## State Write Contract

Every state write must include the lease fencing token:

```json
{
  "worker_lease_id": "00000000-0000-0000-0000-000000000301",
  "claim_attempt": 7,
  "expected_step_status": "running",
  "new_step_status": "succeeded",
  "checkpoint_after_id": "checkpoint-789"
}
```

Rules:

- Stale writes are rejected and recorded as suppressed.
- Writes must preserve tenant id, run id, bundle digest, and policy version.
- Terminal state writes are idempotent only when the existing terminal state
  matches the requested state.

## Resume Contract

Before resuming recovered work, the worker must load:

- Pinned execution bundle and `bundle_digest`
- Latest runtime checkpoint reference
- LangGraph checkpoint for the same thread id
- Side-effect intents for the run step
- Retry schedule and attempt history
- Relevant circuit breaker state
- Current policy version for prospective decisions

Allowed outcomes:

- `resumed`
- `duplicate_suppressed`
- `compensation_requested`
- `dead_lettered`
- `operator_intervention_required`

Unknown side-effect repeatability must produce
`operator_intervention_required`.

## Retry Contract

Retry classification input:

```json
{
  "failure_category": "dependency_unavailable",
  "attempt_count": 2,
  "max_attempts": 3,
  "tenant_retry_budget_remaining": 42,
  "breaker_state": "closed",
  "deadline_at": "2026-04-26T16:10:00Z"
}
```

Rules:

- Retry scheduling consumes tenant retry budget.
- Non-repeatable ambiguous failures cannot be scheduled.
- Open breaker, quota exhaustion, deadline exhaustion, or max attempts produce
  a stopped retry with a safe stop reason.

## Circuit Breaker Contract

Protected operations call breaker evaluation before sending traffic.

Rules:

- `closed` allows protected work while recording success/failure samples.
- `open` blocks unsafe work and returns a protective decision.
- `half_open` requires a trial token; failures return to `open`.
- Recovery from `open` to `half_open` requires cooldown plus configured
  health/probe evidence.

## Compensation Contract

Compensation can be requested only for an existing side-effect intent.

Rules:

- Automatic compensation is unique per
  `(tenant_id, side_effect_intent_id, hook_ref)`.
- Compensation work uses the same worker lease and retry contracts as primary
  work.
- Outcomes must be inspectable as `succeeded`, `failed`, `unavailable`,
  `timed_out`, `skipped_by_policy`, or `manual_follow_up_required`.

## Dead-Letter Contract

Automated recovery must stop and create a dead-letter record when:

- Retry policy is exhausted.
- Recovery safety cannot be determined.
- Compensation is unavailable or exhausted.
- Breaker/policy state blocks further work.
- Required artifact evidence cannot be safely generated.

Dead-letter records must include safe latest state, failure category,
recommended action, policy version, and artifact references for large evidence.

## Artifact Throughput Contract

Workers acquire artifact budget before large reads, writes, exports, load-test
reports, or replay evidence generation.

Rules:

- PostgreSQL stores metadata and audit refs only.
- Object-storage throttling can delay work or open an artifact breaker.
- Failed artifact writes produce partial/unavailable inspection states instead
  of hiding failure evidence.

## Failure Injection Contract

Load and integration tests must support deterministic failure injection at:

- `after_claim`
- `after_checkpoint`
- `after_side_effect_intent`
- `after_side_effect_applied_before_state_advance`
- `after_retry_scheduled`
- `during_compensation`
- `during_artifact_export`

Validation must assert no duplicate irreversible side effects and no stale
worker commits.
