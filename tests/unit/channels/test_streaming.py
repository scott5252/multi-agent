from __future__ import annotations

import pytest

from multi_agent_platform.channels.models import (
    TimelineEvent,
    TimelineEventType,
    UserVisibleRunState,
)
from multi_agent_platform.channels.streaming import (
    format_sse_event,
    stream_timeline_events,
)


@pytest.mark.asyncio
async def test_streaming_formats_events_and_heartbeat() -> None:
    event = TimelineEvent(
        sequence=1,
        event_type=TimelineEventType.PROGRESS,
        state=UserVisibleRunState.RUNNING,
        summary="Working",
        trace_id="trace-1",
    )

    assert "event: progress" in format_sse_event(event)
    chunks = [
        chunk async for chunk in stream_timeline_events([event], heartbeat_seconds=5)
    ]

    assert chunks[0].startswith("id: 1")
    assert "heartbeat" in chunks[1]
