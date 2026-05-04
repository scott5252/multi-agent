from __future__ import annotations

import pytest

from multi_agent_platform.admin.briefing_preferences.models import (
    BriefingPreferenceAccessScope,
    BriefingPreferencePayload,
    BriefingPreferencePermissionError,
    BriefingPreferenceScopeType,
)
from multi_agent_platform.admin.briefing_preferences.redaction import (
    safe_reference_label,
)
from multi_agent_platform.admin.briefing_preferences.service import (
    BriefingPreferenceService,
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


def test_payload_rejects_invalid_timezone_and_raw_credentials() -> None:
    with pytest.raises(ValueError, match="IANA timezone"):
        BriefingPreferencePayload.model_validate(
            {
                "location_label": "Providence",
                "timezone": "Mars/Base",
                "calendar_account_ref": "delegated:calendar:primary",
                "email_account_ref": "delegated:gmail:primary",
            }
        )
    with pytest.raises(ValueError, match="raw credentials"):
        BriefingPreferencePayload.model_validate(
            {
                "location_label": "Providence",
                "timezone": "America/New_York",
                "calendar_account_ref": "Bearer abc",
                "email_account_ref": "delegated:gmail:primary",
            }
        )


def test_safe_reference_label_masks_reference_detail() -> None:
    assert safe_reference_label("delegated:gmail:primary") == "delegated:***"


async def test_service_import_rejects_cross_principal_document(
    session,
    seeded_tenant,
) -> None:
    service = BriefingPreferenceService(BriefingPreferenceRepository(session))
    scope = BriefingPreferenceAccessScope(
        scope_type=BriefingPreferenceScopeType.TENANT,
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin-acme",
        trace_id="trace-test",
    )

    with pytest.raises(BriefingPreferencePermissionError):
        await service.import_own_profile(
            access_scope=scope,
            document={
                "schema_version": "1.0",
                "tenant_id": str(seeded_tenant.tenant_id),
                "principal_id": "other-user",
                "preferences": {},
            },
            revision_token=None,
        )


async def test_service_exports_imports_and_lists_safe_summaries(
    session,
    seeded_tenant,
) -> None:
    service = BriefingPreferenceService(BriefingPreferenceRepository(session))
    scope = BriefingPreferenceAccessScope(
        scope_type=BriefingPreferenceScopeType.TENANT,
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin-acme",
        trace_id="trace-test",
    )

    missing = await service.get_own_profile(scope)
    saved = await service.save_own_profile(
        access_scope=scope,
        payload=_payload(),
        revision_token=None,
    )
    exported = await service.export_own_profile(scope)
    summaries = await service.list_summaries(scope)
    document = dict(exported.document)
    preferences = dict(document["preferences"])
    preferences["output_style"] = "executive"
    document["preferences"] = preferences
    imported = await service.import_own_profile(
        access_scope=scope,
        document=document,
        revision_token=saved.profile.revision_token,
    )

    assert missing is None
    assert exported.document["principal_id"] == "tenant-admin-acme"
    assert len(summaries) == 1
    assert summaries[0].safe_summary["vip_sender_preview"] == ["s***@example.com"]
    assert imported.profile.output_style == "executive"


async def test_service_export_missing_profile_raises_lookup_error(
    session,
    seeded_tenant,
) -> None:
    service = BriefingPreferenceService(BriefingPreferenceRepository(session))
    scope = BriefingPreferenceAccessScope(
        scope_type=BriefingPreferenceScopeType.TENANT,
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin-acme",
        trace_id="trace-test",
    )

    with pytest.raises(LookupError):
        await service.export_own_profile(scope)
