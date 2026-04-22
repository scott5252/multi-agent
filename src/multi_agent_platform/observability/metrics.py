from __future__ import annotations

from prometheus_client import Counter, Gauge

REQUEST_COUNTER = Counter(
    "multi_agent_platform_requests_total",
    "Total requests handled by the platform.",
    labelnames=("route", "status"),
)

READINESS_GAUGE = Gauge(
    "multi_agent_platform_readiness",
    "Readiness state of the platform foundation.",
)
