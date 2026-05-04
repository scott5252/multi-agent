from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

import httpx

from multi_agent_platform.admin.telegram_config.redaction import fingerprint_value
from multi_agent_platform.channels.models import RunResult
from multi_agent_platform.secrets.base import SecretProvider

_TOKENISH_RE = re.compile(r"\b[A-Za-z0-9_-]{32,}\b")


@dataclass(slots=True, frozen=True)
class TelegramSentMessage:
    token_ref: str
    chat_id: int
    text: str
    trace_id: str


@dataclass(slots=True, frozen=True)
class TelegramBotApiSendResult:
    ok: bool
    provider_message_id: str | None = None
    http_status: int | None = None
    failure_category: str | None = None


class TelegramBotApiClient(Protocol):
    async def send_message(
        self, *, token_ref: str, chat_id: int, text: str, trace_id: str
    ) -> TelegramBotApiSendResult:
        raise NotImplementedError


class MockTelegramBotApiClient:
    def __init__(self, *, fail_category: str | None = None) -> None:
        self.fail_category = fail_category
        self.sent_messages: list[TelegramSentMessage] = []

    async def send_message(
        self, *, token_ref: str, chat_id: int, text: str, trace_id: str
    ) -> TelegramBotApiSendResult:
        self.sent_messages.append(
            TelegramSentMessage(
                token_ref=token_ref,
                chat_id=chat_id,
                text=text,
                trace_id=trace_id,
            )
        )
        if self.fail_category is not None:
            return TelegramBotApiSendResult(
                ok=False,
                http_status=503,
                failure_category=self.fail_category,
            )
        return TelegramBotApiSendResult(
            ok=True,
            provider_message_id=f"mock-{len(self.sent_messages)}",
            http_status=200,
        )


class HttpTelegramBotApiClient:
    def __init__(
        self, *, secret_provider: SecretProvider, timeout_seconds: float = 10.0
    ):
        self.secret_provider = secret_provider
        self.timeout_seconds = timeout_seconds

    async def send_message(
        self, *, token_ref: str, chat_id: int, text: str, trace_id: str
    ) -> TelegramBotApiSendResult:
        secret = await self.secret_provider.resolve(_secret_reference(token_ref))
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(
                f"https://api.telegram.org/bot{secret.value}/sendMessage",
                json={"chat_id": chat_id, "text": text},
                headers={"X-Trace-Id": trace_id},
            )
        if response.status_code >= 500:
            return TelegramBotApiSendResult(
                ok=False,
                http_status=response.status_code,
                failure_category="provider_unavailable",
            )
        if response.status_code >= 400:
            return TelegramBotApiSendResult(
                ok=False,
                http_status=response.status_code,
                failure_category="provider_rejected",
            )
        payload = response.json()
        message_id = payload.get("result", {}).get("message_id")
        return TelegramBotApiSendResult(
            ok=True,
            provider_message_id=str(message_id) if message_id is not None else None,
            http_status=response.status_code,
        )


def format_telegram_result(
    *,
    alias_text: str,
    result: RunResult,
    partial_failure: bool = False,
) -> str:
    if partial_failure:
        base = result.summary or "The workflow finished with partial failures."
        return sanitize_telegram_message(
            f"{alias_text} partial update:\n{base}",
            fallback=f"{alias_text} finished with partial failures.",
        )
    base = result.summary or "The workflow completed."
    return sanitize_telegram_message(
        f"{alias_text}:\n{base}",
        fallback=f"{alias_text} completed. Details are available in the run.",
    )


def sanitize_telegram_message(
    value: str,
    *,
    fallback: str = "Result is available, but sensitive details were redacted.",
    max_length: int = 3500,
) -> str:
    text = " ".join(value.replace("\r", "\n").splitlines())
    if _TOKENISH_RE.search(text):
        return fallback
    if len(text) > max_length:
        return f"{text[: max_length - 1].rstrip()}..."
    return text


def payload_fingerprint(text: str) -> str:
    return fingerprint_value(text)


def destination_fingerprint(chat_id: int) -> str:
    return fingerprint_value(chat_id)


def _secret_reference(token_ref: str) -> str:
    if token_ref.startswith("env:"):
        return token_ref.split(":", maxsplit=1)[1]
    if token_ref.startswith("static:"):
        return token_ref.split(":", maxsplit=1)[1]
    return token_ref
