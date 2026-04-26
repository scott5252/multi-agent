from __future__ import annotations

from pathlib import Path

MIGRATION = Path("alembic/versions/0007_model_skill_routing.py")


def test_model_skill_migration_declares_required_tables_indexes_and_downgrade() -> None:
    source = MIGRATION.read_text()

    for table in (
        "model_provider_catalog_entries",
        "model_routing_versions",
        "prompt_reference_versions",
        "skill_binding_versions",
        "allowed_tool_policy_versions",
        "outbound_domain_policy_versions",
        "model_skill_secret_reference_versions",
        "tool_credential_requirement_versions",
        "active_configuration_pointers",
        "resolved_execution_configurations",
        "runtime_policy_decisions",
        "configuration_audit_records",
        "configuration_rollback_records",
        "run_configuration_migration_records",
    ):
        assert f'op.create_table(\n        "{table}"' in source
        assert f'op.drop_table("{table}")' in source

    assert "ix_active_configuration_pointer_singleton" in source
    assert "ix_runtime_policy_decisions_idempotency" in source
    assert "ix_resolved_execution_configuration_run" in source
    assert "scope_hash" in source
