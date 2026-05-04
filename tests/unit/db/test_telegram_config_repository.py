from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from multi_agent_platform.admin.telegram_config.models import (
    TelegramConfigStaleRevisionError,
    TelegramDiagnosticCategory,
    TelegramDiagnosticStatus,
    TelegramIdentityStatus,
    TelegramLinkTokenStatus,
)
from multi_agent_platform.admin.telegram_config.redaction import fingerprint_value
from multi_agent_platform.db.models.telegram_config import TelegramLinkTokenAudit
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


async def test_telegram_alias_repository_normalizes_and_rejects_stale_revision(
    session,
    seeded_tenant,
) -> None:
    repository = TelegramConfigRepository(session)
    workflow_version_id = uuid4()
    alias = await repository.upsert_alias(
        tenant_id=seeded_tenant.tenant_id,
        alias_text="  Morning   Briefing ",
        published_workflow_version_id=workflow_version_id,
        description="Daily Intelligence Briefing",
        protected=True,
        enabled=True,
        expected_revision_token=None,
        principal_id="tenant-admin",
    )

    assert alias.alias_text == "Morning   Briefing"
    assert alias.alias_normalized == "morning briefing"
    assert (
        await repository.find_enabled_alias(
            tenant_id=seeded_tenant.tenant_id,
            alias_text="morning briefing",
        )
        == alias
    )

    with pytest.raises(TelegramConfigStaleRevisionError):
        await repository.upsert_alias(
            tenant_id=seeded_tenant.tenant_id,
            alias_text="Morning briefing",
            published_workflow_version_id=workflow_version_id,
            description=None,
            protected=True,
            enabled=False,
            expected_revision_token="stale",
            principal_id="tenant-admin",
        )


async def test_telegram_alias_repository_handles_edge_paths(
    session,
    seeded_tenant,
) -> None:
    repository = TelegramConfigRepository(session)
    workflow_version_id = uuid4()

    with pytest.raises(ValueError, match="alias text is required"):
        await repository.upsert_alias(
            tenant_id=seeded_tenant.tenant_id,
            alias_text="   ",
            published_workflow_version_id=workflow_version_id,
            description=None,
            protected=True,
            enabled=True,
            expected_revision_token=None,
            principal_id="tenant-admin",
        )
    with pytest.raises(ValueError, match="alias text is too long"):
        await repository.upsert_alias(
            tenant_id=seeded_tenant.tenant_id,
            alias_text="x" * 121,
            published_workflow_version_id=workflow_version_id,
            description=None,
            protected=True,
            enabled=True,
            expected_revision_token=None,
            principal_id="tenant-admin",
        )

    alias = await repository.upsert_alias(
        tenant_id=seeded_tenant.tenant_id,
        alias_text="Morning briefing",
        published_workflow_version_id=workflow_version_id,
        description="Initial",
        protected=True,
        enabled=False,
        expected_revision_token=None,
        principal_id="tenant-admin",
    )
    assert (
        await repository.find_enabled_alias(
            tenant_id=seeded_tenant.tenant_id,
            alias_text="",
        )
        is None
    )
    assert (
        await repository.find_enabled_alias(
            tenant_id=seeded_tenant.tenant_id,
            alias_text="Morning briefing",
        )
        is None
    )
    assert (
        await repository.get_alias(
            tenant_id=seeded_tenant.tenant_id,
            alias_id=alias.telegram_command_alias_id,
        )
        == alias
    )

    updated = await repository.upsert_alias(
        tenant_id=seeded_tenant.tenant_id,
        alias_text=" Morning briefing ",
        published_workflow_version_id=workflow_version_id,
        description="Updated",
        protected=False,
        enabled=True,
        expected_revision_token=alias.revision_token,
        principal_id="tenant-admin",
    )

    assert updated.description == "Updated"
    assert updated.protected is False
    assert await repository.list_aliases(tenant_id=seeded_tenant.tenant_id) == [updated]


async def test_telegram_repository_consumes_tokens_and_replays_update_receipts(
    session,
    seeded_tenant,
) -> None:
    repository = TelegramConfigRepository(session)
    now = datetime.now(UTC)
    token = "qa-token"
    audit = TelegramLinkTokenAudit(
        tenant_id=seeded_tenant.tenant_id,
        issued_by_principal_id="tenant-admin",
        token_fingerprint=fingerprint_value(token),
        status=TelegramLinkTokenStatus.ISSUED.value,
        expires_at=now + timedelta(minutes=10),
        trace_id="trace-token",
    )
    session.add(audit)
    await session.flush()

    consumed = await repository.consume_token_audit_by_fingerprint(
        token_fingerprint=fingerprint_value(token),
        now=now,
    )
    receipt = await repository.add_update_receipt(
        telegram_update_id=22001,
        tenant_id=seeded_tenant.tenant_id,
        platform_identity_id="tenant-admin",
        telegram_chat_fingerprint="chat-hash",
        action_type="alias",
        response_payload={"ok": True, "run_id": "run-1"},
        run_id=None,
        delivery_attempt_id=None,
        trace_id="trace-receipt",
    )
    replay = await repository.add_update_receipt(
        telegram_update_id=22001,
        tenant_id=seeded_tenant.tenant_id,
        platform_identity_id="tenant-admin",
        telegram_chat_fingerprint="chat-hash",
        action_type="alias",
        response_payload={"ok": False},
        run_id=None,
        delivery_attempt_id=None,
        trace_id="trace-receipt",
    )

    assert consumed is audit
    assert audit.status == TelegramLinkTokenStatus.CONSUMED.value
    assert receipt is replay
    assert (await repository.get_update_receipt(22001)).response_payload["ok"] is True


async def test_telegram_repository_token_identity_and_diagnostic_edges(
    session,
    seeded_tenant,
) -> None:
    repository = TelegramConfigRepository(session)
    now = datetime.now(UTC)
    expired = TelegramLinkTokenAudit(
        tenant_id=seeded_tenant.tenant_id,
        issued_by_principal_id="tenant-admin",
        token_fingerprint="expired-token",
        status=TelegramLinkTokenStatus.ISSUED.value,
        expires_at=(now - timedelta(minutes=1)).replace(tzinfo=None),
        trace_id="trace-expired",
    )
    revoked = TelegramLinkTokenAudit(
        tenant_id=seeded_tenant.tenant_id,
        issued_by_principal_id="tenant-admin",
        token_fingerprint="revoked-token",
        status=TelegramLinkTokenStatus.REVOKED.value,
        expires_at=now + timedelta(minutes=1),
        trace_id="trace-revoked",
    )
    session.add_all([expired, revoked])
    await session.flush()

    identity = await repository.upsert_identity_summary(
        tenant_id=seeded_tenant.tenant_id,
        platform_identity_id="tenant-admin",
        telegram_user_fingerprint="user-hash",
        telegram_chat_fingerprint="chat-hash",
        telegram_user_display="123***789",
        telegram_chat_display="987***321",
        command_ready=True,
        trace_id="trace-identity",
    )
    diagnostic = await repository.add_diagnostic(
        tenant_id=seeded_tenant.tenant_id,
        principal_id="tenant-admin",
        category=TelegramDiagnosticCategory.IDENTITY,
        status=TelegramDiagnosticStatus.OK,
        summary="Identity ready.",
        trace_id="trace-diagnostic",
    )

    assert (
        await repository.consume_token_audit_by_fingerprint(
            token_fingerprint="missing",
            now=now,
        )
        is None
    )
    assert (
        await repository.consume_token_audit_by_fingerprint(
            token_fingerprint="expired-token",
            now=now,
        )
        is None
    )
    assert expired.status == TelegramLinkTokenStatus.EXPIRED.value
    assert (
        await repository.consume_token_audit_by_fingerprint(
            token_fingerprint="revoked-token",
            now=now,
        )
        is None
    )
    assert (
        await repository.get_identity_summary_by_fingerprints(
            tenant_id=seeded_tenant.tenant_id,
            telegram_user_fingerprint="user-hash",
            telegram_chat_fingerprint="chat-hash",
        )
        == identity
    )
    refreshed = await repository.upsert_identity_summary(
        tenant_id=seeded_tenant.tenant_id,
        platform_identity_id="tenant-admin-2",
        telegram_user_fingerprint="user-hash",
        telegram_chat_fingerprint="chat-hash",
        telegram_user_display="123***789",
        telegram_chat_display="987***321",
        command_ready=False,
        trace_id="trace-identity-2",
    )
    assert refreshed.platform_identity_id == "tenant-admin-2"
    assert refreshed.status == TelegramIdentityStatus.LINKED.value
    assert (
        await repository.revoke_identity(
            identity_id=uuid4(),
            tenant_id=seeded_tenant.tenant_id,
            principal_id="tenant-admin",
        )
        is None
    )
    assert await repository.list_diagnostics(
        tenant_id=seeded_tenant.tenant_id,
        platform_scope=True,
    ) == [diagnostic]
