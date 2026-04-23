from __future__ import annotations

from multi_agent_platform.admin.workflow_registry.compiler import (
    compile_workflow_blueprint,
)
from multi_agent_platform.admin.workflow_registry.sharing import (
    can_grant_workflow_version_to_tenant,
    sharing_visibility_label,
)
from multi_agent_platform.runtime.versioning import build_run_version_bundle


def test_compile_workflow_blueprint_preserves_document_metadata(
    sample_workflow_document,
) -> None:
    bundle = compile_workflow_blueprint(
        workflow_lineage_id="lineage-123",
        revision_sha256="abc123",
        document=sample_workflow_document,
        version_sequence=2,
        display_version="v2",
        compiler_version="workflow-registry-0.2",
    )

    assert bundle.workflow_lineage_id == "lineage-123"
    assert bundle.source_revision_sha256 == "abc123"
    assert bundle.workflow_key == sample_workflow_document.workflow_key
    assert bundle.workflow_kind == "main_workflow"
    assert bundle.document["display_name"] == sample_workflow_document.display_name
    assert bundle.display_version == "v2"
    assert bundle.version_sequence == 2
    assert bundle.dependencies["skills"][0]["binding_key"] == "triage-skill"
    assert bundle.dependencies["skills"][0]["skill_slug"] == "triage-agent"
    assert bundle.dependencies["skills"][0]["skill_version"] == "2026.04.1"
    assert bundle.dependencies["contracts"][0]["contract_key"] == "intake-request"


def test_compile_workflow_blueprint_builds_run_version_blueprint(
    sample_workflow_document,
) -> None:
    bundle = compile_workflow_blueprint(
        workflow_lineage_id="lineage-123",
        revision_sha256="abc123",
        document=sample_workflow_document,
        version_sequence=1,
        display_version="v1",
        compiler_version="workflow-registry-0.2",
    )

    run_bundle = build_run_version_bundle(
        workflow_version_bundle_id="version-123",
        compiled_bundle=bundle,
    )

    assert run_bundle.workflow_version_bundle_id == "version-123"
    assert run_bundle.workflow_lineage_id == "lineage-123"
    assert run_bundle.workflow_key == sample_workflow_document.workflow_key
    assert run_bundle.pinned_skill_versions == {"triage-agent": "2026.04.1"}
    assert run_bundle.subworkflow_version_refs == {}


def test_sharing_visibility_label_covers_platform_and_tenant() -> None:
    assert sharing_visibility_label(scope_type="platform") == "Platform"
    assert sharing_visibility_label(scope_type="tenant") == "Tenant"


def test_can_grant_workflow_version_to_tenant_requires_platform_scope() -> None:
    assert can_grant_workflow_version_to_tenant(scope_type="platform") is True
    assert can_grant_workflow_version_to_tenant(scope_type="tenant") is False
