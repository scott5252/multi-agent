from __future__ import annotations

from dataclasses import dataclass

from multi_agent_platform.channels.models import (
    ArtifactMetadata,
    RunResult,
    RunStatusView,
    TimelineEvent,
)


@dataclass(slots=True, frozen=True)
class RunDetailsViewModel:
    status: RunStatusView
    timeline: tuple[TimelineEvent, ...]
    result: RunResult
    artifacts: tuple[ArtifactMetadata, ...]
    support_trace_id: str


def build_run_details_model(
    *,
    status: RunStatusView,
    timeline: list[TimelineEvent],
    result: RunResult,
    artifacts: list[ArtifactMetadata],
) -> RunDetailsViewModel:
    return RunDetailsViewModel(
        status=status,
        timeline=tuple(timeline),
        result=result,
        artifacts=tuple(artifacts),
        support_trace_id=status.trace_id,
    )
