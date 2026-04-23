from __future__ import annotations

from multi_agent_platform.runtime.versioning import (
    build_run_version_bundle,
    get_version_bundle,
    get_workflow_registry_compiler_version,
)
from multi_agent_platform.runtime.workflow_bundle import CompiledWorkflowBundle


def test_version_bundle_uses_settings(settings) -> None:
    bundle = get_version_bundle(settings)
    assert bundle.commit_sha == "test-sha"
    assert bundle.service == settings.app_name


def test_workflow_registry_compiler_version_has_stable_prefix() -> None:
    assert get_workflow_registry_compiler_version().startswith("workflow-registry-")


def test_build_run_version_bundle_preserves_exact_dependency_versions() -> None:
    compiled_bundle = CompiledWorkflowBundle(
        workflow_lineage_id="lineage-123",
        source_revision_sha256="sha-123",
        workflow_key="customer-intake",
        workflow_kind="main_workflow",
        version_sequence=4,
        display_version="v4",
        compiler_version="workflow-registry-0.2",
        dependencies={
            "skills": [
                {
                    "binding_key": "triage-skill",
                    "skill_slug": "triage-agent",
                    "skill_version": "2026.04.1",
                }
            ],
            "subworkflows": [
                {
                    "alias": "document-extraction",
                    "workflow_version_ref": "version-456",
                }
            ],
            "contracts": [],
        },
        run_version_blueprint={
            "entry_node_key": "triage-node",
        },
        document={"entry_node_key": "triage-node"},
    )

    run_bundle = build_run_version_bundle(
        workflow_version_bundle_id="version-123",
        compiled_bundle=compiled_bundle,
    )

    assert run_bundle.compiler_version == "workflow-registry-0.2"
    assert run_bundle.pinned_skill_versions == {"triage-agent": "2026.04.1"}
    assert run_bundle.subworkflow_version_refs == {"document-extraction": "version-456"}
