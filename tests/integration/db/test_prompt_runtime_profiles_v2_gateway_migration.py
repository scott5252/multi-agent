from __future__ import annotations

from pathlib import Path

MIGRATION = Path(
    "alembic/versions/0013_prompt_runtime_profiles_v2_gateway_operations.py"
)


def test_prompt_runtime_profiles_v2_gateway_migration_is_additive() -> None:
    source = MIGRATION.read_text()

    for table in (
        "gateway_operations",
        "gateway_physical_attempts",
        "provider_probe_operations",
        "catalog_sync_operations",
    ):
        assert f'op.create_table(\n        "{table}"' in source
        assert f'op.drop_table("{table}")' in source

    assert "ix_gateway_operations_identity" in source
    assert "ix_gateway_physical_attempts_operation_number" in source
    assert "ix_provider_probe_operations_identity" in source
    assert "ix_catalog_sync_operations_identity" in source
    assert 'op.drop_table("prompt_versions")' not in source
    assert 'op.drop_table("agent_profile_versions")' not in source
