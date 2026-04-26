from __future__ import annotations

import pytest

from multi_agent_platform.channels.errors import ChannelError
from multi_agent_platform.channels.models import ChannelActor, ChannelType
from multi_agent_platform.channels.normalization import normalize_channel_request


def test_normalization_redacts_source_metadata_and_requires_idempotency() -> None:
    actor = ChannelActor(None, "user-1", ChannelType.WEB_API, "trace-1")
    request = normalize_channel_request(
        actor=actor,
        action_type="status",
        input_payload={"run_id": "run-1"},
        source_metadata={"telegram_token": "secret", "safe": "ok"},
    )

    assert request.source_metadata["telegram_token"] == "***REDACTED***"
    assert request.source_metadata["safe"] == "ok"

    with pytest.raises(ChannelError):
        normalize_channel_request(
            actor=actor,
            action_type="invoke",
            input_payload={"workflow": "demo"},
        )
