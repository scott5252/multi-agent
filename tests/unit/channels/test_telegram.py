from __future__ import annotations

import pytest

from multi_agent_platform.channels.models import ChannelActor, ChannelType
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.channels.telegram import TelegramCommandHandler
from multi_agent_platform.config.settings import Settings


@pytest.mark.asyncio
async def test_telegram_link_run_status_and_duplicate_update() -> None:
    service = ChannelService(
        settings=Settings(
            _env_file=None,
            app_env="test",
            telegram_webhook_secret="secret",
        )
    )
    actor = ChannelActor(None, "tenant-user", ChannelType.WEB_API, "trace-1")
    link_token = service.create_telegram_link_token(actor)
    handler = TelegramCommandHandler(service, "secret")

    linked = await handler.handle_update(
        provided_secret="secret",
        update={
            "update_id": 1,
            "message": {
                "chat": {"id": 10},
                "from": {"id": 20},
                "text": f"/link {link_token.token}",
            },
        },
    )
    started = await handler.handle_update(
        provided_secret="secret",
        update={
            "update_id": 2,
            "message": {
                "chat": {"id": 10},
                "from": {"id": 20},
                "text": "/run demo hello",
            },
        },
    )
    duplicate = await handler.handle_update(
        provided_secret="secret",
        update={
            "update_id": 2,
            "message": {
                "chat": {"id": 10},
                "from": {"id": 20},
                "text": "/run demo hello",
            },
        },
    )

    assert linked["ok"] is True
    assert started == duplicate
    assert "run_id" in started


@pytest.mark.asyncio
async def test_telegram_rejects_unlinked_protected_command() -> None:
    service = ChannelService(settings=Settings(_env_file=None, app_env="test"))
    handler = TelegramCommandHandler(service, None)

    response = await handler.handle_update(
        provided_secret="",
        update={
            "update_id": 1,
            "message": {
                "chat": {"id": 10},
                "from": {"id": 20},
                "text": "/status 11111111-1111-1111-1111-111111111111",
            },
        },
    )

    assert response["error_category"] == "unauthorized"
