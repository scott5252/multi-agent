from __future__ import annotations

import html
from typing import Annotated
from urllib.parse import urlsplit, urlunsplit
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from multi_agent_platform.api.deps import ContainerDep
from multi_agent_platform.api.schemas.auth import (
    LocalLoginEnvelope,
    LocalPrincipalOption,
    PrincipalContextResponse,
)
from multi_agent_platform.api.ui.admin_console import safe_redirect_target
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import AuthMode, PrincipalContext

router = APIRouter(prefix="/auth", tags=["auth"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
LOCAL_LOGIN_ACTION_TOKEN = "local-principal-login"


@router.get("/me", response_model=PrincipalContextResponse)
async def auth_me(
    principal: PrincipalDep,
) -> PrincipalContextResponse:
    return PrincipalContextResponse(
        principal_id=principal.principal_id,
        auth_mode=principal.auth_mode.value,
        auth_provider=principal.auth_provider.value,
        tenant_id=principal.tenant_id,
        org_id=principal.org_id,
        role_codes=list(principal.role_codes),
        permission_codes=list(principal.permission_codes),
        scope_type=principal.scope_type.value,
        support_override_request_id=principal.support_override_request_id,
    )


@router.get("/tenant-context/{tenant_id}", response_model=PrincipalContextResponse)
async def tenant_context(
    tenant_id: UUID,
    principal: PrincipalDep,
) -> PrincipalContextResponse:
    return PrincipalContextResponse(
        principal_id=principal.principal_id,
        auth_mode=principal.auth_mode.value,
        auth_provider=principal.auth_provider.value,
        tenant_id=tenant_id,
        org_id=principal.org_id,
        role_codes=list(principal.role_codes),
        permission_codes=list(principal.permission_codes),
        scope_type="tenant",
        support_override_request_id=principal.support_override_request_id,
    )


@router.get(
    "/local-login",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def local_login_page(
    request: Request,
    container: ContainerDep,
    redirect_to: str = "/admin/app/workflows",
) -> HTMLResponse:
    settings = container.settings
    if settings.auth_mode is not AuthMode.LOCAL_PRINCIPAL:
        raise HTTPException(status_code=404, detail="local login is unavailable")
    envelope = build_local_login_envelope(
        request=request,
        container=container,
        redirect_to=redirect_to,
    )
    return render_local_login_page(envelope)


@router.get("/local-login.json", response_model=LocalLoginEnvelope)
async def local_login_envelope(
    request: Request,
    container: ContainerDep,
    redirect_to: str = "/admin/app",
) -> LocalLoginEnvelope:
    if container.settings.auth_mode is not AuthMode.LOCAL_PRINCIPAL:
        raise HTTPException(status_code=404, detail="local login is unavailable")
    return build_local_login_envelope(
        request=request,
        container=container,
        redirect_to=redirect_to,
    )


@router.post("/local-login", include_in_schema=False)
async def local_login_submit(
    container: ContainerDep,
    principal: str = Form(),
    redirect_to: str = Form(default="/admin/app"),
    action_token: str = Form(default=LOCAL_LOGIN_ACTION_TOKEN),
) -> RedirectResponse:
    settings = container.settings
    if settings.auth_mode is not AuthMode.LOCAL_PRINCIPAL:
        raise HTTPException(status_code=404, detail="local login is unavailable")
    if action_token != LOCAL_LOGIN_ACTION_TOKEN:
        raise HTTPException(status_code=400, detail="invalid local login token")
    if principal not in settings.local_principal_catalog_json:
        raise HTTPException(status_code=400, detail="unknown local principal")
    if not settings.local_principal_catalog_json[principal].enabled:
        raise HTTPException(status_code=400, detail="unknown local principal")
    response = RedirectResponse(
        url=_safe_auth_redirect(redirect_to),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.set_cookie(
        key=settings.local_principal_cookie_name,
        value=principal,
        httponly=True,
        samesite="lax",
    )
    return response


@router.get("/local-logout", include_in_schema=False)
async def local_logout(
    container: ContainerDep,
    redirect_to: str = "/auth/local-login",
) -> RedirectResponse:
    response = RedirectResponse(
        url=_safe_auth_redirect(redirect_to),
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.delete_cookie(container.settings.local_principal_cookie_name)
    return response


def build_local_login_envelope(
    *,
    request: Request,
    container: ContainerDep,
    redirect_to: str,
) -> LocalLoginEnvelope:
    settings = container.settings
    principals = tuple(
        LocalPrincipalOption(
            catalog_key=entry.catalog_key,
            label=entry.display_name,
            scope_type="tenant" if entry.tenant_id is not None else "platform",
            tenant_id=entry.tenant_id,
            tenant_label="Tenant" if entry.tenant_id is not None else None,
            role_codes=tuple(sorted(entry.role_codes)),
        )
        for entry in sorted(
            (
                candidate
                for candidate in settings.local_principal_catalog_json.values()
                if candidate.enabled
            ),
            key=lambda candidate: candidate.catalog_key,
        )
    )
    current = request.cookies.get(settings.local_principal_cookie_name)
    if current not in settings.local_principal_catalog_json:
        current = None
    return LocalLoginEnvelope(
        auth_mode="local_principal",
        principals=principals,
        current_principal_key=current,
        redirect_to=_safe_auth_redirect(redirect_to),
        action_token=LOCAL_LOGIN_ACTION_TOKEN,
    )


def render_local_login_page(envelope: LocalLoginEnvelope) -> HTMLResponse:
    principal_cards = "\n".join(
        _local_principal_card(principal, envelope) for principal in envelope.principals
    )
    current = ""
    if envelope.current_principal_key:
        current_key = html.escape(envelope.current_principal_key)
        redirect_to = html.escape(envelope.redirect_to, quote=True)
        current = f"""
      <section class="card" style="margin-top: 1rem;">
        <p>Current cookie principal: <span class="mono">{current_key}</span></p>
        <a class="button-link" href="/auth/local-logout?redirect_to={redirect_to}">
          Sign Out
        </a>
      </section>"""
    document = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Local Login</title>
    <style>
      body {{
        font-family: system-ui, sans-serif;
        margin: 0;
        background: #f5f7f4;
        color: #14231d;
      }}
      .page-shell {{
        margin: 0 auto;
        max-width: 960px;
        padding: 2rem;
      }}
      .hero {{
        border: 1px solid #cfd8d2;
        padding: 1.25rem;
      }}
      .eyebrow {{
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0;
        margin: 0 0 0.25rem;
        text-transform: uppercase;
      }}
      h1 {{
        margin: 0 0 0.5rem;
      }}
      .subhead {{
        margin: 0;
      }}
      .registry-grid {{
        display: grid;
        gap: 1rem;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        margin-top: 1rem;
      }}
      .card {{
        background: white;
        border: 1px solid #cfd8d2;
        padding: 1rem;
      }}
      .card-top {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.375rem;
      }}
      .badge {{
        background: #e4efe7;
        border: 1px solid #b7ccbd;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.125rem 0.375rem;
      }}
      .mono {{
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        overflow-wrap: anywhere;
      }}
      button,
      .button-link {{
        background: #1b6f55;
        border: 1px solid #155944;
        color: white;
        display: inline-block;
        font-weight: 700;
        padding: 0.5rem 0.75rem;
        text-decoration: none;
      }}
    </style>
  </head>
  <body class="workflow-page">
    <main class="page-shell">
      <section class="hero compact">
        <div>
          <p class="eyebrow">Local Login</p>
          <h1>Choose a local principal</h1>
          <p class="subhead">
            This local QA sign-in path stores the selected catalog key in a
            protected local cookie.
          </p>
        </div>
      </section>
      <section class="registry-grid">
{principal_cards}
      </section>{current}
    </main>
  </body>
</html>
"""
    return HTMLResponse(document, headers={"X-Local-Login-Response": "non-jinja"})


def _local_principal_card(
    principal: LocalPrincipalOption,
    envelope: LocalLoginEnvelope,
) -> str:
    roles = "".join(
        f'<span class="badge">{html.escape(role)}</span>'
        for role in principal.role_codes
    )
    catalog_key = html.escape(principal.catalog_key, quote=True)
    label = html.escape(principal.label)
    redirect_to = html.escape(envelope.redirect_to, quote=True)
    action_token = html.escape(envelope.action_token, quote=True)
    return f"""
        <article class="card registry-card">
          <div class="card-top">{roles}</div>
          <h2>{label}</h2>
          <p class="mono">{catalog_key}</p>
          <form method="post" action="/auth/local-login">
            <input type="hidden" name="principal" value="{catalog_key}">
            <input type="hidden" name="redirect_to" value="{redirect_to}">
            <input type="hidden" name="action_token" value="{action_token}">
            <button type="submit">Sign In</button>
          </form>
        </article>"""


def _safe_auth_redirect(value: str | None) -> str:
    if value and value.startswith("/auth/local-login") and not value.startswith("//"):
        return value
    if safe_run_redirect := _safe_run_redirect(value):
        return safe_run_redirect
    return safe_redirect_target(value, fallback="/admin/app")


def _safe_run_redirect(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or parsed.path.startswith("//"):
        return None
    if parsed.path in {"/runs", "/runs/new"} or parsed.path.startswith("/runs/"):
        return urlunsplit(("", "", parsed.path, parsed.query, ""))
    return None
