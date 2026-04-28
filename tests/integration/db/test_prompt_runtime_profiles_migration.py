from __future__ import annotations

from pathlib import Path

MIGRATION = Path("alembic/versions/0012_prompt_runtime_profiles.py")


def test_prompt_runtime_profiles_migration_declares_tables_indexes_and_rollback() -> (
    None
):
    source = MIGRATION.read_text()

    for table in (
        "prompt_lineages",
        "prompt_drafts",
        "prompt_draft_revisions",
        "prompt_validation_results",
        "prompt_render_tests",
        "prompt_versions",
        "tenant_prompt_version_grants",
        "prompt_audit_records",
        "agent_runtime_profiles",
        "agent_profile_drafts",
        "agent_profile_draft_revisions",
        "agent_profile_validation_results",
        "agent_profile_versions",
        "tenant_profile_version_grants",
        "active_agent_profile_pointers",
    ):
        assert f'op.create_table(\n        "{table}"' in source
        assert f'op.drop_table("{table}")' in source

    assert "ix_prompt_lineages_scope_slug" in source
    assert "ix_prompt_versions_lineage_sequence" in source
    assert "ix_active_agent_profile_pointer_lookup" in source
    assert "ck_prompt_lineages_scope_tenant" in source
    assert "ck_agent_runtime_profiles_scope_tenant" in source
