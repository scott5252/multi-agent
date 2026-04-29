from __future__ import annotations

from multi_agent_platform.admin.skill_registry.audit import (
    build_lifecycle_audit_event,
    redact_for_audit,
    safe_export,
)


def test_audit_redacts_secret_values_and_payloads() -> None:
    redacted = redact_for_audit(
        {
            "credential_value": "super-secret",
            "nested": {"api_token": "sk-secret1234567890"},
            "safe": "calendar-assistant",
        }
    )

    assert redacted["credential_value"] == "[REDACTED]"
    assert redacted["nested"]["api_token"] == "[REDACTED]"
    assert redacted["safe"] == "calendar-assistant"


def test_safe_export_uses_redacted_summary() -> None:
    event = build_lifecycle_audit_event(
        event_type="skill.published",
        actor_principal_id="admin",
        outcome="passed",
        summary={"raw_payload": {"secret": "value"}, "slug": "calendar-assistant"},
    )

    exported = safe_export([event])

    assert exported[0]["safe_summary"]["raw_payload"] == "[REDACTED]"
    assert exported[0]["safe_summary"]["slug"] == "calendar-assistant"
