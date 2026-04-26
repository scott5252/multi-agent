from __future__ import annotations

import pytest

from multi_agent_platform.channels.errors import ChannelError
from multi_agent_platform.channels.idempotency import (
    IdempotencyStatus,
    InMemoryIdempotencyStore,
    request_fingerprint,
)
from multi_agent_platform.channels.models import ChannelActor, ChannelType


def test_matching_replay_returns_stored_outcome() -> None:
    actor = ChannelActor(None, "user-1", ChannelType.WEB_API, "trace-1")
    store = InMemoryIdempotencyStore()
    fingerprint = request_fingerprint({"input": "same"})

    assert (
        store.get_or_reserve(
            actor=actor,
            action_type="invoke",
            idempotency_key="idem-1",
            fingerprint=fingerprint,
        )
        is None
    )
    store.store(
        actor=actor,
        action_type="invoke",
        idempotency_key="idem-1",
        fingerprint=fingerprint,
        response={"run_id": "run-1"},
    )
    replay = store.get_or_reserve(
        actor=actor,
        action_type="invoke",
        idempotency_key="idem-1",
        fingerprint=fingerprint,
    )

    assert replay is not None
    assert replay.status == IdempotencyStatus.ACCEPTED
    assert replay.response == {"run_id": "run-1"}


def test_conflicting_replay_raises_channel_error() -> None:
    actor = ChannelActor(None, "user-1", ChannelType.WEB_API, "trace-1")
    store = InMemoryIdempotencyStore()
    store.get_or_reserve(
        actor=actor,
        action_type="invoke",
        idempotency_key="idem-1",
        fingerprint=request_fingerprint({"input": "one"}),
    )

    with pytest.raises(ChannelError):
        store.get_or_reserve(
            actor=actor,
            action_type="invoke",
            idempotency_key="idem-1",
            fingerprint=request_fingerprint({"input": "two"}),
        )
