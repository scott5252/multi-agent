from __future__ import annotations

from typing import Any, cast
from uuid import UUID

from multi_agent_platform.channels.errors import ChannelError, telegram_error_message
from multi_agent_platform.channels.models import (
    ChannelType,
    ErrorCategory,
    PromptAction,
)
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.observability.tracing import generate_trace_id


class TelegramCommandHandler:
    def __init__(self, service: ChannelService, webhook_secret: str | None) -> None:
        self.service = service
        self.webhook_secret = webhook_secret

    async def handle_update(
        self, *, provided_secret: str, update: dict[str, object]
    ) -> dict[str, object]:
        if self.webhook_secret and provided_secret != self.webhook_secret:
            return {"ok": True, "messages": ["ignored"]}
        update_id = _int_value(update.get("update_id"))
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
            response = await self._dispatch(
                text=text,
                update_id=update_id,
                chat_id=chat_id,
                user_id=user_id,
            )
        except ChannelError as exc:
            response = {
                "ok": True,
                "messages": [telegram_error_message(exc.category)],
                "error_category": exc.category.value,
            }
        return self.service.store_telegram_update(update_id, response)

    async def _dispatch(
        self, *, text: str, update_id: int, chat_id: int, user_id: int
    ) -> dict[str, object]:
        parts = text.split(maxsplit=2)
        command = parts[0].lower() if parts else "/start"
        if command == "/start":
            return {
                "ok": True,
                "messages": ["Use /link <token> before protected run commands."],
            }
        if command == "/link":
            if len(parts) < 2:
                raise ChannelError(ErrorCategory.MISSING_INPUT)
            identity = self.service.consume_telegram_link_token(
                token=parts[1],
                telegram_user_id=user_id,
                telegram_chat_id=chat_id,
            )
            return {
                "ok": True,
                "messages": [f"Linked Telegram to {identity.platform_identity_id}."],
            }
        trace_id = generate_trace_id()
        actor = self.service.telegram_actor(
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
            return {
                "ok": True,
                "messages": [
                    f"Run {start_result.run_id} is {start_result.state.value}."
                ],
                "run_id": str(start_result.run_id),
            }
        if command == "/status" and len(parts) >= 2:
            status = self.service.get_status(actor=actor, run_id=UUID(parts[1]))
            return {
                "ok": True,
                "messages": [f"Run {status.run_id}: {status.state.value}."],
                "state": status.state.value,
            }
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
            return {
                "ok": True,
                "messages": [f"Decision accepted: {decision.accepted}."],
                "accepted": decision.accepted,
            }
        if command == "/cancel" and len(parts) >= 2:
            status = await self.service.cancel_run(
                actor=actor,
                run_id=UUID(parts[1]),
                reason="telegram cancellation requested",
                idempotency_key=f"telegram-{update_id}",
            )
            return {
                "ok": True,
                "messages": [f"Run {status.run_id}: {status.state.value}."],
            }
        if command == "/result" and len(parts) >= 2:
            run_result = self.service.get_result(actor=actor, run_id=UUID(parts[1]))
            return {
                "ok": True,
                "messages": [run_result.summary or run_result.availability.value],
            }
        if command == "/artifacts" and len(parts) >= 2:
            artifacts = self.service.list_artifacts(actor=actor, run_id=UUID(parts[1]))
            return {
                "ok": True,
                "messages": [
                    f"{artifact.name} ({artifact.status})" for artifact in artifacts
                ],
            }
        if command == "/subscribe" and len(parts) >= 2:
            subscription = self.service.subscribe(
                actor=actor,
                run_id=UUID(parts[1]),
                channel=ChannelType.TELEGRAM,
                event_types=("terminal",),
                idempotency_key=f"telegram-{update_id}",
            )
            return {"ok": True, "messages": [subscription.status]}
        if command in {"/watch", "/unwatch"}:
            return {"ok": True, "messages": ["Watch preference updated."]}
        raise ChannelError(ErrorCategory.MISSING_INPUT, trace_id=trace_id)


def _int_value(value: object) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value:
        return int(value)
    return 0
