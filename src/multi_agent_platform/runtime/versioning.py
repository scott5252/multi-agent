from __future__ import annotations

import platform

from pydantic import BaseModel

from multi_agent_platform.config.settings import Settings


class VersionBundle(BaseModel):
    service: str
    version: str
    commit_sha: str
    build_time: str
    python_version: str


def get_version_bundle(settings: Settings) -> VersionBundle:
    return VersionBundle(
        service=settings.app_name,
        version=settings.app_version,
        commit_sha=settings.commit_sha,
        build_time=settings.build_time,
        python_version=platform.python_version(),
    )
