from __future__ import annotations

import json
import logging

from multi_agent_platform.observability.logging import JsonFormatter
from multi_agent_platform.observability.metrics import READINESS_GAUGE, REQUEST_COUNTER
from multi_agent_platform.observability.tracing import generate_trace_id


def test_json_formatter_includes_redacted_extra_payload() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="multi_agent_platform",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.extra = {"token": "secret", "plain": "ok"}
    payload = json.loads(formatter.format(record))
    assert payload["token"] == "***REDACTED***"
    assert payload["plain"] == "ok"


def test_metrics_and_tracing_helpers_are_available() -> None:
    REQUEST_COUNTER.labels(route="/health/live", status="200")
    READINESS_GAUGE.set(1)
    assert len(generate_trace_id()) == 32
