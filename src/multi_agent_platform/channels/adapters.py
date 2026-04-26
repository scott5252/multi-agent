from __future__ import annotations

from typing import Protocol

from multi_agent_platform.channels.models import ChannelActor, ChannelType


class ChannelAdapter(Protocol):
    channel_type: ChannelType

    def actor(self) -> ChannelActor:
        """Return the platform actor resolved for this channel."""
