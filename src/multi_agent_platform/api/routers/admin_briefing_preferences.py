from __future__ import annotations

import json
from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.briefing_preferences.models import (
    BriefingPreferenceAccessScope,
    BriefingPreferencePayload,
    BriefingPreferencePermissionError,
    BriefingPreferenceScopeType,
    BriefingPreferenceStaleRevisionError,
)
from multi_agent_platform.admin.briefing_preferences.service import (
    BriefingPreferenceRuntimeContext,
    BriefingPreferenceService,
)
from multi_agent_platform.api.deps import get_session
from multi_agent_platform.api.routers.admin_console import build_shell_for_request
from multi_agent_platform.api.schemas.briefing_preferences import (
    BriefingPreferenceExportResponse,
    BriefingPreferenceImportRequest,
    BriefingPreferencePayloadRequest,
    BriefingPreferenceProfileResponse,
    BriefingPreferenceResolveRequest,
    BriefingPreferenceResolveResponse,
    BriefingPreferenceResponse,
    BriefingPreferenceSummaryListResponse,
    BriefingPreferenceSummaryResponse,
)
from multi_agent_platform.api.ui.admin_console import (
    BreadcrumbItem,
    CommonStateType,
    build_common_state,
    is_platform_admin,
)
from multi_agent_platform.api.ui.briefing_preferences import (
    BriefingPreferencesPage,
    redaction_notice,
)
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.briefing_preferences import (
    BriefingPreferenceProfile,
)
from multi_agent_platform.db.repositories.briefing_preferences import (
    BriefingPreferenceRepository,
)

router = APIRouter(
    prefix="/admin/briefing-preferences",
    tags=["briefing-preferences"],
)
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def _service(session: AsyncSession) -> BriefingPreferenceService:
    return BriefingPreferenceService(BriefingPreferenceRepository(session))


@router.get("/api/profile", response_model=BriefingPreferenceProfileResponse)
async def briefing_preference_profile_api(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID | None = None,
    principal_id: str | None = None,
) -> BriefingPreferenceProfileResponse:
    scope = _tenant_access_scope(principal, tenant_id)
    if principal_id not in (None, principal.principal_id):
        await _service(session).record_denial(
            access_scope=scope,
            reason="raw profile reads are limited to the owner",
            metadata={"target_principal": principal_id or ""},
        )
        raise HTTPException(status_code=403, detail="briefing preference access denied")
    profile = await _service(session).get_own_profile(scope)
    return BriefingPreferenceProfileResponse(
        profile=_profile_response(profile) if profile else None
    )


@router.post("/api/profile", response_model=BriefingPreferenceResponse)
async def save_briefing_preference_profile_api(
    payload: BriefingPreferencePayloadRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> BriefingPreferenceResponse:
    service = _service(session)
    scope = _tenant_access_scope(principal, payload.tenant_id)
    try:
        result = await service.save_own_profile(
            access_scope=scope,
            payload=BriefingPreferencePayload.model_validate(
                payload.model_dump(exclude={"tenant_id", "revision_token"})
            ),
            revision_token=payload.revision_token,
        )
    except BriefingPreferenceStaleRevisionError as exc:
        raise HTTPException(status_code=409, detail="stale revision") from exc
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    return _profile_response(result.profile)


@router.get("/api/summaries", response_model=BriefingPreferenceSummaryListResponse)
async def briefing_preference_summaries_api(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID | None = None,
) -> BriefingPreferenceSummaryListResponse:
    summaries = await _service(session).list_summaries(
        _access_scope(principal, tenant_id)
    )
    return BriefingPreferenceSummaryListResponse(
        items=tuple(_summary_response(item) for item in summaries)
    )


@router.get("/api/export", response_model=BriefingPreferenceExportResponse)
async def briefing_preference_export_api(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID | None = None,
) -> BriefingPreferenceExportResponse:
    try:
        exported = await _service(session).export_own_profile(
            _tenant_access_scope(principal, tenant_id)
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="profile not found") from exc
    return BriefingPreferenceExportResponse(document=exported.document)


@router.post("/api/import", response_model=BriefingPreferenceResponse)
async def briefing_preference_import_api(
    payload: BriefingPreferenceImportRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> BriefingPreferenceResponse:
    service = _service(session)
    try:
        result = await service.import_own_profile(
            access_scope=_tenant_access_scope(principal, payload.tenant_id),
            document=payload.document,
            revision_token=payload.revision_token,
        )
    except BriefingPreferencePermissionError as exc:
        raise HTTPException(
            status_code=403, detail="import ownership mismatch"
        ) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    return _profile_response(result.profile)


@router.post("/api/resolve", response_model=BriefingPreferenceResolveResponse)
async def briefing_preference_resolve_api(
    payload: BriefingPreferenceResolveRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> BriefingPreferenceResolveResponse:
    scope = _tenant_access_scope(principal, payload.tenant_id)
    if payload.principal_id != principal.principal_id and not is_platform_admin(
        principal
    ):
        await _service(session).record_denial(
            access_scope=scope,
            reason="runtime resolve principal mismatch",
            metadata={"target_principal": payload.principal_id},
        )
        raise HTTPException(status_code=403, detail="briefing preference access denied")
    context = await _service(session).resolve_runtime_context(
        tenant_id=payload.tenant_id,
        principal_id=payload.principal_id,
        source_channel=payload.source_channel,
        trace_id=payload.trace_id,
    )
    return _resolve_response(context)


@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def briefing_preferences_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID | None = None,
) -> HTMLResponse:
    service = _service(session)
    scope = _access_scope(principal, tenant_id)
    tenant_scope = scope if scope.tenant_id is not None else None
    profile = await service.get_own_profile(tenant_scope) if tenant_scope else None
    summaries = await service.list_summaries(scope)
    page = BriefingPreferencesPage(
        profile=_profile_response(profile) if profile else None,
        summaries=tuple(_summary_response(item) for item in summaries),
        can_edit=bool(
            tenant_scope
            and principal.tenant_id is not None
            and principal.tenant_id == tenant_scope.tenant_id
        ),
    )
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Briefing Preferences",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(
                label="Briefing Preferences",
                href="/admin/briefing-preferences",
            ),
        ),
        common_state=None
        if profile or summaries
        else build_common_state(
            CommonStateType.EMPTY,
            title="No briefing preferences yet",
            summary=(
                "Save a profile to make Daily Intelligence Briefing runs context-aware."
            ),
            trace_id=principal.trace_id,
        ),
    )
    return cast(
        HTMLResponse,
        request.app.state.container.workflow_ui_templates.TemplateResponse(
            request,
            "briefing_preferences/index.html",
            {
                "shell": shell,
                "principal": principal,
                "page": page,
                "redaction_notice": redaction_notice(),
            },
        ),
    )


@router.post("", response_class=HTMLResponse, include_in_schema=False)
async def save_briefing_preferences_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[UUID | None, Form()] = None,
    location_label: Annotated[str, Form()] = "",
    timezone: Annotated[str, Form()] = "",
    news_topics: Annotated[str, Form()] = "",
    vip_senders: Annotated[str, Form()] = "",
    workday_start: Annotated[str, Form()] = "09:00",
    workday_end: Annotated[str, Form()] = "17:00",
    commute_mode: Annotated[str, Form()] = "none",
    calendar_account_ref: Annotated[str, Form()] = "none",
    email_account_ref: Annotated[str, Form()] = "none",
    output_style: Annotated[str, Form()] = "standard",
    scheduled_enabled: Annotated[bool, Form()] = False,
    scheduled_time: Annotated[str | None, Form()] = None,
    revision_token: Annotated[str | None, Form()] = None,
) -> Response:
    service = _service(session)
    scope = _tenant_access_scope(principal, tenant_id)
    try:
        await service.save_own_profile(
            access_scope=scope,
            payload=BriefingPreferencePayload.model_validate(
                {
                    "location_label": location_label,
                    "timezone": timezone,
                    "news_topics": news_topics,
                    "vip_senders": vip_senders,
                    "workday_start": workday_start,
                    "workday_end": workday_end,
                    "commute_mode": commute_mode,
                    "calendar_account_ref": calendar_account_ref,
                    "email_account_ref": email_account_ref,
                    "output_style": output_style,
                    "scheduled_enabled": scheduled_enabled,
                    "scheduled_time": scheduled_time,
                }
            ),
            revision_token=revision_token,
        )
    except BriefingPreferenceStaleRevisionError:
        return await _page_error(
            request=request,
            principal=principal,
            session=session,
            scope=scope,
            status_code=status.HTTP_409_CONFLICT,
            title="Stale briefing preference form",
            summary=(
                "The current profile changed. Review current values before "
                "saving again."
            ),
        )
    except ValidationError as exc:
        return await _page_error(
            request=request,
            principal=principal,
            session=session,
            scope=scope,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Briefing preference validation failed",
            summary=str(exc.errors()[0]["msg"]),
        )
    return RedirectResponse(
        f"/admin/briefing-preferences?tenant_id={scope.tenant_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/import", response_class=HTMLResponse, include_in_schema=False)
async def import_briefing_preferences_page(
    request: Request,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: Annotated[UUID | None, Form()] = None,
    import_document: Annotated[str, Form()] = "",
    revision_token: Annotated[str | None, Form()] = None,
) -> Response:
    service = _service(session)
    scope = _tenant_access_scope(principal, tenant_id)
    try:
        document = json.loads(import_document)
        if not isinstance(document, dict):
            raise ValueError("import document must be a JSON object")
        await service.import_own_profile(
            access_scope=scope,
            document=document,
            revision_token=revision_token,
        )
    except (
        BriefingPreferencePermissionError,
        ValidationError,
        ValueError,
        json.JSONDecodeError,
    ) as exc:
        return await _page_error(
            request=request,
            principal=principal,
            session=session,
            scope=scope,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Briefing preference import failed",
            summary=str(exc),
        )
    return RedirectResponse(
        f"/admin/briefing-preferences?tenant_id={scope.tenant_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/export", include_in_schema=False)
async def export_briefing_preferences_page(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: UUID | None = None,
) -> JSONResponse:
    try:
        exported = await _service(session).export_own_profile(
            _tenant_access_scope(principal, tenant_id)
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="profile not found") from exc
    return JSONResponse(content=exported.document)


async def _page_error(
    *,
    request: Request,
    principal: PrincipalContext,
    session: AsyncSession,
    scope: BriefingPreferenceAccessScope,
    status_code: int,
    title: str,
    summary: str,
) -> HTMLResponse:
    service = _service(session)
    profile = await service.get_own_profile(scope)
    summaries = await service.list_summaries(scope)
    shell = await build_shell_for_request(
        request=request,
        principal=principal,
        session=session,
        title="Briefing Preferences",
        breadcrumbs=(
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(
                label="Briefing Preferences",
                href="/admin/briefing-preferences",
            ),
        ),
        common_state=build_common_state(
            CommonStateType.VALIDATION_ERROR,
            title=title,
            summary=summary,
            trace_id=principal.trace_id,
        ),
    )
    return cast(
        HTMLResponse,
        request.app.state.container.workflow_ui_templates.TemplateResponse(
            request,
            "briefing_preferences/index.html",
            {
                "shell": shell,
                "principal": principal,
                "page": BriefingPreferencesPage(
                    profile=_profile_response(profile) if profile else None,
                    summaries=tuple(_summary_response(item) for item in summaries),
                    error_message=summary,
                    can_edit=True,
                ),
                "redaction_notice": redaction_notice(),
            },
            status_code=status_code,
        ),
    )


def _access_scope(
    principal: PrincipalContext,
    tenant_id: UUID | None,
) -> BriefingPreferenceAccessScope:
    platform = is_platform_admin(principal)
    if platform and tenant_id is None:
        return BriefingPreferenceAccessScope(
            scope_type=BriefingPreferenceScopeType.PLATFORM,
            principal_id=principal.principal_id,
            platform_admin=True,
            trace_id=principal.trace_id,
        )
    selected_tenant = tenant_id or principal.tenant_id
    if selected_tenant is None:
        raise HTTPException(status_code=403, detail="tenant scope required")
    if not platform and selected_tenant != principal.tenant_id:
        raise HTTPException(status_code=403, detail="tenant scope is not authorized")
    return BriefingPreferenceAccessScope(
        scope_type=BriefingPreferenceScopeType.TENANT,
        tenant_id=selected_tenant,
        principal_id=principal.principal_id,
        platform_admin=platform,
        trace_id=principal.trace_id,
    )


def _tenant_access_scope(
    principal: PrincipalContext,
    tenant_id: UUID | None,
) -> BriefingPreferenceAccessScope:
    scope = _access_scope(principal, tenant_id)
    if scope.tenant_id is None:
        raise HTTPException(status_code=403, detail="tenant scope required")
    return scope


def _profile_response(
    profile: BriefingPreferenceProfile,
) -> BriefingPreferenceResponse:
    return BriefingPreferenceResponse(
        briefing_preference_profile_id=profile.briefing_preference_profile_id,
        tenant_id=profile.tenant_id,
        principal_id=profile.principal_id,
        location_label=profile.location_label,
        timezone=profile.timezone,
        news_topics=tuple(profile.news_topics or ()),
        vip_senders=tuple(profile.vip_senders or ()),
        workday_start=profile.workday_start,
        workday_end=profile.workday_end,
        commute_mode=profile.commute_mode,
        calendar_account_ref=profile.calendar_account_ref,
        email_account_ref=profile.email_account_ref,
        output_style=profile.output_style,
        scheduled_enabled=profile.scheduled_enabled,
        scheduled_time=profile.scheduled_time,
        current_revision_id=profile.current_revision_id,
        revision_number=profile.revision_number,
        content_digest=profile.content_digest,
        safe_summary=profile.safe_summary,
        revision_token=profile.revision_token,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def _summary_response(
    profile: BriefingPreferenceProfile,
) -> BriefingPreferenceSummaryResponse:
    return BriefingPreferenceSummaryResponse(
        briefing_preference_profile_id=profile.briefing_preference_profile_id,
        tenant_id=profile.tenant_id,
        principal_id=profile.principal_id,
        current_revision_id=profile.current_revision_id,
        revision_number=profile.revision_number,
        content_digest=profile.content_digest,
        safe_summary=profile.safe_summary,
        updated_at=profile.updated_at,
    )


def _resolve_response(
    context: BriefingPreferenceRuntimeContext,
) -> BriefingPreferenceResolveResponse:
    return BriefingPreferenceResolveResponse(
        available=context.available,
        tenant_id=context.tenant_id,
        principal_id=context.principal_id,
        source_channel=context.source_channel,
        trace_id=context.trace_id,
        revision_id=context.revision_id,
        content_digest=context.content_digest,
        preferences=context.preferences or {},
        safe_summary=context.safe_summary or {},
        reason=context.reason,
    )
