from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.config.settings import Settings


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = Settings()
    container = build_container(settings)
    app.state.container = container
    try:
        yield
    finally:
        await container.dispose()
