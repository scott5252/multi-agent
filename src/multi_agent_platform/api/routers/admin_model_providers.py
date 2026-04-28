from __future__ import annotations

from typing import Annotated
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.routers.admin_console import build_shell_for_request
from multi_agent_platform.api.schemas.model_providers import (
    CatalogSyncResponse,
    ProviderConnectionCreateRequest,
    ProviderConnectionListItem,
    ProviderConnectionListResponse,
    ProviderConnectionResponse,
    ProviderConnectionUpdateRequest,
    ProviderTestResponse,
)
from multi_agent_platform.api.ui.admin_console import (
    BreadcrumbItem,
    CommonStateType,
    build_common_state,
    is_platform_admin,
)
from multi_agent_platform.api.ui.model_providers import (
    build_catalog_page,
    build_detail_page,
    build_form_page,
    build_list_page,
)
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.model_providers import ModelProviderConnection
from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.model_providers.adapters import ProviderAdapterRegistry
from multi_agent_platform.model_providers.allowlist import LocalEndpointAllowlist
from multi_agent_platform.model_providers.local_adapter import (
    LocalOpenAICompatibleAdapter,
)
from multi_agent_platform.model_providers.models import (
    ProviderModel,
    ProviderType,
    TenantVisibility,
    TimeoutPolicy,
    VisibilityMode,
)
from multi_agent_platform.model_providers.openai_adapter import OpenAIAdapter
from multi_agent_platform.model_providers.probes import ProviderProbeRunner
from multi_agent_platform.model_providers.service import (
    ModelProviderPermissionError,
    ModelProviderService,
)
from multi_agent_platform.model_providers.validation import ProviderValidationError

router = APIRouter(prefix="/admin/model-providers", tags=["model-providers"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _allowlist(container: ContainerDep) -> LocalEndpointAllowlist:
    settings = container.settings
    return LocalEndpointAllowlist(
        schemes=settings.model_provider_local_allowed_schemes,
        hosts=settings.model_provider_local_allowed_hosts,
        ports=settings.model_provider_local_allowed_ports,
        cidrs=settings.model_provider_local_allowed_cidrs,
    )


def _service(session: AsyncSession, container: ContainerDep) -> ModelProviderService:
    allowlist = _allowlist(container)
    client = httpx.AsyncClient()
    registry = ProviderAdapterRegistry(
        {
            ProviderType.OPENAI: OpenAIAdapter(client),
            ProviderType.LOCAL_OPENAI_COMPATIBLE: LocalOpenAICompatibleAdapter(
                allowlist=allowlist,
                client=client,
            ),
        }
    )
    repository = ModelProviderRepository(session)
    return ModelProviderService(
        repository=repository,
        allowlist=allowlist,
        probe_runner=ProviderProbeRunner(registry),
    )


@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def model_provider_list_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    service = _service(session, container)
    items = await service.list_connections(principal=principal)
    page = build_list_page(items, can_mutate=is_platform_admin(principal))
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=page.title,
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Model Providers", href="/admin/model-providers"),
        ),
        common_state=build_common_state(
            CommonStateType.EMPTY,
            title="No model providers",
            summary="No model provider connections are visible in this scope.",
            trace_id=principal.trace_id,
        )
        if not items
        else None,
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "model_providers/index.html",
        {"page": page, "principal": principal, "shell": shell},
    )


@router.get("/new", response_class=HTMLResponse, include_in_schema=False)
async def new_model_provider_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    if not is_platform_admin(principal):
        raise HTTPException(status_code=403, detail="platform administrator required")
    page = build_form_page(connection_id=None, can_mutate=True)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=page.title,
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Model Providers", href="/admin/model-providers"),
            BreadcrumbItem(label="New", href="/admin/model-providers/new"),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "model_providers/edit.html",
        {
            "page": page,
            "connection": None,
            "models": (),
            "principal": principal,
            "shell": shell,
        },
    )


@router.get("/catalog", response_class=HTMLResponse, include_in_schema=False)
async def model_provider_catalog_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    page = build_catalog_page(entries=(), can_mutate=is_platform_admin(principal))
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=page.title,
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Model Providers", href="/admin/model-providers"),
            BreadcrumbItem(label="Catalog", href="/admin/model-providers/catalog"),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "model_providers/catalog.html",
        {"page": page, "principal": principal, "shell": shell},
    )


@router.get("/{connection_id}", response_class=HTMLResponse, include_in_schema=False)
async def model_provider_detail_page(
    connection_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    repository = ModelProviderRepository(session)
    service = _service(session, container)
    connection = await service.get_connection(
        connection_id=connection_id,
        principal=principal,
    )
    models = tuple(await repository.list_models(connection_id))
    tenant_ids = await repository.visible_tenant_ids(connection_id)
    latest_test = await repository.latest_test(connection_id)
    page = build_detail_page(
        connection=connection,
        models=models,
        tenant_ids=tenant_ids,
        latest_test=latest_test,
        can_mutate=is_platform_admin(principal),
    )
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=page.title,
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Model Providers", href="/admin/model-providers"),
            BreadcrumbItem(label=page.title, href=request.url.path),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "model_providers/detail.html",
        {"page": page, "principal": principal, "shell": shell},
    )


@router.get(
    "/{connection_id}/edit",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def edit_model_provider_page(
    connection_id: UUID,
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> HTMLResponse:
    if not is_platform_admin(principal):
        raise HTTPException(status_code=403, detail="platform administrator required")
    repository = ModelProviderRepository(session)
    connection = await repository.get_connection(connection_id)
    models = tuple(await repository.list_models(connection_id))
    page = build_form_page(connection_id=connection_id, can_mutate=True)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title=page.title,
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="Model Providers", href="/admin/model-providers"),
            BreadcrumbItem(label="Edit", href=request.url.path),
        ),
    )
    return container.workflow_ui_templates.TemplateResponse(
        request,
        "model_providers/edit.html",
        {
            "page": page,
            "connection": connection,
            "models": models,
            "principal": principal,
            "shell": shell,
        },
    )


@router.get("/api/connections", response_model=ProviderConnectionListResponse)
async def list_provider_connections(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> ProviderConnectionListResponse:
    items = await _service(session, container).list_connections(principal=principal)
    return ProviderConnectionListResponse(
        items=tuple(
            ProviderConnectionListItem(
                provider_connection_id=item.provider_connection_id,
                provider_type=item.provider_type,
                display_name=item.display_name,
                active=item.active,
                health_state=item.health_state,
                last_test_outcome=item.last_test_outcome,
                last_test_reason=item.last_test_reason,
                model_count=item.model_count,
                visibility_mode=item.visibility.mode,
                tenant_count=len(item.visibility.tenant_ids),
                catalog_sync_status=item.catalog_sync_status,
                updated_at=item.updated_at,
            )
            for item in items
        )
    )


@router.post("/api/connections", response_model=ProviderConnectionResponse)
async def create_provider_connection(
    payload: ProviderConnectionCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> ProviderConnectionResponse:
    connection = await _save_connection(
        payload=payload,
        principal=principal,
        session=session,
        container=container,
        connection_id=None,
    )
    await session.commit()
    return await _connection_response(session, connection.provider_connection_id)


@router.put(
    "/api/connections/{connection_id}",
    response_model=ProviderConnectionResponse,
)
async def update_provider_connection(
    connection_id: UUID,
    payload: ProviderConnectionUpdateRequest,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> ProviderConnectionResponse:
    connection = await _save_connection(
        payload=payload,
        principal=principal,
        session=session,
        container=container,
        connection_id=connection_id,
    )
    await session.commit()
    return await _connection_response(session, connection.provider_connection_id)


@router.post("/{connection_id}/activate", include_in_schema=False)
async def activate_connection_form(
    connection_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> RedirectResponse:
    await _service(session, container).set_active(
        principal=principal,
        connection_id=connection_id,
        active=True,
    )
    await session.commit()
    return RedirectResponse(f"/admin/model-providers/{connection_id}", status_code=303)


@router.post("/{connection_id}/deactivate", include_in_schema=False)
async def deactivate_connection_form(
    connection_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> RedirectResponse:
    await _service(session, container).set_active(
        principal=principal,
        connection_id=connection_id,
        active=False,
    )
    await session.commit()
    return RedirectResponse(f"/admin/model-providers/{connection_id}", status_code=303)


@router.post("/{connection_id}/test", response_model=ProviderTestResponse)
async def test_provider_connection(
    connection_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> ProviderTestResponse:
    result = await _service(session, container).test_connection(
        principal=principal,
        connection_id=connection_id,
    )
    await session.commit()
    return ProviderTestResponse.model_validate(result)


@router.post("/{connection_id}/sync-catalog", response_model=CatalogSyncResponse)
async def sync_provider_catalog(
    connection_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> CatalogSyncResponse:
    result = await _service(session, container).sync_catalog(
        principal=principal,
        connection_id=connection_id,
    )
    await session.commit()
    return CatalogSyncResponse(
        created=result.created,
        updated=result.updated,
        blocked=result.blocked,
        marked_unavailable=result.marked_unavailable,
        safe_summary=result.safe_summary,
    )


@router.post(
    "",
    response_class=HTMLResponse,
    response_model=None,
    include_in_schema=False,
)
@router.post(
    "/{connection_id}",
    response_class=HTMLResponse,
    response_model=None,
    include_in_schema=False,
)
async def save_provider_connection_form(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    provider_type: Annotated[ProviderType, Form()],
    display_name: Annotated[str, Form()],
    model_ids: Annotated[str, Form()],
    connection_id: UUID | None = None,
    base_url: Annotated[str, Form()] = "",
    tenant_ids: Annotated[str, Form()] = "",
    visibility_mode: Annotated[VisibilityMode, Form()] = (
        VisibilityMode.PLATFORM_DEFAULT
    ),
    credential_secret_reference_ids: Annotated[str, Form()] = "",
    connect_seconds: Annotated[float, Form()] = 5.0,
    read_seconds: Annotated[float, Form()] = 30.0,
    total_seconds: Annotated[float, Form()] = 45.0,
    active: Annotated[bool, Form()] = False,
) -> HTMLResponse | RedirectResponse:
    del request
    try:
        payload = ProviderConnectionCreateRequest(
            provider_type=provider_type,
            display_name=display_name,
            base_url=base_url or None,
            timeout_policy=TimeoutPolicy(
                connect_seconds=connect_seconds,
                read_seconds=read_seconds,
                total_seconds=total_seconds,
            ),
            visibility=TenantVisibility(
                mode=visibility_mode,
                tenant_ids=tuple(
                    UUID(value.strip())
                    for value in tenant_ids.replace("\n", ",").split(",")
                    if value.strip()
                ),
            ),
            models=tuple(
                ProviderModel(model_id=value.strip())
                for value in model_ids.replace("\n", ",").split(",")
                if value.strip()
            ),
            credential_secret_reference_ids=tuple(
                value.strip()
                for value in credential_secret_reference_ids.replace(
                    "\n",
                    ",",
                ).split(",")
                if value.strip()
            ),
            active=active,
        )
        connection = await _save_connection(
            payload=payload,
            principal=principal,
            session=session,
            container=container,
            connection_id=connection_id,
        )
        await session.commit()
    except (
        ProviderValidationError,
        ModelProviderPermissionError,
        ValueError,
    ) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return RedirectResponse(
        f"/admin/model-providers/{connection.provider_connection_id}",
        status_code=303,
    )


async def _save_connection(
    *,
    payload: ProviderConnectionCreateRequest | ProviderConnectionUpdateRequest,
    principal: PrincipalContext,
    session: AsyncSession,
    container: ContainerDep,
    connection_id: UUID | None,
) -> ModelProviderConnection:
    try:
        return await _service(session, container).save_connection(
            principal=principal,
            connection_id=connection_id,
            provider_type=payload.provider_type,
            display_name=payload.display_name,
            base_url=payload.base_url,
            timeout_policy=payload.timeout_policy,
            visibility=payload.visibility,
            models=payload.models,
            credential_secret_reference_ids=payload.credential_secret_reference_ids,
            active=payload.active,
        )
    except (ProviderValidationError, ModelProviderPermissionError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


async def _connection_response(
    session: AsyncSession,
    connection_id: UUID,
) -> ProviderConnectionResponse:
    repository = ModelProviderRepository(session)
    connection = await repository.get_connection(connection_id)
    models = await repository.list_models(connection_id)
    tenant_ids = await repository.visible_tenant_ids(connection_id)
    return ProviderConnectionResponse(
        provider_connection_id=connection.provider_connection_id,
        provider_type=connection.provider_type,
        display_name=connection.display_name,
        base_url_safe=connection.base_url_safe,
        timeout_policy=TimeoutPolicy.model_validate(connection.timeout_policy),
        visibility=TenantVisibility(
            mode=connection.visibility_mode,
            tenant_ids=tenant_ids,
        ),
        active=connection.active,
        health_state=connection.health_state,
        credential_secret_reference_ids=tuple(
            connection.credential_secret_reference_ids
        ),
        models=tuple(
            ProviderModel(
                model_id=model.model_id,
                display_name=model.display_name,
                capability_metadata=model.capability_metadata,
                cost_metadata=model.cost_metadata,
                default_parameters=model.default_parameters,
                available=model.available,
            )
            for model in models
        ),
        updated_at=connection.updated_at,
    )
