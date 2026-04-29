from __future__ import annotations

from hashlib import sha256

import pytest

from multi_agent_platform.admin.skill_registry.artifact_store import (
    ArtifactChecksumError,
    ContentAddressedSkillArtifactStore,
)


def test_artifact_store_writes_content_addressed_bytes(tmp_path) -> None:
    store = ContentAddressedSkillArtifactStore(tmp_path)
    content = b"safe skill artifact"

    artifact = store.write_bytes(
        slug="calendar-assistant",
        semantic_version="1.2.3",
        purpose="package",
        content=content,
    )

    assert artifact.digest == "sha256:" + sha256(content).hexdigest()
    assert store.read_bytes(artifact.storage_key) == content


def test_artifact_store_rejects_checksum_mismatch(tmp_path) -> None:
    store = ContentAddressedSkillArtifactStore(tmp_path)

    with pytest.raises(ArtifactChecksumError):
        store.write_bytes(
            slug="calendar-assistant",
            semantic_version="1.2.3",
            purpose="package",
            content=b"content",
            expected_digest="sha256:nope",
        )
