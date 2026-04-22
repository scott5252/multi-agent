from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class ArtifactHandle(BaseModel):
    provider: str
    key: str
    url: str
    size_bytes: int


class StorageProvider(ABC):
    provider_name: str

    @abstractmethod
    async def put(self, key: str, payload: bytes) -> ArtifactHandle:
        raise NotImplementedError

    @abstractmethod
    async def get(self, key: str) -> bytes:
        raise NotImplementedError
