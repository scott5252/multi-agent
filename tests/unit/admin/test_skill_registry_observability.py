from __future__ import annotations

from multi_agent_platform.admin.skill_registry.observability import (
    SkillRegistryTraceContext,
    safe_log_context,
)


def test_observability_context_redacts_extra_values() -> None:
    context = SkillRegistryTraceContext(
        trace_id="trace-1",
        tenant_id="tenant-1",
        package_slug="calendar-assistant",
        extra={"credential_value": "secret"},
    )

    safe = safe_log_context(context)

    assert safe["tenant_id"] == "tenant-1"
    assert safe["extra"]["credential_value"] == "[REDACTED]"
