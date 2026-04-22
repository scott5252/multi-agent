from __future__ import annotations

from pathlib import Path

from multi_agent_platform.storage.base import ArtifactHandle
from multi_agent_platform.storage.providers.filesystem import FilesystemStorageProvider


class S3StorageProvider(FilesystemStorageProvider):
    provider_name = "s3"

    def __init__(self, bucket: str, root: Path) -> None:
        self.bucket = bucket
        super().__init__(root=root / bucket)

    async def put(self, key: str, payload: bytes) -> ArtifactHandle:
        handle = await super().put(key, payload)
        return handle.model_copy(
            update={
                "provider": self.provider_name,
                "url": f"s3://{self.bucket}/{key}",
            }
        )
