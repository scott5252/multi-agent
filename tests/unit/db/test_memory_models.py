from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.memory import MemoryVersionRecord


def test_memory_tables_are_registered() -> None:
    import_models()

    assert "memory_scopes" in Base.metadata.tables
    assert "memory_versions" in Base.metadata.tables
    assert "memory_heads" in Base.metadata.tables
    assert "memory_audit_events" in Base.metadata.tables


def test_memory_version_record_tracks_lineage_and_hash() -> None:
    version = MemoryVersionRecord(
        tenant_id=uuid4(),
        memory_scope_id=uuid4(),
        previous_memory_version_id=uuid4(),
        version_sequence=2,
        content={"ok": True},
        content_sha256="a" * 64,
        content_size_bytes=11,
        actor_principal_id="tenant-admin",
        source_type="api",
    )

    assert version.previous_memory_version_id is not None
    assert version.content_sha256 == "a" * 64
