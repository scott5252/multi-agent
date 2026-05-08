from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.telegram_config.models import (
    PROTECTED_TELEGRAM_COMMANDS,
    TelegramConfigStaleRevisionError,
    TelegramDiagnosticCategory,
    TelegramDiagnosticStatus,
    TelegramIdentityStatus,
    TelegramLinkTokenStatus,
    normalize_alias_text,
)
from multi_agent_platform.admin.telegram_config.redaction import sanitize_text
from multi_agent_platform.db.models.telegram_config import (
    TelegramCommandAlias,
    TelegramDiagnosticEvent,
    TelegramLinkedIdentitySummary,
    TelegramLinkTokenAudit,
    TelegramTenantConfiguration,
    TelegramUpdateReceipt,
)


class TelegramConfigRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_tenant_config(
        self, tenant_id: UUID
    ) -> TelegramTenantConfiguration | None:
        stmt = select(TelegramTenantConfiguration).where(
            TelegramTenantConfiguration.tenant_id == tenant_id
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_or_create_tenant_config(
        self, *, tenant_id: UUID, principal_id: str
    ) -> TelegramTenantConfiguration:
        existing = await self.get_tenant_config(tenant_id)
        if existing is not None:
            return existing
        record = TelegramTenantConfiguration(
            tenant_id=tenant_id,
            enabled=False,
            protected_commands=list(PROTECTED_TELEGRAM_COMMANDS),
            status_note="Telegram is not enabled for this tenant.",
            revision_token=uuid4().hex,
            updated_by_principal_id=principal_id,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def update_tenant_config(
        self,
        *,
        tenant_id: UUID,
        enabled: bool,
        protected_commands: list[str],
        status_note: str | None,
        expected_revision_token: str | None,
        principal_id: str,
    ) -> TelegramTenantConfiguration:
        record = await self.get_or_create_tenant_config(
            tenant_id=tenant_id,
            principal_id=principal_id,
        )
        if expected_revision_token and record.revision_token != expected_revision_token:
            raise TelegramConfigStaleRevisionError("stale Telegram config revision")
        record.enabled = enabled
        record.protected_commands = protected_commands
        record.status_note = sanitize_text(status_note, max_length=500) or None
        record.revision_token = uuid4().hex
        record.updated_by_principal_id = principal_id
        await self.session.flush()
        return record

    async def list_aliases(
        self, *, tenant_id: UUID, limit: int = 100
    ) -> list[TelegramCommandAlias]:
        stmt = (
            select(TelegramCommandAlias)
            .where(TelegramCommandAlias.tenant_id == tenant_id)
            .order_by(TelegramCommandAlias.alias_normalized.asc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_alias(
        self, *, tenant_id: UUID, alias_id: UUID
    ) -> TelegramCommandAlias | None:
        stmt = select(TelegramCommandAlias).where(
            TelegramCommandAlias.tenant_id == tenant_id,
            TelegramCommandAlias.telegram_command_alias_id == alias_id,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def find_enabled_alias(
        self, *, tenant_id: UUID, alias_text: str
    ) -> TelegramCommandAlias | None:
        normalized = normalize_alias_text(alias_text)
        if not normalized:
            return None
        stmt = select(TelegramCommandAlias).where(
            TelegramCommandAlias.tenant_id == tenant_id,
            TelegramCommandAlias.alias_normalized == normalized,
            TelegramCommandAlias.enabled.is_(True),
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def upsert_alias(
        self,
        *,
        tenant_id: UUID,
        alias_text: str,
        published_workflow_version_id: UUID,
        description: str | None,
        protected: bool,
        enabled: bool,
        expected_revision_token: str | None,
        principal_id: str,
    ) -> TelegramCommandAlias:
        normalized = normalize_alias_text(alias_text)
        if not normalized:
            raise ValueError("alias text is required")
        if len(normalized) > 120:
            raise ValueError("alias text is too long")
        stmt = select(TelegramCommandAlias).where(
            TelegramCommandAlias.tenant_id == tenant_id,
            TelegramCommandAlias.alias_normalized == normalized,
        )
        record = (await self.session.execute(stmt)).scalar_one_or_none()
        if record is None:
            record = TelegramCommandAlias(
                tenant_id=tenant_id,
                alias_text=alias_text.strip(),
                alias_normalized=normalized,
                published_workflow_version_id=published_workflow_version_id,
                description=sanitize_text(description, max_length=500) or None,
                protected=protected,
                enabled=enabled,
                revision_token=uuid4().hex,
                created_by_principal_id=principal_id,
                updated_by_principal_id=principal_id,
            )
            self.session.add(record)
        else:
            if (
                expected_revision_token
                and record.revision_token != expected_revision_token
            ):
                raise TelegramConfigStaleRevisionError("stale Telegram alias revision")
            record.alias_text = alias_text.strip()
            record.published_workflow_version_id = published_workflow_version_id
            record.description = sanitize_text(description, max_length=500) or None
            record.protected = protected
            record.enabled = enabled
            record.revision_token = uuid4().hex
            record.updated_by_principal_id = principal_id
        await self.session.flush()
        return record

    async def add_token_audit(
        self,
        *,
        tenant_id: UUID,
        issued_by_principal_id: str,
        token_fingerprint: str,
        expires_at: datetime,
        trace_id: str,
    ) -> TelegramLinkTokenAudit:
        record = TelegramLinkTokenAudit(
            tenant_id=tenant_id,
            issued_by_principal_id=issued_by_principal_id,
            token_fingerprint=token_fingerprint,
            status=TelegramLinkTokenStatus.ISSUED.value,
            expires_at=expires_at,
            trace_id=trace_id,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def get_token_audit(
        self, token_audit_id: UUID
    ) -> TelegramLinkTokenAudit | None:
        return await self.session.get(TelegramLinkTokenAudit, token_audit_id)

    async def list_token_audits(
        self, *, tenant_id: UUID, limit: int = 20
    ) -> list[TelegramLinkTokenAudit]:
        stmt = (
            select(TelegramLinkTokenAudit)
            .where(TelegramLinkTokenAudit.tenant_id == tenant_id)
            .order_by(TelegramLinkTokenAudit.issued_at.desc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def revoke_token_audit(
        self,
        *,
        token_audit_id: UUID,
        tenant_id: UUID,
        principal_id: str,
    ) -> TelegramLinkTokenAudit | None:
        record = await self.get_token_audit(token_audit_id)
        if record is None or record.tenant_id != tenant_id:
            return None
        if record.status != TelegramLinkTokenStatus.REVOKED.value:
            record.status = TelegramLinkTokenStatus.REVOKED.value
            record.revoked_at = datetime.now(UTC)
            record.revoked_by_principal_id = principal_id
            await self.session.flush()
        return record

    async def consume_token_audit_by_fingerprint(
        self, *, token_fingerprint: str, now: datetime
    ) -> TelegramLinkTokenAudit | None:
        stmt = select(TelegramLinkTokenAudit).where(
            TelegramLinkTokenAudit.token_fingerprint == token_fingerprint
        )
        record = (await self.session.execute(stmt)).scalar_one_or_none()
        if record is None:
            return None
        expires_at = record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if record.status == TelegramLinkTokenStatus.ISSUED.value and (
            expires_at <= now
        ):
            record.status = TelegramLinkTokenStatus.EXPIRED.value
            await self.session.flush()
            return None
        if record.status != TelegramLinkTokenStatus.ISSUED.value:
            return None
        record.status = TelegramLinkTokenStatus.CONSUMED.value
        record.consumed_at = now
        await self.session.flush()
        return record

    async def upsert_identity_summary(
        self,
        *,
        tenant_id: UUID,
        platform_identity_id: str,
        telegram_user_fingerprint: str,
        telegram_chat_fingerprint: str,
        telegram_user_display: str,
        telegram_chat_display: str,
        command_ready: bool,
        trace_id: str,
    ) -> TelegramLinkedIdentitySummary:
        stmt = select(TelegramLinkedIdentitySummary).where(
            TelegramLinkedIdentitySummary.tenant_id == tenant_id,
            TelegramLinkedIdentitySummary.telegram_user_fingerprint
            == telegram_user_fingerprint,
            TelegramLinkedIdentitySummary.telegram_chat_fingerprint
            == telegram_chat_fingerprint,
        )
        record = (await self.session.execute(stmt)).scalar_one_or_none()
        if record is None:
            record = TelegramLinkedIdentitySummary(
                tenant_id=tenant_id,
                platform_identity_id=platform_identity_id,
                telegram_user_fingerprint=telegram_user_fingerprint,
                telegram_chat_fingerprint=telegram_chat_fingerprint,
                telegram_user_display=telegram_user_display,
                telegram_chat_display=telegram_chat_display,
                status=TelegramIdentityStatus.LINKED.value,
                command_ready=command_ready,
                trace_id=trace_id,
            )
            self.session.add(record)
        else:
            record.platform_identity_id = platform_identity_id
            record.status = TelegramIdentityStatus.LINKED.value
            record.command_ready = command_ready
            record.revoked_at = None
            record.revoked_by_principal_id = None
            record.trace_id = trace_id
        await self.session.flush()
        return record

    async def list_identity_summaries(
        self, *, tenant_id: UUID, limit: int = 50
    ) -> list[TelegramLinkedIdentitySummary]:
        stmt = (
            select(TelegramLinkedIdentitySummary)
            .where(TelegramLinkedIdentitySummary.tenant_id == tenant_id)
            .order_by(TelegramLinkedIdentitySummary.linked_at.desc())
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def revoke_identity(
        self,
        *,
        identity_id: UUID,
        tenant_id: UUID,
        principal_id: str,
    ) -> TelegramLinkedIdentitySummary | None:
        record = await self.session.get(TelegramLinkedIdentitySummary, identity_id)
        if record is None or record.tenant_id != tenant_id:
            return None
        record.status = TelegramIdentityStatus.REVOKED.value
        record.command_ready = False
        record.revoked_at = datetime.now(UTC)
        record.revoked_by_principal_id = principal_id
        await self.session.flush()
        return record

    async def get_identity_summary_by_fingerprints(
        self,
        *,
        tenant_id: UUID,
        telegram_user_fingerprint: str,
        telegram_chat_fingerprint: str,
    ) -> TelegramLinkedIdentitySummary | None:
        stmt = select(TelegramLinkedIdentitySummary).where(
            TelegramLinkedIdentitySummary.tenant_id == tenant_id,
            TelegramLinkedIdentitySummary.telegram_user_fingerprint
            == telegram_user_fingerprint,
            TelegramLinkedIdentitySummary.telegram_chat_fingerprint
            == telegram_chat_fingerprint,
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def add_diagnostic(
        self,
        *,
        tenant_id: UUID | None,
        principal_id: str | None,
        category: TelegramDiagnosticCategory,
        status: TelegramDiagnosticStatus,
        summary: str,
        trace_id: str,
        redacted_metadata: dict[str, object] | None = None,
    ) -> TelegramDiagnosticEvent:
        record = TelegramDiagnosticEvent(
            tenant_id=tenant_id,
            principal_id=principal_id,
            category=category.value,
            status=status.value,
            summary=sanitize_text(summary, max_length=500)
            or "Telegram diagnostic recorded.",
            trace_id=trace_id,
            redacted_metadata=redacted_metadata or {},
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_diagnostics(
        self, *, tenant_id: UUID | None, platform_scope: bool, limit: int = 25
    ) -> list[TelegramDiagnosticEvent]:
        stmt = select(TelegramDiagnosticEvent)
        if not platform_scope:
            stmt = stmt.where(TelegramDiagnosticEvent.tenant_id == tenant_id)
        elif tenant_id is not None:
            stmt = stmt.where(TelegramDiagnosticEvent.tenant_id == tenant_id)
        stmt = stmt.order_by(TelegramDiagnosticEvent.created_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_update_receipt(
        self, telegram_update_id: int
    ) -> TelegramUpdateReceipt | None:
        stmt = select(TelegramUpdateReceipt).where(
            TelegramUpdateReceipt.telegram_update_id == telegram_update_id
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def add_update_receipt(
        self,
        *,
        telegram_update_id: int,
        tenant_id: UUID | None,
        platform_identity_id: str | None,
        telegram_chat_fingerprint: str | None,
        action_type: str,
        response_payload: dict[str, object],
        run_id: UUID | None,
        delivery_attempt_id: UUID | None,
        trace_id: str,
    ) -> TelegramUpdateReceipt:
        existing = await self.get_update_receipt(telegram_update_id)
        if existing is not None:
            return existing
        record = TelegramUpdateReceipt(
            telegram_update_id=telegram_update_id,
            tenant_id=tenant_id,
            platform_identity_id=platform_identity_id,
            telegram_chat_fingerprint=telegram_chat_fingerprint,
            action_type=action_type,
            response_payload=response_payload,
            run_id=run_id,
            delivery_attempt_id=delivery_attempt_id,
            trace_id=trace_id,
            received_at=datetime.now(UTC),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_update_receipts(
        self, *, tenant_id: UUID | None, platform_scope: bool, limit: int = 25
    ) -> list[TelegramUpdateReceipt]:
        stmt = select(TelegramUpdateReceipt)
        if not platform_scope:
            stmt = stmt.where(TelegramUpdateReceipt.tenant_id == tenant_id)
        elif tenant_id is not None:
            stmt = stmt.where(TelegramUpdateReceipt.tenant_id == tenant_id)
        stmt = stmt.order_by(TelegramUpdateReceipt.received_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())
