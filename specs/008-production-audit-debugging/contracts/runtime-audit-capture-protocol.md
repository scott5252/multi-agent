# Contract: Runtime Audit Capture Protocol

This protocol defines how runtime orchestration, memory, channels, model
routing, tool execution, and secret resolution emit audit and trace evidence.

## Common Capture Envelope

**Caller**: Runtime, channel, memory, model routing, tool policy, notification,
or admin inspection service.

**Operation**: `AuditCaptureService.record_event(request)`

**Request fields**:

- `tenant_id`
- `workflow_run_id`
- `parent_run_id`
- `run_step_id`
- `timeline_event_category`
- `run_status_after`
- `origin_type`
- `origin_ref`
- `actor_principal_id`
- `trace_id`
- `correlation_id`
- `source_event_id`
- `criticality`
- `occurred_at`
- `safe_summary`
- `details`
- `field_classifications`
- `idempotency_key`

**Response fields**:

- `timeline_event_id`
- `sequence`
- `recorded_at`
- `capture_outcome`
- `redaction_decisions`
- `unavailable_marker_id`

**Rules**:

- `criticality = security_governance` must be durably recorded before the
  protected action proceeds.
- `criticality = diagnostic` may return `capture_outcome = unavailable` only
  after a CaptureGapMarker is recorded.
- `details` must pass classification before persistence. Unknown dynamic
  fields are redacted by default.
- Idempotent retries return the first persisted event for the same
  `(tenant_id, workflow_run_id, source_event_id, timeline_event_category)`.

## Linked Trace Records

**Operation**: `AuditCaptureService.record_trace(request)`

**Request fields**:

- `tenant_id`
- `workflow_run_id`
- `timeline_event_id`
- `run_step_id`
- `trace_type`
- `trace_id`
- `correlation_id`
- `status`
- `outcome`
- `duration_ms`
- `policy_outcome`
- `subject_ref`
- `safe_input_summary`
- `safe_output_summary`
- `safe_error_summary`
- `metadata`
- `field_classifications`

**Rules**:

- Trace records must link to an existing timeline event in the same tenant.
- Trace types are `agent_handoff`, `contract_validation`, `memory_write`,
  `tool_usage`, `model_selection`, `notification_delivery`,
  `secret_access`, or `capture_gap`.
- Tool, model, notification, and secret records must store safe references and
  policy outcomes before external side effects proceed when the decision is
  security-sensitive.

## Lifecycle Events

Runtime orchestration emits lifecycle timeline events for:

- `accepted`
- `queued`
- `started`
- `waiting`
- `resumed`
- `retried`
- `completed`
- `cancelled`
- `failed`
- `timed_out`

Every terminal event includes a safe terminal summary. Failed events include
failed stage, safe failure reason, related event id when available, and
recommended investigation category.

## Runtime Decision Events

The runtime emits linked traces for:

- Agent handoff source, destination, reason, outcome, and safe payload metadata.
- Contract validation contract identity, related step, outcome, and safe error
  summary.
- Memory write scope, intent, requested/effective version refs, outcome, and
  safe summary.
- Tool identity, action category, policy outcome, execution outcome, duration,
  and safe input/output summaries.
- Model selection provider/model, selection source, prompt/config version refs,
  outcome, and safe trace metadata.
- Notification destination category, status, attempt count, latest attempt
  time, triggering event, and safe failure reason.
- Secret requester, secret reference metadata, policy outcome, reason, and run
  context without raw values.

## Capture Failure Semantics

- Security/governance failures return a blocking error category such as
  `audit_write_unavailable`, `classification_failed`,
  `secret_audit_unavailable`, or `inspection_denial_audit_unavailable`.
- Diagnostic failures record a CaptureGapMarker and return the marker id to
  the caller.
- Capture gaps appear in timeline, replay, metrics, and exports.
- No capture failure may write raw sensitive payloads to logs while reporting
  the failure.

## Structured Logging And Metrics

Every successful capture emits a structured log entry and increments event
counters with `tenant_id`, `workflow_run_id`, `trace_id`, `event_category`,
`trace_type`, and `criticality` labels where safe. Latency histograms record
capture write duration, timeline assembly duration, replay assembly duration,
direct lookup duration, search duration, and export generation duration.
