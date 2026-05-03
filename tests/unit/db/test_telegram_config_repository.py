from __future__ import annotations

import pytest

from multi_agent_platform.admin.telegram_config.models import (
    TelegramConfigStaleRevisionError,
    TelegramDiagnosticCategory,
    TelegramDiagnosticStatus,
)
from multi_agent_platform.db.repositories.telegram_config import (
    TelegramConfigRepository,
)


async def test_telegram_config_repository_updates_with_revision(
    session,
    seeded_tenant,
) -> None:
    repository = TelegramConfigRepository(session)
    config = await repository.get_or_create_tenant_config(
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin",
    )
    original_revision = config.revision_token
    updated = await repository.update_tenant_config(
        tenant_id=seeded_tenant.tenant_id,
        enabled=True,
        protected_commands=["/run", "/status"],
        status_note="Ready for tenant QA",
        expected_revision_token=original_revision,
        principal_id="tenant-admin",
    )

    assert updated.enabled is True
    assert updated.protected_commands == ["/run", "/status"]
    assert updated.revision_token != original_revision

    with pytest.raises(TelegramConfigStaleRevisionError):
        await repository.update_tenant_config(
            tenant_id=seeded_tenant.tenant_id,
            enabled=False,
            protected_commands=["/run"],
            status_note=None,
            expected_revision_token="stale",
            principal_id="tenant-admin",
        )


async def test_telegram_repository_filters_tokens_identities_and_diagnostics(
    session,
    seeded_tenant,
) -> None:
    repository = TelegramConfigRepository(session)
    diagnostic = await repository.add_diagnostic(
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin",
        category=TelegramDiagnosticCategory.WEBHOOK_VALIDATION,
        status=TelegramDiagnosticStatus.OK,
        summary="Webhook validation completed.",
        trace_id="trace-1",
        redacted_metadata={"external_call_performed": False},
    )
    identity = await repository.upsert_identity_summary(
        tenant_id=seeded_tenant.tenant_id,
        platform_identity_id="tenant-admin",
        telegram_user_fingerprint="user-hash",
        telegram_chat_fingerprint="chat-hash",
        telegram_user_display="123***789",
        telegram_chat_display="987***321",
        command_ready=True,
        trace_id="trace-1",
    )

    assert (
        await repository.list_diagnostics(
            tenant_id=seeded_tenant.tenant_id,
            platform_scope=False,
        )
    ) == [diagnostic]
    assert await repository.list_identity_summaries(
        tenant_id=seeded_tenant.tenant_id
    ) == [identity]
