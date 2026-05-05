from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from multi_agent_platform.api.schemas.admin_channel_telegram_briefing_react import (
    BriefingOutputStyle,
    BriefingPreferenceProfile,
    ChannelMutationStatus,
    ChannelReadinessStatus,
    ChannelTelegramBriefingDashboard,
    ChannelTelegramReadiness,
    CommuteMode,
    LinkTokenResult,
    TelegramTenantConfiguration,
    WebhookDiagnosticStatus,
    safe_channel_text,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)


def test_safe_channel_text_rejects_unsafe_markers() -> None:
    for marker in (
        "qa036-secret-value",
        "bot token",
        "webhook secret",
        "full telegram user id",
        "private message",
        "raw preference value",
        "raw prompt",
        "run result",
        "raw tool payload",
        "/Users/scott/project",
    ):
        with pytest.raises(ValueError):
            safe_channel_text(marker)


def test_link_token_is_only_allowed_for_immediate_result() -> None:
    now = datetime.now(UTC)
    immediate = LinkTokenResult(
        link_token_request_id="link-token-request",
        token_value="pair-code-10-qa036",
        masked_status="Visible once.",
        expires_at=now + timedelta(minutes=10),
        next_step="Share before expiration.",
        audit_reference="audit-link-token",
        display_mode="immediate",
    )

    assert immediate.token_value == "pair-code-10-qa036"
    with pytest.raises(ValueError):
        LinkTokenResult(
            link_token_request_id="link-token-request",
            token_value="pair-code-10-qa036",
            masked_status="Hidden later.",
            expires_at=now + timedelta(minutes=10),
            next_step="Create a new code.",
            audit_reference="audit-link-token",
            display_mode="masked",
        )


def test_dashboard_accepts_safe_minimal_payload() -> None:
    now = datetime.now(UTC)
    scope = ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id=UUID("11111111-1111-1111-1111-111111111111"),
        label="Acme",
    )
    dashboard = ChannelTelegramBriefingDashboard(
        page_id="qa036",
        title="Channel, Telegram, and Briefing Preferences",
        description="Safe dashboard.",
        scope=scope,
        readiness=(
            ChannelTelegramReadiness(
                readiness_id="readiness-acme",
                status=ChannelReadinessStatus.READY,
                channel_label="Telegram",
                tenant_label="Acme",
                telegram_enabled=True,
                webhook_status=WebhookDiagnosticStatus.VALID,
                secret_reference_status=ChannelReadinessStatus.READY,
                linked_identity_count=1,
                alias_count=1,
                delivery_health_label="Healthy delivery evidence.",
                preference_resolver_label="Resolver ready.",
                audit_reference="audit-readiness",
                next_step="Review validation.",
            ),
        ),
        tenant_configs=(
            TelegramTenantConfiguration(
                tenant_id=UUID("11111111-1111-1111-1111-111111111111"),
                tenant_label="Acme",
                enabled=True,
                bot_token_reference_label="Telegram provider ref ready",
                webhook_signing_reference_label="Webhook signing ref ready",
                webhook_url_status=ChannelReadinessStatus.READY,
                revision="rev",
                audit_reference="audit-config",
            ),
        ),
        preference_profiles={
            "current_user_profile": BriefingPreferenceProfile(
                profile_id="profile",
                tenant_label="Acme",
                principal_label="tenant-user-acme",
                timezone="America/New_York",
                location_summary="Region summary",
                news_topics_summary="3 topic categories",
                vip_sender_summary="2 masked sender hints",
                workday_hours="08:30-17:30",
                commute_mode=CommuteMode.TRANSIT,
                default_account_summary="2 masked account refs",
                output_style=BriefingOutputStyle.EXECUTIVE,
                revision="pref-rev",
                runtime_ready=True,
                audit_reference="audit-pref",
            ),
            "admin_summaries": [],
            "import_export_evidence": [],
        },
        updated_at=now,
    )

    assert dashboard.readiness[0].status is ChannelReadinessStatus.READY


def test_mutation_status_enum_covers_fail_closed_states() -> None:
    assert ChannelMutationStatus.DENIED.value == "denied"
    assert ChannelMutationStatus.AUDIT_UNAVAILABLE.value == "audit_unavailable"
