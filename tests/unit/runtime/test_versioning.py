from __future__ import annotations

from multi_agent_platform.runtime.versioning import get_version_bundle


def test_version_bundle_uses_settings(settings) -> None:
    bundle = get_version_bundle(settings)
    assert bundle.commit_sha == "test-sha"
    assert bundle.service == settings.app_name
