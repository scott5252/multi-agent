from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from multi_agent_platform.channels.errors import ChannelError
from multi_agent_platform.channels.models import (
    ArtifactDownloadGrant,
    ArtifactMetadata,
    ChannelActor,
    ChannelRun,
    ErrorCategory,
)


def default_artifact_for_run(run_id: UUID) -> ArtifactMetadata:
    return ArtifactMetadata(
        artifact_id=uuid4(),
        name=f"run-{run_id}-summary.json",
        user_facing_type="application/json",
        size_bytes=256,
    )


def create_artifact_grant(
    *,
    run: ChannelRun,
    actor: ChannelActor,
    artifact_id: UUID,
    ttl_seconds: int,
) -> ArtifactDownloadGrant:
    artifact = next(
        (
            candidate
            for candidate in run.artifacts
            if candidate.artifact_id == artifact_id
        ),
        None,
    )
    if artifact is None or artifact.status != "available":
        raise ChannelError(ErrorCategory.ARTIFACT_UNAVAILABLE, trace_id=actor.trace_id)
    expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
    return ArtifactDownloadGrant(
        artifact_id=artifact.artifact_id,
        download_url=(
            f"/runs/{run.run_id}/artifacts/{artifact.artifact_id}/download/"
            f"{uuid4()}?expires={int(expires_at.timestamp())}"
        ),
        expires_at=expires_at,
        trace_id=actor.trace_id,
    )
