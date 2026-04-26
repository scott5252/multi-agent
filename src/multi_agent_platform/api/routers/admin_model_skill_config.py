from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import get_session
from multi_agent_platform.api.schemas.model_skill_config import (
    ActivationRequest,
    ActivationResponse,
    ConfigVersionResponse,
    CredentialRequirementCreateRequest,
    HistoryResponse,
    ModelPreviewRequest,
    ModelPreviewResponse,
    ModelRoutingCreateRequest,
    OutboundDomainPolicyCreateRequest,
    PromptReferenceCreateRequest,
    RollbackRequest,
    RollbackResponse,
    RunProvenanceResponse,
    SecretReferenceCreateRequest,
    SkillBindingCreateRequest,
    ToolPolicyCreateRequest,
    ToolPreviewRequest,
    ToolPreviewResponse,
)
from multi_agent_platform.auth.dependencies import require_authorized_principal
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.config.model_skill import ConfigKind, ScopeSelector
from multi_agent_platform.config.resolver import ResolutionError
from multi_agent_platform.config.service import (
    ModelSkillConfigService,
    ModelSkillServiceError,
)
from multi_agent_platform.config.validation import ModelSkillValidationError
from multi_agent_platform.db.repositories.model_skill_config import (
    ModelSkillConfigRepository,
)

router = APIRouter(prefix="/admin/config", tags=["model-skill-config"])
PrincipalDep = Annotated[PrincipalContext, Depends(require_authorized_principal)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
RequiredTenantQuery = Annotated[UUID, Query()]
OptionalWorkflowQuery = Annotated[UUID | None, Query()]
OptionalConfigKindQuery = Annotated[ConfigKind | None, Query()]
LimitQuery = Annotated[int, Query(ge=1, le=100)]
OptionalTextQuery = Annotated[str | None, Query()]


def _service(session: AsyncSession) -> ModelSkillConfigService:
    return ModelSkillConfigService(
        repository=ModelSkillConfigRepository(session),
    )


def _to_http_error(exc: Exception) -> HTTPException:
    if isinstance(exc, ModelSkillServiceError | ModelSkillValidationError):
        status_code = (
            status.HTTP_403_FORBIDDEN
            if exc.category.value == "authorization_failed"
            else status.HTTP_409_CONFLICT
            if exc.category.value == "stale_configuration"
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        return HTTPException(
            status_code=status_code,
            detail={"category": exc.category.value, "message": str(exc)},
        )
    if isinstance(exc, ResolutionError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"category": exc.category.value, "message": str(exc)},
        )
    return HTTPException(status_code=500, detail=str(exc))


@router.post(
    "/model-routing",
    response_model=ConfigVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_model_routing(
    payload: ModelRoutingCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> ConfigVersionResponse:
    try:
        return await _service(session).create_model_routing(
            principal=principal,
            payload=payload,
        )
    except Exception as exc:
        raise _to_http_error(exc) from exc


@router.post(
    "/model-routing/{version_id}/activate",
    response_model=ActivationResponse,
)
async def activate_model_routing(
    version_id: UUID,
    payload: ActivationRequest,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: RequiredTenantQuery,
    workflow_lineage_id: OptionalWorkflowQuery = None,
    workflow_version_bundle_id: OptionalWorkflowQuery = None,
    agent_key: OptionalTextQuery = None,
    step_key: OptionalTextQuery = None,
) -> ActivationResponse:
    scope = ScopeSelector(
        tenant_id=tenant_id,
        workflow_lineage_id=workflow_lineage_id,
        workflow_version_bundle_id=workflow_version_bundle_id,
        agent_key=agent_key,
        step_key=step_key,
    )
    try:
        return await _service(session).activate_version(
            principal=principal,
            kind=ConfigKind.MODEL_ROUTING,
            scope=scope,
            version_id=version_id,
            reason=payload.reason,
            expected_active_version_id=payload.expected_active_version_id,
        )
    except Exception as exc:
        raise _to_http_error(exc) from exc


@router.post(
    "/prompt-references",
    response_model=ConfigVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_prompt_reference(
    payload: PromptReferenceCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> ConfigVersionResponse:
    try:
        return await _service(session).create_prompt_reference(
            principal=principal,
            payload=payload,
        )
    except Exception as exc:
        raise _to_http_error(exc) from exc


@router.post(
    "/skill-bindings",
    response_model=ConfigVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_skill_binding(
    payload: SkillBindingCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> ConfigVersionResponse:
    try:
        return await _service(session).create_skill_binding(
            principal=principal,
            payload=payload,
        )
    except Exception as exc:
        raise _to_http_error(exc) from exc


@router.post(
    "/tool-policies",
    response_model=ConfigVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tool_policy(
    payload: ToolPolicyCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> ConfigVersionResponse:
    try:
        return await _service(session).create_tool_policy(
            principal=principal,
            payload=payload,
        )
    except Exception as exc:
        raise _to_http_error(exc) from exc


@router.post(
    "/outbound-domain-policies",
    response_model=ConfigVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_outbound_policy(
    payload: OutboundDomainPolicyCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> ConfigVersionResponse:
    try:
        return await _service(session).create_outbound_policy(
            principal=principal,
            payload=payload,
        )
    except Exception as exc:
        raise _to_http_error(exc) from exc


@router.post(
    "/secret-references",
    response_model=ConfigVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_secret_reference(
    payload: SecretReferenceCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> ConfigVersionResponse:
    try:
        return await _service(session).create_secret_reference(
            principal=principal,
            payload=payload,
        )
    except Exception as exc:
        raise _to_http_error(exc) from exc


@router.post(
    "/credential-requirements",
    response_model=ConfigVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_credential_requirement(
    payload: CredentialRequirementCreateRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> ConfigVersionResponse:
    try:
        return await _service(session).create_credential_requirement(
            principal=principal,
            payload=payload,
        )
    except Exception as exc:
        raise _to_http_error(exc) from exc


@router.post("/preview/model", response_model=ModelPreviewResponse)
async def preview_model(
    payload: ModelPreviewRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> ModelPreviewResponse:
    try:
        return await _service(session).preview_model(principal=principal, scope=payload)
    except Exception as exc:
        raise _to_http_error(exc) from exc


@router.post("/preview/tool", response_model=ToolPreviewResponse)
async def preview_tool(
    payload: ToolPreviewRequest,
    principal: PrincipalDep,
    session: SessionDep,
) -> ToolPreviewResponse:
    try:
        return await _service(session).preview_tool(
            principal=principal, payload=payload
        )
    except Exception as exc:
        raise _to_http_error(exc) from exc


@router.get("/history", response_model=HistoryResponse)
async def list_history(
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: RequiredTenantQuery,
    config_kind: OptionalConfigKindQuery = None,
    limit: LimitQuery = 100,
) -> HistoryResponse:
    try:
        return await _service(session).list_history(
            principal=principal,
            tenant_id=tenant_id,
            kind=config_kind,
            limit=limit,
        )
    except Exception as exc:
        raise _to_http_error(exc) from exc


@router.get(
    "/runs/{workflow_run_id}/provenance",
    response_model=RunProvenanceResponse,
)
async def run_provenance(
    workflow_run_id: UUID,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: RequiredTenantQuery,
) -> RunProvenanceResponse:
    try:
        return await _service(session).run_provenance(
            principal=principal,
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
        )
    except Exception as exc:
        raise _to_http_error(exc) from exc


@router.post(
    "/{config_kind}/{version_id}/rollback",
    response_model=RollbackResponse,
)
async def rollback_configuration(
    config_kind: ConfigKind,
    version_id: UUID,
    payload: RollbackRequest,
    principal: PrincipalDep,
    session: SessionDep,
    tenant_id: RequiredTenantQuery,
    workflow_lineage_id: OptionalWorkflowQuery = None,
    workflow_version_bundle_id: OptionalWorkflowQuery = None,
    agent_key: OptionalTextQuery = None,
    step_key: OptionalTextQuery = None,
) -> RollbackResponse:
    scope = ScopeSelector(
        tenant_id=tenant_id,
        workflow_lineage_id=workflow_lineage_id,
        workflow_version_bundle_id=workflow_version_bundle_id,
        agent_key=agent_key,
        step_key=step_key,
    )
    if payload.expected_active_version_id is None:
        payload = payload.model_copy(update={"expected_active_version_id": version_id})
    try:
        return await _service(session).rollback_version(
            principal=principal,
            kind=config_kind,
            scope=scope,
            payload=payload,
        )
    except Exception as exc:
        raise _to_http_error(exc) from exc
