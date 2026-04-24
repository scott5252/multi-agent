from __future__ import annotations

from multi_agent_platform.memory.canonical import JsonValue
from multi_agent_platform.memory.models import MemoryDiffEntry


def diff_json(
    base: JsonValue, compare: JsonValue
) -> tuple[
    tuple[MemoryDiffEntry, ...],
    tuple[MemoryDiffEntry, ...],
    tuple[MemoryDiffEntry, ...],
]:
    additions: list[MemoryDiffEntry] = []
    removals: list[MemoryDiffEntry] = []
    changes: list[MemoryDiffEntry] = []
    _walk("", base, compare, additions, removals, changes)
    return tuple(additions), tuple(removals), tuple(changes)


def _walk(
    path: str,
    base: JsonValue,
    compare: JsonValue,
    additions: list[MemoryDiffEntry],
    removals: list[MemoryDiffEntry],
    changes: list[MemoryDiffEntry],
) -> None:
    if base == compare:
        return
    if isinstance(base, dict) and isinstance(compare, dict):
        base_keys = set(base)
        compare_keys = set(compare)
        for key in sorted(compare_keys - base_keys):
            additions.append(MemoryDiffEntry(path=_join(path, key), after=compare[key]))
        for key in sorted(base_keys - compare_keys):
            removals.append(MemoryDiffEntry(path=_join(path, key), before=base[key]))
        for key in sorted(base_keys & compare_keys):
            _walk(
                _join(path, key),
                base[key],
                compare[key],
                additions,
                removals,
                changes,
            )
        return
    if isinstance(base, list) and isinstance(compare, list):
        shared = min(len(base), len(compare))
        for index in range(shared):
            _walk(
                f"{path}/{index}",
                base[index],
                compare[index],
                additions,
                removals,
                changes,
            )
        for index in range(shared, len(compare)):
            additions.append(
                MemoryDiffEntry(path=f"{path}/{index}", after=compare[index])
            )
        for index in range(shared, len(base)):
            removals.append(MemoryDiffEntry(path=f"{path}/{index}", before=base[index]))
        return
    changes.append(MemoryDiffEntry(path=path or "/", before=base, after=compare))


def _join(path: str, key: str) -> str:
    escaped = key.replace("~", "~0").replace("/", "~1")
    return f"{path}/{escaped}" if path else f"/{escaped}"
