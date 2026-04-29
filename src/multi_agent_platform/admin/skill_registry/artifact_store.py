from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path


class ArtifactChecksumError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class StoredSkillArtifact:
    artifact_id: str
    storage_key: str
    digest: str
    size_bytes: int
    media_type: str


class ContentAddressedSkillArtifactStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def write_bytes(
        self,
        *,
        slug: str,
        semantic_version: str,
        purpose: str,
        content: bytes,
        media_type: str = "application/octet-stream",
        expected_digest: str | None = None,
    ) -> StoredSkillArtifact:
        digest = "sha256:" + sha256(content).hexdigest()
        if expected_digest is not None and expected_digest != digest:
            raise ArtifactChecksumError("artifact checksum mismatch")
        key = f"skill-registry/{slug}/{semantic_version}/{purpose}/{digest[7:]}"
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(content)
        elif path.read_bytes() != content:
            raise ArtifactChecksumError("content-addressed key collision")
        return StoredSkillArtifact(
            artifact_id=digest[7:39],
            storage_key=key,
            digest=digest,
            size_bytes=len(content),
            media_type=media_type,
        )

    def read_bytes(self, storage_key: str) -> bytes:
        return (self.root / storage_key).read_bytes()
