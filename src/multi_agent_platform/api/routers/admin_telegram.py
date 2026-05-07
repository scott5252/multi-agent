from __future__ import annotations

from typing import Annotated
from urllib.parse import urlencode
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.telegram_config.models import (
    TelegramAccessScope,
    TelegramConfigScopeType,
    TelegramConfigStaleRevisionError,
    TelegramDiagnosticCategory,
    TelegramDiagnosticStatus,
    TelegramIdentityStatus,
    TelegramLinkTokenStatus,
    TelegramProviderReadiness,
)
from multi_agent_platform.admin.telegram_config.service import (
    TelegramConfigurationService,
)
from multi_agent_platform.api.deps import ContainerDep, get_session
from multi_agent_platform.api.schemas.telegram_config import (
    TelegramCommandAliasListResponse,
    TelegramCommandAliasResponse,
    TelegramCommandAliasUpsertRequest,
    TelegramConsoleSnapshotResponse,
    TelegramDiagnosticResponse,
    TelegramDiagnosticsResponse,
    TelegramIdentityListResponse,
    TelegramIdentitySummaryResponse,
    TelegramLinkTokenAuditResponse,
    TelegramLinkTokenIssueResponse,
    TelegramLinkTokenListResponse,
    TelegramReadinessResponse,
    TenantTelegramConfigResponse,
    TenantTelegramConfigUpdateRequest,
)
from multi_agent_platform.api.ui.admin_console import (
    is_platform_admin,
)
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.db.models.telegram_config import (
    TelegramCommandAlias,
    TelegramDiagnosticEvent,
    TelegramLinkedIdentitySummary,
    TelegramLinkTokenAudit,
    TelegramTenantConfiguration,
)
from multi_agent_platform.db.repositories.telegram_config import (
    TelegramConfigRepository,
)

router = APIRouter(prefix="/admin/telegram", tags=["telegram-config"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
SEE_OTHER = status.HTTP_303_SEE_OTHER
TELEGRAM_QUERY_KEYS = frozenset(
    {
        "tenant_id",
        "alias_id",
        "identity_id",
        "token_audit_id",
        "status",
        "category",
        "enabled",
        "saved_filter_id",
        "panel",
    }
)


def _channel_service(container: ContainerDep) -> ChannelService:
    service = container.state.get("channel_service")
    if isinstance(service, ChannelService):
        return service
    service = ChannelService(settings=container.settings)
    container.state["channel_service"] = service
    return service


def _service(
    *, session: AsyncSession, container: ContainerDep
) -> TelegramConfigurationService:
    return TelegramConfigurationService(
        repository=TelegramConfigRepository(session),
        settings=container.settings,
        channel_service=_channel_service(container),
    )


@router.get("/api/readiness", response_model=TelegramReadinessResponse)
async def telegram_readiness_api(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> TelegramReadinessResponse:
    _ = principal, session
    return _readiness_response(_service(session=session, container=container))


@router.get("/api/config", response_model=TenantTelegramConfigResponse)
async def telegram_config_api(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: UUID | None = None,
) -> TenantTelegramConfigResponse:
    service = _service(session=session, container=container)
    scope = _tenant_access_scope(principal, tenant_id)
    config = await service.tenant_config(scope)
    if config is None:
        raise HTTPException(status_code=403, detail="tenant Telegram scope required")
    return _config_response(config, service.provider_readiness())


@router.post("/api/config", response_model=TenantTelegramConfigResponse)
async def update_telegram_config_api(
    payload: TenantTelegramConfigUpdateRequest,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> TenantTelegramConfigResponse:
    service = _service(session=session, container=container)
    scope = _tenant_access_scope(principal, payload.tenant_id)
    try:
        config = await service.update_tenant_config(
            access_scope=scope,
            enabled=payload.enabled,
            protected_commands=payload.protected_commands,
            status_note=payload.status_note,
            revision_token=payload.revision_token,
        )
    except TelegramConfigStaleRevisionError as exc:
        raise HTTPException(status_code=409, detail="stale revision") from exc
    return _config_response(config, service.provider_readiness())


@router.post("/api/webhook/validate", response_model=TelegramDiagnosticResponse)
async def validate_telegram_webhook_api(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: UUID | None = None,
) -> TelegramDiagnosticResponse:
    service = _service(session=session, container=container)
    diagnostic = await service.validate_webhook(_access_scope(principal, tenant_id))
    return _diagnostic_response(diagnostic)


@router.get("/api/aliases", response_model=TelegramCommandAliasListResponse)
async def telegram_aliases_api(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: UUID | None = None,
) -> TelegramCommandAliasListResponse:
    service = _service(session=session, container=container)
    aliases = await service.list_aliases(_tenant_access_scope(principal, tenant_id))
    return TelegramCommandAliasListResponse(
        items=tuple(_alias_response(item) for item in aliases)
    )


@router.post("/api/aliases", response_model=TelegramCommandAliasResponse)
async def upsert_telegram_alias_api(
    payload: TelegramCommandAliasUpsertRequest,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
) -> TelegramCommandAliasResponse:
    service = _service(session=session, container=container)
    scope = _tenant_access_scope(principal, payload.tenant_id)
    try:
        alias = await service.upsert_alias(
            access_scope=scope,
            alias_text=payload.alias_text,
            published_workflow_version_id=payload.published_workflow_version_id,
            description=payload.description,
            protected=payload.protected,
            enabled=payload.enabled,
            revision_token=payload.revision_token,
        )
    except TelegramConfigStaleRevisionError as exc:
        raise HTTPException(status_code=409, detail="stale revision") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _alias_response(alias)


@router.get("/api/diagnostics", response_model=TelegramDiagnosticsResponse)
async def telegram_diagnostics_api(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: UUID | None = None,
) -> TelegramDiagnosticsResponse:
    service = _service(session=session, container=container)
    diagnostics = await service.list_diagnostics(_access_scope(principal, tenant_id))
    return TelegramDiagnosticsResponse(
        items=tuple(_diagnostic_response(item) for item in diagnostics)
    )


@router.get("/api/link-tokens", response_model=TelegramLinkTokenListResponse)
async def telegram_link_tokens_api(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: UUID | None = None,
) -> TelegramLinkTokenListResponse:
    service = _service(session=session, container=container)
    tokens = await service.list_link_tokens(_tenant_access_scope(principal, tenant_id))
    return TelegramLinkTokenListResponse(
        items=tuple(_token_response(item) for item in tokens)
    )


@router.post(
    "/api/link-tokens",
    response_model=TelegramLinkTokenIssueResponse,
    status_code=status.HTTP_201_CREATED,
)
async def issue_telegram_link_token_api(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: UUID | None = None,
) -> TelegramLinkTokenIssueResponse:
    service = _service(session=session, container=container)
    issued = await service.issue_link_token(_tenant_access_scope(principal, tenant_id))
    return TelegramLinkTokenIssueResponse(
        link_token=issued.raw_token,
        token_audit=_token_response(issued.audit),
    )


@router.post(
    "/api/link-tokens/{token_audit_id}/revoke",
    response_model=TelegramLinkTokenAuditResponse,
)
async def revoke_telegram_link_token_api(
    token_audit_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: UUID | None = None,
) -> TelegramLinkTokenAuditResponse:
    service = _service(session=session, container=container)
    audit = await service.revoke_link_token(
        access_scope=_tenant_access_scope(principal, tenant_id),
        token_audit_id=token_audit_id,
    )
    if audit is None:
        raise HTTPException(status_code=404, detail="Telegram link token not found")
    return _token_response(audit)


@router.get("/api/identities", response_model=TelegramIdentityListResponse)
async def telegram_identities_api(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: UUID | None = None,
) -> TelegramIdentityListResponse:
    service = _service(session=session, container=container)
    identities = await service.list_identities(
        _tenant_access_scope(principal, tenant_id)
    )
    return TelegramIdentityListResponse(
        items=tuple(_identity_response(item) for item in identities)
    )


@router.post(
    "/api/identities/{identity_id}/revoke",
    response_model=TelegramIdentitySummaryResponse,
)
async def revoke_telegram_identity_api(
    identity_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: UUID | None = None,
) -> TelegramIdentitySummaryResponse:
    service = _service(session=session, container=container)
    identity = await service.revoke_identity(
        access_scope=_tenant_access_scope(principal, tenant_id),
        identity_id=identity_id,
    )
    if identity is None:
        raise HTTPException(status_code=404, detail="Telegram identity not found")
    return _identity_response(identity)


@router.get("/api/snapshot", response_model=TelegramConsoleSnapshotResponse)
async def telegram_snapshot_api(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: UUID | None = None,
) -> TelegramConsoleSnapshotResponse:
    service = _service(session=session, container=container)
    scope = _access_scope(principal, tenant_id)
    tenant_scope = (
        _tenant_access_scope(principal, tenant_id)
        if scope.tenant_id is not None
        else None
    )
    config = await service.tenant_config(tenant_scope) if tenant_scope else None
    aliases = await service.list_aliases(tenant_scope) if tenant_scope else ()
    tokens = await service.list_link_tokens(tenant_scope) if tenant_scope else ()
    identities = await service.list_identities(tenant_scope) if tenant_scope else ()
    diagnostics = await service.list_diagnostics(scope)
    readiness = service.provider_readiness()
    return TelegramConsoleSnapshotResponse(
        readiness=_readiness_response(service),
        tenant_config=_config_response(config, readiness) if config else None,
        aliases=tuple(_alias_response(item) for item in aliases),
        token_audits=tuple(_token_response(item) for item in tokens),
        identities=tuple(_identity_response(item) for item in identities),
        diagnostics=tuple(_diagnostic_response(item) for item in diagnostics),
    )


@router.get("", response_model=None, include_in_schema=False)
async def telegram_configuration_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: UUID | None = None,
) -> RedirectResponse:
    _ = (session, container)
    _access_scope(principal, tenant_id)
    return _react_redirect(request, panel="telegram")


@router.post("/config", response_model=None, include_in_schema=False)
async def update_telegram_config_page(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[UUID | None, Form()] = None,
    enabled: Annotated[bool, Form()] = False,
    protected_commands: Annotated[list[str] | None, Form()] = None,
    status_note: Annotated[str | None, Form()] = None,
    revision_token: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    service = _service(session=session, container=container)
    scope = _tenant_access_scope(principal, tenant_id)
    try:
        await service.update_tenant_config(
            access_scope=scope,
            enabled=enabled,
            protected_commands=tuple(protected_commands or ()),
            status_note=status_note,
            revision_token=revision_token,
        )
    except TelegramConfigStaleRevisionError as exc:
        raise HTTPException(status_code=409, detail="stale revision") from exc
    return RedirectResponse(
        _redirect_target(scope, panel="telegram"),
        status_code=SEE_OTHER,
    )


@router.post("/webhook/validate", response_model=None, include_in_schema=False)
async def validate_telegram_webhook_page(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[UUID | None, Form()] = None,
) -> RedirectResponse:
    service = _service(session=session, container=container)
    scope = _access_scope(principal, tenant_id)
    await service.validate_webhook(scope)
    return RedirectResponse(
        _redirect_target(scope, panel="webhook"),
        status_code=SEE_OTHER,
    )


@router.post("/aliases", response_model=None, include_in_schema=False)
async def upsert_telegram_alias_page(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[UUID | None, Form()] = None,
    alias_text: Annotated[str, Form()] = "",
    published_workflow_version_id: Annotated[UUID | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    protected: Annotated[bool, Form()] = True,
    enabled: Annotated[bool, Form()] = True,
    revision_token: Annotated[str | None, Form()] = None,
) -> RedirectResponse:
    if published_workflow_version_id is None:
        raise HTTPException(
            status_code=422, detail="published workflow version required"
        )
    service = _service(session=session, container=container)
    scope = _tenant_access_scope(principal, tenant_id)
    try:
        await service.upsert_alias(
            access_scope=scope,
            alias_text=alias_text,
            published_workflow_version_id=published_workflow_version_id,
            description=description,
            protected=protected,
            enabled=enabled,
            revision_token=revision_token,
        )
    except TelegramConfigStaleRevisionError as exc:
        raise HTTPException(status_code=409, detail="stale revision") from exc
    return RedirectResponse(
        _redirect_target(scope, panel="aliases"),
        status_code=SEE_OTHER,
    )


@router.post("/link-tokens", response_model=None, include_in_schema=False)
async def issue_telegram_link_token_page(
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[UUID | None, Form()] = None,
) -> JSONResponse:
    service = _service(session=session, container=container)
    scope = _tenant_access_scope(principal, tenant_id)
    issued = await service.issue_link_token(scope)
    response = TelegramLinkTokenIssueResponse(
        link_token=issued.raw_token,
        token_audit=_token_response(issued.audit),
    )
    return JSONResponse(
        content=response.model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
    )


@router.post(
    "/link-tokens/{token_audit_id}/revoke",
    response_model=None,
    include_in_schema=False,
)
async def revoke_telegram_link_token_page(
    token_audit_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[UUID | None, Form()] = None,
) -> RedirectResponse:
    service = _service(session=session, container=container)
    scope = _tenant_access_scope(principal, tenant_id)
    audit = await service.revoke_link_token(
        access_scope=scope,
        token_audit_id=token_audit_id,
    )
    if audit is None:
        raise HTTPException(status_code=404, detail="Telegram link token not found")
    return RedirectResponse(
        _redirect_target(scope, panel="link-tokens"),
        status_code=SEE_OTHER,
    )


@router.post(
    "/identities/{identity_id}/revoke",
    response_model=None,
    include_in_schema=False,
)
async def revoke_telegram_identity_page(
    identity_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    container: ContainerDep,
    tenant_id: Annotated[UUID | None, Form()] = None,
) -> RedirectResponse:
    service = _service(session=session, container=container)
    scope = _tenant_access_scope(principal, tenant_id)
    identity = await service.revoke_identity(
        access_scope=scope,
        identity_id=identity_id,
    )
    if identity is None:
        raise HTTPException(status_code=404, detail="Telegram identity not found")
    return RedirectResponse(
        _redirect_target(scope, panel="identities"),
        status_code=SEE_OTHER,
    )


def _access_scope(
    principal: PrincipalContext,
    tenant_id: UUID | None,
) -> TelegramAccessScope:
    platform = is_platform_admin(principal)
    if platform and tenant_id is None:
        return TelegramAccessScope(
            scope_type=TelegramConfigScopeType.PLATFORM,
            principal_id=principal.principal_id,
            platform_admin=True,
        )
    selected_tenant = tenant_id or principal.tenant_id
    if selected_tenant is None:
        raise HTTPException(status_code=403, detail="tenant Telegram scope required")
    if not platform and selected_tenant != principal.tenant_id:
        raise HTTPException(status_code=403, detail="tenant scope is not authorized")
    return TelegramAccessScope(
        scope_type=TelegramConfigScopeType.TENANT,
        tenant_id=selected_tenant,
        principal_id=principal.principal_id,
        platform_admin=platform,
    )


def _tenant_access_scope(
    principal: PrincipalContext,
    tenant_id: UUID | None,
) -> TelegramAccessScope:
    scope = _access_scope(principal, tenant_id)
    if scope.tenant_id is None:
        raise HTTPException(status_code=403, detail="tenant Telegram scope required")
    return scope


def _redirect_target(
    scope: TelegramAccessScope,
    *,
    panel: str | None = None,
    extra: dict[str, object] | None = None,
) -> str:
    query: dict[str, str] = {}
    if scope.tenant_id is not None:
        query["tenant_id"] = str(scope.tenant_id)
    if panel:
        query["panel"] = panel
    if extra:
        for key, value in extra.items():
            if value is not None:
                query[key] = str(value)
    suffix = f"?{urlencode(query)}" if query else ""
    return f"/admin/app/channels{suffix}"


def _react_redirect(
    request: Request,
    *,
    panel: str | None = None,
    extra: dict[str, object] | None = None,
) -> RedirectResponse:
    query: dict[str, str] = {
        key: value
        for key, value in request.query_params.items()
        if key in TELEGRAM_QUERY_KEYS and value
    }
    if panel:
        query.setdefault("panel", panel)
    if extra:
        for key, value in extra.items():
            if value is not None:
                query[key] = str(value)
    suffix = f"?{urlencode(query)}" if query else ""
    return RedirectResponse(f"/admin/app/channels{suffix}", status_code=SEE_OTHER)


def _readiness_response(
    service: TelegramConfigurationService,
) -> TelegramReadinessResponse:
    return _readiness_from_model(service.provider_readiness())


def _readiness_from_model(
    readiness: TelegramProviderReadiness,
) -> TelegramReadinessResponse:
    return TelegramReadinessResponse.model_validate(
        readiness,
        from_attributes=True,
    )


def _config_response(
    config: TelegramTenantConfiguration,
    readiness: TelegramProviderReadiness,
) -> TenantTelegramConfigResponse:
    ready = bool(config.enabled and readiness.ready)
    return TenantTelegramConfigResponse(
        telegram_tenant_config_id=config.telegram_tenant_config_id,
        tenant_id=config.tenant_id,
        enabled=config.enabled,
        protected_commands=tuple(config.protected_commands),
        status_note=config.status_note,
        revision_token=config.revision_token,
        updated_by_principal_id=config.updated_by_principal_id,
        created_at=config.created_at,
        updated_at=config.updated_at,
        command_ready=ready,
    )


def _alias_response(record: TelegramCommandAlias) -> TelegramCommandAliasResponse:
    return TelegramCommandAliasResponse(
        telegram_command_alias_id=record.telegram_command_alias_id,
        tenant_id=record.tenant_id,
        alias_text=record.alias_text,
        alias_normalized=record.alias_normalized,
        published_workflow_version_id=record.published_workflow_version_id,
        description=record.description,
        protected=record.protected,
        enabled=record.enabled,
        revision_token=record.revision_token,
        updated_by_principal_id=record.updated_by_principal_id,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _token_response(record: TelegramLinkTokenAudit) -> TelegramLinkTokenAuditResponse:
    return TelegramLinkTokenAuditResponse(
        telegram_link_token_audit_id=record.telegram_link_token_audit_id,
        tenant_id=record.tenant_id,
        issued_by_principal_id=record.issued_by_principal_id,
        token_fingerprint=record.token_fingerprint[:12],
        status=TelegramLinkTokenStatus(record.status),
        expires_at=record.expires_at,
        issued_at=record.issued_at,
        consumed_at=record.consumed_at,
        revoked_at=record.revoked_at,
        trace_id=record.trace_id,
    )


def _identity_response(
    record: TelegramLinkedIdentitySummary,
) -> TelegramIdentitySummaryResponse:
    return TelegramIdentitySummaryResponse(
        telegram_linked_identity_summary_id=record.telegram_linked_identity_summary_id,
        tenant_id=record.tenant_id,
        platform_identity_id=record.platform_identity_id,
        telegram_user_display=record.telegram_user_display,
        telegram_chat_display=record.telegram_chat_display,
        status=TelegramIdentityStatus(record.status),
        linked_at=record.linked_at,
        revoked_at=record.revoked_at,
        command_ready=record.command_ready,
        trace_id=record.trace_id,
    )


def _diagnostic_response(
    record: TelegramDiagnosticEvent,
) -> TelegramDiagnosticResponse:
    return TelegramDiagnosticResponse(
        telegram_diagnostic_event_id=record.telegram_diagnostic_event_id,
        tenant_id=record.tenant_id,
        principal_id=record.principal_id,
        category=TelegramDiagnosticCategory(record.category),
        status=TelegramDiagnosticStatus(record.status),
        summary=record.summary,
        trace_id=record.trace_id,
        redacted_metadata=record.redacted_metadata,
        created_at=record.created_at,
    )
