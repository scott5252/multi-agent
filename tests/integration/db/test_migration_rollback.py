from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from multi_agent_platform.db.models.reliability import ReliabilityPolicyRecord


def test_alembic_upgrade_and_downgrade_round_trip(tmp_path, monkeypatch) -> None:
    database_path = tmp_path / "rollback.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{database_path}")
    config = Config(str(Path("alembic.ini").resolve()))
    command.upgrade(config, "head")
    command.downgrade(config, "base")
    engine = create_engine(f"sqlite:///{database_path}")
    assert "tenants" not in inspect(engine).get_table_names()
    command.upgrade(config, "head")
    assert "tenants" in inspect(engine).get_table_names()


def test_reliability_metadata_is_importable_for_migrations() -> None:
    assert ReliabilityPolicyRecord.__tablename__ == "reliability_policies"
