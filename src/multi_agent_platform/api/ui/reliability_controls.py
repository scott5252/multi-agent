from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from multi_agent_platform.config.settings import Settings

router = APIRouter(prefix="/admin/reliability/ui", tags=["reliability-ui"])
templates = Jinja2Templates(directory=str(Settings().web_admin_templates_dir))


def reliability_template(name: str) -> Path:
    return Settings().web_admin_templates_dir / "reliability" / name


@router.get("/", response_class=HTMLResponse)
async def reliability_dashboard_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "reliability/index.html", {"title": "Reliability"}
    )


@router.get("/breakers", response_class=HTMLResponse)
async def reliability_breakers_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "reliability/breakers.html", {"title": "Circuit Breakers"}
    )


@router.get("/dead-letters", response_class=HTMLResponse)
async def reliability_dead_letters_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "reliability/dead_letters.html", {"title": "Dead Letters"}
    )
