from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.channels.artifacts import (
    create_artifact_grant,
    default_artifact_for_run,
)
from multi_agent_platform.channels.errors import ChannelError
from multi_agent_platform.channels.models import ChannelActor, ChannelRun, ChannelType


def test_artifact_grant_uses_short_lived_platform_url() -> None:
    actor = ChannelActor(None, "user-1", ChannelType.WEB_API, "trace-1")
    run = ChannelRun(
        run_id=uuid4(),
        tenant_id=None,
        requester_identity_id="user-1",
        channel_type=ChannelType.WEB_API,
        trace_id="trace-1",
    )
    artifact = default_artifact_for_run(run.run_id)
    run.artifacts.append(artifact)

    grant = create_artifact_grant(
        run=run,
        actor=actor,
        artifact_id=artifact.artifact_id,
        ttl_seconds=60,
    )

    assert str(run.run_id) in grant.download_url
    assert grant.trace_id == "trace-1"


def test_missing_artifact_raises_channel_error() -> None:
    actor = ChannelActor(None, "user-1", ChannelType.WEB_API, "trace-1")
    run = ChannelRun(
        run_id=uuid4(),
        tenant_id=None,
        requester_identity_id="user-1",
        channel_type=ChannelType.WEB_API,
        trace_id="trace-1",
    )

    with pytest.raises(ChannelError):
        create_artifact_grant(
            run=run,
            actor=actor,
            artifact_id=uuid4(),
            ttl_seconds=60,
        )
