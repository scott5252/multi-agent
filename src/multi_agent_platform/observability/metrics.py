from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

REQUEST_COUNTER = Counter(
    "multi_agent_platform_requests_total",
    "Total requests handled by the platform.",
    labelnames=("route", "status"),
)

WORKFLOW_REGISTRY_ACTION_COUNTER = Counter(
    "multi_agent_platform_workflow_registry_actions_total",
    "Workflow registry actions by scope.",
    labelnames=("action", "scope_type"),
)

READINESS_GAUGE = Gauge(
    "multi_agent_platform_readiness",
    "Readiness state of the platform foundation.",
)

RUNTIME_ACTION_COUNTER = Counter(
    "multi_agent_platform_runtime_actions_total",
    "Durable runtime actions by action and status.",
    labelnames=("action", "status"),
)

RUNTIME_ACTIVE_LEASES_GAUGE = Gauge(
    "multi_agent_platform_runtime_active_leases",
    "Active durable orchestration worker leases.",
)

MEMORY_ACTION_COUNTER = Counter(
    "multi_agent_platform_memory_actions_total",
    "Immutable memory actions by action and outcome.",
    labelnames=("action", "outcome"),
)

MEMORY_CONFLICT_COUNTER = Counter(
    "multi_agent_platform_memory_conflicts_total",
    "Immutable memory conflicts by conflict type.",
    labelnames=("conflict_type",),
)

MEMORY_NOISY_NEIGHBOR_COUNTER = Counter(
    "multi_agent_platform_memory_budget_denials_total",
    "Tenant memory operation budget denials.",
    labelnames=("operation",),
)

CHANNEL_ACTION_COUNTER = Counter(
    "multi_agent_platform_channel_actions_total",
    "User interaction channel actions by channel, action, and outcome.",
    labelnames=("channel", "action", "outcome"),
)

CHANNEL_DELIVERY_ATTEMPT_COUNTER = Counter(
    "multi_agent_platform_channel_delivery_attempts_total",
    "Notification and callback delivery attempts by kind and outcome.",
    labelnames=("delivery_kind", "outcome"),
)

CHANNEL_TENANT_DELIVERY_BUDGET_GAUGE = Gauge(
    "multi_agent_platform_channel_tenant_delivery_budget",
    "Per-tenant delivery concurrency budget remaining.",
    labelnames=("tenant_id", "delivery_kind"),
)

MODEL_SKILL_POLICY_DECISION_COUNTER = Counter(
    "multi_agent_platform_model_skill_policy_decisions_total",
    "Model-skill policy allow and deny outcomes.",
    labelnames=("decision_category", "outcome", "denial_category"),
)

MODEL_SKILL_CONFIG_ACTION_COUNTER = Counter(
    "multi_agent_platform_model_skill_config_actions_total",
    "Model-skill configuration actions.",
    labelnames=("action", "config_kind", "outcome"),
)

AUDIT_CAPTURE_COUNTER = Counter(
    "multi_agent_platform_audit_capture_total",
    "Audit capture events by category, criticality, and outcome.",
    labelnames=("event_category", "criticality", "outcome"),
)

AUDIT_INSPECTION_DENIED_COUNTER = Counter(
    "multi_agent_platform_audit_inspection_denied_total",
    "Denied admin inspection attempts.",
    labelnames=("tenant_id", "action"),
)

AUDIT_LOOKUP_LATENCY = Histogram(
    "multi_agent_platform_audit_lookup_latency_seconds",
    "Run audit lookup latency.",
    labelnames=("lookup_type",),
)

AUDIT_EXPORT_COUNTER = Counter(
    "multi_agent_platform_audit_exports_total",
    "Debug evidence export lifecycle events.",
    labelnames=("tenant_id", "status"),
)

AUDIT_REDACTION_COUNTER = Counter(
    "multi_agent_platform_audit_redactions_total",
    "Redaction decisions by sensitivity label and action.",
    labelnames=("sensitivity_label", "action"),
)

RELIABILITY_DECISION_COUNTER = Counter(
    "multi_agent_platform_reliability_decisions_total",
    "Reliability admission and quota outcomes.",
    labelnames=("decision", "reason_code"),
)

RELIABILITY_QUEUE_DEPTH_GAUGE = Gauge(
    "multi_agent_platform_reliability_queue_depth",
    "Reliability queue depth by state.",
    labelnames=("state",),
)

RELIABILITY_LEASE_COUNTER = Counter(
    "multi_agent_platform_reliability_leases_total",
    "Reliability lease lifecycle events.",
    labelnames=("outcome",),
)

RELIABILITY_RETRY_COUNTER = Counter(
    "multi_agent_platform_reliability_retries_total",
    "Reliability retry decisions.",
    labelnames=("status", "reason"),
)

RELIABILITY_BREAKER_COUNTER = Counter(
    "multi_agent_platform_reliability_breakers_total",
    "Circuit breaker transitions and actions.",
    labelnames=("state", "reason"),
)

RELIABILITY_ARTIFACT_THROUGHPUT_COUNTER = Counter(
    "multi_agent_platform_reliability_artifact_throughput_total",
    "Artifact throughput budget outcomes.",
    labelnames=("operation_kind", "outcome"),
)


def record_model_skill_policy_decision(
    *, decision_category: str, outcome: str, denial_category: str | None = None
) -> None:
    MODEL_SKILL_POLICY_DECISION_COUNTER.labels(
        decision_category=decision_category,
        outcome=outcome,
        denial_category=denial_category or "none",
    ).inc()


def record_audit_capture(
    *, event_category: str, criticality: str, outcome: str
) -> None:
    AUDIT_CAPTURE_COUNTER.labels(
        event_category=event_category, criticality=criticality, outcome=outcome
    ).inc()


def record_audit_denied_inspection(*, tenant_id: str | None, action: str) -> None:
    AUDIT_INSPECTION_DENIED_COUNTER.labels(
        tenant_id=tenant_id or "none", action=action
    ).inc()


def record_audit_export(*, tenant_id: str | None, status: str) -> None:
    AUDIT_EXPORT_COUNTER.labels(tenant_id=tenant_id or "none", status=status).inc()


def record_audit_redaction(*, sensitivity_label: str, action: str) -> None:
    AUDIT_REDACTION_COUNTER.labels(
        sensitivity_label=sensitivity_label, action=action
    ).inc()


def record_reliability_decision(*, decision: str, reason_code: str) -> None:
    RELIABILITY_DECISION_COUNTER.labels(
        decision=decision, reason_code=reason_code
    ).inc()


def set_reliability_queue_depth(*, state: str, depth: int) -> None:
    RELIABILITY_QUEUE_DEPTH_GAUGE.labels(state=state).set(depth)


def record_reliability_retry(*, status: str, reason: str | None = None) -> None:
    RELIABILITY_RETRY_COUNTER.labels(status=status, reason=reason or "none").inc()


def record_reliability_breaker(*, state: str, reason: str) -> None:
    RELIABILITY_BREAKER_COUNTER.labels(state=state, reason=reason).inc()


def record_reliability_artifact_throughput(
    *, operation_kind: str, outcome: str
) -> None:
    RELIABILITY_ARTIFACT_THROUGHPUT_COUNTER.labels(
        operation_kind=operation_kind, outcome=outcome
    ).inc()
