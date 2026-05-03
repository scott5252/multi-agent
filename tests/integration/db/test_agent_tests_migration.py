from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_agent_test_bench_migration_creates_tables(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "agent-test-migration.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    config = Config(str(Path("alembic.ini").resolve()))
    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database_path}")
    tables = set(inspect(engine).get_table_names())

    assert {
        "agent_test_suites",
        "agent_test_cases",
        "agent_test_assertions",
        "agent_test_runs",
        "agent_test_run_steps",
        "agent_test_publication_requirements",
    } <= tables
