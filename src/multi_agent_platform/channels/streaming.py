from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Iterable

from multi_agent_platform.channels.models import TimelineEvent


def format_sse_event(event: TimelineEvent) -> str:
    payload = {
        "event_id": str(event.event_id),
        "sequence": event.sequence,
        "event_type": event.event_type.value,
        "state": event.state.value,
        "summary": event.summary,
        "severity": event.severity.value,
        "occurred_at": event.occurred_at.isoformat(),
        "trace_id": event.trace_id,
    }
    return (
        f"id: {event.sequence}\n"
        f"event: {event.event_type.value}\n"
        f"data: {json.dumps(payload, default=str)}\n\n"
    )


async def stream_timeline_events(
    events: Iterable[TimelineEvent], *, heartbeat_seconds: float
) -> AsyncIterator[str]:
    for event in events:
        yield format_sse_event(event)
    await asyncio.sleep(0)
    yield f'event: heartbeat\ndata: {{"interval": {heartbeat_seconds}}}\n\n'
