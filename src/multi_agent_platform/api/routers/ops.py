from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from multi_agent_platform.api.deps import get_container
from multi_agent_platform.api.schemas.ops import (
    DependencyStatusResponse,
    LiveResponse,
    ReadyResponse,
    VersionResponse,
)
from multi_agent_platform.bootstrap.container import Container
from multi_agent_platform.runtime.health.models import ReadinessStatus
from multi_agent_platform.runtime.health.service import HealthService
from multi_agent_platform.runtime.versioning import get_version_bundle

router = APIRouter(tags=["operations"])
ContainerDep = Annotated[Container, Depends(get_container)]


@router.get("/health/live", response_model=LiveResponse)
async def liveness(container: ContainerDep) -> LiveResponse:
    bundle = get_version_bundle(container.settings)
    return LiveResponse(service=bundle.service, version=bundle.version)


@router.get(
    "/health/ready",
    response_model=ReadyResponse,
    responses={503: {"model": ReadyResponse}},
)
async def readiness(
    response: Response,
    container: ContainerDep,
) -> ReadyResponse:
    report = await HealthService(container).readiness()
    if report.status is ReadinessStatus.NOT_READY:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadyResponse(
        service=report.service,
        status=report.status.value,
        checks=report.checks,
        checked_at=report.checked_at,
    )


@router.get("/version", response_model=VersionResponse)
async def version(container: ContainerDep) -> VersionResponse:
    bundle = get_version_bundle(container.settings)
    return VersionResponse(**bundle.model_dump())


@router.get("/dependencies", response_model=DependencyStatusResponse)
async def dependency_status(
    container: ContainerDep,
) -> DependencyStatusResponse:
    report = await HealthService(container).dependency_status()
    return DependencyStatusResponse(**report.model_dump())
