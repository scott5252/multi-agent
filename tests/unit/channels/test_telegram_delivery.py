from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.channels.models import (
    ResultAvailability,
    RunResult,
    UserVisibleRunState,
)
from multi_agent_platform.channels.telegram_delivery import (
    HttpTelegramBotApiClient,
    MockTelegramBotApiClient,
    destination_fingerprint,
    format_telegram_result,
    payload_fingerprint,
    sanitize_telegram_message,
)
from multi_agent_platform.secrets.base import SecretProvider, SecretValue


class _FakeSecretProvider(SecretProvider):
    provider_name = "fake"

    def __init__(self) -> None:
        self.references: list[str] = []

    async def resolve(self, reference: str) -> SecretValue:
        self.references.append(reference)
        return SecretValue(reference=reference, value="telegram-token")


def test_telegram_delivery_formats_safe_final_result() -> None:
    run_id = uuid4()
    result = RunResult(
        run_id=run_id,
        availability=ResultAvailability.AVAILABLE,
        state=UserVisibleRunState.COMPLETED,
        trace_id="trace-1",
        summary="Daily Intelligence Briefing completed.",
    )
    text = format_telegram_result(alias_text="Morning briefing", result=result)

    assert "Morning briefing" in text
    assert "Daily Intelligence Briefing completed." in text
    assert payload_fingerprint(text) != text
    assert destination_fingerprint(123456789) != "123456789"


def test_telegram_delivery_formats_partial_redacted_and_truncated_results() -> None:
    run_id = uuid4()
    result = RunResult(
        run_id=run_id,
        availability=ResultAvailability.AVAILABLE,
        state=UserVisibleRunState.COMPLETED,
        trace_id="trace-1",
        summary="partial summary",
    )

    partial = format_telegram_result(
        alias_text="Morning briefing",
        result=result,
        partial_failure=True,
    )
    redacted = sanitize_telegram_message(
        "token abcdefghijklmnopqrstuvwxyz123456",
        fallback="safe fallback",
    )
    truncated = sanitize_telegram_message("abcdefghij", max_length=8)

    assert "partial update" in partial
    assert redacted == "safe fallback"
    assert truncated == "abcdefg..."


@pytest.mark.asyncio
async def test_mock_telegram_bot_api_client_records_send_message() -> None:
    client = MockTelegramBotApiClient()
    result = await client.send_message(
        token_ref="env:QA022_TELEGRAM_TOKEN",
        chat_id=123456789,
        text="Morning briefing delivered.",
        trace_id="trace-1",
    )

    assert result.ok is True
    assert result.provider_message_id == "mock-1"
    assert client.sent_messages[0].token_ref == "env:QA022_TELEGRAM_TOKEN"


@pytest.mark.asyncio
async def test_mock_telegram_bot_api_client_can_record_failure() -> None:
    client = MockTelegramBotApiClient(fail_category="provider_unavailable")

    result = await client.send_message(
        token_ref="env:QA022_TELEGRAM_TOKEN",
        chat_id=123456789,
        text="Morning briefing delivered.",
        trace_id="trace-1",
    )

    assert result.ok is False
    assert result.http_status == 503
    assert result.failure_category == "provider_unavailable"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "expected_ok", "expected_failure", "expected_message_id"),
    [
        (200, True, None, "42"),
        (400, False, "provider_rejected", None),
        (503, False, "provider_unavailable", None),
    ],
)
async def test_http_telegram_bot_api_client_maps_provider_responses(
    monkeypatch,
    status_code,
    expected_ok,
    expected_failure,
    expected_message_id,
) -> None:
    provider = _FakeSecretProvider()
    posts: list[dict[str, object]] = []

    class _FakeResponse:
        def __init__(self, status_code: int) -> None:
            self.status_code = status_code

        def json(self) -> dict[str, object]:
            return {"result": {"message_id": 42}}

    class _FakeAsyncClient:
        def __init__(self, *, timeout: float) -> None:
            self.timeout = timeout

        async def __aenter__(self) -> _FakeAsyncClient:
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def post(
            self,
            url: str,
            *,
            json: dict[str, object],
            headers: dict[str, str],
        ) -> _FakeResponse:
            posts.append({"url": url, "json": json, "headers": headers})
            return _FakeResponse(status_code)

    monkeypatch.setattr(
        "multi_agent_platform.channels.telegram_delivery.httpx.AsyncClient",
        _FakeAsyncClient,
    )
    client = HttpTelegramBotApiClient(
        secret_provider=provider,
        timeout_seconds=1.5,
    )

    result = await client.send_message(
        token_ref="env:QA022_TELEGRAM_TOKEN",
        chat_id=123456789,
        text="Morning briefing delivered.",
        trace_id="trace-1",
    )

    assert provider.references == ["QA022_TELEGRAM_TOKEN"]
    assert posts[0]["url"] == "https://api.telegram.org/bottelegram-token/sendMessage"
    assert result.ok is expected_ok
    assert result.provider_message_id == expected_message_id
    assert result.failure_category == expected_failure
