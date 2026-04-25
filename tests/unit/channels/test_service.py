from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.channels.errors import ChannelError
from multi_agent_platform.channels.models import (
    ChannelActor,
    ChannelType,
    PromptAction,
    ResultAvailability,
    UserVisibleRunState,
)
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.config.settings import Settings


def make_service() -> ChannelService:
    return ChannelService(settings=Settings(_env_file=None, app_env="test"))


def make_actor() -> ChannelActor:
    return ChannelActor(uuid4(), "tenant-user", ChannelType.WEB_API, "trace-1")


@pytest.mark.asyncio
async def test_start_status_timeline_and_idempotent_replay() -> None:
    service = make_service()
    actor = make_actor()

    first = await service.start_run(
        actor=actor,
        workflow_id="demo-workflow",
        inputs={"topic": "demo"},
        idempotency_key="idem-start-1",
    )
    replay = await service.start_run(
        actor=actor,
        workflow_id="demo-workflow",
        inputs={"topic": "demo"},
        idempotency_key="idem-start-1",
    )

    status = service.get_status(actor=actor, run_id=first.run_id)
    timeline, next_cursor = service.list_timeline(
        actor=actor,
        run_id=first.run_id,
        cursor=None,
        limit=100,
    )

    assert replay.run_id == first.run_id
    assert status.state == UserVisibleRunState.QUEUED
    assert timeline[0].event_type.value == "run_queued"
    assert next_cursor is None


@pytest.mark.asyncio
async def test_waiting_prompt_decision_and_stale_response() -> None:
    service = make_service()
    actor = make_actor()
    result = await service.start_run(
        actor=actor,
        workflow_id="approval-demo",
        inputs={"topic": "demo", "_channel_state": "waiting"},
        idempotency_key="idem-start-waiting",
    )
    status = service.get_status(actor=actor, run_id=result.run_id)
    assert status.waiting_prompt is not None

    decision = service.decide_prompt(
        actor=actor,
        run_id=result.run_id,
        prompt_id=status.waiting_prompt.prompt_id,
        action=PromptAction.APPROVE,
        prompt_version=status.waiting_prompt.prompt_version,
        decision_payload={},
        idempotency_key="idem-decision-1",
    )
    stale = service.decide_prompt(
        actor=actor,
        run_id=result.run_id,
        prompt_id=status.waiting_prompt.prompt_id,
        action=PromptAction.APPROVE,
        prompt_version=status.waiting_prompt.prompt_version,
        decision_payload={},
        idempotency_key="idem-decision-2",
    )

    assert decision.accepted is True
    assert decision.run_status.state == UserVisibleRunState.RUNNING
    assert stale.accepted is False


@pytest.mark.asyncio
async def test_result_artifact_subscription_callback_and_cancel() -> None:
    service = make_service()
    actor = make_actor()
    result = await service.start_run(
        actor=actor,
        workflow_id="completed-demo",
        inputs={"topic": "demo", "_channel_state": "completed"},
        idempotency_key="idem-start-complete",
    )

    run_result = service.get_result(actor=actor, run_id=result.run_id)
    artifacts = service.list_artifacts(actor=actor, run_id=result.run_id)
    subscription = service.subscribe(
        actor=actor,
        run_id=result.run_id,
        channel=ChannelType.WEB_API,
        event_types=("terminal",),
        idempotency_key="idem-sub-1",
    )
    callback = service.register_callback(
        actor=actor,
        run_id=result.run_id,
        callback_url="https://example.test/callback",
        event_types=("terminal",),
        idempotency_key="idem-callback-1",
    )
    grant = service.create_artifact_download_url(
        actor=actor,
        run_id=result.run_id,
        artifact_id=artifacts[0].artifact_id,
        idempotency_key="idem-artifact-1",
    )

    assert run_result.availability == ResultAvailability.AVAILABLE
    assert subscription.status == "active"
    assert callback.status == "active"
    assert str(artifacts[0].artifact_id) in grant.download_url

    with pytest.raises(ChannelError):
        await service.cancel_run(
            actor=actor,
            run_id=result.run_id,
            reason="too late",
            idempotency_key="idem-cancel-terminal",
        )


@pytest.mark.asyncio
async def test_cross_tenant_and_rate_limit_denials() -> None:
    settings = Settings(
        _env_file=None,
        app_env="test",
        channel_rate_limit_per_minute=1,
    )
    service = ChannelService(settings=settings)
    actor = make_actor()
    other_actor = ChannelActor(uuid4(), "other", ChannelType.WEB_API, "trace-2")
    result = await service.start_run(
        actor=actor,
        workflow_id="demo",
        inputs={"topic": "demo"},
        idempotency_key="idem-rate-1",
    )

    with pytest.raises(ChannelError):
        service.get_status(actor=other_actor, run_id=result.run_id)

    with pytest.raises(ChannelError):
        await service.start_run(
            actor=actor,
            workflow_id="demo-two",
            inputs={"topic": "demo"},
            idempotency_key="idem-rate-2",
        )
