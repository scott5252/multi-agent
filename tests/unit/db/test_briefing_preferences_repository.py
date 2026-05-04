from __future__ import annotations

import pytest

from multi_agent_platform.admin.briefing_preferences.models import (
    BriefingPreferenceAction,
    BriefingPreferenceDecision,
    BriefingPreferencePayload,
    BriefingPreferenceStaleRevisionError,
)
from multi_agent_platform.db.repositories.briefing_preferences import (
    BriefingPreferenceRepository,
)


def _payload() -> BriefingPreferencePayload:
    return BriefingPreferencePayload.model_validate(
        {
            "location_label": "Providence, RI",
            "timezone": "America/New_York",
            "news_topics": ["AI", "markets"],
            "vip_senders": ["sarah@example.com"],
            "workday_start": "09:00",
            "workday_end": "17:30",
            "commute_mode": "driving",
            "calendar_account_ref": "delegated:calendar:primary",
            "email_account_ref": "delegated:gmail:primary",
            "output_style": "standard",
            "scheduled_enabled": True,
            "scheduled_time": "08:00",
        }
    )


async def test_repository_upserts_head_and_appends_revisions(
    session,
    seeded_tenant,
) -> None:
    repository = BriefingPreferenceRepository(session)
    profile, first, created = await repository.upsert_profile(
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin-acme",
        payload=_payload(),
        expected_revision_token=None,
        actor_principal_id="tenant-admin-acme",
        trace_id="trace-1",
    )
    original_token = profile.revision_token
    profile, second, updated_created = await repository.upsert_profile(
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin-acme",
        payload=_payload().model_copy(update={"output_style": "executive"}),
        expected_revision_token=original_token,
        actor_principal_id="tenant-admin-acme",
        trace_id="trace-2",
    )

    assert created is True
    assert updated_created is False
    assert profile.current_revision_id == second.briefing_preference_revision_id
    assert (
        first.briefing_preference_revision_id != second.briefing_preference_revision_id
    )
    assert profile.revision_number == 2
    assert profile.safe_summary["vip_sender_preview"] == ["s***@example.com"]

    with pytest.raises(BriefingPreferenceStaleRevisionError):
        await repository.upsert_profile(
            tenant_id=seeded_tenant.tenant_id,
            principal_id="tenant-admin-acme",
            payload=_payload(),
            expected_revision_token="stale",
            actor_principal_id="tenant-admin-acme",
            trace_id="trace-3",
        )


async def test_repository_filters_summaries_by_tenant(session, seeded_tenant) -> None:
    repository = BriefingPreferenceRepository(session)
    await repository.upsert_profile(
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin-acme",
        payload=_payload(),
        expected_revision_token=None,
        actor_principal_id="tenant-admin-acme",
        trace_id="trace-1",
    )

    assert (
        len(
            await repository.list_profiles(
                tenant_id=seeded_tenant.tenant_id,
                platform_scope=False,
            )
        )
        == 1
    )
    assert (
        await repository.get_profile(
            tenant_id=seeded_tenant.tenant_id,
            principal_id="missing",
        )
        is None
    )


async def test_repository_filters_platform_profiles_and_audit_events(
    session,
    seeded_tenant,
) -> None:
    repository = BriefingPreferenceRepository(session)
    await repository.upsert_profile(
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin-acme",
        payload=_payload(),
        expected_revision_token=None,
        actor_principal_id="tenant-admin-acme",
        trace_id="trace-1",
    )
    audit = await repository.add_audit_event(
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin-acme",
        actor_principal_id="platform-admin",
        action=BriefingPreferenceAction.PROFILE_SUMMARY_READ,
        decision=BriefingPreferenceDecision.ALLOW,
        summary="safe summary inspected",
        trace_id="trace-audit",
        redacted_metadata={"secret_token": "raw-token", "status": "ok"},
    )

    platform_profiles = await repository.list_profiles(
        tenant_id=seeded_tenant.tenant_id,
        platform_scope=True,
    )
    tenant_events = await repository.list_audit_events(
        tenant_id=seeded_tenant.tenant_id,
        platform_scope=False,
    )
    platform_events = await repository.list_audit_events(
        tenant_id=seeded_tenant.tenant_id,
        platform_scope=True,
    )

    assert len(platform_profiles) == 1
    assert tenant_events == [audit]
    assert platform_events == [audit]
    assert audit.redacted_metadata["secret_token"] == "redacted"
