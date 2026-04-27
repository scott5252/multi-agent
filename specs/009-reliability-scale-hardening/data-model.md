# Data Model: Reliability And Scale Hardening

**Feature**: Reliability And Scale Hardening  
**Date**: 2026-04-26

## Overview

Reliability hardening adds durable policy, decision, and operational state
around the existing runtime queue, worker lease, side-effect intent, audit,
artifact, and workflow run tables. Current-state heads support fast scheduling
and dashboards; append-only event/decision tables support inspection, audit,
retention, and replay of operational behavior.

## Entities

### Reliability Policy

Scoped configuration for backpressure, quotas, fairness, leases, retries,
breakers, compensation, dead letters, artifact throughput, and unsafe override
rules.

- `policy_id`: UUID primary key
- `tenant_id`: nullable tenant scope; null means global/default
- `scope_type`: `global`, `tenant`, `workflow`, `dependency`, `artifact_store`
- `scope_key`: nullable workflow id, dependency name, or artifact operation
- `policy_version`: monotonically increasing integer
- `settings`: JSON settings payload
- `status`: `draft`, `active`, `retired`
- `effective_at`, `retired_at`: timestamps
- `created_by`, `created_reason`: actor and reason

Validation rules:

- Only one active policy per `(tenant_id, scope_type, scope_key)`.
- Settings that disable required safety controls are rejected unless an
  authorized override is recorded.
- New policy versions apply prospectively to new decisions.

### Admission Decision

Append-only record of whether submitted work was accepted, queued, delayed,
throttled, rejected, or retry-eligible.

- `admission_decision_id`: UUID primary key
- `tenant_id`: tenant owner
- `workflow_run_id`: nullable affected run
- `queue_job_id`: nullable queue job
- `policy_id`, `policy_version`: governing policy
- `decision`: `accepted`, `queued`, `delayed`, `throttled`, `rejected`,
  `retry_eligible`
- `reason_code`: safe reason
- `available_at`: nullable delayed eligibility time
- `capacity_snapshot_id`: nullable snapshot used for decision
- `trace_id`, `created_at`: trace and timestamp

Validation rules:

- Every overload path must create an admission decision.
- Rejected decisions must include a safe user/operator-facing reason.

### Tenant Quota Counter

Current quota usage for bounded shared resources.

- `quota_counter_id`: UUID primary key
- `tenant_id`: tenant owner
- `resource_kind`: `submitted_work`, `active_work`, `worker_lease`,
  `recovery_work`, `retry_attempt`, `compensation_work`, `artifact_io`,
  `operational_action`
- `limit_value`: configured limit
- `used_value`: current usage
- `window_start`, `window_end`: applicable window
- `policy_id`, `policy_version`: governing policy
- `updated_at`: timestamp

Validation rules:

- Usage increments and decrements are atomic within the same transaction as
  the accepted decision or release.
- Quota denials produce an admission or control decision record.

### Fairness Window

Tracks fair-share scheduling state and debt for a tenant.

- `fairness_window_id`: UUID primary key
- `tenant_id`: tenant owner
- `window_start`, `window_end`: scheduling window
- `weight`: configured fair-share weight
- `allocated_tokens`, `consumed_tokens`: token budget
- `fairness_debt`: positive when tenant received less than fair share
- `burst_debt`: positive when tenant borrowed extra capacity
- `updated_at`: timestamp

Validation rules:

- Fairness debt cannot starve tenants with current demand.
- Burst debt lowers future priority until repaid or expired by policy.

### Capacity Snapshot

Periodic operational snapshot for admission, autoscaling, and dashboards.

- `capacity_snapshot_id`: UUID primary key
- `snapshot_scope`: `global`, `tenant`, `worker_pool`, `dependency`,
  `artifact_store`
- `tenant_id`: nullable tenant scope
- `worker_pool`: nullable pool name
- `runnable_depth`, `delayed_depth`, `active_leases`, `recovery_backlog`
- `retry_backlog`, `compensation_backlog`, `dead_letter_count`
- `db_pool_wait_p95_ms`, `db_pool_in_use`, `db_pool_available`
- `artifact_inflight`, `artifact_wait_p95_ms`
- `open_breaker_count`, `fairness_debt_total`
- `created_at`: timestamp

Validation rules:

- Snapshots are append-only and may be downsampled by retention policy.
- Autoscaling decisions reference the snapshot they used.

### Worker Pool Scaling Decision

Append-only record of a worker scale recommendation or action.

- `scaling_decision_id`: UUID primary key
- `worker_pool`: pool name
- `decision`: `scale_out`, `scale_in`, `hold`, `block_scale_out`
- `current_workers`, `target_workers`: counts
- `reason_code`: safe reason
- `capacity_snapshot_id`: source snapshot
- `policy_id`, `policy_version`: governing policy
- `created_at`: timestamp

Validation rules:

- Scale-out is blocked while DB or dependency health lacks headroom.
- Scale-in requires sustained low backlog and no unpaid recovery/fairness debt.

### Retry Schedule

Durable state for a retryable run step or queue job.

- `retry_schedule_id`: UUID primary key
- `tenant_id`: tenant owner
- `workflow_run_id`: nullable run
- `run_step_id`: nullable step
- `queue_job_id`: nullable queue job
- `failure_category`: classified category
- `attempt_count`, `max_attempts`: counts
- `next_eligible_at`: retry time
- `deadline_at`: maximum retry deadline
- `status`: `scheduled`, `leased`, `stopped`, `completed`
- `stop_reason`: nullable safe reason
- `policy_id`, `policy_version`: governing policy
- `created_at`, `updated_at`: timestamps

Validation rules:

- Non-retryable categories cannot enter `scheduled`.
- Attempt count cannot exceed policy budget.
- Tenant retry budget is consumed before scheduling.

### Circuit Breaker

Current state for a protected dependency or operation.

- `circuit_breaker_id`: UUID primary key
- `tenant_id`: nullable tenant scope
- `scope_type`: `dependency`, `tenant_dependency`, `workflow_step`,
  `artifact_operation`
- `scope_key`: dependency/operation key
- `state`: `closed`, `open`, `half_open`
- `reason_code`: latest transition reason
- `thresholds`: JSON threshold settings
- `cooldown_until`: nullable timestamp
- `probe_required`: boolean
- `half_open_tokens`: trial traffic tokens
- `policy_id`, `policy_version`: governing policy
- `last_transition_at`: timestamp

Validation rules:

- Open breakers block unsafe protected work.
- Half-open requires cooldown plus successful configured health/probe evidence.

### Circuit Breaker Event

Append-only transition and probe evidence for a breaker.

- `breaker_event_id`: UUID primary key
- `circuit_breaker_id`: breaker
- `tenant_id`: nullable tenant scope
- `from_state`, `to_state`: states
- `reason_code`: transition reason
- `probe_result`: nullable probe evidence summary
- `actor_id`: nullable operator/service actor
- `override_id`: nullable unsafe override
- `created_at`: timestamp

Validation rules:

- Operator resets require actor, reason, previous state, new state, and audit.

### Compensation Request

Durable compensation work derived from a side-effect intent.

- `compensation_request_id`: UUID primary key
- `tenant_id`: tenant owner
- `workflow_run_id`, `run_step_id`: affected work
- `side_effect_intent_id`: affected intent
- `hook_ref`: declared compensation hook
- `status`: `requested`, `queued`, `running`, `succeeded`, `failed`,
  `unavailable`, `timed_out`, `skipped_by_policy`,
  `manual_follow_up_required`
- `retry_schedule_id`: nullable retry schedule
- `dead_letter_id`: nullable dead-letter record
- `requested_at`, `updated_at`, `finished_at`: timestamps

Validation rules:

- Unique `(tenant_id, side_effect_intent_id, hook_ref)` for automatic
  compensation.
- Manual reattempt requires authorized operator action.

### Dead Letter Record

Inspectable terminal or intervention queue for exhausted/unsafe work.

- `dead_letter_id`: UUID primary key
- `tenant_id`: tenant owner
- `source_kind`: `queue_job`, `workflow_run`, `run_step`, `retry_schedule`,
  `compensation_request`, `artifact_export`
- `source_id`: source UUID
- `failure_category`: classified category
- `latest_state`: safe JSON summary
- `recommended_action`: `requeue`, `compensate`, `mark_resolved`,
  `operator_intervention`, `escalate`
- `artifact_refs`: JSON metadata references
- `policy_id`, `policy_version`: governing policy
- `status`: `open`, `requeued`, `compensating`, `resolved`, `escalated`
- `created_at`, `updated_at`, `resolved_at`: timestamps

Validation rules:

- Large evidence payloads use object storage refs.
- Every operator action is authorized and audited.

### Operational Control Change

Append-only record for changes to reliability settings.

- `control_change_id`: UUID primary key
- `tenant_id`: nullable scope
- `policy_id`: affected policy
- `actor_id`, `actor_role`: actor information
- `scope_type`, `scope_key`: affected scope
- `previous_value`, `new_value`: redacted JSON
- `validation_outcome`: `accepted`, `rejected`, `override_required`,
  `override_accepted`
- `reason`: operator reason
- `effective_at`, `created_at`: timestamps

Validation rules:

- Rejected and denied changes are auditable.
- Unsafe overrides require explicit authorization and reason.

### Artifact Throughput Window

Current throughput budget for object storage operations and exports.

- `artifact_window_id`: UUID primary key
- `tenant_id`: nullable tenant scope
- `operation`: `read`, `write`, `export`, `load_report`, `replay_evidence`
- `limit_value`, `inflight_value`, `queued_value`: counts
- `window_start`, `window_end`: window
- `breaker_id`: nullable protected operation breaker
- `updated_at`: timestamp

Validation rules:

- Artifact operations acquire budget before large transfer.
- Object storage overload can delay work or open a breaker.

### Resume Failure Injection Record

Test-only and load-test evidence for deterministic resume validation.

- `failure_injection_id`: UUID primary key
- `tenant_id`: tenant owner
- `workflow_run_id`: affected run
- `injection_point`: named boundary
- `seed`: deterministic workload seed
- `worker_id`: worker interrupted
- `expected_outcome`: expected safe recovery outcome
- `observed_outcome`: observed outcome
- `duplicate_side_effect_count`: count
- `stale_write_suppressed`: boolean
- `created_at`: timestamp

Validation rules:

- Acceptance load reports must include all required injection points.
- Any duplicate irreversible side effect fails validation.

## Relationships

- `Reliability Policy` governs decisions and state machines through
  `(policy_id, policy_version)` references.
- `Admission Decision`, `Retry Schedule`, `Circuit Breaker Event`,
  `Compensation Request`, `Dead Letter Record`, and `Operational Control Change`
  are audit-visible and tenant-scoped.
- `Compensation Request` references existing `Side-Effect Intent` and executes
  as durable runtime work.
- `Dead Letter Record` references queue jobs, workflow runs, run steps, retry
  schedules, compensation requests, or artifact exports.
- `Artifact Throughput Window` protects object storage operations used by
  failure inspection, replay evidence, load reports, and exports.

## State Transitions

### Admission

`submitted -> accepted | queued | delayed | throttled | rejected`

Delayed work becomes eligible at `available_at`; throttled/rejected work returns
safe retry metadata when policy permits.

### Retry

`scheduled -> leased -> completed`

`scheduled -> stopped` when attempts, deadline, breaker, quota, or safety
policy prevents another retry.

### Breaker

`closed -> open -> half_open -> closed`

`half_open -> open` on protected failure. Operator reset can transition to
`open`, `half_open`, or `closed` only with authorization and audit.

### Compensation

`requested -> queued -> running -> succeeded`

`running -> failed | unavailable | timed_out | skipped_by_policy |
manual_follow_up_required`

Failed or unsafe compensation can create a dead-letter record.

### Dead Letter

`open -> requeued | compensating | resolved | escalated`

Requeue and compensation actions create new durable work and preserve the
original record.

## Partitioning And Indexing

- Partition append-only decision/event/sample tables by `created_at` month or
  day depending on write volume.
- Add tenant-hash subpartitioning for high-volume admission, retry, breaker
  event, compensation event, dead-letter event, and load-test sample tables.
- Index current heads by `(tenant_id, scope_type, scope_key, status)` and
  `(tenant_id, workflow_run_id)`.
- Index inspection queries by `(tenant_id, created_at)`,
  `(tenant_id, failure_category, created_at)`, and
  `(tenant_id, decision, created_at)`.
