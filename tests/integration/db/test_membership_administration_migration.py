from __future__ import annotations

from pathlib import Path


def test_membership_migration_revision_metadata() -> None:
    migration = Path(
        "alembic/versions/0018_user_tenant_membership_administration.py"
    ).read_text()

    assert 'revision = "0018_membership_admin"' in migration
    assert 'down_revision = "0017_telegram_config_console"' in migration
