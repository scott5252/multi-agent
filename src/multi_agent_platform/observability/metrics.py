from __future__ import annotations

from prometheus_client import Counter, Gauge

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
