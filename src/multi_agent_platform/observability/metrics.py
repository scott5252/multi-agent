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
