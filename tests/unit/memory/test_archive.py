from __future__ import annotations

from multi_agent_platform.db.models.memory import MemoryArchiveEventRecord


def test_archive_event_is_separate_from_version_content() -> None:
    event = MemoryArchiveEventRecord(
        archive_reason="retention review",
        actor_principal_id="tenant-admin",
    )

    assert event.archive_reason == "retention review"
    assert not hasattr(event, "content")
