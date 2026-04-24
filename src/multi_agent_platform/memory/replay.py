from __future__ import annotations

from multi_agent_platform.memory.canonical import JsonValue
from multi_agent_platform.memory.models import MemoryReplayResult, MemoryVersion


def build_replay_result(
    *, target: MemoryVersion, lineage: list[MemoryVersion]
) -> MemoryReplayResult:
    ordered = tuple(sorted(lineage, key=lambda version: version.version_sequence))
    if target.content is None:
        raise ValueError("replay target must include content")
    if not ordered or ordered[-1].memory_version_id != target.memory_version_id:
        ordered = (*ordered, target)
    _assert_lineage(target=target, lineage=ordered)
    return MemoryReplayResult(target=target, content=target.content, lineage=ordered)


def _assert_lineage(
    *, target: MemoryVersion, lineage: tuple[MemoryVersion, ...]
) -> None:
    expected_previous = None
    for version in lineage:
        if version.memory_scope_id != target.memory_scope_id:
            raise ValueError("replay lineage contains an incompatible scope")
        if version.previous_memory_version_id != expected_previous:
            raise ValueError("replay lineage is not contiguous")
        expected_previous = version.memory_version_id


def replay_content(target: MemoryVersion) -> JsonValue:
    if target.content is None:
        raise ValueError("replay target must include content")
    return target.content
