from __future__ import annotations

from multi_agent_platform.runtime.versioning import (
    get_version_bundle,
    get_workflow_registry_compiler_version,
)


def test_version_bundle_uses_settings(settings) -> None:
    bundle = get_version_bundle(settings)
    assert bundle.commit_sha == "test-sha"
    assert bundle.service == settings.app_name


def test_workflow_registry_compiler_version_has_stable_prefix() -> None:
    assert get_workflow_registry_compiler_version().startswith("workflow-registry-")
