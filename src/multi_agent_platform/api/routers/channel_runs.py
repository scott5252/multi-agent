from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Request, status
from fastapi.responses import JSONResponse, RedirectResponse, Response
from starlette.responses import StreamingResponse

from multi_agent_platform.api.deps import ContainerDep, get_scope
from multi_agent_platform.api.schemas.channel_runs import (
    ArtifactDownloadUrlResponse,
    ArtifactListResponse,
    ArtifactMetadataResponse,
    CallbackRegistrationRequest,
    CallbackRegistrationResponse,
    CancelRunRequest,
    ChannelErrorDetail,
    ChannelErrorResponse,
    NotificationSubscriptionRequest,
    NotificationSubscriptionResponse,
    PromptDecisionRequest,
    PromptDecisionResponse,
    RunInvocationRequest,
    RunInvocationResponse,
    RunResultResponse,
    RunStatusResponse,
    TelegramLinkTokenResponse,
    TimelineEventResponse,
    TimelineResponse,
    WaitingPromptResponse,
)
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.channels.errors import ChannelError
from multi_agent_platform.channels.models import (
    ChannelType,
    ErrorCategory,
    PromptDecisionResult,
    RunInvocationResult,
    RunResult,
    RunStatusView,
    TimelineEvent,
)
from multi_agent_platform.channels.normalization import actor_from_scope
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.channels.streaming import stream_timeline_events
from multi_agent_platform.tenancy.context import ScopeContext

router = APIRouter(tags=["channels"])
IdempotencyHeader = Annotated[str | None, Header(alias="X-Idempotency-Key")]
PrincipalDep = Annotated[object, Depends(require_authorized_principal)]


async def get_authorized_scope(
    request: Request,
    _principal: PrincipalDep,
) -> ScopeContext:
    return get_scope(request)


ScopeDep = Annotated[ScopeContext, Depends(get_authorized_scope)]


def get_channel_service(container: ContainerDep) -> ChannelService:
    service = container.state.get("channel_service")
    if not isinstance(service, ChannelService):
        service = ChannelService(settings=container.settings)
        container.state["channel_service"] = service
    return service


ChannelServiceDep = Annotated[ChannelService, Depends(get_channel_service)]


@router.post(
    "/runs",
    response_model=RunInvocationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ChannelErrorResponse},
        403: {"model": ChannelErrorResponse},
        409: {"model": ChannelErrorResponse},
        429: {"model": ChannelErrorResponse},
    },
)
async def start_run(
    request: Request,
    scope: ScopeDep,
    service: ChannelServiceDep,
    idempotency_key: IdempotencyHeader = None,
) -> Response:
    try:
        payload, wants_html = await _parse_invocation(request)
        key = idempotency_key or request.headers.get("X-Idempotency-Key")
        if key is None and not wants_html:
            raise ChannelError(
                ErrorCategory.MISSING_INPUT, "Idempotency key is required."
            )
        if key is None:
            key = f"web-ui-{payload.workflow_id}-{scope.principal_id}"
        actor = actor_from_scope(
            scope,
            channel_type=ChannelType.WEB_UI if wants_html else payload.channel,
        )
        result = await service.start_run(
            actor=actor,
            workflow_id=payload.workflow_id,
            inputs=payload.inputs,
            idempotency_key=key,
        )
    except ChannelError as exc:
        return _channel_error(exc, trace_id=scope.trace_id)
    if wants_html:
        return RedirectResponse(f"/runs/{result.run_id}", status_code=303)
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=_invocation_response(result).model_dump(mode="json"),
    )


@router.get("/runs/{run_id}/status", response_model=RunStatusResponse)
async def get_run_status(
    run_id: UUID,
    scope: ScopeDep,
    service: ChannelServiceDep,
) -> Response:
    try:
        actor = actor_from_scope(scope, channel_type=ChannelType.WEB_API)
        return JSONResponse(
            content=_status_response(
                service.get_status(actor=actor, run_id=run_id)
            ).model_dump(mode="json")
        )
    except ChannelError as exc:
        return _channel_error(exc, trace_id=scope.trace_id)


@router.get("/runs/{run_id}/timeline", response_model=TimelineResponse)
async def get_run_timeline(
    run_id: UUID,
    scope: ScopeDep,
    service: ChannelServiceDep,
    cursor: str | None = None,
    limit: int = 100,
) -> Response:
    try:
        actor = actor_from_scope(scope, channel_type=ChannelType.WEB_API)
        items, next_cursor = service.list_timeline(
            actor=actor,
            run_id=run_id,
            cursor=cursor,
            limit=min(max(limit, 1), 500),
        )
        return JSONResponse(
            content=TimelineResponse(
                items=[_timeline_event_response(item) for item in items],
                next_cursor=next_cursor,
            ).model_dump(mode="json")
        )
    except ChannelError as exc:
        return _channel_error(exc, trace_id=scope.trace_id)


@router.get(
    "/runs/{run_id}/events",
    response_class=StreamingResponse,
    response_model=None,
)
async def get_run_events(
    run_id: UUID,
    scope: ScopeDep,
    service: ChannelServiceDep,
    last_event_id: Annotated[str | None, Header(alias="Last-Event-ID")] = None,
) -> Response:
    try:
        actor = actor_from_scope(scope, channel_type=ChannelType.WEB_UI)
        events, _next_cursor = service.list_timeline(
            actor=actor,
            run_id=run_id,
            cursor=last_event_id,
            limit=500,
        )
        return StreamingResponse(
            stream_timeline_events(
                events,
                heartbeat_seconds=service.settings.channel_sse_heartbeat_seconds,
            ),
            media_type="text/event-stream",
        )
    except ChannelError as exc:
        return _channel_error(exc, trace_id=scope.trace_id)


@router.get("/runs/{run_id}/result", response_model=RunResultResponse)
async def get_run_result(
    run_id: UUID,
    scope: ScopeDep,
    service: ChannelServiceDep,
) -> Response:
    try:
        actor = actor_from_scope(scope, channel_type=ChannelType.WEB_API)
        return JSONResponse(
            content=_result_response(
                service.get_result(actor=actor, run_id=run_id)
            ).model_dump(mode="json")
        )
    except ChannelError as exc:
        return _channel_error(exc, trace_id=scope.trace_id)


@router.post(
    "/runs/{run_id}/approvals/{prompt_id}/decision",
    response_model=PromptDecisionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def decide_prompt(
    run_id: UUID,
    prompt_id: UUID,
    payload: PromptDecisionRequest,
    scope: ScopeDep,
    service: ChannelServiceDep,
    idempotency_key: IdempotencyHeader = None,
) -> Response:
    try:
        actor = actor_from_scope(scope, channel_type=ChannelType.WEB_API)
        result = service.decide_prompt(
            actor=actor,
            run_id=run_id,
            prompt_id=prompt_id,
            action=payload.action,
            prompt_version=payload.prompt_version,
            decision_payload=payload.decision_payload,
            idempotency_key=_require_key(idempotency_key, scope.trace_id),
        )
        return JSONResponse(
            status_code=202 if result.accepted else 409,
            content=_decision_response(result).model_dump(mode="json"),
        )
    except ChannelError as exc:
        return _channel_error(exc, trace_id=scope.trace_id)


@router.post(
    "/runs/{run_id}/cancel",
    response_model=RunStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def cancel_run(
    run_id: UUID,
    payload: CancelRunRequest,
    scope: ScopeDep,
    service: ChannelServiceDep,
    idempotency_key: IdempotencyHeader = None,
) -> Response:
    try:
        actor = actor_from_scope(scope, channel_type=ChannelType.WEB_API)
        result = await service.cancel_run(
            actor=actor,
            run_id=run_id,
            reason=payload.reason,
            idempotency_key=_require_key(idempotency_key, scope.trace_id),
        )
        return JSONResponse(
            status_code=202,
            content=_status_response(result).model_dump(mode="json"),
        )
    except ChannelError as exc:
        return _channel_error(exc, trace_id=scope.trace_id)


@router.get("/runs/{run_id}/artifacts", response_model=ArtifactListResponse)
async def list_artifacts(
    run_id: UUID,
    scope: ScopeDep,
    service: ChannelServiceDep,
) -> Response:
    try:
        actor = actor_from_scope(scope, channel_type=ChannelType.WEB_API)
        items = service.list_artifacts(actor=actor, run_id=run_id)
        return JSONResponse(
            content=ArtifactListResponse(
                run_id=run_id,
                items=[
                    ArtifactMetadataResponse(
                        artifact_id=item.artifact_id,
                        name=item.name,
                        user_facing_type=item.user_facing_type,
                        status=item.status,
                        download_url_available=item.download_url_available,
                        size_bytes=item.size_bytes,
                    )
                    for item in items
                ],
            ).model_dump(mode="json")
        )
    except ChannelError as exc:
        return _channel_error(exc, trace_id=scope.trace_id)


@router.post(
    "/runs/{run_id}/artifacts/{artifact_id}/download-url",
    response_model=ArtifactDownloadUrlResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_artifact_download_url(
    run_id: UUID,
    artifact_id: UUID,
    scope: ScopeDep,
    service: ChannelServiceDep,
    idempotency_key: IdempotencyHeader = None,
) -> Response:
    try:
        actor = actor_from_scope(scope, channel_type=ChannelType.WEB_API)
        grant = service.create_artifact_download_url(
            actor=actor,
            run_id=run_id,
            artifact_id=artifact_id,
            idempotency_key=_require_key(idempotency_key, scope.trace_id),
        )
        return JSONResponse(
            status_code=201,
            content=ArtifactDownloadUrlResponse(
                artifact_id=grant.artifact_id,
                download_url=grant.download_url,
                expires_at=grant.expires_at,
                trace_id=grant.trace_id,
            ).model_dump(mode="json"),
        )
    except ChannelError as exc:
        return _channel_error(exc, trace_id=scope.trace_id)


@router.post(
    "/runs/{run_id}/subscriptions",
    response_model=NotificationSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def subscribe_to_run(
    run_id: UUID,
    payload: NotificationSubscriptionRequest,
    scope: ScopeDep,
    service: ChannelServiceDep,
    idempotency_key: IdempotencyHeader = None,
) -> Response:
    try:
        actor = actor_from_scope(scope, channel_type=payload.channel)
        subscription = service.subscribe(
            actor=actor,
            run_id=run_id,
            channel=payload.channel,
            event_types=payload.event_types,
            idempotency_key=_require_key(idempotency_key, scope.trace_id),
        )
        return JSONResponse(
            status_code=201,
            content=NotificationSubscriptionResponse(
                subscription_id=subscription.subscription_id,
                status=subscription.status,
            ).model_dump(mode="json"),
        )
    except ChannelError as exc:
        return _channel_error(exc, trace_id=scope.trace_id)


@router.post(
    "/runs/{run_id}/callbacks",
    response_model=CallbackRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_callback(
    run_id: UUID,
    payload: CallbackRegistrationRequest,
    scope: ScopeDep,
    service: ChannelServiceDep,
    idempotency_key: IdempotencyHeader = None,
) -> Response:
    try:
        actor = actor_from_scope(scope, channel_type=ChannelType.WEB_API)
        registration = service.register_callback(
            actor=actor,
            run_id=run_id,
            callback_url=payload.callback_url,
            event_types=payload.event_types,
            idempotency_key=_require_key(idempotency_key, scope.trace_id),
        )
        return JSONResponse(
            status_code=201,
            content=CallbackRegistrationResponse(
                callback_registration_id=registration.callback_registration_id,
                status=registration.status,
            ).model_dump(mode="json"),
        )
    except ChannelError as exc:
        return _channel_error(exc, trace_id=scope.trace_id)


@router.post(
    "/channels/telegram/link-token",
    response_model=TelegramLinkTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_telegram_link_token(
    scope: ScopeDep,
    service: ChannelServiceDep,
) -> TelegramLinkTokenResponse:
    actor = actor_from_scope(scope, channel_type=ChannelType.WEB_API)
    token = service.create_telegram_link_token(actor)
    return TelegramLinkTokenResponse(
        link_token=token.token, expires_at=token.expires_at
    )


async def _parse_invocation(request: Request) -> tuple[RunInvocationRequest, bool]:
    content_type = request.headers.get("content-type", "")
    if (
        "application/x-www-form-urlencoded" in content_type
        or "multipart/form-data" in content_type
    ):
        form = await request.form()
        workflow_id = str(form.get("workflow_id", ""))
        raw_input = str(form.get("input", ""))
        return (
            RunInvocationRequest(
                workflow_id=workflow_id,
                channel=ChannelType.WEB_UI,
                inputs={"text": raw_input},
            ),
            True,
        )
    return RunInvocationRequest.model_validate(await request.json()), False


def _require_key(idempotency_key: str | None, trace_id: str) -> str:
    if not idempotency_key:
        raise ChannelError(
            ErrorCategory.MISSING_INPUT,
            "Idempotency key is required.",
            trace_id=trace_id,
        )
    return idempotency_key


def _channel_error(exc: ChannelError, *, trace_id: str) -> JSONResponse:
    payload = ChannelErrorResponse(
        error=ChannelErrorDetail(category=exc.category, message=exc.message),
        trace_id=exc.trace_id or trace_id,
    )
    return JSONResponse(
        status_code=exc.status_code, content=payload.model_dump(mode="json")
    )


def _invocation_response(result: RunInvocationResult) -> RunInvocationResponse:
    return RunInvocationResponse(
        run_id=result.run_id,
        state=result.state,
        status_url=result.status_url,
        timeline_url=result.timeline_url,
        events_url=result.events_url,
        trace_id=result.trace_id,
    )


def _status_response(status_view: RunStatusView) -> RunStatusResponse:
    prompt = status_view.waiting_prompt
    return RunStatusResponse(
        run_id=status_view.run_id,
        state=status_view.state,
        progress_summary=status_view.progress_summary,
        latest_timeline_cursor=status_view.latest_timeline_cursor,
        waiting_prompt=(
            WaitingPromptResponse(
                prompt_id=prompt.prompt_id,
                prompt_type=prompt.prompt_type,
                prompt_version=prompt.prompt_version,
                summary=prompt.summary,
                context=prompt.context,
                allowed_actions=prompt.allowed_actions,
                deadline_at=prompt.deadline_at,
            )
            if prompt is not None
            else None
        ),
        terminal_outcome=status_view.terminal_outcome,
        result_availability=status_view.result_availability,
        artifact_availability=status_view.artifact_availability,
        subscribed=status_view.subscribed,
        permitted_actions=status_view.permitted_actions,
        trace_id=status_view.trace_id,
    )


def _timeline_event_response(event: TimelineEvent) -> TimelineEventResponse:
    return TimelineEventResponse(
        event_id=event.event_id,
        sequence=event.sequence,
        event_type=event.event_type,
        state=event.state,
        summary=event.summary,
        severity=event.severity,
        occurred_at=event.occurred_at,
        trace_id=event.trace_id,
    )


def _result_response(result: RunResult) -> RunResultResponse:
    return RunResultResponse(
        run_id=result.run_id,
        availability=result.availability,
        state=result.state,
        summary=result.summary,
        structured_result=result.structured_result,
        trace_id=result.trace_id,
    )


def _decision_response(result: PromptDecisionResult) -> PromptDecisionResponse:
    return PromptDecisionResponse(
        accepted=result.accepted,
        decision_id=result.decision_id,
        rejection_category=result.rejection_category,
        run_status=_status_response(result.run_status),
        trace_id=result.trace_id,
    )
