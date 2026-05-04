from __future__ import annotations

from typing import Annotated, cast

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.routers.channel_runs import ChannelServiceDep
from multi_agent_platform.channels.telegram import TelegramCommandHandler
from multi_agent_platform.channels.telegram_delivery import (
    HttpTelegramBotApiClient,
    TelegramBotApiClient,
)
from multi_agent_platform.db.repositories.channels import ChannelRepository
from multi_agent_platform.db.repositories.telegram_config import (
    TelegramConfigRepository,
)

router = APIRouter(prefix="/channels/telegram", tags=["telegram"])
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/webhook/{secret}")
async def telegram_webhook(
    secret: str,
    update: dict[str, object],
    service: ChannelServiceDep,
    session: SessionDep,
    container: ContainerDep,
) -> dict[str, object]:
    bot_client = container.state.get("telegram_bot_client")
    if bot_client is None:
        bot_client = HttpTelegramBotApiClient(secret_provider=container.secret_provider)
    handler = TelegramCommandHandler(
        service,
        service.settings.telegram_webhook_secret,
        settings=service.settings,
        telegram_config_repository=TelegramConfigRepository(session),
        channel_repository=ChannelRepository(session),
        bot_client=cast(TelegramBotApiClient, bot_client),
    )
    return await handler.handle_update(provided_secret=secret, update=update)
