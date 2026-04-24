from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import get_scope, get_session
from multi_agent_platform.api.schemas.memory import (
    ErrorResponse,
    MemoryAuditResponse,
    MemoryConflictResponse,
    MemoryDiffEntry,
    MemoryDiffRequest,
    MemoryDiffResponse,
    MemoryHeadResponse,
    MemoryHistoryResponse,
    MemoryReplayResponse,
    MemoryScopeRef,
    MemoryVersionResponse,
    MemoryVersionSummary,
    MemoryWriteRequest,
    MemoryWriteResponse,
)
from multi_agent_platform.api.schemas.memory import (
    MemoryAuditAction as ApiAuditAction,
)
from multi_agent_platform.api.schemas.memory import (
    MemoryAuditEvent as ApiAuditEvent,
)
from multi_agent_platform.api.schemas.memory import (
    MemoryAuditOutcome as ApiAuditOutcome,
)
from multi_agent_platform.api.schemas.memory import (
    RuntimeSourceRef as ApiRuntimeSourceRef,
)
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.db.repositories.memory import SqlAlchemyMemoryRepository
from multi_agent_platform.memory.models import (
    MemoryAuditAction,
    MemoryAuditOutcome,
    MemoryConflictError,
    MemoryInvalidRequestError,
    MemoryNotFoundError,
    MemoryScopeIdentity,
    MemoryVersion,
    RuntimeSourceRef,
)
from multi_agent_platform.memory.models import (
    MemoryDiffEntry as DomainMemoryDiffEntry,
)
from multi_agent_platform.memory.policy import MemoryAccessPolicy
from multi_agent_platform.memory.service import MemoryService
from multi_agent_platform.tenancy.context import ScopeContext

router = APIRouter(prefix="/memory", tags=["memory"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_authorized_scope(
    request: Request,
    _principal: Annotated[object, Depends(require_authorized_principal)],
) -> ScopeContext:
    return get_scope(request)


ScopeDep = Annotated[ScopeContext, Depends(get_authorized_scope)]


def _service(session: AsyncSession) -> MemoryService:
    return MemoryService(SqlAlchemyMemoryRepository(session))


def _policy(scope: ScopeContext) -> MemoryAccessPolicy:
    return MemoryAccessPolicy(
        tenant_id=scope.tenant_id,
        principal_id=scope.principal_id,
    )


@router.post(
    "/versions",
    response_model=MemoryWriteResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": MemoryConflictResponse},
    },
)
async def create_memory_version(
    request: MemoryWriteRequest,
    scope: ScopeDep,
    session: SessionDep,
) -> MemoryWriteResponse:
    try:
        result = await _service(session).write_version(
            policy=_policy(scope),
            workflow_lineage_id=request.scope.workflow_lineage_id,
            agent_key=request.scope.agent_key,
            memory_key=request.scope.memory_key,
            content=request.content,
            expected_current_version_id=request.expected_current_version_id,
            assert_no_current_head=request.assert_no_current_head,
            idempotency_key=request.idempotency_key,
            change_reason=request.change_reason,
            change_summary_redacted=request.change_summary_redacted,
            source=_runtime_source(request.source),
            trace_id=scope.trace_id,
        )
    except MemoryConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": exc.detail,
                "conflict_type": exc.conflict_type.value,
                "latest_memory_version_id": str(exc.latest_memory_version_id)
                if exc.latest_memory_version_id
                else None,
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MemoryWriteResponse(
        scope=_scope_response(result.scope.identity, result.scope.memory_scope_id),
        version=_version_summary(result.version),
        head_advanced=result.head_advanced,
    )


@router.get("/head", response_model=MemoryHeadResponse)
async def get_memory_head(
    workflow_lineage_id: str,
    agent_key: str,
    memory_key: str,
    scope: ScopeDep,
    session: SessionDep,
) -> MemoryHeadResponse:
    head = await _service(session).get_current_head(
        policy=_policy(scope),
        workflow_lineage_id=workflow_lineage_id,
        agent_key=agent_key,
        memory_key=memory_key,
        include_content=True,
        trace_id=scope.trace_id,
    )
    return MemoryHeadResponse(
        has_memory=head.has_memory,
        scope=_scope_response(head.scope, head.memory_scope_id),
        head=_version_summary(head.version) if head.version else None,
        content=head.version.content if head.version else None,
    )


@router.get("/versions/{memory_version_id}", response_model=MemoryVersionResponse)
async def get_memory_version(
    memory_version_id: UUID,
    scope: ScopeDep,
    session: SessionDep,
    include_content: bool = True,
) -> MemoryVersionResponse:
    try:
        version = await _service(session).get_version(
            policy=_policy(scope),
            memory_version_id=memory_version_id,
            include_content=include_content,
            trace_id=scope.trace_id,
        )
    except MemoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail="memory version not found") from exc
    return _version_response(version)


@router.get(
    "/scopes/{memory_scope_id}/versions",
    response_model=MemoryHistoryResponse,
)
async def list_memory_history(
    memory_scope_id: UUID,
    scope: ScopeDep,
    session: SessionDep,
    cursor: str | None = None,
    limit: int = 100,
    include_content: bool = False,
) -> MemoryHistoryResponse:
    try:
        scope_identity, versions, next_cursor = await _service(session).list_history(
            policy=_policy(scope),
            memory_scope_id=memory_scope_id,
            include_content=include_content,
            limit=limit,
            cursor=cursor,
            trace_id=scope.trace_id,
        )
    except MemoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail="memory scope not found") from exc
    return MemoryHistoryResponse(
        scope=_scope_response(scope_identity, memory_scope_id),
        versions=[_version_response(version) for version in versions],
        next_cursor=next_cursor,
    )


@router.get(
    "/versions/{memory_version_id}/replay",
    response_model=MemoryReplayResponse,
)
async def replay_memory_version(
    memory_version_id: UUID,
    scope: ScopeDep,
    session: SessionDep,
) -> MemoryReplayResponse:
    try:
        result = await _service(session).replay_version(
            policy=_policy(scope),
            memory_version_id=memory_version_id,
            trace_id=scope.trace_id,
        )
    except MemoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail="memory version not found") from exc
    return MemoryReplayResponse(
        target=_version_summary(result.target),
        content=result.content,
        lineage=[_version_summary(version) for version in result.lineage],
    )


@router.post(
    "/diffs",
    response_model=MemoryDiffResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def diff_memory_versions(
    request: MemoryDiffRequest,
    scope: ScopeDep,
    session: SessionDep,
) -> MemoryDiffResponse:
    try:
        result = await _service(session).diff_versions(
            policy=_policy(scope),
            base_memory_version_id=request.base_memory_version_id,
            compare_memory_version_id=request.compare_memory_version_id,
            trace_id=scope.trace_id,
        )
    except MemoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail="memory version not found") from exc
    except MemoryInvalidRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MemoryDiffResponse(
        base=_version_summary(result.base),
        compare=_version_summary(result.compare),
        additions=[_diff_entry(entry) for entry in result.additions],
        removals=[_diff_entry(entry) for entry in result.removals],
        changes=[_diff_entry(entry) for entry in result.changes],
    )


@router.get("/audit", response_model=MemoryAuditResponse)
async def list_memory_audit(
    scope: ScopeDep,
    session: SessionDep,
    memory_scope_id: UUID | None = None,
    memory_version_id: UUID | None = None,
    workflow_run_id: UUID | None = None,
    action_type: ApiAuditAction | None = None,
    outcome: ApiAuditOutcome | None = None,
    base_memory_version_id: UUID | None = None,
    compare_memory_version_id: UUID | None = None,
    limit: int = 100,
) -> MemoryAuditResponse:
    events = await _service(session).list_audit(
        policy=_policy(scope),
        memory_scope_id=memory_scope_id,
        memory_version_id=memory_version_id,
        workflow_run_id=workflow_run_id,
        action_type=MemoryAuditAction(action_type.value) if action_type else None,
        outcome=MemoryAuditOutcome(outcome.value) if outcome else None,
        base_memory_version_id=base_memory_version_id,
        compare_memory_version_id=compare_memory_version_id,
        limit=limit,
    )
    return MemoryAuditResponse(
        events=[
            ApiAuditEvent.model_validate(event, from_attributes=True)
            for event in events
        ]
    )


def _runtime_source(source: ApiRuntimeSourceRef | None) -> RuntimeSourceRef:
    if source is None:
        return RuntimeSourceRef()
    return RuntimeSourceRef(
        workflow_run_id=source.workflow_run_id,
        run_step_id=source.run_step_id,
        run_bundle_id=source.run_bundle_id,
        bundle_digest=source.bundle_digest,
        run_lineage_id=source.run_lineage_id,
    )


def _scope_response(
    identity: MemoryScopeIdentity, memory_scope_id: UUID | None
) -> MemoryScopeRef:
    return MemoryScopeRef(
        memory_scope_id=memory_scope_id,
        workflow_lineage_id=identity.workflow_lineage_id,
        agent_key=identity.agent_key,
        memory_key=identity.memory_key,
    )


def _source_response(source: RuntimeSourceRef) -> ApiRuntimeSourceRef:
    return ApiRuntimeSourceRef(
        workflow_run_id=source.workflow_run_id,
        run_step_id=source.run_step_id,
        run_bundle_id=source.run_bundle_id,
        bundle_digest=source.bundle_digest,
        run_lineage_id=source.run_lineage_id,
    )


def _version_summary(version: MemoryVersion) -> MemoryVersionSummary:
    return MemoryVersionSummary(
        memory_version_id=version.memory_version_id,
        memory_scope_id=version.memory_scope_id,
        previous_memory_version_id=version.previous_memory_version_id,
        version_sequence=version.version_sequence,
        content_sha256=version.content_sha256,
        change_summary_redacted=version.change_summary_redacted,
        source=_source_response(version.source),
        created_at=version.created_at,
    )


def _version_response(version: MemoryVersion) -> MemoryVersionResponse:
    return MemoryVersionResponse(
        **_version_summary(version).model_dump(),
        scope=MemoryScopeRef(
            memory_scope_id=version.memory_scope_id,
            workflow_lineage_id=version.workflow_lineage_id,
            agent_key=version.agent_key,
            memory_key=version.memory_key,
        ),
        content=version.content,
    )


def _diff_entry(entry: DomainMemoryDiffEntry) -> MemoryDiffEntry:
    return MemoryDiffEntry(
        path=entry.path,
        before=entry.before,
        after=entry.after,
    )
