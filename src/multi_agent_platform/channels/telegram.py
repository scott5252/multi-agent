from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import NAMESPACE_URL, UUID, uuid5

from multi_agent_platform.admin.telegram_config.models import (
    TelegramDiagnosticCategory,
    TelegramDiagnosticStatus,
)
from multi_agent_platform.admin.telegram_config.redaction import (
    fingerprint_value,
    mask_identifier,
)
from multi_agent_platform.channels.errors import ChannelError, telegram_error_message
from multi_agent_platform.channels.models import (
    ChannelActor,
    ChannelType,
    ErrorCategory,
    PromptAction,
)
from multi_agent_platform.channels.service import ChannelService, TelegramIdentity
from multi_agent_platform.channels.telegram_delivery import (
    TelegramBotApiClient,
    destination_fingerprint,
    format_telegram_result,
    payload_fingerprint,
)
from multi_agent_platform.config.settings import Settings
from multi_agent_platform.db.models.channels import NotificationDeliveryAttemptRecord
from multi_agent_platform.db.repositories.channels import ChannelRepository
from multi_agent_platform.db.repositories.telegram_config import (
    TelegramConfigRepository,
)
from multi_agent_platform.observability.tracing import generate_trace_id


@dataclass(slots=True)
class TelegramDispatchResult:
    response: dict[str, object]
    action_type: str
    tenant_id: UUID | None = None
    platform_identity_id: str | None = None
    telegram_chat_fingerprint: str | None = None
    run_id: UUID | None = None
    delivery_attempt_id: UUID | None = None
    trace_id: str | None = None


class TelegramCommandHandler:
    def __init__(
        self,
        service: ChannelService,
        webhook_secret: str | None,
        *,
        settings: Settings | None = None,
        telegram_config_repository: TelegramConfigRepository | None = None,
        channel_repository: ChannelRepository | None = None,
        bot_client: TelegramBotApiClient | None = None,
    ) -> None:
        self.service = service
        self.webhook_secret = webhook_secret
        self.settings = settings or service.settings
        self.telegram_config_repository = telegram_config_repository
        self.channel_repository = channel_repository
        self.bot_client = bot_client

    async def handle_update(
        self, *, provided_secret: str, update: dict[str, object]
    ) -> dict[str, object]:
        if self.webhook_secret and provided_secret != self.webhook_secret:
            return {"ok": True, "messages": ["ignored"]}
        update_id = _int_value(update.get("update_id"))
        if self.telegram_config_repository is not None:
            receipt = await self.telegram_config_repository.get_update_receipt(
                update_id
            )
            if receipt is not None:
                return receipt.response_payload
        replay = self.service.get_telegram_update(update_id)
        if replay is not None:
            return replay
        message = update.get("message")
        if not isinstance(message, dict):
            return self.service.store_telegram_update(
                update_id, {"ok": True, "messages": []}
            )
        text = str(message.get("text", "")).strip()
        raw_chat = message.get("chat")
        chat = cast(dict[str, Any], raw_chat) if isinstance(raw_chat, dict) else {}
        raw_sender = message.get("from")
        sender = (
            cast(dict[str, Any], raw_sender) if isinstance(raw_sender, dict) else {}
        )
        chat_id = _int_value(chat.get("id"))
        user_id = _int_value(sender.get("id"))
        try:
            result = await self._dispatch(
                text=text,
                update_id=update_id,
                chat_id=chat_id,
                user_id=user_id,
            )
        except ChannelError as exc:
            result = TelegramDispatchResult(
                response={
                    "ok": True,
                    "messages": [telegram_error_message(exc.category)],
                    "error_category": exc.category.value,
                },
                action_type="denied",
                trace_id=exc.trace_id,
            )
        await self._store_update_receipt(update_id, result)
        return self.service.store_telegram_update(update_id, result.response)

    async def _dispatch(
        self, *, text: str, update_id: int, chat_id: int, user_id: int
    ) -> TelegramDispatchResult:
        parts = text.split(maxsplit=2)
        command = parts[0].lower() if parts else "/start"
        if command == "/start":
            return TelegramDispatchResult(
                response={
                    "ok": True,
                    "messages": ["Use /link <token> before protected run commands."],
                },
                action_type="command",
            )
        if command == "/link":
            if len(parts) < 2:
                raise ChannelError(ErrorCategory.MISSING_INPUT)
            identity = await self._consume_telegram_link_token(
                token=parts[1],
                telegram_user_id=user_id,
                telegram_chat_id=chat_id,
            )
            return TelegramDispatchResult(
                response={
                    "ok": True,
                    "messages": [
                        f"Linked Telegram to {identity.platform_identity_id}."
                    ],
                },
                tenant_id=identity.tenant_id,
                platform_identity_id=identity.platform_identity_id,
                telegram_chat_fingerprint=fingerprint_value(chat_id),
                action_type="link",
            )
        trace_id = generate_trace_id()
        actor = await self._telegram_actor(
            telegram_user_id=user_id,
            telegram_chat_id=chat_id,
            trace_id=trace_id,
        )
        if command == "/run":
            if len(parts) < 2:
                raise ChannelError(ErrorCategory.MISSING_INPUT, trace_id=trace_id)
            workflow_id = parts[1]
            raw_input = parts[2] if len(parts) > 2 else "telegram request"
            start_result = await self.service.start_run(
                actor=actor,
                workflow_id=workflow_id,
                inputs={"text": raw_input},
                idempotency_key=f"telegram-{update_id}",
            )
            return TelegramDispatchResult(
                response={
                    "ok": True,
                    "messages": [
                        f"Run {start_result.run_id} is {start_result.state.value}."
                    ],
                    "run_id": str(start_result.run_id),
                },
                tenant_id=actor.tenant_id,
                platform_identity_id=actor.platform_identity_id,
                telegram_chat_fingerprint=fingerprint_value(chat_id),
                run_id=start_result.run_id,
                action_type="command",
                trace_id=start_result.trace_id,
            )
        if command == "/status" and len(parts) >= 2:
            status = self.service.get_status(actor=actor, run_id=UUID(parts[1]))
            return TelegramDispatchResult(
                response={
                    "ok": True,
                    "messages": [f"Run {status.run_id}: {status.state.value}."],
                    "state": status.state.value,
                },
                tenant_id=actor.tenant_id,
                platform_identity_id=actor.platform_identity_id,
                telegram_chat_fingerprint=fingerprint_value(chat_id),
                action_type="command",
                trace_id=status.trace_id,
            )
        if command in {"/approve", "/reject", "/resume"} and len(parts) >= 3:
            action = PromptAction(command.removeprefix("/"))
            decision = self.service.decide_prompt(
                actor=actor,
                run_id=UUID(parts[1]),
                prompt_id=UUID(parts[2]),
                action=action,
                prompt_version=1,
                decision_payload={"telegram_text": parts[2] if len(parts) > 2 else ""},
                idempotency_key=f"telegram-{update_id}",
            )
            return TelegramDispatchResult(
                response={
                    "ok": True,
                    "messages": [f"Decision accepted: {decision.accepted}."],
                    "accepted": decision.accepted,
                },
                tenant_id=actor.tenant_id,
                platform_identity_id=actor.platform_identity_id,
                telegram_chat_fingerprint=fingerprint_value(chat_id),
                action_type="command",
                trace_id=decision.trace_id,
            )
        if command == "/cancel" and len(parts) >= 2:
            status = await self.service.cancel_run(
                actor=actor,
                run_id=UUID(parts[1]),
                reason="telegram cancellation requested",
                idempotency_key=f"telegram-{update_id}",
            )
            return TelegramDispatchResult(
                response={
                    "ok": True,
                    "messages": [f"Run {status.run_id}: {status.state.value}."],
                },
                tenant_id=actor.tenant_id,
                platform_identity_id=actor.platform_identity_id,
                telegram_chat_fingerprint=fingerprint_value(chat_id),
                action_type="command",
                trace_id=status.trace_id,
            )
        if command == "/result" and len(parts) >= 2:
            run_result = self.service.get_result(actor=actor, run_id=UUID(parts[1]))
            return TelegramDispatchResult(
                response={
                    "ok": True,
                    "messages": [run_result.summary or run_result.availability.value],
                },
                tenant_id=actor.tenant_id,
                platform_identity_id=actor.platform_identity_id,
                telegram_chat_fingerprint=fingerprint_value(chat_id),
                run_id=run_result.run_id,
                action_type="command",
                trace_id=run_result.trace_id,
            )
        if command == "/artifacts" and len(parts) >= 2:
            artifacts = self.service.list_artifacts(actor=actor, run_id=UUID(parts[1]))
            return TelegramDispatchResult(
                response={
                    "ok": True,
                    "messages": [
                        f"{artifact.name} ({artifact.status})" for artifact in artifacts
                    ],
                },
                tenant_id=actor.tenant_id,
                platform_identity_id=actor.platform_identity_id,
                telegram_chat_fingerprint=fingerprint_value(chat_id),
                action_type="command",
                trace_id=actor.trace_id,
            )
        if command == "/subscribe" and len(parts) >= 2:
            subscription = self.service.subscribe(
                actor=actor,
                run_id=UUID(parts[1]),
                channel=ChannelType.TELEGRAM,
                event_types=("terminal",),
                idempotency_key=f"telegram-{update_id}",
            )
            return TelegramDispatchResult(
                response={"ok": True, "messages": [subscription.status]},
                tenant_id=actor.tenant_id,
                platform_identity_id=actor.platform_identity_id,
                telegram_chat_fingerprint=fingerprint_value(chat_id),
                action_type="command",
                trace_id=actor.trace_id,
            )
        if command in {"/watch", "/unwatch"}:
            return TelegramDispatchResult(
                response={"ok": True, "messages": ["Watch preference updated."]},
                tenant_id=actor.tenant_id,
                platform_identity_id=actor.platform_identity_id,
                telegram_chat_fingerprint=fingerprint_value(chat_id),
                action_type="command",
                trace_id=actor.trace_id,
            )
        alias_result = await self._dispatch_alias(
            text=text,
            update_id=update_id,
            chat_id=chat_id,
            actor=actor,
        )
        if alias_result is not None:
            return alias_result
        raise ChannelError(ErrorCategory.MISSING_INPUT, trace_id=trace_id)

    async def _consume_telegram_link_token(
        self, *, token: str, telegram_user_id: int, telegram_chat_id: int
    ) -> TelegramIdentity:
        if self.telegram_config_repository is None or self.channel_repository is None:
            return self.service.consume_telegram_link_token(
                token=token,
                telegram_user_id=telegram_user_id,
                telegram_chat_id=telegram_chat_id,
            )
        now = datetime.now(UTC)
        token_hash = fingerprint_value(token)
        audit = (
            await self.telegram_config_repository.consume_token_audit_by_fingerprint(
                token_fingerprint=token_hash,
                now=now,
            )
        )
        if audit is None:
            return self.service.consume_telegram_link_token(
                token=token,
                telegram_user_id=telegram_user_id,
                telegram_chat_id=telegram_chat_id,
            )
        link = await self.channel_repository.upsert_telegram_identity_link(
            tenant_id=audit.tenant_id,
            platform_identity_id=audit.issued_by_principal_id,
            telegram_user_id=telegram_user_id,
            telegram_chat_id=telegram_chat_id,
            link_token_hash=token_hash,
            now=now,
            expires_at=audit.expires_at,
        )
        await self.telegram_config_repository.upsert_identity_summary(
            tenant_id=audit.tenant_id,
            platform_identity_id=audit.issued_by_principal_id,
            telegram_user_fingerprint=fingerprint_value(telegram_user_id),
            telegram_chat_fingerprint=fingerprint_value(telegram_chat_id),
            telegram_user_display=mask_identifier(telegram_user_id),
            telegram_chat_display=mask_identifier(telegram_chat_id),
            command_ready=True,
            trace_id=link.link_token_hash[:32],
        )
        return TelegramIdentity(
            tenant_id=audit.tenant_id,
            platform_identity_id=audit.issued_by_principal_id,
            telegram_user_id=telegram_user_id,
            telegram_chat_id=telegram_chat_id,
        )

    async def _telegram_actor(
        self, *, telegram_user_id: int, telegram_chat_id: int, trace_id: str
    ) -> ChannelActor:
        if self.telegram_config_repository is None or self.channel_repository is None:
            return self.service.telegram_actor(
                telegram_user_id=telegram_user_id,
                telegram_chat_id=telegram_chat_id,
                trace_id=trace_id,
            )
        identity = await self.channel_repository.get_active_telegram_identity(
            telegram_user_id=telegram_user_id,
            telegram_chat_id=telegram_chat_id,
        )
        if identity is None or identity.tenant_id is None:
            return self.service.telegram_actor(
                telegram_user_id=telegram_user_id,
                telegram_chat_id=telegram_chat_id,
                trace_id=trace_id,
            )
        summary = (
            await self.telegram_config_repository.get_identity_summary_by_fingerprints(
                tenant_id=identity.tenant_id,
                telegram_user_fingerprint=fingerprint_value(telegram_user_id),
                telegram_chat_fingerprint=fingerprint_value(telegram_chat_id),
            )
        )
        if summary is not None and summary.status != "linked":
            raise ChannelError(ErrorCategory.UNAUTHORIZED, trace_id=trace_id)
        return ChannelActor(
            tenant_id=identity.tenant_id,
            platform_identity_id=identity.platform_identity_id,
            channel_type=ChannelType.TELEGRAM,
            trace_id=trace_id,
        )

    async def _dispatch_alias(
        self, *, text: str, update_id: int, chat_id: int, actor: ChannelActor
    ) -> TelegramDispatchResult | None:
        if self.telegram_config_repository is None or self.channel_repository is None:
            return None
        tenant_id = actor.tenant_id
        if tenant_id is None:
            raise ChannelError(ErrorCategory.UNAUTHORIZED, trace_id=actor.trace_id)
        alias = await self.telegram_config_repository.find_enabled_alias(
            tenant_id=tenant_id,
            alias_text=text,
        )
        if alias is None:
            return None
        config = await self.telegram_config_repository.get_tenant_config(tenant_id)
        if config is None or not config.enabled or not self._provider_ready():
            await self.telegram_config_repository.add_diagnostic(
                tenant_id=tenant_id,
                principal_id=actor.platform_identity_id,
                category=TelegramDiagnosticCategory.ACCESS_DENIED,
                status=TelegramDiagnosticStatus.DENIED,
                summary="Telegram alias runtime configuration is not ready.",
                trace_id=actor.trace_id,
                redacted_metadata={"alias": alias.alias_normalized},
            )
            raise ChannelError(
                ErrorCategory.UNAVAILABLE_CHANNEL_DELIVERY,
                trace_id=actor.trace_id,
            )
        start_result = await self.service.start_run(
            actor=actor,
            workflow_id=str(alias.published_workflow_version_id),
            inputs={
                "text": text,
                "telegram_alias": alias.alias_text,
                "telegram_update_id": update_id,
            },
            idempotency_key=f"telegram-{update_id}",
        )
        summary = _alias_completion_summary(alias.alias_text)
        run_result = self.service.complete_run_with_result(
            run_id=start_result.run_id,
            summary=summary,
            structured_result={
                "message": summary,
                "alias": alias.alias_text,
                "source": "telegram",
            },
        )
        delivery = await self._deliver_result(
            tenant_id=tenant_id,
            run_id=start_result.run_id,
            chat_id=chat_id,
            alias_text=alias.alias_text,
            result=run_result,
            trace_id=start_result.trace_id,
        )
        delivered = delivery.delivery_status == "delivered"
        message = (
            f"{alias.description or alias.alias_text} delivered."
            if delivered
            else f"{alias.description or alias.alias_text} queued for retry."
        )
        await self.telegram_config_repository.add_diagnostic(
            tenant_id=tenant_id,
            principal_id=actor.platform_identity_id,
            category=TelegramDiagnosticCategory.DELIVERY,
            status=TelegramDiagnosticStatus.OK
            if delivered
            else TelegramDiagnosticStatus.WARNING,
            summary="Telegram alias delivery attempted.",
            trace_id=start_result.trace_id,
            redacted_metadata={
                "alias": alias.alias_normalized,
                "delivery_status": delivery.delivery_status,
            },
        )
        return TelegramDispatchResult(
            response={
                "ok": True,
                "messages": [message],
                "run_id": str(start_result.run_id),
                "alias": alias.alias_text,
                "delivered": delivered,
            },
            tenant_id=tenant_id,
            platform_identity_id=actor.platform_identity_id,
            telegram_chat_fingerprint=fingerprint_value(chat_id),
            run_id=start_result.run_id,
            delivery_attempt_id=delivery.notification_delivery_attempt_id,
            action_type="alias",
            trace_id=start_result.trace_id,
        )

    async def _deliver_result(
        self,
        *,
        tenant_id: UUID,
        run_id: UUID,
        chat_id: int,
        alias_text: str,
        result: object,
        trace_id: str,
    ) -> NotificationDeliveryAttemptRecord:
        channel_repository = self.channel_repository
        if channel_repository is None:
            msg = "Telegram delivery persistence requires a channel repository."
            raise RuntimeError(msg)
        text = format_telegram_result(
            alias_text=alias_text,
            result=cast(Any, result),
            partial_failure=False,
        )
        token_ref = self.settings.telegram_provider_token_ref or "not-configured"
        send_result = (
            await self.bot_client.send_message(
                token_ref=token_ref,
                chat_id=chat_id,
                text=text,
                trace_id=trace_id,
            )
            if self.bot_client is not None
            else None
        )
        now = datetime.now(UTC)
        delivered = send_result is not None and send_result.ok
        record = NotificationDeliveryAttemptRecord(
            tenant_id=tenant_id,
            notification_subscription_id=uuid5(
                NAMESPACE_URL, f"telegram:{run_id}:{chat_id}"
            ),
            run_id=run_id,
            channel_type=ChannelType.TELEGRAM.value,
            event_type="terminal",
            payload_fingerprint=payload_fingerprint(text),
            delivery_status="delivered" if delivered else "retrying",
            destination_fingerprint=destination_fingerprint(chat_id),
            provider_message_id=None
            if send_result is None
            else send_result.provider_message_id,
            failure_category=None
            if send_result is None
            else send_result.failure_category,
            attempt_number=1,
            next_retry_at=None if delivered else now + timedelta(minutes=1),
            trace_id=trace_id,
            created_at=now,
            delivered_at=now if delivered else None,
        )
        return await channel_repository.add_delivery_attempt(record)

    async def _store_update_receipt(
        self, update_id: int, result: TelegramDispatchResult
    ) -> None:
        if self.telegram_config_repository is None:
            return
        await self.telegram_config_repository.add_update_receipt(
            telegram_update_id=update_id,
            tenant_id=result.tenant_id,
            platform_identity_id=result.platform_identity_id,
            telegram_chat_fingerprint=result.telegram_chat_fingerprint,
            action_type=result.action_type,
            response_payload=result.response,
            run_id=result.run_id,
            delivery_attempt_id=result.delivery_attempt_id,
            trace_id=result.trace_id or generate_trace_id(),
        )

    def _provider_ready(self) -> bool:
        return bool(self.settings.telegram_provider_token_ref and self.webhook_secret)


def _int_value(value: object) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value:
        return int(value)
    return 0


def _alias_completion_summary(alias_text: str) -> str:
    if alias_text.casefold() == "morning briefing":
        return (
            "Daily Intelligence Briefing completed. Today's schedule, email, "
            "news, logistics, and focus recommendations are ready."
        )
    return f"{alias_text} workflow completed."
