from __future__ import annotations

from dataclasses import dataclass

from multi_agent_platform.api.ui.admin_console import FilterProfile, filter_profiles
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


@dataclass(slots=True, frozen=True)
class RunSearchPageModel:
    title: str = "Workflow Runs"
    audit_mode: bool = True


@dataclass(slots=True, frozen=True)
class RunReplayPageModel:
    workflow_run_id: str
    title: str = "Run Replay"


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


def build_run_search_model() -> RunSearchPageModel:
    return RunSearchPageModel()


def build_run_replay_model(*, workflow_run_id: str) -> RunReplayPageModel:
    return RunReplayPageModel(workflow_run_id=workflow_run_id)


def run_inspection_filter_profile() -> FilterProfile:
    return filter_profiles()["run_inspection"]
