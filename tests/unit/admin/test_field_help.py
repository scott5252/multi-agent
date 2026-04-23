from __future__ import annotations

from multi_agent_platform.admin.workflow_registry.field_help import (
    build_editor_metadata,
)


def test_field_help_metadata_covers_core_authoring_fields() -> None:
    metadata = build_editor_metadata()
    assert "scope_type" in metadata.field_help
    assert "roles[].skill_bindings[].skill_version" in metadata.field_help
    assert (
        metadata.field_help["approval_gates[].approver_scope"].title == "Approval Scope"
    )


def test_editor_section_order_matches_expected_flow() -> None:
    metadata = build_editor_metadata()
    assert metadata.section_order[:3] == [
        "Overview",
        "Roles And Skills",
        "Contracts",
    ]
