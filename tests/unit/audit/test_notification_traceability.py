from __future__ import annotations

from multi_agent_platform.channels.notifications import notification_audit_summary


def test_notification_traceability_summary_is_safe() -> None:
    summary = notification_audit_summary(
        destination_category="telegram",
        delivery_status="retrying",
        attempt_count=2,
        provider_correlation_ref="provider-ref",
        safe_failure_reason="transient provider failure",
    )
    assert summary["destination_category"] == "telegram"
    assert summary["attempt_count"] == 2
    assert "@" not in str(summary)
