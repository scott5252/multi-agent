from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_memory_migration_creates_tables_and_indexes(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "memory-migration.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    config = Config(str(Path("alembic.ini").resolve()))

    command.upgrade(config, "head")

    engine = create_engine(f"sqlite:///{database_path}")
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    assert {
        "memory_scopes",
        "memory_versions",
        "memory_heads",
        "memory_audit_events",
        "memory_archive_events",
    } <= tables
    indexes = {index["name"] for index in inspector.get_indexes("memory_versions")}
    assert "ix_memory_versions_scope_sequence" in indexes
