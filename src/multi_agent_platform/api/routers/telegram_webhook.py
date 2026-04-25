from __future__ import annotations

from fastapi import APIRouter

from multi_agent_platform.api.routers.channel_runs import ChannelServiceDep
from multi_agent_platform.channels.telegram import TelegramCommandHandler

router = APIRouter(prefix="/channels/telegram", tags=["telegram"])


@router.post("/webhook/{secret}")
async def telegram_webhook(
    secret: str,
    update: dict[str, object],
    service: ChannelServiceDep,
) -> dict[str, object]:
    handler = TelegramCommandHandler(
        service,
        service.settings.telegram_webhook_secret,
    )
    return await handler.handle_update(provided_secret=secret, update=update)
