from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from multi_agent_platform.api.lifespan import app_lifespan
from multi_agent_platform.api.routers.admin_access import router as admin_access_router
from multi_agent_platform.api.routers.admin_model_skill_config import (
    router as admin_model_skill_config_router,
)
from multi_agent_platform.api.routers.admin_run_inspection import (
    router as admin_run_inspection_router,
)
from multi_agent_platform.api.routers.admin_workflow_ui import (
    router as admin_workflow_ui_router,
)
from multi_agent_platform.api.routers.admin_workflows import (
    router as admin_workflows_router,
)
from multi_agent_platform.api.routers.auth import router as auth_router
from multi_agent_platform.api.routers.channel_runs import router as channel_runs_router
from multi_agent_platform.api.routers.memory import router as memory_router
from multi_agent_platform.api.routers.ops import router as ops_router
from multi_agent_platform.api.routers.runtime_runs import router as runtime_runs_router
from multi_agent_platform.api.routers.telegram_webhook import (
    router as telegram_webhook_router,
)
from multi_agent_platform.api.routers.web_run_ui import router as web_run_ui_router
from multi_agent_platform.config.settings import Settings
from multi_agent_platform.tenancy.middleware import TenancyMiddleware


def create_app() -> FastAPI:
    app = FastAPI(title="Multi-Agent Platform", lifespan=app_lifespan)
    app.add_middleware(TenancyMiddleware)
    app.mount(
        "/admin/static",
        StaticFiles(directory=str(Settings().web_admin_static_dir)),
        name="admin-static",
    )
    app.include_router(ops_router)
    app.include_router(auth_router)
    app.include_router(admin_access_router)
    app.include_router(admin_run_inspection_router)
    app.include_router(admin_workflows_router)
    app.include_router(admin_model_skill_config_router)
    app.include_router(admin_workflow_ui_router)
    app.include_router(runtime_runs_router)
    app.include_router(memory_router)
    app.include_router(channel_runs_router)
    app.include_router(web_run_ui_router)
    app.include_router(telegram_webhook_router)
    return app


app = create_app()
