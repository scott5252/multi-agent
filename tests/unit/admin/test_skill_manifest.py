from __future__ import annotations

import pytest

from multi_agent_platform.admin.skill_registry.manifest import (
    SkillManifest,
    canonical_manifest_digest,
)
from tests.fixtures.skill_registry import (
    invalid_entrypoint_manifest,
    invalid_secret_manifest,
    valid_skill_manifest,
)


def test_skill_manifest_accepts_declarative_approved_tool_ref() -> None:
    manifest = SkillManifest.model_validate(valid_skill_manifest())

    assert manifest.slug == "calendar-assistant"
    assert manifest.entrypoint.type == "approved_tool_ref"
    assert canonical_manifest_digest(manifest).startswith("sha256:")


@pytest.mark.parametrize(
    "field,value",
    [
        ("semantic_version", "1.2"),
        ("semantic_version", "latest"),
    ],
)
def test_skill_manifest_rejects_malformed_semver(field: str, value: str) -> None:
    payload = valid_skill_manifest()
    payload[field] = value

    with pytest.raises(ValueError):
        SkillManifest.model_validate(payload)


def test_skill_manifest_rejects_executable_entrypoints() -> None:
    with pytest.raises(ValueError):
        SkillManifest.model_validate(invalid_entrypoint_manifest())


def test_skill_manifest_rejects_secret_like_material() -> None:
    with pytest.raises(ValueError):
        SkillManifest.model_validate(invalid_secret_manifest())
