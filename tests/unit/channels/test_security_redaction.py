from __future__ import annotations

from multi_agent_platform.channels.models import ChannelActor, ChannelType
from multi_agent_platform.channels.normalization import normalize_channel_request


def test_channel_source_metadata_redacts_secret_like_keys() -> None:
    actor = ChannelActor(None, "user-1", ChannelType.TELEGRAM, "trace-1")
    request = normalize_channel_request(
        actor=actor,
        action_type="status",
        input_payload={"run_id": "run-1"},
        source_metadata={
            "telegram_token": "secret",
            "nested": {"authorization": "bearer"},
        },
    )

    assert request.source_metadata["telegram_token"] == "***REDACTED***"
    assert request.source_metadata["nested"] == {"authorization": "***REDACTED***"}
