from __future__ import annotations

from multi_agent_platform.admin.briefing_preferences.models import (
    BriefingPreferencePayload,
)
from multi_agent_platform.admin.briefing_preferences.service import (
    BriefingPreferenceService,
)
from multi_agent_platform.db.repositories.briefing_preferences import (
    BriefingPreferenceRepository,
)
from multi_agent_platform.runtime.briefing_preferences import (
    resolve_briefing_preferences,
)


async def test_runtime_resolver_returns_pinned_context(session, seeded_tenant) -> None:
    repository = BriefingPreferenceRepository(session)
    payload = BriefingPreferencePayload.model_validate(
        {
            "location_label": "Providence, RI",
            "timezone": "America/New_York",
            "news_topics": ["AI"],
            "vip_senders": ["sarah@example.com"],
            "calendar_account_ref": "delegated:calendar:primary",
            "email_account_ref": "delegated:gmail:primary",
        }
    )
    await repository.upsert_profile(
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin-acme",
        payload=payload,
        expected_revision_token=None,
        actor_principal_id="tenant-admin-acme",
        trace_id="trace-save",
    )

    context = await resolve_briefing_preferences(
        repository=repository,
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin-acme",
        source_channel="telegram",
        trace_id="trace-resolve",
    )

    assert context.available is True
    assert context.revision_id is not None
    assert context.preferences is not None
    assert context.preferences["timezone"] == "America/New_York"
    assert context.safe_summary is not None
    assert context.safe_summary["vip_sender_preview"] == ["s***@example.com"]


async def test_runtime_resolver_records_missing_without_private_data(
    session,
    seeded_tenant,
) -> None:
    repository = BriefingPreferenceRepository(session)
    context = await BriefingPreferenceService(repository).resolve_runtime_context(
        tenant_id=seeded_tenant.tenant_id,
        principal_id="missing",
        source_channel="telegram",
        trace_id="trace-missing",
    )

    assert context.available is False
    assert context.preferences is None
    assert context.reason == "missing_profile"
