from __future__ import annotations

from fastapi import FastAPI

from multi_agent_platform.api.lifespan import app_lifespan
from multi_agent_platform.api.routers.admin_access import router as admin_access_router
from multi_agent_platform.api.routers.auth import router as auth_router
from multi_agent_platform.api.routers.ops import router as ops_router
from multi_agent_platform.tenancy.middleware import TenancyMiddleware


def create_app() -> FastAPI:
    app = FastAPI(title="Multi-Agent Platform", lifespan=app_lifespan)
    app.add_middleware(TenancyMiddleware)
    app.include_router(ops_router)
    app.include_router(auth_router)
    app.include_router(admin_access_router)
    return app


app = create_app()
