from __future__ import annotations

from pathlib import Path


def test_admin_console_migration_creates_saved_filters_table() -> None:
    migration = Path("alembic/versions/0010_admin_console_shell.py").read_text()

    assert "admin_saved_filters" in migration
    assert "uq_admin_saved_filters_scope_name" in migration
    assert "ck_admin_saved_filters_scope_tenant" in migration
    assert "downgrade" in migration
