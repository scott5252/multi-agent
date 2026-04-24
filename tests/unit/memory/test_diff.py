from __future__ import annotations

from multi_agent_platform.memory.diff import diff_json


def test_diff_reports_additions_removals_changes_and_arrays() -> None:
    additions, removals, changes = diff_json(
        {"name": "old", "remove": True, "items": [1, 2]},
        {"name": "new", "added": None, "items": [1, 3, 4]},
    )

    assert [entry.path for entry in additions] == ["/added", "/items/2"]
    assert [entry.path for entry in removals] == ["/remove"]
    assert [entry.path for entry in changes] == ["/items/1", "/name"]


def test_diff_distinguishes_removal_marker_from_null() -> None:
    _, _, changes = diff_json(
        {"field": None}, {"field": {"$memory_removed": ["field"]}}
    )

    assert changes[0].path == "/field"
