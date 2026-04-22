from __future__ import annotations

import asyncio
from pathlib import Path

from multi_agent_platform.storage.base import ArtifactHandle, StorageProvider


class FilesystemStorageProvider(StorageProvider):
    provider_name = "filesystem"

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    async def put(self, key: str, payload: bytes) -> ArtifactHandle:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(path.write_bytes, payload)
        return ArtifactHandle(
            provider=self.provider_name,
            key=key,
            url=path.resolve().as_uri(),
            size_bytes=len(payload),
        )

    async def get(self, key: str) -> bytes:
        path = self.root / key
        return await asyncio.to_thread(path.read_bytes)
