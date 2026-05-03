from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from multi_agent_platform.admin.telegram_config.models import (
    PROTECTED_TELEGRAM_COMMANDS,
    TelegramAccessScope,
    TelegramConfigScopeType,
    TelegramDiagnosticCategory,
    TelegramDiagnosticStatus,
    TelegramProviderReadiness,
)
from multi_agent_platform.admin.telegram_config.redaction import (
    fingerprint_prefix,
    fingerprint_value,
    is_safe_secret_reference,
    mask_identifier,
    safe_reference_label,
    sanitize_metadata,
)
from multi_agent_platform.channels.models import ChannelActor, ChannelType
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.config.settings import AppEnvironment, Settings
from multi_agent_platform.db.models.telegram_config import (
    TelegramDiagnosticEvent,
    TelegramLinkedIdentitySummary,
    TelegramLinkTokenAudit,
    TelegramTenantConfiguration,
)
from multi_agent_platform.db.repositories.telegram_config import (
    TelegramConfigRepository,
)


@dataclass(frozen=True, slots=True)
class IssuedTelegramLinkToken:
    raw_token: str
    audit: TelegramLinkTokenAudit


class TelegramConfigurationService:
    def __init__(
        self,
        *,
        repository: TelegramConfigRepository,
        settings: Settings,
        channel_service: ChannelService,
    ) -> None:
        self.repository = repository
        self.settings = settings
        self.channel_service = channel_service

    def provider_readiness(self) -> TelegramProviderReadiness:
        token_ref = self.settings.telegram_provider_token_ref
        webhook_secret = self.settings.telegram_webhook_secret
        token_configured = bool(token_ref)
        webhook_configured = bool(webhook_secret)
        token_safe = is_safe_secret_reference(token_ref)
        webhook_safe = is_safe_secret_reference(webhook_secret)
        if self.settings.app_env is AppEnvironment.PRODUCTION:
            production_ready = token_configured and webhook_configured
            production_ready = production_ready and token_safe and webhook_safe
        else:
            production_ready = True
        ready = token_configured and webhook_configured and production_ready
        return TelegramProviderReadiness(
            token_reference_configured=token_configured,
            webhook_secret_configured=webhook_configured,
            token_reference_safe=token_safe,
            webhook_secret_safe=webhook_safe,
            production_guardrails_ready=production_ready,
            local_validation_only=self.settings.app_env
            in {AppEnvironment.LOCAL, AppEnvironment.TEST, AppEnvironment.CI},
            ready=ready,
            token_reference_label=safe_reference_label(token_ref),
            webhook_secret_label=safe_reference_label(webhook_secret),
        )

    async def tenant_config(
        self, access_scope: TelegramAccessScope
    ) -> TelegramTenantConfiguration | None:
        if access_scope.scope_type is TelegramConfigScopeType.PLATFORM:
            if access_scope.tenant_id is None:
                return None
        tenant_id = access_scope.require_tenant()
        return await self.repository.get_or_create_tenant_config(
            tenant_id=tenant_id,
            principal_id=access_scope.principal_id,
        )

    async def update_tenant_config(
        self,
        *,
        access_scope: TelegramAccessScope,
        enabled: bool,
        protected_commands: tuple[str, ...],
        status_note: str | None,
        revision_token: str | None,
    ) -> TelegramTenantConfiguration:
        tenant_id = access_scope.require_tenant()
        commands = [
            command
            for command in protected_commands
            if command in PROTECTED_TELEGRAM_COMMANDS
        ]
        record = await self.repository.update_tenant_config(
            tenant_id=tenant_id,
            enabled=enabled,
            protected_commands=commands or list(PROTECTED_TELEGRAM_COMMANDS),
            status_note=status_note,
            expected_revision_token=revision_token,
            principal_id=access_scope.principal_id,
        )
        await self.repository.add_diagnostic(
            tenant_id=tenant_id,
            principal_id=access_scope.principal_id,
            category=TelegramDiagnosticCategory.READINESS,
            status=TelegramDiagnosticStatus.OK
            if enabled
            else TelegramDiagnosticStatus.WARNING,
            summary="Tenant Telegram enablement updated.",
            trace_id=self._trace_id(access_scope),
            redacted_metadata={
                "enabled": enabled,
                "protected_command_count": len(record.protected_commands),
            },
        )
        return record

    async def validate_webhook(
        self, access_scope: TelegramAccessScope
    ) -> TelegramDiagnosticEvent:
        readiness = self.provider_readiness()
        status = (
            TelegramDiagnosticStatus.READY
            if readiness.ready
            else TelegramDiagnosticStatus.NOT_READY
        )
        summary = (
            "Webhook configuration is ready for local command validation."
            if readiness.ready
            else "Webhook configuration is not ready for protected commands."
        )
        return await self.repository.add_diagnostic(
            tenant_id=access_scope.tenant_id,
            principal_id=access_scope.principal_id,
            category=TelegramDiagnosticCategory.WEBHOOK_VALIDATION,
            status=status,
            summary=summary,
            trace_id=self._trace_id(access_scope),
            redacted_metadata={
                "local_validation_only": readiness.local_validation_only,
                "token_reference": readiness.token_reference_label,
                "webhook_secret": readiness.webhook_secret_label,
                "external_call_performed": False,
            },
        )

    async def issue_link_token(
        self, access_scope: TelegramAccessScope
    ) -> IssuedTelegramLinkToken:
        tenant_id = access_scope.require_tenant()
        actor = ChannelActor(
            tenant_id=tenant_id,
            platform_identity_id=access_scope.principal_id,
            channel_type=ChannelType.WEB_API,
            trace_id=self._trace_id(access_scope),
        )
        token = self.channel_service.create_telegram_link_token(actor)
        audit = await self.repository.add_token_audit(
            tenant_id=tenant_id,
            issued_by_principal_id=access_scope.principal_id,
            token_fingerprint=fingerprint_value(token.token),
            expires_at=token.expires_at,
            trace_id=actor.trace_id,
        )
        await self.repository.add_diagnostic(
            tenant_id=tenant_id,
            principal_id=access_scope.principal_id,
            category=TelegramDiagnosticCategory.LINK_TOKEN,
            status=TelegramDiagnosticStatus.OK,
            summary="One-time Telegram link token issued.",
            trace_id=actor.trace_id,
            redacted_metadata={
                "token_fingerprint": audit.token_fingerprint[:12],
                "expires_at": token.expires_at.isoformat(),
            },
        )
        return IssuedTelegramLinkToken(raw_token=token.token, audit=audit)

    async def revoke_link_token(
        self, *, access_scope: TelegramAccessScope, token_audit_id: UUID
    ) -> TelegramLinkTokenAudit | None:
        tenant_id = access_scope.require_tenant()
        audit = await self.repository.revoke_token_audit(
            token_audit_id=token_audit_id,
            tenant_id=tenant_id,
            principal_id=access_scope.principal_id,
        )
        if audit is not None:
            self.channel_service.revoke_telegram_link_token_by_hash(
                audit.token_fingerprint
            )
            await self.repository.add_diagnostic(
                tenant_id=tenant_id,
                principal_id=access_scope.principal_id,
                category=TelegramDiagnosticCategory.LINK_TOKEN,
                status=TelegramDiagnosticStatus.REVOKED,
                summary="One-time Telegram link token revoked.",
                trace_id=self._trace_id(access_scope),
                redacted_metadata={"token_fingerprint": audit.token_fingerprint[:12]},
            )
        return audit

    async def sync_channel_identities(
        self, access_scope: TelegramAccessScope
    ) -> tuple[TelegramLinkedIdentitySummary, ...]:
        tenant_id = access_scope.require_tenant()
        synced: list[TelegramLinkedIdentitySummary] = []
        for identity in self.channel_service.telegram_identity_snapshots(
            tenant_id=tenant_id
        ):
            synced.append(
                await self.repository.upsert_identity_summary(
                    tenant_id=tenant_id,
                    platform_identity_id=identity.platform_identity_id,
                    telegram_user_fingerprint=fingerprint_value(
                        identity.telegram_user_id
                    ),
                    telegram_chat_fingerprint=fingerprint_value(
                        identity.telegram_chat_id
                    ),
                    telegram_user_display=mask_identifier(identity.telegram_user_id),
                    telegram_chat_display=mask_identifier(identity.telegram_chat_id),
                    command_ready=True,
                    trace_id=self._trace_id(access_scope),
                )
            )
        return tuple(synced)

    async def list_link_tokens(
        self, access_scope: TelegramAccessScope
    ) -> tuple[TelegramLinkTokenAudit, ...]:
        tenant_id = access_scope.require_tenant()
        return tuple(await self.repository.list_token_audits(tenant_id=tenant_id))

    async def list_identities(
        self, access_scope: TelegramAccessScope
    ) -> tuple[TelegramLinkedIdentitySummary, ...]:
        await self.sync_channel_identities(access_scope)
        tenant_id = access_scope.require_tenant()
        return tuple(await self.repository.list_identity_summaries(tenant_id=tenant_id))

    async def revoke_identity(
        self, *, access_scope: TelegramAccessScope, identity_id: UUID
    ) -> TelegramLinkedIdentitySummary | None:
        tenant_id = access_scope.require_tenant()
        record = await self.repository.revoke_identity(
            identity_id=identity_id,
            tenant_id=tenant_id,
            principal_id=access_scope.principal_id,
        )
        if record is not None:
            self.channel_service.revoke_telegram_identity_by_fingerprints(
                user_fingerprint=record.telegram_user_fingerprint,
                chat_fingerprint=record.telegram_chat_fingerprint,
            )
            await self.repository.add_diagnostic(
                tenant_id=tenant_id,
                principal_id=access_scope.principal_id,
                category=TelegramDiagnosticCategory.IDENTITY,
                status=TelegramDiagnosticStatus.REVOKED,
                summary="Telegram linked identity revoked.",
                trace_id=self._trace_id(access_scope),
                redacted_metadata={
                    "telegram_user": record.telegram_user_display,
                    "telegram_chat": record.telegram_chat_display,
                },
            )
        return record

    async def list_diagnostics(
        self, access_scope: TelegramAccessScope
    ) -> tuple[TelegramDiagnosticEvent, ...]:
        return tuple(
            await self.repository.list_diagnostics(
                tenant_id=access_scope.tenant_id,
                platform_scope=access_scope.scope_type
                is TelegramConfigScopeType.PLATFORM,
            )
        )

    async def record_access_denied(
        self,
        *,
        principal_id: str,
        trace_id: str,
        metadata: dict[str, object] | None = None,
    ) -> TelegramDiagnosticEvent:
        redacted_metadata: dict[str, object] = dict(sanitize_metadata(metadata))
        return await self.repository.add_diagnostic(
            tenant_id=None,
            principal_id=principal_id,
            category=TelegramDiagnosticCategory.ACCESS_DENIED,
            status=TelegramDiagnosticStatus.DENIED,
            summary="Telegram configuration access denied.",
            trace_id=trace_id,
            redacted_metadata=redacted_metadata,
        )

    def token_fingerprint_display(self, value: str) -> str:
        return fingerprint_prefix(value)

    @staticmethod
    def _trace_id(access_scope: TelegramAccessScope) -> str:
        return f"telegram-config-{access_scope.principal_id}"
